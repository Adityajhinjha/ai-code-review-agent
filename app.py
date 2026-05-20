import json
import streamlit as st
from agent.pipeline import run_review_pipeline


# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CodeSight · AI Code Review",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global Styles ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Import Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500&family=Inter:wght@400;500;600&display=swap');

/* ── CSS Variables ── */
:root {
    --bg-base:       #0a0c10;
    --bg-card:       #0f1219;
    --bg-panel:      #141820;
    --bg-hover:      #1a2030;
    --border:        #1e2535;
    --border-accent: #2a3348;
    --text-primary:  #e8edf5;
    --text-secondary:#8899b4;
    --text-muted:    #4a5568;
    --accent-blue:   #4f8ef7;
    --accent-cyan:   #22d3ee;
    --accent-green:  #10b981;
    --accent-orange: #f59e0b;
    --accent-red:    #ef4444;
    --accent-purple: #a78bfa;
    --glow-blue:     rgba(79, 142, 247, 0.15);
    --glow-cyan:     rgba(34, 211, 238, 0.12);
}

/* ── Base Reset ── */
html, body, .stApp {
    background-color: var(--bg-base) !important;
    font-family: 'Inter', sans-serif;
    color: var(--text-primary);
}

/* ── Hide Streamlit Branding ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 2rem 3rem 4rem !important;
    max-width: 1200px;
}

/* ── Hero Section ── */
.hero-wrap {
    text-align: center;
    padding: 3rem 0 2.5rem;
    position: relative;
}
.hero-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.22em;
    color: var(--accent-cyan);
    text-transform: uppercase;
    margin-bottom: 1rem;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2.4rem, 5vw, 3.6rem);
    font-weight: 800;
    line-height: 1.05;
    letter-spacing: -0.03em;
    margin-bottom: 0;
    background: linear-gradient(135deg, #e8edf5 30%, var(--accent-cyan) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub {
    font-size: 1.05rem;
    color: var(--text-secondary);
    margin-top: 0.9rem;
    line-height: 1.6;
}

/* ── Input Area ── */
.stTextInput > div > div > input {
    background: var(--bg-panel) !important;
    border: 1.5px solid var(--border-accent) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.92rem !important;
    padding: 0.75rem 1rem !important;
    transition: border-color 0.2s, box-shadow 0.2s;
}
.stTextInput > div > div > input:focus {
    border-color: var(--accent-blue) !important;
    box-shadow: 0 0 0 3px var(--glow-blue) !important;
    outline: none !important;
}
.stTextInput > div > div > input::placeholder {
    color: var(--text-muted) !important;
}
.stTextInput label {
    color: var(--text-secondary) !important;
    font-size: 0.82rem !important;
    font-family: 'JetBrains Mono', monospace !important;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

/* ── Button ── */
.stButton > button {
    background: linear-gradient(135deg, var(--accent-blue), var(--accent-cyan)) !important;
    color: #0a0c10 !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.04em;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.65rem 2.2rem !important;
    cursor: pointer !important;
    transition: opacity 0.2s, transform 0.15s, box-shadow 0.2s !important;
}
.stButton > button:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px rgba(79,142,247,0.3) !important;
}
.stButton > button:active {
    transform: translateY(0px) !important;
}

/* ── Metric Cards (st.metric) ── */
[data-testid="metric-container"] {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.1rem 1.4rem !important;
}
[data-testid="metric-container"]:nth-child(1) { border-top: 2px solid var(--accent-blue); }
[data-testid="metric-container"]:nth-child(2) { border-top: 2px solid var(--accent-cyan); }
[data-testid="metric-container"]:nth-child(3) { border-top: 2px solid var(--accent-red); }
[data-testid="metric-container"]:nth-child(4) { border-top: 2px solid var(--accent-green); }
[data-testid="stMetricLabel"] > div {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.72rem !important;
    color: var(--text-muted) !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
[data-testid="stMetricValue"] > div {
    font-family: 'Syne', sans-serif !important;
    font-size: 2rem !important;
    font-weight: 800 !important;
    color: var(--text-primary) !important;
}

/* ── Section Header ── */
.section-header {
    font-family: 'Syne', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.01em;
    margin: 2rem 0 1rem;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid var(--border);
}

/* ── Filter Bar ── */
.filter-bar {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem 1.4rem;
    margin-bottom: 1.4rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
}
.filter-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    white-space: nowrap;
}

