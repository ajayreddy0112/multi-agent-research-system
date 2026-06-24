from typing import Iterator, Literal, TypedDict

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from agents import build_reader_agent, build_search_agent, critic_chain, writer_chain

Stage = Literal["search", "reader", "writer", "critic"]

STAGES: tuple[Stage, ...] = ("search", "reader", "writer", "critic")

STAGE_TITLES: dict[Stage, str] = {
    "search": "🔍 Search Agent",
    "reader": "📄 Reader Agent",
    "writer": "✍️  Writer Chain",
    "critic": "🧐 Critic Chain",
}

SEARCH_EXCERPT_CHARS = 800


class ResearchState(TypedDict, total=False):
    topic: str
    search: str
    reader: str
    writer: str
    critic: str


def _agent_response(agent, prompt: str) -> str:
    result = agent.invoke({"messages": [("user", prompt)]})
    return result["messages"][-1].content


def stream_research_pipeline(topic: str) -> Iterator[tuple[Stage, str]]:
    """Run the four-stage pipeline, yielding (stage, output) after each step.

    Stages are emitted in fixed order: search → reader → writer → critic.
    Used by both the CLI and the Streamlit UI so progress can be rendered
    incrementally.
    """
    state: ResearchState = {"topic": topic}

    search = _agent_response(
        build_search_agent(),
        f"Find recent, reliable and detailed information about: {topic}",
    )
    state["search"] = search
    yield "search", search

    reader = _agent_response(
        build_reader_agent(),
        (
            f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{search[:SEARCH_EXCERPT_CHARS]}"
        ),
    )
    state["reader"] = reader
    yield "reader", reader

    research_combined = (
        f"SEARCH RESULTS:\n{search}\n\n"
        f"DETAILED SCRAPED CONTENT:\n{reader}"
    )
    report = writer_chain.invoke({"topic": topic, "research": research_combined})
    state["writer"] = report
    yield "writer", report

    feedback = critic_chain.invoke({"report": report})
    state["critic"] = feedback
    yield "critic", feedback


def run_research_pipeline(topic: str) -> ResearchState:
    """CLI entry point: run the pipeline and pretty-print each stage with Rich."""
    console = Console()
    state: ResearchState = {"topic": topic}

    console.rule(f"[bold orange1]ResearchMind · {topic}")

    for stage, output in stream_research_pipeline(topic):
        state[stage] = output
        body = Markdown(output) if stage in ("writer", "critic") else output
        console.print(Panel(body, title=STAGE_TITLES[stage], border_style="orange1"))

    return state


if __name__ == "__main__":
    topic = input("\nEnter a research topic: ").strip()
    if not topic:
        raise SystemExit("No topic provided.")
    run_research_pipeline(topic)
