import os

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain.tools import tool
from tavily import TavilyClient
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

load_dotenv()

_TAVILY = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

SEARCH_MAX_RESULTS = 5
SCRAPE_MAX_CHARS = 3000
SCRAPE_TIMEOUT = 10
USER_AGENT = "Mozilla/5.0 (compatible; ResearchMind/0.1)"
_STRIPPED_TAGS = ("script", "style", "nav", "footer", "aside", "form", "noscript")


@tool
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    reraise=True,
)
def web_search(query: str) -> str:
    """Search the web for recent, reliable information on a topic. Returns titles, URLs, and snippets."""
    results = _TAVILY.search(query=query, max_results=SEARCH_MAX_RESULTS)
    chunks = [
        f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:300]}\n"
        for r in results.get("results", [])
    ]
    return "\n----\n".join(chunks) if chunks else "No results found."


@tool
@retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=1, max=4),
    retry=retry_if_exception_type(requests.RequestException),
    reraise=False,
)
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading."""
    try:
        resp = requests.get(url, timeout=SCRAPE_TIMEOUT, headers={"User-Agent": USER_AGENT})
        resp.raise_for_status()
    except requests.RequestException as e:
        return f"Could not scrape URL ({url}): {e}"

    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(_STRIPPED_TAGS):
        tag.decompose()
    return soup.get_text(separator=" ", strip=True)[:SCRAPE_MAX_CHARS]