/* ── Review Card ── */
.review-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 1.2rem;
    transition: border-color 0.2s, box-shadow 0.2s;
}
.review-card:hover {
    border-color: var(--border-accent);
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
}
.review-card-header {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    margin-bottom: 1rem;
}
.fn-name {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1rem;
    font-weight: 500;
    color: var(--accent-cyan);
}
.fn-type-badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    padding: 0.18rem 0.6rem;
    border-radius: 999px;
    background: var(--bg-panel);
    border: 1px solid var(--border-accent);
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
.fn-file {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: var(--text-muted);
    margin-top: -0.5rem;
    margin-bottom: 1rem;
}

/* ── Issue Item ── */
.issue-item {
    background: var(--bg-panel);
    border-left: 3px solid;
    border-radius: 0 10px 10px 0;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
}
.issue-item.high   { border-color: var(--accent-red); }
.issue-item.medium { border-color: var(--accent-orange); }
.issue-item.low    { border-color: var(--accent-green); }

.issue-top {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 0.5rem;
    flex-wrap: wrap;
}
.sev-badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.64rem;
    font-weight: 500;
    padding: 0.15rem 0.55rem;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
.sev-badge.high   { background: rgba(239,68,68,0.15);   color: var(--accent-red); }
.sev-badge.medium { background: rgba(245,158,11,0.15);  color: var(--accent-orange); }
.sev-badge.low    { background: rgba(16,185,129,0.15);  color: var(--accent-green); }

/* ── Verify This Badge ── */
.verify-badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.64rem;
    font-weight: 600;
    padding: 0.15rem 0.6rem;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    background: rgba(167,139,250,0.15);
    color: var(--accent-purple);
    border: 1px solid rgba(167,139,250,0.3);
}

.issue-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--text-primary);
}
.issue-meta {
    font-size: 0.83rem;
    color: var(--text-secondary);
    line-height: 1.55;
    margin-bottom: 0.4rem;
}
.issue-suggestion {
    font-size: 0.82rem;
    color: var(--accent-cyan);
    font-style: italic;
    line-height: 1.5;
}
.issue-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.15rem;
}

/* ── Confidence Bar ── */
.conf-row {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-top: 0.6rem;
}
.conf-bar-bg {
    flex: 1;
    height: 4px;
    background: var(--border);
    border-radius: 999px;
    overflow: hidden;
}
.conf-bar-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, var(--accent-blue), var(--accent-cyan));
}
.conf-bar-fill.low-conf {
    background: linear-gradient(90deg, var(--accent-purple), rgba(167,139,250,0.5));
}
.conf-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: var(--text-muted);
    min-width: 2.5rem;
    text-align: right;
}

/* ── No Issues ── */
.no-issues {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(16,185,129,0.08);
    border: 1px solid rgba(16,185,129,0.2);
    border-radius: 8px;
    padding: 0.7rem 1rem;
    font-size: 0.85rem;
    color: var(--accent-green);
    font-family: 'JetBrains Mono', monospace;
}

/* ── Low Confidence Section ── */
.low-conf-header {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: var(--accent-purple);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin: 1.2rem 0 0.6rem;
    padding: 0.5rem 0.8rem;
    background: rgba(167,139,250,0.06);
    border: 1px solid rgba(167,139,250,0.15);
    border-radius: 6px;
    display: inline-block;
}

/* ── Download Button ── */
.stDownloadButton > button {
    background: transparent !important;
    border: 1.5px solid var(--border-accent) !important;
    color: var(--text-secondary) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.82rem !important;
    border-radius: 8px !important;
    padding: 0.5rem 1.2rem !important;
    transition: border-color 0.2s, color 0.2s !important;
}
.stDownloadButton > button:hover {
    border-color: var(--accent-blue) !important;
    color: var(--accent-blue) !important;
}

