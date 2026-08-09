from langchain.tools import tool
from ddgs import DDGS


@tool
def flight_search(origin: str, destination: str, travel_date: str) -> dict:
    """
    Retrieve available flights from origin to destination on a given date.
    Call this first before all other tools.
    """
    query = f"Get me all the available flights from {origin} to {destination} on {travel_date}"
    results = DDGS().text(
        query=query, region="wt-wt", safesearch="on", timelimit="7d", max_results=10
    )
    output = " ".join(
        [result.get("body", "") for result in results if "body" in result]
    )
    return {"flights": output}


@tool
def hotel_search(destination: str, travel_date: str, total_days: str) -> dict:
    """
    Retrieve available hotels in the destination area for the duration of the trip.
    Call this after flight_search and before results_comparison.
    """
    query = f"Get me all available hotels in {destination} on {travel_date}. Staying for {total_days} days"
    results = DDGS().text(
        query=query, region="wt-wt", safesearch="on", timelimit="7d", max_results=10
    )
    output = " ".join(
        [result.get("body", "") for result in results if "body" in result]
    )
    return {"hotels": output}


tools = [flight_search, hotel_search]
tools_by_name = {tool.name: tool for tool in tools}
