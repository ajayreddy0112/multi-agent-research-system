# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

`uv`-managed project (see `uv.lock`, `pyproject.toml`), Python 3.13.

- Install dependencies: `uv sync`
- Run the Streamlit UI: `uv run streamlit run app.py`
- Run the CLI pipeline (prompts for a topic): `uv run python pipeline.py`

There is no test suite, linter config, or build step.

### Required environment variables

Copy `.env.example` to `.env` and set:
- `MISTRAL_API_KEY` — used by `ChatMistralAI` in `agents.py`
- `TAVILY_API_KEY` — used by the `web_search` tool in `tools.py`
- `MISTRAL_MODEL` (optional) — overrides the default `mistral-small-2506`

Note: `pyproject.toml` lists `langchain-openai`, `openai`, `pandas`, `tiktoken`,
`aiohttp`, `lxml`, `html5lib`, and `orjson`, but none of them are imported by
the current code. They were brought in during scaffolding and have not been
pruned. Don't assume they're load-bearing. `requirements.txt` (used by
Streamlit Community Cloud) has already been slimmed to the actual deps.

## Deployment

Target: **Streamlit Community Cloud**.

- `requirements.txt` is the dep manifest the cloud build reads (preferred over
  `pyproject.toml` for explicit pinning).
- `.streamlit/config.toml` — theme + server settings, committed.
- `.streamlit/secrets.toml.example` — template; the real `secrets.toml` is
  gitignored and only used for local Streamlit runs. On Cloud, secrets are
  pasted into the dashboard, which then auto-exposes each key as an env var —
  so `os.getenv("MISTRAL_API_KEY")` works in both local-dotenv and Cloud-secrets
  modes without any code branching.
- `.python-version` pins Python 3.13 for Streamlit Cloud's runtime selection.

## Architecture

A four-stage sequential pipeline whose orchestration lives in a **single
generator** consumed by both the CLI and the Streamlit UI.

```
topic ──► search_agent ──► reader_agent ──► writer_chain ──► critic_chain
         (Tavily search)   (BS4 URL scrape)  (drafts report)  (scores report)
```

### Module layout

- **`pipeline.py`** — the **only** orchestrator. `stream_research_pipeline(topic)`
  is a generator that yields `(Stage, output_str)` after each stage in fixed
  order. `run_research_pipeline(topic)` is the CLI wrapper that pretty-prints
  each yield with Rich. **Both `app.py` and the CLI go through this generator** —
  do not reintroduce inline pipeline calls in `app.py`. The `STAGES` tuple and
  `Stage` `Literal` type are the canonical stage enumeration; consumers iterate
  it to lay out UI placeholders.
- **`agents.py`** — single shared `llm = ChatMistralAI(...)` instance plus the
  four stage definitions:
  - `build_search_agent()` / `build_reader_agent()` — `langchain.agents.create_agent`
    ReAct agents bound to one tool each.
  - `writer_chain` / `critic_chain` — module-level LCEL chains
    (`prompt | llm | StrOutputParser()`), **not** tool-using agents. Both
    prompts emit Markdown so they render cleanly in Streamlit and Rich.
- **`tools.py`** — the two `@tool`s consumed by the agents. Both are wrapped
  with Tenacity retries; `scrape_url` catches `requests.RequestException` and
  returns a human-readable error string rather than raising, so the agent loop
  can decide what to do.
- **`app.py`** — Streamlit UI. Holds an `st.empty()` placeholder per stage
  (keyed by the `STAGES` tuple) and rewrites each placeholder as the generator
  yields, so cards flip `waiting → running → done` mid-execution. Example chips
  are real `st.button`s with an `on_click` callback that prefills the topic
  input. The CSS block is intentionally large — it carries the visual design
  and should be preserved when editing.

### Inter-stage data flow

Stages communicate via plain strings, not structured objects:
- The search agent's final message is truncated to `SEARCH_EXCERPT_CHARS` (800)
  before being fed into the reader agent's prompt.
- Search + scraped content are concatenated into a single `research` string and
  passed to the writer chain alongside the original `topic`.
- The writer's report string is the sole input to the critic chain.

Both agents are invoked with `agent.invoke({"messages": [("user", "...")]})`
and the response is read from `result["messages"][-1].content` — this is
abstracted by `_agent_response` in `pipeline.py`.

### Gotchas

- `create_agent` here comes from `langchain.agents` (not `langgraph.prebuilt`).
- Streamlit will rerun the whole script on any widget interaction; the
  `step_slots` placeholders are re-created on each run, which is why we
  re-render their initial state from `st.session_state.results` before
  potentially overwriting them inside the run branch.
