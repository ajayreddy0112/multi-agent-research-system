# ResearchMind

A multi-agent research assistant built with **LangChain** and **Mistral**. Four
specialized agents collaborate end-to-end — searching the web, scraping the most
relevant source, drafting a structured report, and critiquing it — and the whole
pipeline is exposed through both a Rich-powered CLI and a Streamlit UI.

## Pipeline

```
topic ──► search agent ──► reader agent ──► writer chain ──► critic chain
         (Tavily search)   (BS4 URL scrape)  (Markdown report)  (scored review)
```

| Stage      | Type        | Purpose                                       |
| ---------- | ----------- | --------------------------------------------- |
| **Search** | ReAct agent | Pulls top-N web sources via the Tavily API    |
| **Reader** | ReAct agent | Picks the most relevant URL and scrapes it    |
| **Writer** | LCEL chain  | Produces a structured Markdown report         |
| **Critic** | LCEL chain  | Scores the report and lists strengths/gaps    |

Stages stream incrementally — each one's output is yielded as soon as it's
ready, so the Streamlit step cards transition `WAITING → RUNNING → DONE` live
instead of after the whole run.

## Quick start

Requires **Python 3.13** and [`uv`](https://docs.astral.sh/uv/).

```bash
# 1. Install dependencies
uv sync

# 2. Add your API keys
cp .env.example .env
# then edit .env and fill in MISTRAL_API_KEY and TAVILY_API_KEY

# 3. Run the Streamlit UI
uv run streamlit run app.py

# …or the CLI
uv run python pipeline.py
```

Get keys at:
- Mistral — https://console.mistral.ai/
- Tavily — https://app.tavily.com/

## Configuration

| Variable          | Required | Default              | Purpose                         |
| ----------------- | -------- | -------------------- | ------------------------------- |
| `MISTRAL_API_KEY` | yes      | —                    | LLM access for every stage      |
| `TAVILY_API_KEY`  | yes      | —                    | Web search for the Search agent |
| `MISTRAL_MODEL`   | no       | `mistral-small-2506` | Override the chat model         |

## Project layout

| File          | Role                                                                            |
| ------------- | ------------------------------------------------------------------------------- |
| `agents.py`   | Shared `llm`, the two ReAct agents, the writer & critic chains                  |
| `tools.py`    | `web_search` (Tavily) and `scrape_url` (requests + BS4), with Tenacity retries  |
| `pipeline.py` | `stream_research_pipeline` generator + Rich-powered CLI entry                   |
| `app.py`      | Streamlit UI; consumes the generator to render live progress                    |

## Design notes

- **Single source of orchestration.** Both the CLI and the UI consume the same
  `stream_research_pipeline` generator from `pipeline.py`. Adding a stage means
  editing one place.
- **Live progress in Streamlit.** The UI keeps a `st.empty()` placeholder per
  stage and rewrites each one as the generator yields, so cards visibly flip to
  `RUNNING`/`DONE` mid-execution instead of in a single end-of-run batch update.
- **Resilience.** Outbound calls (Tavily search, URL scraping) are wrapped with
  Tenacity exponential-backoff retries; pipeline failures surface in the UI as
  an inline error instead of a stack trace.
- **Markdown all the way through.** The writer emits Markdown, the critic emits
  Markdown, both render natively in Streamlit and via `rich.markdown` in the CLI.

## Deploy to Streamlit Community Cloud

1. Push this repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io/) → **New app**.
3. Pick the repo, set **Main file path** to `app.py`, and leave the branch as
   `main`.
4. Open **Advanced settings → Secrets** and paste the contents of
   `.streamlit/secrets.toml.example`, filled in with your real keys:
   ```toml
   MISTRAL_API_KEY = "..."
   TAVILY_API_KEY  = "..."
   ```
   Streamlit auto-exposes every key as an environment variable, so the
   existing `os.getenv(...)` calls work unchanged.
5. Click **Deploy**. First build pulls the deps from `requirements.txt`
   (~2 min). Subsequent pushes redeploy on each commit to `main`.

The theme (dark + orange accent) is locked in via `.streamlit/config.toml`,
so the deployed UI matches local exactly.

## Tech stack

LangChain · langchain-mistralai · Tavily · BeautifulSoup · Tenacity · Rich · Streamlit
