import streamlit as st
import pandas as pd
import numpy as np
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="SME Risk Analyzer", layout="wide")

st.title("📊 SME Risk Analyzer")
st.caption("Turn financial data into lender-ready risk insights")

# -----------------------------
# 📥 Download Template
# -----------------------------
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

# -----------------------------
# 📄 PDF Generator
# -----------------------------
def generate_pdf_report(data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    elements = []
    elements.append(Paragraph("SME Credit Risk Report", styles['Title']))
    elements.append(Spacer(1, 12))

    for key, value in data.items():
        elements.append(Paragraph(f"{key}: {value}", styles['Normal']))
        elements.append(Spacer(1, 10))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# -----------------------------
# 📤 File Upload
# -----------------------------
uploaded_file = st.file_uploader("Upload your financial file (CSV or Excel)", type=["csv", "xlsx"])

if uploaded_file:
    try:
        file_name = uploaded_file.name.lower()

        # Load file
        if file_name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif file_name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file type.")
            st.stop()

        # -----------------------------
        # 🧠 Normalize Column Names
        # -----------------------------
        df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

        # -----------------------------
        # 🔍 Column Mapping
        # -----------------------------
        column_map = {
            "revenue": [
                "revenue", "income", "total_income", "sales",
                "deposit", "credits", "inflow"
            ],
            "expenses": [
                "expenses", "cost", "costs", "operating_expenses",
                "withdrawal", "debits", "outflow"
            ],
            "debt_payment": [
                "debt_payment", "loan_payment", "debt", "payment",
                "interest_payment", "principal_payment"
            ]
        }

        def find_column(possible_names):
            for col in df.columns:
                for name in possible_names:
                    if name in col:
                        return col
            return None

        rev_col = find_column(column_map["revenue"])
        exp_col = find_column(column_map["expenses"])
        debt_col = find_column(column_map["debt_payment"])

        # -----------------------------
        # 🟡 QuickBooks Fallback
        # -----------------------------
        if not rev_col and "total_income" in df.columns:
            rev_col = "total_income"

        if not exp_col and "total_expenses" in df.columns:
            exp_col = "total_expenses"

        if not debt_col:
            df["debt_payment"] = 0
            debt_col = "debt_payment"

        # -----------------------------
        # ❌ Validation
        # -----------------------------
        if not rev_col or not exp_col:
            st.error("Missing required financial columns (revenue / expenses).")
            st.stop()

        # Rename to standard
        df = df.rename(columns={
            rev_col: "revenue",
            exp_col: "expenses",
            debt_col: "debt_payment"
        })

        st.success(f"Detected columns → revenue: {rev_col}, expenses: {exp_col}, debt: {debt_col}")

        # -----------------------------
        # 📁 Show Data
        # -----------------------------
        st.subheader("📁 Uploaded Data")
        st.dataframe(df)

        # -----------------------------
        # ⚙️ Normalize
        # -----------------------------
        df["profit"] = df["revenue"] - df["expenses"]
        df["cash_flow"] = df["profit"] - df["debt_payment"]

        # -----------------------------
        # 📊 Risk Calculation
        # -----------------------------
        avg_cash = df["cash_flow"].mean()
        debt = df["debt_payment"].mean()

        dscr = avg_cash / debt if debt else 0
        volatility = np.std(df["revenue"]) / np.mean(df["revenue"]) if np.mean(df["revenue"]) != 0 else 0

        score = 100
        explanations = []

        if dscr < 1.2:
            score -= 30
            explanations.append("Low DSCR (cash flow may not cover debt obligations)")

        if volatility > 0.2:
            score -= 20
            explanations.append("High revenue volatility (unstable income)")

        # -----------------------------
        # 🎯 Risk Level
        # -----------------------------
        if score >= 80:
            level = "Low"
            color = "🟢"
        elif score >= 60:
            level = "Moderate"
            color = "🟡"
        else:
            level = "High"
            color = "🔴"

        # -----------------------------
        # 📈 UI Display
        # -----------------------------
        st.subheader("📈 Risk Summary")

        col1, col2, col3 = st.columns(3)
        col1.metric("Risk Score", score)
        col2.metric("DSCR", round(dscr, 2))
        col3.metric("Volatility", round(volatility, 2))

        st.markdown(f"### Risk Level: {color} {level}")

        # Chart
        st.subheader("📊 Revenue Trend")
        st.line_chart(df["revenue"])

        # Risk factors
        st.subheader("⚠️ Risk Factors")
        if explanations:
            for e in explanations:
                st.warning(e)
        else:
            st.success("No major risk signals detected")

        # -----------------------------
        # 📄 CREDIT MEMO
        # -----------------------------
        st.subheader("📄 Credit Memo (Lender View)")
        
        # -----------------------------
        # 🧾 Executive Summary
        # -----------------------------
        st.markdown("## 🧾 Executive Summary")
        
        st.markdown(f"""
        The business demonstrates a **{level.lower()} level of credit risk** with a composite risk score of **{score}**.  
        Based on available financial data, the company's ability to service debt obligations is evaluated through cash flow coverage and revenue stability.
        """)
        
        # -----------------------------
        # 📊 Financial Analysis
        # -----------------------------
        st.markdown("## 📊 Financial Analysis")
        
        col1, col2 = st.columns(2)
        
        col1.markdown(f"""
        **Debt Service Coverage Ratio (DSCR):**  
        **{round(dscr, 2)}**
        
        This metric evaluates the company's ability to cover debt payments using operating cash flow.
        """)
        
        col2.markdown(f"""
        **Revenue Volatility:**  
        **{round(volatility, 2)}**
        
        This reflects stability of income over time. Higher volatility indicates greater uncertainty.
        """)
        
        # -----------------------------
        # ⚠️ Risk Factors
        # -----------------------------
        st.markdown("## ⚠️ Key Risk Factors")
        
        if explanations:
            for e in explanations:
                st.markdown(f"- {e}")
        else:
            st.markdown("- No significant risk factors identified")
        
        # -----------------------------
        # 🧠 Credit Interpretation
        # -----------------------------
        st.markdown("## 🧠 Credit Interpretation")
        
        if level == "Low":
            st.success("""
        The business demonstrates strong financial performance and stable cash flow generation.  
        Risk of default is considered low under current conditions.
        """)
        
        elif level == "Moderate":
            st.warning("""
        The business shows moderate risk characteristics.  
        Cash flow coverage or revenue consistency may present some constraints under stress scenarios.
        """)
        
        else:
            st.error("""
        The business presents elevated credit risk.  
        Weak cash flow coverage or unstable revenue trends may impact debt repayment capacity.
        """)
        
        # -----------------------------
        # 🏦 Lending Consideration
        # -----------------------------
        st.markdown("## 🏦 Lending Consideration")
        
        if level == "Low":
            st.markdown("""
        **Recommendation:** Eligible for standard lending terms.
        
        - Typical approval likely  
        - Competitive interest rates  
        - Minimal additional conditions
        """)
        
        elif level == "Moderate":
            st.markdown("""
        **Recommendation:** Conditional approval.
        
        - May require higher interest rate  
        - Additional documentation recommended  
        - Monitoring of cash flow stability advised
        """)
        
        else:
            st.markdown("""
        **Recommendation:** High caution.
        
        - Approval unlikely without strong compensating factors  
        - May require collateral or guarantees  
        - Further due diligence strongly recommended
        """)
        
        # -----------------------------
        # 📌 Final Summary Box
        # -----------------------------
        st.markdown("---")
        st.markdown(f"""
        ### 📌 Final Risk Rating: **{level} ({score})**
        """)
        
        # -----------------------------
        # 🔍 Optional Raw Data
        # -----------------------------
        with st.expander("🔍 View Technical Details"):
            st.json({
                "risk_score": score,
                "risk_level": level,
                "dscr": round(dscr, 2),
                "volatility": round(volatility, 2),
                "explanations": explanations
            })
        # -----------------------------
        # 📥 PDF Download
        # -----------------------------
        pdf_file = generate_pdf_report({
            "Risk Score": score,
            "Risk Level": level,
            "DSCR": round(dscr, 2),
            "Volatility": round(volatility, 2),
            "Explanations": ", ".join(explanations) if explanations else "None"
        })

        st.download_button(
            label="📄 Download Credit Report (PDF)",
            data=pdf_file,
            file_name="risk_report.pdf",
            mime="application/pdf"
        )

    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
