import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def web_search(query: str) -> str:
    """Search the internet using Tavily for research-ready content."""
    response = client.search(query=query, search_depth="advanced", max_results=5)
    results = response.get("results", [])
    return "\n\n".join(
        f"Title: {r['title']}\nURL: {r['url']}\nContent: {r['content']}"
        for r in results
    )
