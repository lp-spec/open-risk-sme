import streamlit as st
import pandas as pd
import numpy as np
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

st.set_page_config(page_title="SME Risk Analyzer", layout="wide")

# -----------------------------
# 🎨 Fintech-style UI tweaks
# -----------------------------
st.markdown("""
<style>
.block-container {padding-top: 1.5rem;}
h1 {font-size: 30px !important;}
h2 {font-size: 22px !important;}
h3 {font-size: 18px !important;}
.metric-card {
    padding: 12px;
    border-radius: 10px;
    background-color: #f6f7fb;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 SME Risk Analyzer")
st.caption("Underwriting-style risk analysis, simulation, and lending decision")

# -----------------------------
# 📥 Template
# -----------------------------
template = """month,revenue,expenses,debt_payment
Jan,80000,60000,10000
Feb,85000,62000,10000
"""

st.download_button("📥 Download Template", template, "template.csv")

# -----------------------------
# 📄 PDF Generator (bank-style)
# -----------------------------
def generate_pdf(score, level, dscr, volatility):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    section = ParagraphStyle('section', parent=styles['Heading2'], fontSize=12)

    elements = []
    elements.append(Paragraph("SME Credit Memo", styles['Title']))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("Executive Summary", section))
    elements.append(Paragraph(f"Risk Level: {level}, Score: {score}", styles["Normal"]))

    elements.append(Spacer(1, 10))
    elements.append(Paragraph("Financial Analysis", section))
    elements.append(Paragraph(f"DSCR: {round(dscr,2)}", styles["Normal"]))
    elements.append(Paragraph(f"Volatility: {round(volatility,2)}", styles["Normal"]))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# -----------------------------
# 📊 Core calculation function
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
        explanations.append("Low DSCR")

    if volatility > 0.2:
        score -= 20
        explanations.append("High volatility")

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

    # -----------------------------
    # 📊 BASE METRICS
    # -----------------------------
    score, level, dscr, volatility, explanations, avg_cash = compute_metrics(df)

    # -----------------------------
    # 🧭 Sidebar Scenario Controls
    # -----------------------------
    st.sidebar.header("⚙️ Scenario Simulator")

    rev_change = st.sidebar.slider("Revenue Change %", -50, 50, 0)
    exp_change = st.sidebar.slider("Expense Change %", -50, 50, 0)
    debt_change = st.sidebar.slider("Debt Change %", -50, 50, 0)

    scenario_df = df.copy()
    scenario_df["revenue"] *= (1 + rev_change/100)
    scenario_df["expenses"] *= (1 + exp_change/100)
    scenario_df["debt_payment"] *= (1 + debt_change/100)

    s_score, s_level, s_dscr, s_vol, s_exp, s_cash = compute_metrics(scenario_df)

    # -----------------------------
    # 📑 TABS
    # -----------------------------
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🧪 Simulator", "📄 Credit Memo"])

    # =============================
    # 📊 DASHBOARD
    # =============================
    with tab1:
        st.subheader("📈 Risk Summary")

        c1, c2, c3 = st.columns(3)
        c1.metric("Risk Score", score)
        c2.metric("DSCR", round(dscr, 2))
        c3.metric("Volatility", round(volatility, 2))

        st.markdown(f"### Risk Level: **{level}**")

        st.subheader("📊 Revenue Trend")
        st.line_chart(df["revenue"])

        st.subheader("⚠️ Risk Factors")
        if explanations:
            for e in explanations:
                st.warning(f"⚠️ {e}")
        else:
            st.success("✅ No major risk signals detected")

    # =============================
    # 🧪 SIMULATOR
    # =============================
    with tab2:
        st.subheader("🧪 Scenario Comparison")

        c1, c2 = st.columns(2)

        with c1:
            st.markdown("### Base Case")
            st.metric("Score", score)
            st.metric("DSCR", round(dscr, 2))

        with c2:
            st.markdown("### Scenario Case")
            st.metric("Score", s_score)
            st.metric("DSCR", round(s_dscr, 2))

        st.markdown("### 📉 Impact")

        delta_score = s_score - score
        st.write(f"Score Change: {delta_score}")

        if s_level == "High":
            st.error("Scenario leads to high risk")
        elif s_level == "Moderate":
            st.warning("Scenario increases risk")
        else:
            st.success("Scenario remains stable")

    # =============================
    # 📄 CREDIT MEMO + LOAN ENGINE
    # =============================
    with tab3:
        st.subheader("📄 Credit Memo")

        st.markdown(f"""
**Risk Level:** {level}  
**Score:** {score}
""")

        st.markdown("### 🏦 Lending Decision")

        loan = max(avg_cash * 3, 0)

        if level == "Low":
            decision = "Approved"
            rate = "6–10%"
        elif level == "Moderate":
            decision = "Conditional"
            rate = "10–16%"
            loan *= 0.7
        else:
            decision = "Declined"
            rate = "N/A"
            loan = 0

        st.write(f"Decision: {decision}")
        st.write(f"Max Loan: ${int(loan):,}")
        st.write(f"Rate: {rate}")

        st.download_button(
            "📄 Download PDF",
            data=generate_pdf(score, level, dscr, volatility),
            file_name="credit_memo.pdf"
        )
