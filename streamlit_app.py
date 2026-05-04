import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="SME Risk Analyzer", layout="wide")

# -----------------------------
# UI Styling
# -----------------------------
st.markdown("""
<style>
.block-container {padding-top: 1.5rem; padding-bottom: 2rem;}
section[data-testid="stSidebar"] {background-color: #111827; color: white;}

.kpi {
    padding: 18px;
    border-radius: 12px;
    background: #f9fafb;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.section-title {
    font-size: 22px;
    font-weight: 600;
    margin-top: 20px;
    margin-bottom: 10px;
}

.card-light {
    padding: 15px;
    border-radius: 10px;
    background: #f3f4f6;
}

.card {
    padding: 12px;
    border-radius: 8px;
    margin-bottom: 8px;
    font-weight: 500;
}
.green {background:#d1fae5; color:#065f46;}
.yellow {background:#fef3c7; color:#92400e;}
.red {background:#fee2e2; color:#991b1b;}
</style>
""", unsafe_allow_html=True)

st.title("📊 SME Risk Analyzer")
st.caption("Financial risk analysis, benchmarking, simulation, and lending decisions")

# -----------------------------
# Template Download
# -----------------------------
template = """month,revenue,expenses,debt_payment
Jan,80000,60000,10000
Feb,85000,62000,10000
Mar,90000,65000,10000
Apr,78000,61000,10000
"""
st.download_button("📥 Download Sample CSV", template, "sample.csv")

# -----------------------------
# Industry Benchmarks
# -----------------------------
def get_industry_benchmark(industry):
    return {
        "General":      {"dscr": 1.2, "volatility": 0.15},
        "Restaurant":   {"dscr": 1.3, "volatility": 0.25},
        "Retail":       {"dscr": 1.25, "volatility": 0.2},
        "SaaS":         {"dscr": 1.1, "volatility": 0.1},
        "Construction": {"dscr": 1.4, "volatility": 0.3},
    }.get(industry, {"dscr": 1.2, "volatility": 0.15})

# -----------------------------
# Probability of Default Model
# -----------------------------
def calculate_pd(score, dscr, volatility):
    pd_val = 0.02
    if dscr < 1.0:
        pd_val += 0.15
    elif dscr < 1.2:
        pd_val += 0.08
    if volatility > 0.25:
        pd_val += 0.12
    elif volatility > 0.15:
        pd_val += 0.06
    if score < 60:
        pd_val += 0.15
    elif score < 80:
        pd_val += 0.07
    return min(pd_val, 0.6)

# -----------------------------
# Monthly payment with interest (amortization)
# -----------------------------
def monthly_payment(principal, annual_rate_pct, term_months):
    """Standard amortizing payment. Falls back to principal-only if rate is 0."""
    if principal <= 0 or term_months <= 0:
        return 0.0
    r = annual_rate_pct / 100 / 12
    if r == 0:
        return principal / term_months
    return principal * r * (1 + r) ** term_months / ((1 + r) ** term_months - 1)

# -----------------------------
# Core Metrics
# -----------------------------
def compute_metrics(df):
    df = df.copy()
    df["profit"] = df["revenue"] - df["expenses"]
    df["cash_flow"] = df["profit"] - df["debt_payment"]

    avg_cash = df["cash_flow"].mean()
    avg_debt = df["debt_payment"].mean()

    # DSCR = net operating cash flow / debt service
    dscr = avg_cash / avg_debt if avg_debt > 0 else 0.0

    avg_rev = df["revenue"].mean()
    volatility = np.std(df["revenue"]) / avg_rev if avg_rev > 0 else 0.0

    score = 100
    explanations = []

    if dscr < 1.2:
        score -= 30
        explanations.append(("Low DSCR: weak debt coverage", "red"))

    if volatility > 0.2:
        score -= 20
        explanations.append(("High revenue volatility", "yellow"))

    if score >= 80:
        level = "Low"
    elif score >= 60:
        level = "Moderate"
    else:
        level = "High"

    return score, level, dscr, volatility, explanations, avg_cash

# -----------------------------
# File Upload
# -----------------------------
file = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])

