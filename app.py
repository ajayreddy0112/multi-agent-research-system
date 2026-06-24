import time

import streamlit as st

from pipeline import STAGES, Stage, stream_research_pipeline

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResearchMind · AI Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #e8e4dc;
}

.stApp {
    background: #0a0a0f;
    background-image:
        radial-gradient(ellipse 80% 50% at 20% -10%, rgba(255,140,50,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 110%, rgba(255,80,30,0.08) 0%, transparent 55%);
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 4rem; max-width: 1200px; }

.hero { text-align: center; padding: 3.5rem 0 2.5rem; position: relative; }
.hero-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem; font-weight: 500;
    letter-spacing: 0.25em; text-transform: uppercase;
    color: #ff8c32; margin-bottom: 1rem; opacity: 0.9;
}
.hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2.8rem, 6vw, 5rem);
    font-weight: 800; line-height: 1.0;
    letter-spacing: -0.03em; color: #f0ebe0;
    margin: 0 0 1rem;
}
.hero h1 span { color: #ff8c32; }
.hero-sub {
    font-size: 1.05rem; font-weight: 300;
    color: #a09890; max-width: 520px;
    margin: 0 auto; line-height: 1.65;
}

.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,140,50,0.3), transparent);
    margin: 2rem 0;
}

.input-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,140,50,0.15);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.2rem;
    backdrop-filter: blur(8px);
}

.stTextInput > div > div > input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,140,50,0.25) !important;
    border-radius: 10px !important;
    color: #f0ebe0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.75rem 1rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: #ff8c32 !important;
    box-shadow: 0 0 0 3px rgba(255,140,50,0.12) !important;
}
.stTextInput > label {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    color: #ff8c32 !important;
    font-weight: 500 !important;
}

