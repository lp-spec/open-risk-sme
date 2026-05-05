import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="SME Risk Analyzer",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL STYLES  — professional light theme
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
    color: #1a202c;
    background-color: #f7f8fa;
}
.block-container {
    padding: 2rem 2.5rem 3rem 2.5rem;
    max-width: 1280px;
    background: #f7f8fa;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e2e8f0;
    padding-top: 1.5rem;
}
section[data-testid="stSidebar"] .stMarkdown h2 {
    font-size: 14px !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #1e293b !important;
    margin-bottom: 4px;
}
section[data-testid="stSidebar"] p {
    font-size: 13px;
    color: #334155;
}
section[data-testid="stSidebar"] hr {
    border-color: #e2e8f0 !important;
    margin: 16px 0;
}
section[data-testid="stSidebar"] label {
    font-size: 12px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
    color: #334155 !important;
}

/* ── App header ── */
.app-header {
    display: flex;
    align-items: baseline;
    gap: 16px;
    padding: 0 0 20px 0;
    border-bottom: 2px solid #e2e8f0;
    margin-bottom: 28px;
}
.app-logo {
    width: 36px; height: 36px;
    background: #1e40af;
    border-radius: 8px;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 18px; line-height: 1; margin-right: 4px;
    flex-shrink: 0;
}
.app-title {
    font-size: 24px;
    font-weight: 600;
    color: #0f172a;
    letter-spacing: -0.4px;
}
.app-pill {
    font-size: 12px;
    font-weight: 600;
    background: #dbeafe;
    color: #1d4ed8;
    padding: 3px 10px;
    border-radius: 999px;
    letter-spacing: 0.05em;
}
.app-subtitle {
    font-size: 13px;
    color: #334155;
    margin-left: auto;
}

/* ── Section headings ── */
.sh {
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.10em;
    text-transform: uppercase;
    color: #334155;
    margin: 30px 0 14px 0;
    padding-bottom: 8px;
    border-bottom: 1px solid #e8ecf0;
    display: flex;
    align-items: center;
    gap: 8px;
}
.sh-icon {
    width: 18px; height: 18px;
    background: #eff6ff;
    border-radius: 4px;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 12px;
}

