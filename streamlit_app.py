import streamlit as st
import pandas as pd
import numpy as np
import io

st.set_page_config(page_title="SME Risk Analyzer", layout="wide")

st.title("📊 SME Risk Analyzer")
st.caption("Turn financial data into lender-ready risk insights")

# --- Download template ---
template = """month,revenue,expenses,debt_payment
Jan,80000,60000,10000
Feb,85000,62000,10000
Mar,78000,61000,10000
Apr,90000,65000,10000
"""

st.download_button(
    label="📥 Download CSV Template",
    data=template,
    file_name="sample_template.csv",
    mime="text/csv"
)

# --- File upload ---
uploaded_file = st.file_uploader("Upload your financial CSV", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)

        # --- Normalize column names ---
        df.columns = [col.strip().lower() for col in df.columns]

        # --- Column alias mapping ---
        column_map = {
            "revenue": ["revenue", "income", "total_income", "sales"],
            "expenses": ["expenses", "cost", "costs", "operating_expenses"],
            "debt_payment": ["debt_payment", "loan_payment", "debt", "payment"]
        }

        def find_column(possible_names):
            for name in possible_names:
                if name in df.columns:
                    return name
            return None

        rev_col = find_column(column_map["revenue"])
        exp_col = find_column(column_map["expenses"])
        debt_col = find_column(column_map["debt_payment"])

        # --- Validate required columns ---
        if not rev_col or not exp_col or not debt_col:
            st.error(
                "❌ Missing required columns.\n\n"
                "Please include columns for revenue, expenses, and debt payment.\n\n"
                "Tip: Download the template above."
            )
            st.stop()

        # --- Rename to standard ---
        df = df.rename(columns={
            rev_col: "revenue",
            exp_col: "expenses",
            debt_col: "debt_payment"
        })

        st.success(f"✅ Detected columns → revenue: {rev_col}, expenses: {exp_col}, debt: {debt_col}")

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
        volatility = np.std(df["revenue"]) / np.mean(df["revenue"]) if np.mean(df["revenue"]) != 0 else 0

        score = 100
        explanations = []

        if dscr < 1.2:
            score -= 30
            explanations.append("Low DSCR (cash flow may not sufficiently cover debt obligations)")

        if volatility > 0.2:
            score -= 20
            explanations.append("High revenue volatility (unstable income patterns)")

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
        st.json({
            "risk_score": score,
            "risk_level": level,
            "dscr": round(dscr, 2),
            "volatility": round(volatility, 2),
            "explanations": explanations
        })

    except Exception as e:
        st.error(f"⚠️ Error processing file: {str(e)}")
