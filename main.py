import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.types import Command
from agent import graph

load_dotenv(override=True)


def run_trip_planner():

    config = {"configurable": {"thread_id": "trip-session-1"}}

    user_prompt = input("Enter your travel-related query:\n")

    print("\n--- Starting Trip Planner Agent ---")
    initial_input = {
        "messages": [HumanMessage(content=user_prompt)],
        "steps": 0,
        "status": "Pending",
        "user_feedback": "",
    }

    # Stream graph execution until interrupt or completion
    for event in graph.stream(initial_input, config, stream_mode="updates"):
        print(event)

    state = graph.get_state(config)

    # Check if execution was paused by human_approval interrupt
    if bool(state.tasks):
        print(f"\n[INTERRUPT]: {state.tasks[0].interrupts[0].value}")
        user_choice = input("Approve tool execution? (yes/no): ").strip()

        # Resume execution with human feedback
        resume_events = graph.stream(
            Command(resume=user_choice), config, stream_mode="updates"
        )
        for event in resume_events:
            print(event)

    final_state = graph.get_state(config).values
    print("\n--- Final Agent Response ---")
    print(final_state["messages"][-1].content)


if __name__ == "__main__":
    run_trip_planner()