/* ── Success / Error / Warning ── */
.stSuccess {
    background: rgba(16,185,129,0.08) !important;
    border: 1px solid rgba(16,185,129,0.2) !important;
    color: var(--accent-green) !important;
    border-radius: 10px !important;
}
.stError {
    background: rgba(239,68,68,0.08) !important;
    border: 1px solid rgba(239,68,68,0.2) !important;
    border-radius: 10px !important;
}
.stWarning {
    background: rgba(245,158,11,0.08) !important;
    border: 1px solid rgba(245,158,11,0.2) !important;
    border-radius: 10px !important;
}

/* ── Spinner ── */
.stSpinner > div {
    border-top-color: var(--accent-blue) !important;
}

/* ── Divider ── */
hr {
    border-color: var(--border) !important;
    margin: 2rem 0 !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg-base); }
::-webkit-scrollbar-thumb { background: var(--border-accent); border-radius: 999px; }

/* ── Streamlit select/multiselect styling ── */
[data-baseweb="select"] {
    background: var(--bg-panel) !important;
}
[data-baseweb="select"] > div {
    background: var(--bg-panel) !important;
    border-color: var(--border-accent) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.82rem !important;
}
</style>
""", unsafe_allow_html=True)


# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrap">
    <div class="hero-eyebrow">⬡ AI-Powered · AST-Based · Confidence-Scored</div>
    <div class="hero-title">CodeSight</div>
    <div class="hero-sub">Drop in a GitHub repo and get a deep semantic code review in seconds.</div>
</div>
""", unsafe_allow_html=True)


# ── Input ──────────────────────────────────────────────────────────────────────
col_input, col_btn = st.columns([5, 1], vertical_alignment="bottom")

with col_input:
    repo_url = st.text_input(
        "repository url",
        placeholder="https://github.com/user/repository",
        label_visibility="visible",
    )

with col_btn:
    run_clicked = st.button("Analyze →", use_container_width=True)



# ── Run Pipeline ───────────────────────────────────────────────────────────────
if run_clicked:
    if not repo_url.strip():
        st.warning("Please enter a valid GitHub repository URL.")
    else:
        with st.spinner("Cloning, parsing, and reviewing — this may take a moment…"):
            try:
                results, summary = run_review_pipeline(repo_url)
                st.session_state["results"] = results
                st.session_state["summary"] = summary
            except Exception as e:
                st.error(f"Pipeline error: {e}")
                st.stop()