if file:
    try:
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
    except Exception as e:
        st.error(f"Could not read file: {e}")
        st.stop()

    df.columns = [c.lower().strip().replace(" ", "_") for c in df.columns]

    # Validate required columns
    required = {"revenue", "expenses"}
    missing = required - set(df.columns)
    if missing:
        st.error(f"Missing required columns: {', '.join(missing)}")
        st.stop()

    if "debt_payment" not in df.columns:
        df["debt_payment"] = 0

    # Drop rows where revenue or expenses are non-numeric / NaN
    for col in ["revenue", "expenses", "debt_payment"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["revenue", "expenses"])

    if df.empty:
        st.error("No valid numeric rows found in the file.")
        st.stop()

    score, level, dscr, volatility, explanations, avg_cash = compute_metrics(df)

    # -----------------------------
    # Sidebar
    # -----------------------------
    st.sidebar.title("⚙️ Scenario Controls")

    rev_pct  = st.sidebar.slider("Revenue change (%)",  -50, 50, 0)
    exp_pct  = st.sidebar.slider("Expense change (%)",  -50, 50, 0)
    debt_pct = st.sidebar.slider("Debt payment change (%)", -50, 50, 0)

    industry  = st.sidebar.selectbox(
        "Industry", ["General", "Restaurant", "Retail", "SaaS", "Construction"]
    )
    benchmark = get_industry_benchmark(industry)

    # Sidebar scenario computation
    sim_df = df.copy()
    sim_df["revenue"]      *= (1 + rev_pct  / 100)
    sim_df["expenses"]     *= (1 + exp_pct  / 100)
    sim_df["debt_payment"] *= (1 + debt_pct / 100)
    s_score, s_level, s_dscr, s_vol, _, _ = compute_metrics(sim_df)

    st.sidebar.markdown("---")
    st.sidebar.write(f"**Scenario Score:** {s_score}")
    st.sidebar.write(f"**Scenario Risk:** {s_level}")
    st.sidebar.write(f"**Scenario DSCR:** {s_dscr:.2f}")

    # -----------------------------
    # Tabs
    # -----------------------------
    tab1, tab2, tab3 = st.tabs(["Dashboard", "Simulator", "Credit Memo"])

    # =============================
    # DASHBOARD
    # =============================
    with tab1:
        st.markdown('<div class="section-title">📊 Key Metrics</div>', unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f'<div class="kpi"><b>Risk Score</b><br>{score}</div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="kpi"><b>DSCR</b><br>{dscr:.2f}</div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="kpi"><b>Volatility</b><br>{volatility:.2f}</div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="kpi"><b>PD</b><br>{calculate_pd(score, dscr, volatility)*100:.1f}%</div>', unsafe_allow_html=True)

        st.subheader("🏦 Risk Alerts")
        if explanations:
            for text, color in explanations:
                st.markdown(f'<div class="card {color}">{text}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="card green">No major risks detected</div>', unsafe_allow_html=True)

        st.subheader("🏭 Industry Comparison")
        col_b, col_v = st.columns(2)
        dscr_color  = "green" if dscr  >= benchmark["dscr"]       else "red"
        vol_color   = "green" if volatility <= benchmark["volatility"] else "red"
        col_b.markdown(
            f'<div class="card {dscr_color}">DSCR: {dscr:.2f} (benchmark: {benchmark["dscr"]:.2f})</div>',
            unsafe_allow_html=True
        )
        col_v.markdown(
            f'<div class="card {vol_color}">Volatility: {volatility:.2f} (benchmark: {benchmark["volatility"]:.2f})</div>',
            unsafe_allow_html=True
        )

        st.markdown('<div class="section-title">📈 Revenue Trend</div>', unsafe_allow_html=True)
        chart_df = df[["revenue", "expenses"]].copy()
        if "month" in df.columns:
            chart_df.index = df["month"]
        st.line_chart(chart_df)

    # =============================
    # SIMULATOR
    # =============================
    with tab2:
        st.subheader("🧪 Scenario Simulator")
        st.caption("Use sidebar sliders for custom scenarios, or pick a preset below.")

        preset = st.selectbox(
            "Quick preset",
            ["Base", "Mild Stress (−10% revenue)", "Severe Stress (−30% revenue)", "Expense Shock (+20% expenses)"]
        )

        temp = df.copy()
        if "Mild" in preset:
            temp["revenue"] *= 0.9
        elif "Severe" in preset:
            temp["revenue"] *= 0.7
        elif "Expense" in preset:
            temp["expenses"] *= 1.2

        sc_score, sc_level, sc_dscr, sc_vol, _, _ = compute_metrics(temp)

        st.table({
            "Metric":   ["Risk Score", "DSCR",         "Volatility"],
            "Base":     [score,        round(dscr, 2),  round(volatility, 2)],
            "Scenario": [sc_score,     round(sc_dscr,2), round(sc_vol, 2)],
        })

        st.markdown("---")
        st.subheader("💳 Loan Coverage Test")

        # FIX: single number_input, no dangling slider
        max_loan = int(max(avg_cash * 36, 10000))
        test_loan = st.number_input(
            "Loan amount ($)", min_value=0, max_value=max_loan * 3,
            value=int(max(avg_cash * 24, 0)), step=1000
        )
        test_rate = st.slider("Annual interest rate (%)", 0.0, 25.0, 8.0, step=0.5)
        test_term = st.selectbox("Term (months)", [12, 24, 36, 48, 60], index=1, key="sim_term")

        pay = monthly_payment(test_loan, test_rate, test_term)
        cov = avg_cash / pay if pay > 0 else 0.0

        col_p, col_c = st.columns(2)
        col_p.metric("Monthly payment", f"${pay:,.0f}")
        col_c.metric("Cash flow coverage", f"{cov:.2f}")

        if cov > 1.2:
            st.success("✅ Coverage sufficient — likely approved")
        elif cov > 1.0:
            st.warning("⚠️ Marginal coverage — conditional approval")
        else:
            st.error("❌ Insufficient coverage — likely declined")

        st.markdown("---")
        st.subheader("📉 Revenue Sensitivity")
        x_vals = np.linspace(0.5, 1.5, 20)
        y_vals = []
        for r in x_vals:
            t = df.copy()
            t["revenue"] *= r
            s, _, _, _, _, _ = compute_metrics(t)
            y_vals.append(s)

        sens_df = pd.DataFrame({"Revenue multiplier": x_vals, "Risk score": y_vals}).set_index("Revenue multiplier")
        st.line_chart(sens_df)

        st.subheader("💡 Improvement Suggestions")
        tips = []
        if sc_dscr < 1.2:
            tips.append("Increase revenue or reduce loan size to improve DSCR")
        if sc_vol > 0.2:
            tips.append("Stabilize revenue streams to reduce volatility")
        if sc_level == "High":
            tips.append("Reduce overall risk exposure before applying")
        if cov < 1.2:
            tips.append("Lower loan amount or extend term to improve coverage ratio")
        if dscr < benchmark["dscr"]:
            tips.append(f"Improve DSCR to meet {industry} industry benchmark ({benchmark['dscr']:.2f})")
        if tips:
            for tip in tips:
                st.write(f"- {tip}")
        else:
            st.success("No major improvements needed")

    # =============================
    # CREDIT MEMO
    # =============================
    with tab3:
        st.markdown('<div class="section-title">📄 Credit Memo</div>', unsafe_allow_html=True)

        st.markdown('<div class="card-light">Executive Summary</div>', unsafe_allow_html=True)
        st.write(f"""
The business presents a **{level} risk profile** with a risk score of **{score}**.
This reflects revenue stability, debt coverage, and overall financial health.
""")

        st.markdown("### 📊 Key Metrics")
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Risk Score",  f"{score}")
        col_b.metric("DSCR",        f"{dscr:.2f}")
        col_c.metric("Volatility",  f"{volatility:.2f}")
        pd_val = calculate_pd(score, dscr, volatility)
        st.metric("Probability of Default (PD)", f"{pd_val * 100:.1f}%")

        st.markdown("""
**Interpretation guide**
- DSCR > 1.2 → healthy debt coverage
- Low volatility → stable, predictable income
- PD = estimated likelihood of default over the loan period
""")

        st.markdown('<div class="section-title">⚠️ Risk Signals</div>', unsafe_allow_html=True)
        if explanations:
            for text, color in explanations:
                st.markdown(f'<div class="card {color}">{text}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="card green">No major risk detected</div>', unsafe_allow_html=True)

        # -----------------------------
        # Loan Structuring (single consistent block)
        # -----------------------------
        st.markdown("---")
        st.markdown("### 🏦 Loan Structuring")

        baseline_suggestion = int(max(avg_cash * 24, 0))
        max_loan_memo = int(max(avg_cash * 48, 10000))

        # FIX: use session_state to keep slider and input in sync
        if "memo_loan" not in st.session_state:
            st.session_state["memo_loan"] = baseline_suggestion

        memo_loan_slider = st.slider(
            "Requested loan amount",
            min_value=0,
            max_value=max_loan_memo,
            value=st.session_state["memo_loan"],
            step=1000,
            key="memo_loan_slider"
        )
        st.session_state["memo_loan"] = memo_loan_slider
        memo_loan = memo_loan_slider  # single source of truth

        if "memo_collateral" not in st.session_state:
            st.session_state["memo_collateral"] = int(baseline_suggestion * 0.5)

        collateral_slider = st.slider(
            "Collateral value",
            min_value=0,
            max_value=max_loan_memo,
            value=st.session_state["memo_collateral"],
            step=1000,
            key="memo_collateral_slider"
        )
        st.session_state["memo_collateral"] = collateral_slider
        memo_collateral = collateral_slider

        memo_term = st.selectbox("Loan term (months)", [12, 24, 36, 48, 60], index=1, key="memo_term")

        # Interest rate is driven by risk level
        if level == "Low":
            base_rate = 8.0
        elif level == "Moderate":
            base_rate = 13.0
        else:
            base_rate = 18.0

        memo_rate = st.slider(
            "Annual interest rate (%)", 0.0, 25.0, base_rate, step=0.5, key="memo_rate"
        )

        # Calculations
        payment  = monthly_payment(memo_loan, memo_rate, memo_term)
        coverage = avg_cash / payment if payment > 0 else 0.0
        ltv      = memo_loan / memo_collateral if memo_collateral > 0 else 999.0

        col1, col2, col3 = st.columns(3)
        col1.metric("Monthly payment",      f"${payment:,.0f}")
        col2.metric("Cash flow coverage",   f"{coverage:.2f}")
        col3.metric("LTV (loan-to-value)",  f"{ltv:.2f}")

        # -----------------------------
        # Decision logic (single pass, no overwrites)
        # -----------------------------
        if coverage < 1.0 or ltv > 1.2 or level == "High":
            decision    = "Declined"
            rate_range  = "N/A"
            conditions  = ["Improve financial stability before reapplying"]
            improvements = []
        elif coverage < 1.2 or ltv > 0.9 or level == "Moderate":
            decision    = "Conditionally Approved"
            rate_range  = "10% – 16%"
            conditions  = []
            improvements = []
            if coverage < 1.2:
                conditions.append("Demonstrate stronger cash flow or reduce loan size")
            if ltv > 0.9:
                conditions.append("Provide additional collateral or reduce loan amount")
            if volatility > 0.2:
                conditions.append("Provide revenue history to explain volatility")
            conditions.append("Provide updated financial statements and projections")
        else:
            decision    = "Approved"
            rate_range  = "6% – 10%"
            conditions  = ["Standard underwriting documentation"]
            improvements = []

        # Improvement suggestions (applicable to all decisions)
        if coverage < 1.2:
            improvements.append("Increase revenue or reduce requested loan amount")
        if ltv > 0.9:
            improvements.append("Increase collateral or reduce loan size")
        if volatility > 0.2:
            improvements.append("Stabilize revenue streams or show longer track record")
        if dscr < 1.2:
            improvements.append("Improve DSCR by increasing profit or reducing expenses")
        if dscr < benchmark["dscr"]:
            improvements.append(f"Bring DSCR in line with {industry} industry benchmark ({benchmark['dscr']:.2f})")

        st.markdown("---")
        col_dec, col_price = st.columns(2)
        with col_dec:
            st.markdown(f"### Decision: **{decision}**")
            st.write(f"- Loan amount: ${memo_loan:,.0f}")
            st.write(f"- Term: {memo_term} months")
            st.write(f"- Risk level: {level}")
        with col_price:
            st.markdown("### Pricing")
            st.write(f"- Indicative rate: {rate_range}")
            st.write(f"- Applied rate (above): {memo_rate:.1f}%")
            st.write(f"- Monthly payment: ${payment:,.0f}")

        st.markdown("### 📋 Lender Requirements")
        for c in conditions:
            st.write(f"- {c}")

        if improvements:
            st.markdown("### 💡 How to Improve Approval")
            for i in improvements:
                st.write(f"- {i}")
        else:
            st.success("Strong profile — no major improvements needed")

        st.markdown("### 🧠 Credit Interpretation")
        if decision == "Approved":
            st.success("Business demonstrates strong repayment ability with manageable risk.")
        elif decision == "Conditionally Approved":
            st.warning("Business is viable but requires mitigations to reduce risk.")
        else:
            st.error("Current financial profile does not support additional debt.")
