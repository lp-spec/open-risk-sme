import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="SME Risk Analyzer", layout="wide")

# -----------------------------
# 🎨 UI Styling
# -----------------------------
st.markdown("""
<style>
.card {
    padding: 15px;
    border-radius: 10px;
    color: white;
    font-weight: 500;
    margin-bottom:10px;
}
.green {background-color: #2ecc71;}
.yellow {background-color: #f1c40f; color:black;}
.red {background-color: #e74c3c;}
</style>
""", unsafe_allow_html=True)

st.title("📊 SME Risk Analyzer")
st.caption("Financial risk analysis, benchmarking, and lending simulation")

# -----------------------------
# 📥 Template
# -----------------------------
template = """month,revenue,expenses,debt_payment
Jan,80000,60000,10000
Feb,85000,62000,10000
"""
st.download_button("📥 Download Sample CSV", template, "sample.csv")

# -----------------------------
# 🏭 Industry Benchmarks
# -----------------------------
def get_industry_benchmark(industry):
    return {
        "General": {"dscr": 1.2, "volatility": 0.15},
        "Restaurant": {"dscr": 1.3, "volatility": 0.25},
        "Retail": {"dscr": 1.25, "volatility": 0.2},
        "SaaS": {"dscr": 1.1, "volatility": 0.1},
        "Construction": {"dscr": 1.4, "volatility": 0.3},
    }.get(industry)

# -----------------------------
# 📉 PD Model
# -----------------------------
def calculate_pd(score, dscr, volatility):
    pd = 0.02
    if dscr < 1.0: pd += 0.15
    elif dscr < 1.2: pd += 0.08

    if volatility > 0.25: pd += 0.12
    elif volatility > 0.15: pd += 0.06

    if score < 60: pd += 0.15
    elif score < 80: pd += 0.07

    return min(pd, 0.6)

# -----------------------------
# 📊 Core Metrics
# -----------------------------
def compute_metrics(df):
    df["profit"] = df["revenue"] - df["expenses"]
    df["cash_flow"] = df["profit"] - df["debt_payment"]

    avg_cash = df["cash_flow"].mean()
    debt = df["debt_payment"].mean()

    dscr = avg_cash / debt if debt else 0
    volatility = np.std(df["revenue"]) / np.mean(df["revenue"]) if np.mean(df["revenue"]) else 0

    score = 100
    explanations = []

    if dscr < 1.2:
        score -= 30
        explanations.append(("Low DSCR: weak debt coverage", "red"))

    if volatility > 0.2:
        score -= 20
        explanations.append(("High revenue volatility", "yellow"))

    if score >= 80: level = "Low"
    elif score >= 60: level = "Moderate"
    else: level = "High"

    return score, level, dscr, volatility, explanations, avg_cash

# -----------------------------
# 📤 Upload
# -----------------------------
file = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])

if file:
    df = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)
    df.columns = [c.lower().strip().replace(" ", "_") for c in df.columns]

    if "debt_payment" not in df.columns:
        df["debt_payment"] = 0

    score, level, dscr, volatility, explanations, avg_cash = compute_metrics(df)

    # -----------------------------
    # 🧪 Sidebar Simulator
    # -----------------------------
    st.sidebar.header("🧪 Scenario Simulator")

    rev = st.sidebar.slider("Revenue Change %", -50, 50, 0)
    exp = st.sidebar.slider("Expense Change %", -50, 50, 0)
    debt = st.sidebar.slider("Debt Change %", -50, 50, 0)

    sim_df = df.copy()
    sim_df["revenue"] *= (1 + rev / 100)
    sim_df["expenses"] *= (1 + exp / 100)
    sim_df["debt_payment"] *= (1 + debt / 100)

    s_score, s_level, *_ = compute_metrics(sim_df)

    st.sidebar.write(f"Scenario Score: {s_score}")
    st.sidebar.write(f"Scenario Risk: {s_level}")

    # -----------------------------
    # 🏭 Industry
    # -----------------------------
    industry = st.selectbox("Select Industry", ["General","Restaurant","Retail","SaaS","Construction"])
    benchmark = get_industry_benchmark(industry)

    # -----------------------------
    # 📑 TABS RESTORED
    # -----------------------------
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🧪 Simulator", "📄 Credit Memo"])

    # =============================
    # 📊 DASHBOARD
    # =============================
    with tab1:
        st.subheader("📈 Risk Summary")

        c1, c2, c3 = st.columns(3)
        c1.metric("Risk Score", f"{score:,}")
        c2.metric("DSCR", round(dscr,2))
        c3.metric("Volatility", round(volatility,2))

        st.markdown(f"### Risk Level: **{level}**")

        st.markdown("""
**Definitions:**
- DSCR > 1.2 = healthy  
- Volatility < 0.15 = stable  
""")

        st.subheader("📊 Revenue Trend")
        st.line_chart(df["revenue"])

        st.subheader("🏦 Risk Alerts")

        if explanations:
            for text, color in explanations:
                st.markdown(f'<div class="card {color}">{text}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="card green">No major risks</div>', unsafe_allow_html=True)

        st.subheader("🏭 Industry Comparison")
        st.write(f"Your DSCR: {round(dscr,2)} vs {benchmark['dscr']}")
        st.write(f"Your Volatility: {round(volatility,2)} vs {benchmark['volatility']}")

    # =============================
    # 🧪 SIMULATOR TAB
    # =============================
    with tab2:
        st.subheader("Scenario Comparison")

        st.metric("Base Score", score)
        st.metric("Scenario Score", s_score)

    # =============================
    # 📄 CREDIT MEMO TAB RESTORED
    # =============================
    with tab3:
        st.subheader("📄 Credit Memo")

        st.write(f"Risk Level: {level} | Score: {score}")

        pd_val = calculate_pd(score, dscr, volatility)
        st.metric("Probability of Default", f"{pd_val*100:.1f}%")

        st.markdown("""
**What this means:**
- <5% = low risk  
- 5–15% = moderate  
- >15% = high  
""")

        # -----------------------------
        # 🏦 Lending Simulation
        # -----------------------------
        st.subheader("🏦 Loan Simulation")

        baseline = max(avg_cash * 3, 0)

        loan_slider = st.slider("Loan Amount (Slider)", 0, int(baseline*2), int(baseline), step=1000)
        loan = st.number_input("Loan Amount (Manual)", value=int(loan_slider), step=1000)

        collateral_slider = st.slider("Collateral (Slider)", 0, int(baseline*2), int(baseline*0.5), step=1000)
        collateral = st.number_input("Collateral (Manual)", value=int(collateral_slider), step=1000)

        term = st.selectbox("Loan Term", [12,24,36,48,60])

        payment = loan / term if term else 0
        coverage = avg_cash / payment if payment else 0
        ltv = loan / collateral if collateral else 999

        st.markdown("""
- Coverage >1.2 = safe  
- LTV <0.9 = safe  
""")

        decision = "Approved"

        if coverage < 1.0 or ltv > 1.2 or level == "High":
            decision = "Declined"
        elif coverage < 1.2 or ltv > 0.9:
            decision = "Conditional"

        col1, col2, col3 = st.columns(3)
        col1.metric("Decision", decision)
        col2.metric("Payment", f"${payment:,.0f}")
        col3.metric("Coverage", round(coverage,2))

        col4, col5 = st.columns(2)
        col4.metric("LTV", round(ltv,2))
        col5.metric("Rate", "6–16%" if decision != "Declined" else "N/A")