.stButton > button {
    background: linear-gradient(135deg, #ff8c32 0%, #ff5a1a 100%) !important;
    color: #0a0a0f !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.04em !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.7rem 2.2rem !important;
    cursor: pointer !important;
    transition: transform 0.15s, box-shadow 0.15s, opacity 0.15s !important;
    box-shadow: 0 4px 20px rgba(255,140,50,0.3) !important;
    width: 100%;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(255,140,50,0.4) !important;
    opacity: 0.95 !important;
}

/* Example "chip" buttons (secondary type) */
.stButton > button[kind="secondary"] {
    background: rgba(255,255,255,0.04) !important;
    color: #cdc8bf !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 400 !important;
    font-size: 0.78rem !important;
    letter-spacing: 0 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 6px !important;
    padding: 0.3rem 0.75rem !important;
    box-shadow: none !important;
    width: auto !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: rgba(255,140,50,0.4) !important;
    color: #ff8c32 !important;
    transform: none !important;
}

.step-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 1.5rem 1.8rem;
    margin-bottom: 1.2rem;
    position: relative; overflow: hidden;
    transition: border-color 0.3s;
}
.step-card.active {
    border-color: rgba(255,140,50,0.4);
    background: rgba(255,140,50,0.04);
}
.step-card.done {
    border-color: rgba(80,200,120,0.3);
    background: rgba(80,200,120,0.03);
}
.step-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    border-radius: 14px 0 0 14px;
    background: rgba(255,255,255,0.05);
    transition: background 0.3s;
}
.step-card.active::before { background: #ff8c32; }
.step-card.done::before   { background: #50c878; }

.step-header { display: flex; align-items: center; gap: 0.8rem; margin-bottom: 0.3rem; }
.step-num {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem; font-weight: 500;
    letter-spacing: 0.15em; color: #ff8c32; opacity: 0.7;
}
.step-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.95rem; font-weight: 700; color: #f0ebe0;
}
.step-status {
    margin-left: auto;
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem; letter-spacing: 0.1em;
}
.status-waiting  { color: #555; }
.status-running  { color: #ff8c32; }
.status-done     { color: #50c878; }
.step-desc { font-size: 0.82rem; color: #706860; margin-top: 0.3rem; }

.result-panel {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 1.8rem 2rem;
    margin: 1rem 0 1.5rem;
}
.result-panel-title {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem; font-weight: 500;
    letter-spacing: 0.2em; text-transform: uppercase;
    color: #ff8c32; margin-bottom: 1rem;
    padding-bottom: 0.7rem;
    border-bottom: 1px solid rgba(255,140,50,0.15);
}
.result-content {
    font-size: 0.92rem; line-height: 1.8; color: #cdc8bf;
    white-space: pre-wrap; font-family: 'DM Sans', sans-serif;
}

.report-panel {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,140,50,0.2);
    border-radius: 16px;
    padding: 2rem 2.5rem; margin-top: 1rem;
}
.feedback-panel {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(80,200,120,0.2);
    border-radius: 16px;
    padding: 2rem 2.5rem; margin-top: 1rem;
}
.panel-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem; letter-spacing: 0.2em;
    text-transform: uppercase; margin-bottom: 1.2rem;
    padding-bottom: 0.7rem;
}
.panel-label.orange { color: #ff8c32; border-bottom: 1px solid rgba(255,140,50,0.15); }
.panel-label.green  { color: #50c878; border-bottom: 1px solid rgba(80,200,120,0.15); }

.stSpinner > div { color: #ff8c32 !important; }

details summary {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
    color: #a09890 !important;
    letter-spacing: 0.1em !important;
    cursor: pointer;
}

.section-heading {
    font-family: 'Syne', sans-serif;
    font-size: 1.3rem; font-weight: 700;
    color: #f0ebe0; margin: 2rem 0 1rem;
}

.try-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem; color: #605850;
    letter-spacing: 0.1em; margin-bottom: 0.5rem;
}

.notice {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem; color: #605850;
    text-align: center; margin-top: 3rem; letter-spacing: 0.08em;
}
</style>
""", unsafe_allow_html=True)


# ── Step card rendering ──────────────────────────────────────────────────────
_STEP_META: dict[Stage, tuple[str, str, str]] = {
    "search": ("01", "Search Agent", "Gathers recent web information"),
    "reader": ("02", "Reader Agent", "Scrapes & extracts deep content"),
    "writer": ("03", "Writer Chain", "Drafts the full research report"),
    "critic": ("04", "Critic Chain", "Reviews & scores the report"),
}

_STATUS_LABEL = {
    "waiting": ("WAITING", "status-waiting", ""),
    "running": ("● RUNNING", "status-running", "active"),
    "done":    ("✓ DONE", "status-done", "done"),
}


def render_step_card(stage: Stage, status: str) -> str:
    num, title, desc = _STEP_META[stage]
    label, status_cls, card_cls = _STATUS_LABEL[status]
    return f"""
    <div class="step-card {card_cls}">
        <div class="step-header">
            <span class="step-num">{num}</span>
            <span class="step-title">{title}</span>
            <span class="step-status {status_cls}">{label}</span>
        </div>
        <div class="step-desc">{desc}</div>
    </div>
    """


# ── Session state init ────────────────────────────────────────────────────────
st.session_state.setdefault("results", {})
st.session_state.setdefault("error", None)
st.session_state.setdefault("topic_value", "")


def set_topic(value: str) -> None:
    st.session_state.topic_value = value


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">Multi-Agent AI System</div>
    <h1>Research<span>Mind</span></h1>
    <p class="hero-sub">
        Four specialized AI agents collaborate — searching, scraping, writing,
        and critiquing — to deliver a polished research report on any topic.
    </p>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)


# ── Layout: input left, pipeline right ───────────────────────────────────────
col_input, _, col_pipeline = st.columns([5, 0.5, 4])

with col_input:
    topic = st.text_input(
        "Research Topic",
        value=st.session_state.topic_value,
        placeholder="e.g. Quantum computing breakthroughs in 2025",
        key="topic_input",
    )
    run_btn = st.button("⚡  Run Research Pipeline", use_container_width=True)

    st.markdown('<div class="try-label">TRY →</div>', unsafe_allow_html=True)
    examples = ["LLM agents 2025", "CRISPR gene editing", "Fusion energy progress"]
    chip_cols = st.columns(len(examples))
    for col, ex in zip(chip_cols, examples):
        with col:
            st.button(
                ex,
                key=f"chip_{ex}",
                type="secondary",
                on_click=set_topic,
                args=(ex,),
            )

with col_pipeline:
    st.markdown('<div class="section-heading">Pipeline</div>', unsafe_allow_html=True)
    step_slots: dict[Stage, "st.delta_generator.DeltaGenerator"] = {
        stage: st.empty() for stage in STAGES
    }
    # Initial render (all waiting unless results from a prior run exist)
    for stage in STAGES:
        status = "done" if stage in st.session_state.results else "waiting"
        step_slots[stage].markdown(render_step_card(stage, status), unsafe_allow_html=True)


# ── Run pipeline ──────────────────────────────────────────────────────────────
if run_btn:
    topic_val = topic.strip()
    if not topic_val:
        st.warning("Please enter a research topic first.")
    else:
        st.session_state.results = {}
        st.session_state.error = None

        # Reset all cards to waiting
        for stage in STAGES:
            step_slots[stage].markdown(render_step_card(stage, "waiting"), unsafe_allow_html=True)

        next_stage: Stage = STAGES[0]
        step_slots[next_stage].markdown(render_step_card(next_stage, "running"), unsafe_allow_html=True)

        try:
            for stage, output in stream_research_pipeline(topic_val):
                st.session_state.results[stage] = output
                step_slots[stage].markdown(render_step_card(stage, "done"), unsafe_allow_html=True)

                idx = STAGES.index(stage)
                if idx + 1 < len(STAGES):
                    upcoming = STAGES[idx + 1]
                    step_slots[upcoming].markdown(render_step_card(upcoming, "running"), unsafe_allow_html=True)
        except Exception as e:  # noqa: BLE001 — surface any pipeline failure to the UI
            st.session_state.error = f"{type(e).__name__}: {e}"


# ── Error display ─────────────────────────────────────────────────────────────
if st.session_state.error:
    st.error(f"Pipeline failed → {st.session_state.error}")


# ── Results display ───────────────────────────────────────────────────────────
r = st.session_state.results

if r:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Results</div>', unsafe_allow_html=True)

    if "search" in r:
        with st.expander("🔍 Search Results (raw)", expanded=False):
            st.markdown(
                f'<div class="result-panel"><div class="result-panel-title">Search Agent Output</div>'
                f'<div class="result-content">{r["search"]}</div></div>',
                unsafe_allow_html=True,
            )

    if "reader" in r:
        with st.expander("📄 Scraped Content (raw)", expanded=False):
            st.markdown(
                f'<div class="result-panel"><div class="result-panel-title">Reader Agent Output</div>'
                f'<div class="result-content">{r["reader"]}</div></div>',
                unsafe_allow_html=True,
            )

    if "writer" in r:
        st.markdown(
            '<div class="panel-label orange">📝 Final Research Report</div>',
            unsafe_allow_html=True,
        )
        st.markdown(r["writer"])

        st.download_button(
            label="⬇  Download Report (.md)",
            data=r["writer"],
            file_name=f"research_report_{int(time.time())}.md",
            mime="text/markdown",
        )

    if "critic" in r:
        st.markdown(
            '<div class="panel-label green">🧐 Critic Feedback</div>',
            unsafe_allow_html=True,
        )
        st.markdown(r["critic"])


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="notice">
    ResearchMind · Powered by LangChain multi-agent pipeline · Built with Streamlit
</div>
""", unsafe_allow_html=True)
