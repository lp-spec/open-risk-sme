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
st.caption("Financial risk analysis, benchmarking, simulation, and lending decisions")

# -----------------------------
# 📥 Template
# -----------------------------
template = """month,revenue,expenses,debt_payment
Jan,80000,60000,10000
Feb,85000,62000,10000
"""
st.download_button("📥 Download Sample CSV", template, "sample.csv")

# -----------------------------
# 🏭 Benchmark
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
# 📊 Metrics
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

    if score >= 80:
        level = "Low"
    elif score >= 60:
        level = "Moderate"
    else:
        level = "High"

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

    s_score, s_level, s_dscr, s_vol, *_ = compute_metrics(sim_df)

    st.sidebar.write(f"Scenario Score: {s_score:,}")
    st.sidebar.write(f"Scenario Risk: {s_level}")

    # -----------------------------
    # Industry
    # -----------------------------
    industry = st.selectbox("Select Industry", ["General","Restaurant","Retail","SaaS","Construction"])
    benchmark = get_industry_benchmark(industry)

    # -----------------------------
    # Tabs
    # -----------------------------
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🧪 Simulator", "📄 Credit Memo"])

    # =============================
    # DASHBOARD
    # =============================
    with tab1:
        st.subheader("📈 Risk Summary")

        c1, c2, c3 = st.columns(3)
        c1.metric("Risk Score", f"{score:,}")
        c2.metric("DSCR", round(dscr,2))
        c3.metric("Volatility", round(volatility,2))

        st.subheader("🏦 Risk Alerts")
        if explanations:
            for text, color in explanations:
                st.markdown(f'<div class="card {color}">{text}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="card green">No major risks</div>', unsafe_allow_html=True)

        st.subheader("🏭 Industry Comparison")
        st.write(f"DSCR: {dscr:.2f} vs {benchmark['dscr']}")
        st.write(f"Volatility: {volatility:.2f} vs {benchmark['volatility']}")

    # =============================
    # SIMULATOR (FULL FEATURES)
    # =============================
    with tab2:
        st.subheader("🧪 Advanced Scenario Simulator")

        scenario = st.selectbox("Scenario",
            ["Base", "Mild Stress", "Severe Stress", "Expense Shock"])

        temp = df.copy()
        if scenario == "Mild Stress":
            temp["revenue"] *= 0.9
        elif scenario == "Severe Stress":
            temp["revenue"] *= 0.7
        elif scenario == "Expense Shock":
            temp["expenses"] *= 1.2

        sc_score, sc_level, sc_dscr, sc_vol, *_ = compute_metrics(temp)

        st.table({
            "Metric":["Score","DSCR","Volatility"],
            "Base":[score,round(dscr,2),round(volatility,2)],
            "Scenario":[sc_score,round(sc_dscr,2),round(sc_vol,2)]
        })

        # Boundary
        baseline = max(avg_cash*3,0)
        test = st.slider("Test Loan",0,int(baseline*3),int(baseline),step=1000)

        pay = test/24 if test else 0
        cov = avg_cash/pay if pay else 0

        if cov>1.2:
            st.success("Approved")
        elif cov>1.0:
            st.warning("Conditional")
        else:
            st.error("Declined")

        # Sensitivity
        st.subheader("📈 Sensitivity")

        x = np.linspace(0.5,1.5,20)
        y=[]
        for r in x:
            t=df.copy()
            t["revenue"]*=r
            s,*_=compute_metrics(t)
            y.append(s)

        st.line_chart(pd.DataFrame({"x":x,"score":y}).set_index("x"))

        # Tips
        st.subheader("💡 Improve Approval")

        tips=[]
        if sc_dscr<1.2: tips.append("Increase revenue or reduce loan")
        if sc_vol>0.2: tips.append("Stabilize income")
        if sc_level=="High": tips.append("Reduce risk exposure")

        for t in tips:
            st.write(f"- {t}")

    # =============================
    # CREDIT MEMO
    # =============================
    with tab3:
        st.subheader("📄 Credit Memo")

        st.write(f"Risk Level: {level} | Score: {score:,}")

        pd_val = calculate_pd(score, dscr, volatility)
        st.metric("PD", f"{pd_val*100:.1f}%")

        st.subheader("🏦 Lending Recommendation")

        base = max(avg_cash*3,0)

        if level=="Low":
            decision="Approved"
            rate="6–10%"
        elif level=="Moderate":
            decision="Conditional"
            rate="10–16%"
            base*=0.7
        else:
            decision="Declined"
            rate="N/A"
            base=0

        st.write(f"Decision: {decision}")
        st.write(f"Loan: ${base:,.0f}")
        st.write(f"Rate: {rate}")
