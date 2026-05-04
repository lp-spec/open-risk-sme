import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="SME Risk Analyzer", layout="wide")

st.title("📊 SME Risk Analyzer")
st.caption("Turn financial data into lender-ready risk insights")

uploaded_file = st.file_uploader("Upload your financial CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # --- Show raw data ---
    st.subheader("📁 Uploaded Data")
    st.dataframe(df)

    # --- Normalize ---
    df["profit"] = df["revenue"] - df["expenses"]
    df["cash_flow"] = df["profit"] - df["debt_payment"]

    # --- Risk calculations ---
    avg_cash = df["cash_flow"].mean()
    debt = df["debt_payment"].mean()

    dscr = avg_cash / debt if debt else 0
    volatility = np.std(df["revenue"]) / np.mean(df["revenue"])

    score = 100
    explanations = []

    if dscr < 1.2:
        score -= 30
        explanations.append("Low DSCR")

    if volatility > 0.2:
        score -= 20
        explanations.append("High revenue volatility")

    # --- Risk level ---
    if score >= 80:
        level = "Low"
        color = "🟢"
    elif score >= 60:
        level = "Moderate"
        color = "🟡"
    else:
        level = "High"
        color = "🔴"

    # --- Display metrics ---
    st.subheader("📈 Risk Summary")

    col1, col2, col3 = st.columns(3)

    col1.metric("Risk Score", score)
    col2.metric("DSCR", round(dscr, 2))
    col3.metric("Volatility", round(volatility, 2))

    st.markdown(f"### Risk Level: {color} {level}")

    # --- Chart ---
    st.subheader("📊 Revenue Trend")
    st.line_chart(df["revenue"])

    # --- Explanations ---
    st.subheader("⚠️ Risk Factors")
    if explanations:
        for e in explanations:
            st.warning(e)
    else:
        st.success("No major risk signals detected")

    # --- Final Report ---
    st.subheader("📄 Summary Report")
    st.write({
        "risk_score": score,
        "risk_level": level,
        "dscr": round(dscr, 2),
        "volatility": round(volatility, 2),
        "explanations": explanations
    })
