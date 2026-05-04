import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="SME Risk Analyzer")

st.title("📊 SME Risk Analyzer")

st.write("Upload your financial data (CSV) to generate a risk report.")

uploaded_file = st.file_uploader("Upload CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.subheader("Raw Data")
    st.dataframe(df)

    # Normalize
    df["profit"] = df["revenue"] - df["expenses"]
    df["cash_flow"] = df["profit"] - df["debt_payment"]

    # Risk calculation
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

    st.subheader("📈 Risk Results")

    st.json({
        "risk_score": score,
        "dscr": round(dscr, 2),
        "volatility": round(volatility, 2),
        "explanations": explanations
    })
