# Human-in-the-Loop Trip Planning Agent (LangGraph + Claude)

A stateful, multi-node travel planning assistant built using **LangGraph** and **Anthropic Claude API**. The agent generates live web search queries for flights and hotels using DuckDuckGo, pauses execution for explicit human approval before running tools, and processes raw search outputs through dedicated comparison and summarization nodes.

The project includes two tools:

- **Flight Search** — fetches the available flights from the origin country to the destionation country on the specified date.
- **Hotel Search** — fetches the available hotels in the destionation country on the specified date and total number of days.

---

## The Problem

Planning a trip typically involves multiple manual search steps (flights, accommodations, itinerary synthesis) and risks unintended API costs or external actions if delegated fully to an autonomous agent. This project implements a Human-in-the-Loop (HITL) travel planner that automates the multi-step research workflow while enforcing an explicit safety pause (`interrupt()`) for user approval before triggering web search tools.

---

## Architecture Diagram

![Graph Architecture](docs/graph.png)

---

## Node Breakdown

| Node                     | Responsibilities                                                                               |
| ------------------------ | ---------------------------------------------------------------------------------------------- |
| **`llm_call`**           | Evaluates conversation state and determines if search tools are needed.                        |
| **`human_approval`**     | Pauses execution via `interrupt()` to require human user sign-off before running web searches. |
| **`tool_call`**          | Executes live DuckDuckGo web searches for flights and hotels using input parameters.           |
| **`results_comparison`** | Evaluates retrieved flight and hotel options side-by-side to extract optimal choices.          |
| **`rejected_path`**      | Handles graceful termination if the human reviewer rejects tool execution.                     |

---

## Tradeoffs & Design Decisions

- **HITL Interrupt vs. Pure Automation:** Pausing the graph at `human_approval` introduces human latency, but prevents runaway API calls and guarantees that tool parameters match user intent before external execution.
- **Specialized Extraction vs. Single-Pass Prompt:** Using separate `results_comparison` and `results_summarizer` nodes adds an extra LLM call, but separates raw analysis from presentation formatting, reducing hallucination in itinerary suggestions.
- **In-Memory Checkpointing vs. External Database:** Selected `InMemorySaver` for local session tracing without external database dependencies; production would require persistent state (e.g., PostgreSQL).

---

## What I'd Do Differently / Next Improvements

- **Tool Parameter Modification on Resume:** Allow the user not only to approve/reject, but also to edit tool call parameters (e.g., modify travel dates or destination) directly via `Command(resume=...)`.
- **Structured JSON Output:** Use `with_structured_output` in the comparison node to output structured pricing and flight schedules for downstream frontend rendering.
- **Async Parallel Search:** Run `flight_search` and `hotel_search` concurrently using `asyncio` to reduce latency.

---

## Tech stack

| Layer                       | Technology                              |
| --------------------------- | --------------------------------------- |
| LLM                         | Claude Haiku 4.5                        |
| Language                    | Python                                  |
| Framework                   | LangGraph                               |
| Web Search Tools            | DuckDuckGo Search                       |
| State Persistence           | `InMemorySaver`                         |
| Human-in-the-Loop Mechanics | `interrupt()` and `Command(resume=...)` |

---

## Project structure

```text
langgraph-trip-planner/
│
├── agent.py          # State definition, nodes, graph assembly, and checkpointer
├── tools.py          # DuckDuckGo flight and hotel search tools
├── main.py           # CLI runner & HITL interrupt resumption handling
├── requirements.txt
├── .gitignore
├── README.md
│
└── docs/
    └── graph.png     # Graph architecture diagram
```

---

## Getting started

### Prerequisites

- Python 3.10+

Needs to be updated!

### 1. Clone the repository

```bash
git clone https://github.com/SuryaPrakash-24/langgraph-trip-planner.git
cd langgraph-trip-planner
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set your Claude API key

Sign up on [platform.claude.com](https://platform.claude.com/), if not done already, and generate a new API key.

**Linux / macOS**

```bash
export ANTHROPIC_API_KEY="your_api_key_here"
```

**Windows (PowerShell)**

```powershell
setx ANTHROPIC_API_KEY "your_api_key_here"
```

Restart the terminal after setting the variable.

### 4. Run the code

```bash
python main.py
```

The inital Claude API connection takes ~10–15 seconds and the final response (after user approval) takes ~30-40 seconds.

---

## License

MIT