/* ── KPI cards ── */
.kpi {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 18px 20px 16px;
    position: relative;
    overflow: hidden;
    height: 100%;
}
.kpi-accent {
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: #3b82f6;
    border-radius: 10px 10px 0 0;
}
.kpi-accent-green  { background: #10b981; }
.kpi-accent-amber  { background: #f59e0b; }
.kpi-accent-red    { background: #ef4444; }
.kpi-accent-blue   { background: #3b82f6; }
.kpi-accent-purple { background: #8b5cf6; }

.kpi-label {
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #334155;
    margin-bottom: 8px;
}
.kpi-value {
    font-size: 28px;
    font-weight: 600;
    color: #0f172a;
    font-family: 'IBM Plex Mono', monospace;
    line-height: 1.1;
    letter-spacing: -0.5px;
}
.kpi-sub {
    font-size: 12px;
    color: #334155;
    margin-top: 5px;
    font-weight: 400;
}
.kpi-delta-up   { color: #10b981; font-size: 12px; font-weight: 600; }
.kpi-delta-down { color: #ef4444; font-size: 12px; font-weight: 600; }

/* ── Alert / signal rows ── */
.alert {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 11px 16px;
    border-radius: 7px;
    margin-bottom: 7px;
    font-size: 14px;
    font-weight: 500;
    border: 1px solid transparent;
}
.alert-green  { background: #f0fdf4; color: #166534; border-color: #bbf7d0; }
.alert-yellow { background: #fffbeb; color: #92400e; border-color: #fde68a; }
.alert-red    { background: #fef2f2; color: #991b1b; border-color: #fecaca; }

.dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.dot-green  { background: #10b981; }
.dot-yellow { background: #f59e0b; }
.dot-red    { background: #ef4444; }

/* ── Benchmark bar rows ── */
.brow {
    display: flex; align-items: center; gap: 14px;
    padding: 11px 0; border-bottom: 1px solid #f1f5f9;
}
.brow:last-child { border-bottom: none; }
.blabel { font-size: 13px; color: #1e293b; width: 110px; flex-shrink: 0; font-weight: 500; }
.btrack { flex: 1; background: #f1f5f9; border-radius: 4px; height: 7px; overflow: hidden; }
.bfill  { height: 7px; border-radius: 4px; }
.bvals  {
    font-size: 12px; color: #334155; width: 200px;
    text-align: right; flex-shrink: 0;
    font-family: 'IBM Plex Mono', monospace;
    letter-spacing: 0;
}

/* ── Info box ── */
.ibox {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-left: 3px solid #3b82f6;
    border-radius: 0 8px 8px 0;
    padding: 14px 18px;
    font-size: 14px;
    color: #1e293b;
    line-height: 1.7;
    margin: 12px 0;
}

/* ── List items ── */
.li {
    display: flex; align-items: flex-start; gap: 10px;
    padding: 10px 14px;
    background: #ffffff;
    border: 1px solid #e8ecf0;
    border-radius: 7px;
    margin-bottom: 6px;
    font-size: 14px;
    color: #1e293b;
}
.li-dot {
    width: 5px; height: 5px; border-radius: 50%;
    background: #3b82f6; margin-top: 7px; flex-shrink: 0;
}
.li-warn .li-dot { background: #f59e0b; }

/* ── Decision badge ── */
.badge {
    display: inline-block;
    padding: 5px 16px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.badge-approved    { background: #dcfce7; color: #15803d; }
.badge-conditional { background: #fef9c3; color: #a16207; }
.badge-declined    { background: #fee2e2; color: #b91c1c; }

/* ── Metric rows (inside cards) ── */
.mrow {
    display: flex; justify-content: space-between; align-items: center;
    padding: 9px 0; border-bottom: 1px solid #f1f5f9;
    font-size: 13px;
}
.mrow:last-child { border-bottom: none; }
.mk { color: #334155; font-weight: 400; }
.mv { color: #0f172a; font-weight: 600; font-family: 'IBM Plex Mono', monospace; font-size: 13px; }

/* ── Sidebar result card ── */
.sr {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 14px 16px;
    margin-top: 4px;
}
.sr-label {
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #334155;
    margin-bottom: 2px;
}
.sr-val {
    font-size: 22px;
    font-weight: 600;
    color: #0f172a;
    font-family: 'IBM Plex Mono', monospace;
}

/* ── White panel (generic card wrapper) ── */
.panel {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 20px 22px;
    margin-bottom: 16px;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 1.5px solid #e2e8f0;
    background: transparent;
}
.stTabs [data-baseweb="tab"] {
    font-size: 14px;
    font-weight: 500;
    color: #334155;
    padding: 10px 24px;
    border-radius: 0;
    border-bottom: 2px solid transparent;
    margin-bottom: -2px;
    background: transparent;
}
.stTabs [aria-selected="true"] {
    color: #1e40af;
    border-bottom: 2px solid #1e40af;
    background: transparent;
    font-weight: 600;
}

/* ── Input labels ── */
.stNumberInput label,
.stSelectbox label,
.stSlider label {
    font-size: 12px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
    color: #334155 !important;
}

/* ── Streamlit overrides ── */
.stDownloadButton > button {
    background: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    color: #334155 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    border-radius: 7px !important;
    padding: 6px 16px !important;
}
.stDownloadButton > button:hover {
    background: #f8fafc !important;
    border-color: #94a3b8 !important;
}
[data-testid="stFileUploader"] {
    border: 2px dashed #cbd5e1;
    border-radius: 10px;
    background: #ffffff;
    padding: 6px;
}
div[data-testid="stHorizontalBlock"] { gap: 14px; }

/* ── Divider ── */
.divider { border: none; border-top: 1px solid #e2e8f0; margin: 20px 0; }

/* ── Upload placeholder ── */
.upload-hint {
    background: #fffbeb;
    border: 1px solid #fde68a;
    border-radius: 8px;
    padding: 14px 18px;
    font-size: 14px;
    color: #78350f;
    margin-top: 16px;
}

/* ── Comparison table ── */
.ctable {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
}
.ctable th {
    background: #f8fafc;
    color: #334155;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding: 10px 14px;
    border-bottom: 1px solid #e2e8f0;
    text-align: left;
}
.ctable td {
    padding: 10px 14px;
    border-bottom: 1px solid #f1f5f9;
    color: #1e293b;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 14px;
}
.ctable tr:last-child td { border-bottom: none; }
.ctable .metric-name {
    font-family: 'IBM Plex Sans', sans-serif;
    color: #1e293b;
    font-weight: 500;
}
.td-better { color: #15803d; font-weight: 600; }
.td-worse  { color: #b91c1c; font-weight: 600; }
.td-same   { color: #334155; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# FORMAT HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def fmt_money(v):
    """$##,###,###"""
    return f"${v:,.0f}"

def fmt_num(v, d=2):
    """##,###.##"""
    return f"{v:,.{d}f}"

def fmt_pct(v, d=1):
    """##.#%"""
    return f"{v:,.{d}f}%"


# ─────────────────────────────────────────────────────────────────────────────
# DOMAIN LOGIC
# ─────────────────────────────────────────────────────────────────────────────
def get_industry_benchmark(industry):
    return {
        "General":      {"dscr": 1.20, "volatility": 0.15},
        "Restaurant":   {"dscr": 1.30, "volatility": 0.25},
        "Retail":       {"dscr": 1.25, "volatility": 0.20},
        "SaaS":         {"dscr": 1.10, "volatility": 0.10},
        "Construction": {"dscr": 1.40, "volatility": 0.30},
    }.get(industry, {"dscr": 1.20, "volatility": 0.15})


def calculate_pd(score, dscr, volatility):
    pd_val = 0.02
    if dscr < 1.0:          pd_val += 0.15
    elif dscr < 1.2:        pd_val += 0.08
    if volatility > 0.25:   pd_val += 0.12
    elif volatility > 0.15: pd_val += 0.06
    if score < 60:          pd_val += 0.15
    elif score < 80:        pd_val += 0.07
    return min(pd_val, 0.6)


def monthly_payment(principal, annual_rate_pct, term_months):
    """Standard amortizing payment; falls back to principal-only if rate == 0."""
    if principal <= 0 or term_months <= 0:
        return 0.0
    r = annual_rate_pct / 100 / 12
    if r == 0:
        return principal / term_months
    return principal * r * (1 + r) ** term_months / ((1 + r) ** term_months - 1)


def compute_metrics(df):
    df = df.copy()
    df["profit"]    = df["revenue"] - df["expenses"]
    df["cash_flow"] = df["profit"] - df["debt_payment"]
    avg_cash   = df["cash_flow"].mean()
    avg_debt   = df["debt_payment"].mean()
    dscr       = avg_cash / avg_debt if avg_debt > 0 else 0.0
    avg_rev    = df["revenue"].mean()
    volatility = np.std(df["revenue"]) / avg_rev if avg_rev > 0 else 0.0

    score, explanations = 100, []
    if dscr < 1.2:
        score -= 30
        explanations.append(("Low DSCR — weak debt coverage", "red"))
    if volatility > 0.2:
        score -= 20
        explanations.append(("High revenue volatility detected", "yellow"))

    level = "Low" if score >= 80 else ("Moderate" if score >= 60 else "High")
    return score, level, dscr, volatility, explanations, avg_cash


# ─────────────────────────────────────────────────────────────────────────────
# APP HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <div class="app-logo">📊</div>
  <span class="app-title">SME Risk Analyzer</span>
  <span class="app-pill">Beta</span>
  <span class="app-subtitle">Financial Risk · Benchmarking · Simulation · Lending Decisions</span>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TEMPLATE DOWNLOAD
# ─────────────────────────────────────────────────────────────────────────────
template = (
    "month,revenue,expenses,debt_payment\n"
    "Jan,80000,60000,10000\n"
    "Feb,85000,62000,10000\n"
    "Mar,90000,65000,10000\n"
    "Apr,78000,61000,10000\n"
    "May,92000,63000,10000\n"
    "Jun,88000,64000,10000\n"
)
col_dl, _ = st.columns([1, 6])
with col_dl:
    st.download_button(
        "↓ Download Sample CSV", template, "sample.csv",
        use_container_width=True,
    )

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# FILE UPLOAD
# ─────────────────────────────────────────────────────────────────────────────
file = st.file_uploader(
    "Upload financial data — CSV or Excel",
    type=["csv", "xlsx"],
    label_visibility="visible",
)

if not file:
    st.markdown("""
    <div class="upload-hint">
      <strong>Required columns:</strong> &nbsp;<code>month</code>, &nbsp;<code>revenue</code>,
      &nbsp;<code>expenses</code> &nbsp; — &nbsp; <code>debt_payment</code> is optional
      (defaults to 0). Download the sample CSV above to get started.
    </div>
    """, unsafe_allow_html=True)
    st.stop()

try:
    df = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)
except Exception as e:
    st.error(f"Could not read file: {e}")
    st.stop()

df.columns = [c.lower().strip().replace(" ", "_") for c in df.columns]
missing = {"revenue", "expenses"} - set(df.columns)
if missing:
    st.error(f"Missing required columns: {', '.join(missing)}")
    st.stop()

if "debt_payment" not in df.columns:
    df["debt_payment"] = 0

for col in ["revenue", "expenses", "debt_payment"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")
df = df.dropna(subset=["revenue", "expenses"])

if df.empty:
    st.error("No valid numeric rows found in the uploaded file.")
    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
# COMPUTE BASE METRICS
# ─────────────────────────────────────────────────────────────────────────────
score, level, dscr, volatility, explanations, avg_cash = compute_metrics(df)
pd_val = calculate_pd(score, dscr, volatility)

# Accent color helpers
def acc(val, good_thresh, warn_thresh, low_is_good=False):
    """Return accent class: green / amber / red."""
    if low_is_good:
        if val <= good_thresh: return "green"
        if val <= warn_thresh: return "amber"
        return "red"
    else:
        if val >= good_thresh: return "green"
        if val >= warn_thresh: return "amber"
        return "red"

risk_acc = {"Low": "green", "Moderate": "amber", "High": "red"}.get(level, "blue")
dscr_acc = acc(dscr, 1.2, 1.0)
vol_acc  = acc(volatility, 0.15, 0.25, low_is_good=True)
pd_acc   = acc(pd_val, 0.10, 0.20, low_is_good=True)


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Scenario Controls")
    st.markdown("Stress-test the business financials by adjusting revenue, expenses, and debt.")
    st.markdown("---")

    rev_pct  = st.slider("Revenue change (%)",       -50, 50, 0, key="sb_rev")
    exp_pct  = st.slider("Expense change (%)",        -50, 50, 0, key="sb_exp")
    debt_pct = st.slider("Debt payment change (%)",  -50, 50, 0, key="sb_debt")
    st.markdown("---")

    industry  = st.selectbox(
        "Industry benchmark",
        ["General", "Restaurant", "Retail", "SaaS", "Construction"],
    )
    benchmark = get_industry_benchmark(industry)

    # Simulate
    sim_df = df.copy()
    sim_df["revenue"]      *= (1 + rev_pct  / 100)
    sim_df["expenses"]     *= (1 + exp_pct  / 100)
    sim_df["debt_payment"] *= (1 + debt_pct / 100)
    s_score, s_level, s_dscr, s_vol, _, _ = compute_metrics(sim_df)

    st.markdown("---")
    st.markdown("**Scenario Output**")
    lvl_color = {"Low": "#10b981", "Moderate": "#f59e0b", "High": "#ef4444"}.get(s_level, "#64748b")
    st.markdown(f"""
    <div class="sr">
      <div class="sr-label">Risk Score</div>
      <div class="sr-val">{s_score}</div>
      <div style="margin-top:10px;"></div>
      <div class="sr-label">Risk Level</div>
      <div class="sr-val" style="font-size:18px; color:{lvl_color};">{s_level}</div>
      <div style="margin-top:10px;"></div>
      <div class="sr-label">DSCR</div>
      <div class="sr-val" style="font-size:18px;">{fmt_num(s_dscr)}</div>
      <div style="margin-top:10px;"></div>
      <div class="sr-label">Volatility</div>
      <div class="sr-val" style="font-size:18px;">{fmt_num(s_vol)}</div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(
    ["    Dashboard    ", "    Simulator    ", "    Credit Memo    "]
)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
with tab1:

    # ── KPI Row ──
    st.markdown('<div class="sh"><span class="sh-icon">📌</span>Key Performance Indicators</div>',
                unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(f"""
    <div class="kpi">
      <div class="kpi-accent kpi-accent-{risk_acc}"></div>
      <div class="kpi-label">Risk Score</div>
      <div class="kpi-value">{score}</div>
      <div class="kpi-sub">out of 100 &nbsp;·&nbsp; <strong>{level} risk</strong></div>
    </div>""", unsafe_allow_html=True)

    k2.markdown(f"""
    <div class="kpi">
      <div class="kpi-accent kpi-accent-{dscr_acc}"></div>
      <div class="kpi-label">DSCR</div>
      <div class="kpi-value">{fmt_num(dscr)}</div>
      <div class="kpi-sub">benchmark: {fmt_num(benchmark['dscr'])}</div>
    </div>""", unsafe_allow_html=True)

    k3.markdown(f"""
    <div class="kpi">
      <div class="kpi-accent kpi-accent-{vol_acc}"></div>
      <div class="kpi-label">Revenue Volatility</div>
      <div class="kpi-value">{fmt_num(volatility)}</div>
      <div class="kpi-sub">benchmark: {fmt_num(benchmark['volatility'])}</div>
    </div>""", unsafe_allow_html=True)

    k4.markdown(f"""
    <div class="kpi">
      <div class="kpi-accent kpi-accent-{pd_acc}"></div>
      <div class="kpi-label">Prob. of Default</div>
      <div class="kpi-value">{fmt_pct(pd_val * 100)}</div>
      <div class="kpi-sub">estimated default likelihood</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Risk Alerts + Industry Benchmark ──
    left_col, right_col = st.columns([1, 1])

    with left_col:
        st.markdown('<div class="sh"><span class="sh-icon">⚠️</span>Risk Alerts</div>',
                    unsafe_allow_html=True)
        if explanations:
            for text, color in explanations:
                dot_cls   = f"dot-{color}"
                alert_cls = f"alert-{'yellow' if color=='yellow' else color}"
                st.markdown(f"""
                <div class="alert {alert_cls}">
                  <span class="dot {dot_cls}"></span>{text}
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="alert alert-green">
              <span class="dot dot-green"></span>No major risk signals detected
            </div>""", unsafe_allow_html=True)

    with right_col:
        st.markdown('<div class="sh"><span class="sh-icon">🏭</span>Industry Benchmark</div>',
                    unsafe_allow_html=True)

        dscr_pct = min(dscr / (benchmark["dscr"] * 2), 1.0) * 100
        dscr_col = "#10b981" if dscr >= benchmark["dscr"] else "#ef4444"
        st.markdown(f"""
        <div class="brow">
          <div class="blabel">DSCR</div>
          <div class="btrack"><div class="bfill" style="width:{dscr_pct:.0f}%; background:{dscr_col};"></div></div>
          <div class="bvals">You: {fmt_num(dscr)} &nbsp;·&nbsp; Target ≥ {fmt_num(benchmark['dscr'])}</div>
        </div>""", unsafe_allow_html=True)

        vol_pct = min(volatility / (benchmark["volatility"] * 2), 1.0) * 100
        vol_col = "#10b981" if volatility <= benchmark["volatility"] else "#ef4444"
        st.markdown(f"""
        <div class="brow">
          <div class="blabel">Volatility</div>
          <div class="btrack"><div class="bfill" style="width:{vol_pct:.0f}%; background:{vol_col};"></div></div>
          <div class="bvals">You: {fmt_num(volatility)} &nbsp;·&nbsp; Target ≤ {fmt_num(benchmark['volatility'])}</div>
        </div>""", unsafe_allow_html=True)

        st.markdown(
            f"<div style='font-size:13px;color:#334155;margin-top:10px;'>Industry: <strong>{industry}</strong></div>",
            unsafe_allow_html=True,
        )

    # ── Revenue & Expense Trend ──
    st.markdown('<div class="sh"><span class="sh-icon">📈</span>Revenue &amp; Expense Trend</div>',
                unsafe_allow_html=True)
    chart_df = df[["revenue", "expenses"]].copy()
    if "month" in df.columns:
        chart_df.index = df["month"]
    st.line_chart(chart_df, use_container_width=True)

    # ── Summary financial table ──
    st.markdown('<div class="sh"><span class="sh-icon">📋</span>Monthly Data Summary</div>',
                unsafe_allow_html=True)
    display_df = df.copy()
    for c in ["revenue", "expenses", "debt_payment"]:
        if c in display_df.columns:
            display_df[c] = display_df[c].apply(lambda x: f"${x:,.0f}")
    if "profit" in display_df.columns:
        display_df["profit"] = df["profit"].apply(lambda x: f"${x:,.0f}")
    if "cash_flow" in display_df.columns:
        display_df["cash_flow"] = df["cash_flow"].apply(lambda x: f"${x:,.0f}")
    st.dataframe(display_df, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — SIMULATOR
# ══════════════════════════════════════════════════════════════════════════════
with tab2:

    st.markdown('<div class="sh"><span class="sh-icon">🧪</span>Scenario Presets</div>',
                unsafe_allow_html=True)
    st.caption("Pick a quick preset to stress-test the financials, or use the sidebar sliders for a custom scenario.")

    preset = st.selectbox("Quick preset", [
        "Base",
        "Mild Stress (−10% revenue)",
        "Severe Stress (−30% revenue)",
        "Expense Shock (+20% expenses)",
    ], key="preset")

    temp = df.copy()
    if "Mild"     in preset: temp["revenue"]  *= 0.9
    elif "Severe" in preset: temp["revenue"]  *= 0.7
    elif "Expense" in preset: temp["expenses"] *= 1.2

    sc_score, sc_level, sc_dscr, sc_vol, _, _ = compute_metrics(temp)

    # ── Base vs Scenario cards ──
    st.markdown('<div class="sh"><span class="sh-icon">📊</span>Base vs Scenario Comparison</div>',
                unsafe_allow_html=True)
    comp1, comp2 = st.columns(2)

    with comp1:
        st.markdown(f"""
        <div class="kpi" style="margin-bottom:14px;">
          <div class="kpi-accent kpi-accent-{risk_acc}"></div>
          <div class="kpi-label">Base Scenario</div>
          <div class="kpi-value">{score}</div>
          <div class="kpi-sub">
            {level} risk &nbsp;·&nbsp; DSCR {fmt_num(dscr)} &nbsp;·&nbsp; Vol {fmt_num(volatility)}
          </div>
        </div>""", unsafe_allow_html=True)

    with comp2:
        sc_acc = {"Low": "green", "Moderate": "amber", "High": "red"}.get(sc_level, "blue")
        sc_delta = sc_score - score
        delta_html = (
            f'<span class="kpi-delta-up">▲ {sc_delta}</span>' if sc_delta > 0
            else f'<span class="kpi-delta-down">▼ {abs(sc_delta)}</span>' if sc_delta < 0
            else '<span style="color:#334155;">— No change</span>'
        )
        st.markdown(f"""
        <div class="kpi" style="margin-bottom:14px;">
          <div class="kpi-accent kpi-accent-{sc_acc}"></div>
          <div class="kpi-label">Stressed Scenario</div>
          <div class="kpi-value">{sc_score} &nbsp;{delta_html}</div>
          <div class="kpi-sub">
            {sc_level} risk &nbsp;·&nbsp; DSCR {fmt_num(sc_dscr)} &nbsp;·&nbsp; Vol {fmt_num(sc_vol)}
          </div>
        </div>""", unsafe_allow_html=True)

    # ── Detailed comparison table ──
    st.markdown(f"""
    <table class="ctable">
      <thead>
        <tr>
          <th>Metric</th>
          <th>Base</th>
          <th>Scenario</th>
          <th>Change</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td class="metric-name">Risk Score</td>
          <td>{score}</td>
          <td class="{'td-better' if sc_score >= score else 'td-worse'}">{sc_score}</td>
          <td class="{'td-better' if sc_score >= score else 'td-worse'}">
            {'▲' if sc_score > score else '▼' if sc_score < score else '—'} {abs(sc_score - score)}
          </td>
        </tr>
        <tr>
          <td class="metric-name">DSCR</td>
          <td>{fmt_num(dscr)}</td>
          <td class="{'td-better' if sc_dscr >= dscr else 'td-worse'}">{fmt_num(sc_dscr)}</td>
          <td class="{'td-better' if sc_dscr >= dscr else 'td-worse'}">
            {'▲' if sc_dscr > dscr else '▼'} {fmt_num(abs(sc_dscr - dscr))}
          </td>
        </tr>
        <tr>
          <td class="metric-name">Volatility</td>
          <td>{fmt_num(sc_vol)}</td>
          <td class="{'td-better' if sc_vol <= volatility else 'td-worse'}">{fmt_num(sc_vol)}</td>
          <td class="{'td-better' if sc_vol <= volatility else 'td-worse'}">
            {'▼' if sc_vol < volatility else '▲'} {fmt_num(abs(sc_vol - volatility))}
          </td>
        </tr>
      </tbody>
    </table>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Loan Coverage Test ──
    st.markdown('<div class="sh"><span class="sh-icon">💳</span>Loan Coverage Test</div>',
                unsafe_allow_html=True)
    max_loan_sim = int(max(avg_cash * 36, 10000))

    lc1, lc2, lc3 = st.columns(3)
    with lc1:
        test_loan = st.number_input(
            "Loan amount ($)",
            min_value=0, max_value=max_loan_sim * 3,
            value=int(max(avg_cash * 24, 0)),
            step=1000, format="%d", key="sim_loan",
            help="Total loan amount to test coverage against current cash flows",
        )
    with lc2:
        test_rate = st.number_input(
            "Annual interest rate (%)",
            min_value=0.0, max_value=25.0,
            value=8.0, step=0.5, format="%.1f", key="sim_rate",
            help="Annual interest rate used in amortizing payment calculation",
        )
    with lc3:
        test_term = st.selectbox(
            "Loan term (months)",
            [12, 24, 36, 48, 60], index=1, key="sim_term",
        )

    pay = monthly_payment(test_loan, test_rate, test_term)
    cov = avg_cash / pay if pay > 0 else 0.0
    cov_acc = "green" if cov > 1.2 else ("amber" if cov > 1.0 else "red")

    lm1, lm2, lm3 = st.columns(3)
    lm1.markdown(f"""
    <div class="kpi" style="margin-top:10px;">
      <div class="kpi-accent kpi-accent-blue"></div>
      <div class="kpi-label">Monthly Payment</div>
      <div class="kpi-value">{fmt_money(pay)}</div>
      <div class="kpi-sub">principal + interest</div>
    </div>""", unsafe_allow_html=True)
    lm2.markdown(f"""
    <div class="kpi" style="margin-top:10px;">
      <div class="kpi-accent kpi-accent-{cov_acc}"></div>
      <div class="kpi-label">Cash Flow Coverage</div>
      <div class="kpi-value">{fmt_num(cov)}</div>
      <div class="kpi-sub">min 1.20 recommended</div>
    </div>""", unsafe_allow_html=True)
    lm3.markdown(f"""
    <div class="kpi" style="margin-top:10px;">
      <div class="kpi-accent kpi-accent-blue"></div>
      <div class="kpi-label">Total Repayment</div>
      <div class="kpi-value">{fmt_money(pay * test_term)}</div>
      <div class="kpi-sub">over {test_term} months</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if cov > 1.2:
        st.success("Coverage is sufficient — loan is likely serviceable at this level.")
    elif cov > 1.0:
        st.warning("Marginal coverage — conditional approval may apply; consider a smaller loan or longer term.")
    else:
        st.error("Insufficient coverage — cash flows cannot service this loan at current levels.")

    # ── Revenue Sensitivity ──
    st.markdown('<div class="sh"><span class="sh-icon">📉</span>Revenue Sensitivity Analysis</div>',
                unsafe_allow_html=True)
    x_vals = np.linspace(0.5, 1.5, 20)
    y_vals = [compute_metrics(df.assign(revenue=df["revenue"] * r))[0] for r in x_vals]
    sens_df = (
        pd.DataFrame({"Revenue multiplier": x_vals.round(2), "Risk score": y_vals})
        .set_index("Revenue multiplier")
    )
    st.line_chart(sens_df, use_container_width=True)

    # ── Improvement Suggestions ──
    st.markdown('<div class="sh"><span class="sh-icon">💡</span>Improvement Suggestions</div>',
                unsafe_allow_html=True)
    tips = []
    if sc_dscr < 1.2:
        tips.append("Increase revenue or reduce loan size to improve DSCR")
    if sc_vol > 0.2:
        tips.append("Stabilize revenue streams to reduce volatility")
    if sc_level == "High":
        tips.append("Reduce overall risk exposure before applying for credit")
    if cov < 1.2:
        tips.append("Lower loan amount or extend term to improve cash flow coverage")
    if dscr < benchmark["dscr"]:
        tips.append(f"Improve DSCR to meet {industry} benchmark ({fmt_num(benchmark['dscr'])})")
    if tips:
        for tip in tips:
            st.markdown(f'<div class="li"><span class="li-dot"></span>{tip}</div>',
                        unsafe_allow_html=True)
    else:
        st.success("No major improvements needed for the selected scenario.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — CREDIT MEMO
# ══════════════════════════════════════════════════════════════════════════════
with tab3:

    # ── Executive Summary ──
    st.markdown('<div class="sh"><span class="sh-icon">📄</span>Executive Summary</div>',
                unsafe_allow_html=True)
    risk_badge_cls = {"Low": "badge-approved", "Moderate": "badge-conditional",
                      "High": "badge-declined"}.get(level, "")
    st.markdown(f"""
    <div class="ibox">
      <span class="badge {risk_badge_cls}">{level} Risk</span>
      <br><br>
      The business presents a <strong>{level} risk profile</strong> with a risk score of
      <strong>{score} / 100</strong>. This assessment reflects revenue stability,
      debt service coverage, and overall financial health relative to the
      <strong>{industry}</strong> industry benchmark.
    </div>
    """, unsafe_allow_html=True)

    # ── Key Financial Metrics ──
    st.markdown('<div class="sh"><span class="sh-icon">📊</span>Key Financial Metrics</div>',
                unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    m1.markdown(f"""
    <div class="kpi">
      <div class="kpi-accent kpi-accent-{risk_acc}"></div>
      <div class="kpi-label">Risk Score</div>
      <div class="kpi-value">{score}</div>
      <div class="kpi-sub">out of 100</div>
    </div>""", unsafe_allow_html=True)
    m2.markdown(f"""
    <div class="kpi">
      <div class="kpi-accent kpi-accent-{dscr_acc}"></div>
      <div class="kpi-label">DSCR</div>
      <div class="kpi-value">{fmt_num(dscr)}</div>
      <div class="kpi-sub">min 1.20 recommended</div>
    </div>""", unsafe_allow_html=True)
    m3.markdown(f"""
    <div class="kpi">
      <div class="kpi-accent kpi-accent-{vol_acc}"></div>
      <div class="kpi-label">Volatility</div>
      <div class="kpi-value">{fmt_num(volatility)}</div>
      <div class="kpi-sub">lower is more stable</div>
    </div>""", unsafe_allow_html=True)
    m4.markdown(f"""
    <div class="kpi">
      <div class="kpi-accent kpi-accent-{pd_acc}"></div>
      <div class="kpi-label">Prob. of Default</div>
      <div class="kpi-value">{fmt_pct(pd_val * 100)}</div>
      <div class="kpi-sub">estimated likelihood</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="ibox">
      <strong>Interpretation guide</strong><br>
      DSCR &gt; 1.20 &nbsp;→&nbsp; healthy debt coverage &nbsp;&nbsp;·&nbsp;&nbsp;
      Low volatility &nbsp;→&nbsp; stable, predictable income &nbsp;&nbsp;·&nbsp;&nbsp;
      PD = estimated likelihood of default over the loan period
    </div>""", unsafe_allow_html=True)

    # ── Risk Signals ──
    st.markdown('<div class="sh"><span class="sh-icon">⚠️</span>Risk Signals</div>',
                unsafe_allow_html=True)
    if explanations:
        for text, color in explanations:
            dot_cls   = f"dot-{color}"
            alert_cls = f"alert-{'yellow' if color == 'yellow' else color}"
            st.markdown(f"""
            <div class="alert {alert_cls}">
              <span class="dot {dot_cls}"></span>{text}
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="alert alert-green">
          <span class="dot dot-green"></span>No major risk signals detected
        </div>""", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════
    # LOAN STRUCTURING — number inputs only, no sliders
    # ════════════════════════════════════════════════════════════════
    st.markdown('<div class="sh"><span class="sh-icon">🏦</span>Loan Structuring</div>',
                unsafe_allow_html=True)
    st.markdown("""
    <div class="ibox">
      Enter the loan parameters below. All values update the decision and
      pricing analysis instantly.
    </div>""", unsafe_allow_html=True)

    baseline_suggestion = int(max(avg_cash * 24, 0))
    max_loan_memo       = int(max(avg_cash * 48, 100_000))

    # Rate suggestion based on risk
    if level == "Low":        suggested_rate = 8.0
    elif level == "Moderate": suggested_rate = 13.0
    else:                     suggested_rate = 18.0

    # Four inputs in a single row
    inp1, inp2, inp3, inp4 = st.columns(4)
    with inp1:
        memo_loan = st.number_input(
            "Loan amount ($)",
            min_value=0,
            max_value=999_999_999,
            value=baseline_suggestion,
            step=1_000,
            format="%d",
            key="memo_loan_input",
            help="Total loan amount requested by the borrower",
        )
    with inp2:
        memo_collateral = st.number_input(
            "Collateral value ($)",
            min_value=0,
            max_value=999_999_999,
            value=int(baseline_suggestion * 0.5),
            step=1_000,
            format="%d",
            key="memo_collateral_input",
            help="Market value of assets pledged as collateral",
        )
    with inp3:
        memo_rate = st.number_input(
            "Annual interest rate (%)",
            min_value=0.0,
            max_value=99.9,
            value=suggested_rate,
            step=0.25,
            format="%.2f",
            key="memo_rate_input",
            help="Proposed or indicative annual interest rate for the loan",
        )
    with inp4:
        memo_term = st.selectbox(
            "Loan term (months)",
            [12, 24, 36, 48, 60],
            index=1,
            key="memo_term_input",
        )

    # ── Calculated outputs ──
    payment  = monthly_payment(memo_loan, memo_rate, memo_term)
    coverage = avg_cash / payment if payment > 0 else 0.0
    ltv      = memo_loan / memo_collateral if memo_collateral > 0 else 999.0
    total_repayment = payment * memo_term
    total_interest  = total_repayment - memo_loan

    st.markdown("<br>", unsafe_allow_html=True)
    calc1, calc2, calc3, calc4 = st.columns(4)
    pay_acc = "green" if coverage > 1.2 else ("amber" if coverage > 1.0 else "red")
    ltv_acc = "green" if ltv <= 0.8     else ("amber" if ltv <= 1.0      else "red")

    calc1.markdown(f"""
    <div class="kpi">
      <div class="kpi-accent kpi-accent-blue"></div>
      <div class="kpi-label">Monthly Payment</div>
      <div class="kpi-value">{fmt_money(payment)}</div>
      <div class="kpi-sub">principal + interest</div>
    </div>""", unsafe_allow_html=True)
    calc2.markdown(f"""
    <div class="kpi">
      <div class="kpi-accent kpi-accent-{pay_acc}"></div>
      <div class="kpi-label">Cash Flow Coverage</div>
      <div class="kpi-value">{fmt_num(coverage)}</div>
      <div class="kpi-sub">min 1.20 recommended</div>
    </div>""", unsafe_allow_html=True)
    calc3.markdown(f"""
    <div class="kpi">
      <div class="kpi-accent kpi-accent-{ltv_acc}"></div>
      <div class="kpi-label">Loan-to-Value (LTV)</div>
      <div class="kpi-value">{fmt_num(ltv)}</div>
      <div class="kpi-sub">max 0.80 – 0.90 typical</div>
    </div>""", unsafe_allow_html=True)
    calc4.markdown(f"""
    <div class="kpi">
      <div class="kpi-accent kpi-accent-blue"></div>
      <div class="kpi-label">Total Interest Cost</div>
      <div class="kpi-value">{fmt_money(max(total_interest, 0))}</div>
      <div class="kpi-sub">total repayment: {fmt_money(total_repayment)}</div>
    </div>""", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════
    # DECISION LOGIC — single pass, no overwrites
    # ════════════════════════════════════════════════════════════════
    if coverage < 1.0 or ltv > 1.2 or level == "High":
        decision   = "Declined"
        rate_range = "N/A"
        conditions   = ["Improve financial stability before reapplying"]
        improvements = []
    elif coverage < 1.2 or ltv > 0.9 or level == "Moderate":
        decision   = "Conditionally Approved"
        rate_range = "10% – 16%"
        conditions, improvements = [], []
        if coverage < 1.2:
            conditions.append("Demonstrate stronger cash flow or reduce loan size")
        if ltv > 0.9:
            conditions.append("Provide additional collateral or reduce loan amount")
        if volatility > 0.2:
            conditions.append("Provide revenue history to explain volatility")
        conditions.append("Provide updated financial statements and projections")
    else:
        decision   = "Approved"
        rate_range = "6% – 10%"
        conditions   = ["Standard underwriting documentation"]
        improvements = []

    # Universal improvement tips
    if coverage < 1.2:
        improvements.append("Increase revenue or reduce the requested loan amount")
    if ltv > 0.9:
        improvements.append("Increase collateral value or reduce loan size")
    if volatility > 0.2:
        improvements.append("Stabilize revenue streams or provide a longer track record")
    if dscr < 1.2:
        improvements.append("Improve DSCR by increasing profit or reducing expenses")
    if dscr < benchmark["dscr"]:
        improvements.append(
            f"Bring DSCR in line with {industry} benchmark ({fmt_num(benchmark['dscr'])})"
        )

    # ── Decision Output ──
    st.markdown('<div class="sh"><span class="sh-icon">⚖️</span>Lending Decision</div>',
                unsafe_allow_html=True)
    badge_cls = {
        "Approved": "badge-approved",
        "Conditionally Approved": "badge-conditional",
        "Declined": "badge-declined",
    }.get(decision, "")

    dec_col, price_col = st.columns(2)
    with dec_col:
        st.markdown(f"""
        <div class="kpi" style="min-height:200px;">
          <div class="kpi-accent kpi-accent-{'green' if decision=='Approved' else 'amber' if 'Conditional' in decision else 'red'}"></div>
          <div class="kpi-label">Decision</div>
          <div style="margin:10px 0 16px;">
            <span class="badge {badge_cls}">{decision}</span>
          </div>
          <div class="mrow"><span class="mk">Loan amount</span><span class="mv">{fmt_money(memo_loan)}</span></div>
          <div class="mrow"><span class="mk">Loan term</span><span class="mv">{memo_term} months</span></div>
          <div class="mrow"><span class="mk">Risk level</span><span class="mv">{level}</span></div>
          <div class="mrow"><span class="mk">Collateral</span><span class="mv">{fmt_money(memo_collateral)}</span></div>
        </div>""", unsafe_allow_html=True)

    with price_col:
        st.markdown(f"""
        <div class="kpi" style="min-height:200px;">
          <div class="kpi-accent kpi-accent-blue"></div>
          <div class="kpi-label">Pricing &amp; Repayment</div>
          <div style="margin-top:16px;"></div>
          <div class="mrow"><span class="mk">Indicative rate</span><span class="mv">{rate_range}</span></div>
          <div class="mrow"><span class="mk">Applied rate</span><span class="mv">{fmt_pct(memo_rate)}</span></div>
          <div class="mrow"><span class="mk">Monthly payment</span><span class="mv">{fmt_money(payment)}</span></div>
          <div class="mrow"><span class="mk">Total repayment</span><span class="mv">{fmt_money(total_repayment)}</span></div>
          <div class="mrow"><span class="mk">Total interest</span><span class="mv">{fmt_money(max(total_interest,0))}</span></div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    cond_col, impr_col = st.columns(2)

    with cond_col:
        st.markdown('<div class="sh"><span class="sh-icon">📋</span>Lender Requirements</div>',
                    unsafe_allow_html=True)
        for c in conditions:
            st.markdown(f'<div class="li"><span class="li-dot"></span>{c}</div>',
                        unsafe_allow_html=True)

    with impr_col:
        st.markdown('<div class="sh"><span class="sh-icon">💡</span>How to Improve Approval</div>',
                    unsafe_allow_html=True)
        if improvements:
            for i in improvements:
                st.markdown(f'<div class="li"><span class="li-dot"></span>{i}</div>',
                            unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="alert alert-green">
              <span class="dot dot-green"></span>Strong profile — no major improvements needed
            </div>""", unsafe_allow_html=True)

    # ── Credit Interpretation ──
    st.markdown('<div class="sh"><span class="sh-icon">🧠</span>Credit Interpretation</div>',
                unsafe_allow_html=True)
    if decision == "Approved":
        st.success("Business demonstrates strong repayment ability with manageable risk.")
    elif decision == "Conditionally Approved":
        st.warning("Business is viable but requires mitigations to reduce lender risk.")
    else:
        st.error("Current financial profile does not support additional debt at this level.")
