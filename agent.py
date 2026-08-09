import os
from typing import Annotated, Literal
from typing_extensions import TypedDict

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import ToolMessage, SystemMessage
from langgraph.types import interrupt, Command
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver

from tools import tools, tools_by_name

MAX_ITERATION_GUARD = 5


class State(TypedDict):
    messages: Annotated[list, add_messages]
    steps: int
    status: str
    user_feedback: str
    flights: str
    hotels: str


llm = ChatAnthropic(model="claude-haiku-4-5")
model_with_tools = llm.bind_tools(tools)


# Node Functions
def llm_call(state: State) -> dict:
    response = model_with_tools.invoke(state["messages"])
    return {"messages": [response]}


def tool_call(state: State) -> dict:
    last_message = state["messages"][-1]
    steps = state.get("steps", 0) + 1
    tool_outputs = []

    for call in last_message.tool_calls:
        tool = tools_by_name[call["name"]]
        observation = tool.invoke(call["args"])
        tool_outputs.append(
            ToolMessage(content=str(observation), tool_call_id=call["id"])
        )
    return {"messages": tool_outputs, "steps": steps}


def human_approval(state: State) -> Command[Literal["tool_call", "rejected_path"]]:
    decision = interrupt("Do you approve executing this search tool? (yes/no)")
    if str(decision).strip().lower() == "yes":
        return Command(goto="tool_call", update={"status": "Approved"})
    return Command(goto="rejected_path", update={"status": "Rejected"})


def results_comparison(state: State) -> dict:
    prompt = "You are a helpful assistant. Compare the flight and hotel options available and return the best option."
    response = llm.invoke([SystemMessage(content=prompt)] + state["messages"])
    return {"messages": [response]}


def rejected_node(state: State) -> dict:
    print("\n[Action Rejected by User]")
    return state


def should_continue(state: State) -> str:
    if state.get("steps", 0) > MAX_ITERATION_GUARD:
        print("\nReached max iteration guard limit.")
        return END
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "human_approval"
    return END


# Graph Construction
builder = StateGraph(State)
builder.add_node("llm_call", llm_call)
builder.add_node("tool_call", tool_call)
builder.add_node("human_approval", human_approval)
builder.add_node("results_comparison", results_comparison)
builder.add_node("rejected_path", rejected_node)

builder.add_edge(START, "llm_call")
builder.add_conditional_edges("llm_call", should_continue)
builder.add_edge("human_approval", "tool_call")
builder.add_edge("tool_call", "results_comparison")
builder.add_edge("results_comparison", END)
builder.add_edge("rejected_path", END)

memory = InMemorySaver()
graph = builder.compile(checkpointer=memory)