# ── Render Results (outside run_clicked so filters don't crash the page) ───────
if "results" in st.session_state:

    results = st.session_state["results"]
    summary = st.session_state["summary"]

    # ── Summary Stats ──────────────────────────────────────────────────────────
    all_issues  = [i for r in results for i in r["issues"]]
    high_issues = sum(1 for i in all_issues if i["severity"] == "high")
    low_conf    = sum(1 for i in all_issues if i.get("confidence", 100) < 50)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(label="Files Scanned",   value=len(set(r["file"] for r in results)))
    with c2:
        st.metric(label="Chunks Reviewed", value=len(results))
    with c3:
        st.metric(label="High Severity",   value=high_issues)
    with c4:
        st.metric(label="Verify This",     value=low_conf)

    # ── Repository Health Summary ──────────────────────────────────────────────
    st.markdown('<div class="section-header">Repository Health Summary</div>', unsafe_allow_html=True)

    health_score = summary.get("health_score", 0)
    health_label = summary.get("health_label", "Unknown")
    breakdown    = summary.get("issue_breakdown", {})

    if health_score >= 90:
        score_color = "var(--accent-green)"
    elif health_score >= 70:
        score_color = "var(--accent-cyan)"
    elif health_score >= 50:
        score_color = "var(--accent-orange)"
    else:
        score_color = "var(--accent-red)"

    st.markdown(f"""
    <div class="review-card" style="margin-bottom:1.2rem">
        <div style="display:flex;align-items:center;gap:1.5rem;flex-wrap:wrap">
            <div style="text-align:center;min-width:90px">
                <div style="font-family:'Syne',sans-serif;font-size:3rem;font-weight:800;
                            color:{score_color};line-height:1">{health_score}</div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:0.68rem;
                            color:var(--text-muted);text-transform:uppercase;
                            letter-spacing:.1em;margin-top:.3rem">/100 · {health_label}</div>
            </div>
            <div style="flex:1;min-width:220px">
                <div style="height:8px;background:var(--border);border-radius:999px;overflow:hidden;margin-bottom:.5rem">
                    <div style="height:100%;width:{health_score}%;
                                background:linear-gradient(90deg,var(--accent-blue),{score_color});
                                border-radius:999px;transition:width .4s"></div>
                </div>
                <div style="display:flex;gap:1.2rem;flex-wrap:wrap">
                    <span style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:var(--accent-red)">
                        ▲ {breakdown.get('high', 0)} High
                    </span>
                    <span style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:var(--accent-orange)">
                        ● {breakdown.get('medium', 0)} Medium
                    </span>
                    <span style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:var(--accent-green)">
                        ▼ {breakdown.get('low', 0)} Low
                    </span>
                    <span style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:var(--accent-purple)">
                        ◈ {low_conf} Verify This
                    </span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Top critical issues
    top_issues = summary.get("top_critical_issues", [])
    if top_issues:
        st.markdown('<div class="issue-label" style="margin-bottom:.5rem">Top Critical Issues</div>', unsafe_allow_html=True)
        for ti in top_issues:
            sev = ti.get("severity", "low").lower()
            st.markdown(f"""
            <div class="issue-item {sev}" style="margin-bottom:.6rem">
                <div class="issue-top">
                    <span class="sev-badge {sev}">{sev}</span>
                    <span class="issue-title">{ti.get('title','')}</span>
                </div>
                <div class="fn-file">📄 {ti.get('file','')} · {ti.get('function','')}</div>
                <div class="issue-meta">{ti.get('description','')}</div>
            </div>
            """, unsafe_allow_html=True)

    # Recurring patterns
    patterns = summary.get("recurring_patterns", [])
    if patterns:
        st.markdown('<div class="issue-label" style="margin:.8rem 0 .4rem">Recurring Patterns</div>', unsafe_allow_html=True)
        for p in patterns:
            st.markdown(f'<div class="issue-meta" style="margin-bottom:.3rem">⚠ {p}</div>', unsafe_allow_html=True)

    # Positive observations
    positives = summary.get("positive_observations", [])
    if positives:
        st.markdown('<div class="issue-label" style="margin:.8rem 0 .4rem">Positive Observations</div>', unsafe_allow_html=True)
        for obs in positives:
            st.markdown(f'<div class="issue-meta" style="color:var(--accent-green);margin-bottom:.3rem">✓ {obs}</div>', unsafe_allow_html=True)

    # Next steps
    steps = summary.get("recommended_next_steps", [])
    if steps:
        st.markdown('<div class="issue-label" style="margin:.8rem 0 .4rem">Recommended Next Steps</div>', unsafe_allow_html=True)
        for idx, step in enumerate(steps, start=1):
            st.markdown(f'<div class="issue-meta" style="margin-bottom:.3rem"><strong style="color:var(--accent-cyan)">{idx}.</strong> {step}</div>', unsafe_allow_html=True)

    # ── Filters ────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Review Results</div>', unsafe_allow_html=True)

    fc1, fc2, fc3 = st.columns([2, 2, 2])
    with fc1:
        sev_filter = st.multiselect(
            "Filter by Severity",
            options=["high", "medium", "low"],
            default=["high", "medium", "low"],
            key="sev_filter",
        )
    with fc2:
        conf_filter = st.selectbox(
            "Filter by Confidence",
            options=["All", "High confidence (≥75)", "Medium confidence (50–74)", "Low confidence / Verify (<50)"],
            key="conf_filter",
        )
    with fc3:
        chunk_filter = st.selectbox(
            "Filter by Type",
            options=["All", "function", "class", "file"],
            key="chunk_filter",
        )

    # ── Helper: confidence bucket ──────────────────────────────────────────────
    def conf_bucket(conf: int) -> str:
        if conf >= 75:
            return "High confidence (≥75)"
        elif conf >= 50:
            return "Medium confidence (50–74)"
        else:
            return "Low confidence / Verify (<50)"

    # ── Render filtered results ────────────────────────────────────────────────
    shown_chunks = 0

    for result in results:

        fn     = result["function"]
        ftype  = result["type"]
        ffile  = result["file"]
        issues = result["issues"]

        # Apply chunk-type filter
        if chunk_filter != "All" and ftype != chunk_filter:
            continue

        # Filter issues by severity and confidence
        filtered_issues = []
        for issue in issues:
            sev  = issue.get("severity", "low").lower()
            conf = issue.get("confidence", 100)
            if sev not in sev_filter:
                continue
            if conf_filter != "All" and conf_bucket(conf) != conf_filter:
                continue
            filtered_issues.append(issue)

        # Skip chunks with no matching issues
        if issues and not filtered_issues:
            continue

        shown_chunks += 1

        normal_issues = [i for i in filtered_issues if i.get("confidence", 100) >= 50]
        verify_issues = [i for i in filtered_issues if i.get("confidence", 100) < 50]

        st.markdown(f"""
        <div class="review-card">
            <div class="review-card-header">
                <span class="fn-name">{fn}</span>
                <span class="fn-type-badge">{ftype}</span>
            </div>
            <div class="fn-file">📄 {ffile}</div>
        """, unsafe_allow_html=True)

        if not filtered_issues:
            st.markdown('<div class="no-issues">✓ No issues detected</div>', unsafe_allow_html=True)
        else:
            for issue in normal_issues:
                sev   = issue.get("severity", "low").lower()
                conf  = issue.get("confidence", 0)
                title = issue.get("title", "Issue")
                desc  = issue.get("description", "")
                sugg  = issue.get("suggestion", "")

                st.markdown(f"""
                <div class="issue-item {sev}">
                    <div class="issue-top">
                        <span class="sev-badge {sev}">{sev}</span>
                        <span class="issue-title">{title}</span>
                    </div>
                    <div class="issue-label">Description</div>
                    <div class="issue-meta">{desc}</div>
                    <div class="issue-label">Suggestion</div>
                    <div class="issue-suggestion">{sugg}</div>
                    <div class="issue-label" style="margin-top:0.7rem">Confidence Score</div>
                    <div class="conf-row">
                        <div class="conf-bar-bg">
                            <div class="conf-bar-fill" style="width:{conf}%"></div>
                        </div>
                        <span class="conf-value" style="font-weight:600;color:var(--accent-cyan)">{conf}%</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            if verify_issues:
                st.markdown('<div class="low-conf-header">◈ Verify This — Low Confidence Findings</div>', unsafe_allow_html=True)

                for issue in verify_issues:
                    sev   = issue.get("severity", "low").lower()
                    conf  = issue.get("confidence", 0)
                    title = issue.get("title", "Issue")
                    desc  = issue.get("description", "")
                    sugg  = issue.get("suggestion", "")

                    st.markdown(f"""
                    <div class="issue-item {sev}" style="border-left-color:var(--accent-purple);opacity:0.85;">
                        <div class="issue-top">
                            <span class="sev-badge {sev}">{sev}</span>
                            <span class="verify-badge">⚠ Verify This</span>
                            <span class="issue-title">{title}</span>
                        </div>
                        <div class="issue-label">Description</div>
                        <div class="issue-meta">{desc}</div>
                        <div class="issue-label">Suggestion</div>
                        <div class="issue-suggestion">{sugg}</div>
                        <div class="issue-label" style="margin-top:0.7rem">Confidence Score</div>
                        <div class="conf-row">
                            <div class="conf-bar-bg">
                                <div class="conf-bar-fill low-conf" style="width:{conf}%"></div>
                            </div>
                            <span class="conf-value" style="font-weight:600;color:var(--accent-purple)">{conf}%</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    if shown_chunks == 0:
        st.info("No results match the current filters. Try adjusting the filters above.")

    # ── Download ───────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Export</div>', unsafe_allow_html=True)

    st.download_button(
        label="↓  Download JSON Report",
        data=json.dumps({"summary": summary, "reviews": results}, indent=2),
        file_name="codesight_review.json",
        mime="application/json",
    )