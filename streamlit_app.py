import streamlit as st
import pandas as pd
import numpy as np
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

st.set_page_config(page_title="SME Risk Analyzer", layout="wide")

# -----------------------------
# 🎨 Fix Font Hierarchy
# -----------------------------
st.markdown("""
<style>
h1 {font-size: 32px !important;}
h2 {font-size: 22px !important;}
h3 {font-size: 18px !important;}
</style>
""", unsafe_allow_html=True)

st.title("📊 SME Risk Analyzer")
st.caption("Turn financial data into lender-ready risk insights")

# -----------------------------
# 📥 Template
# -----------------------------
template = """month,revenue,expenses,debt_payment
Jan,80000,60000,10000
Feb,85000,62000,10000
"""

st.download_button(
    "📥 Download CSV Template",
    data=template,
    file_name="sample_template.csv",
    mime="text/csv"
)

# -----------------------------
# 📄 BANK-STYLE PDF
# -----------------------------
def generate_pdf_report(score, level, dscr, volatility, explanations):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    title = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontSize=18,
        spaceAfter=12
    )

    section = ParagraphStyle(
        'Section',
        parent=styles['Heading2'],
        fontSize=12,
        spaceAfter=6
    )

    normal = styles["Normal"]

    elements = []

    # Title
    elements.append(Paragraph("SME Credit Risk Memo", title))
    elements.append(Spacer(1, 10))

    # Executive Summary
    elements.append(Paragraph("Executive Summary", section))
    elements.append(Paragraph(
        f"The business presents a <b>{level}</b> credit risk profile with a score of <b>{score}</b>.",
        normal))
    elements.append(Spacer(1, 10))

    # Financial Metrics
    elements.append(Paragraph("Financial Analysis", section))
    elements.append(Paragraph(f"DSCR: {round(dscr,2)}", normal))
    elements.append(Paragraph(f"Revenue Volatility: {round(volatility,2)}", normal))
    elements.append(Spacer(1, 10))

    # Risk Factors
    elements.append(Paragraph("Risk Factors", section))
    if explanations:
        for e in explanations:
            elements.append(Paragraph(f"- {e}", normal))
    else:
        elements.append(Paragraph("No major risk factors.", normal))
    elements.append(Spacer(1, 10))

    # Recommendation
    elements.append(Paragraph("Lending Recommendation", section))

    if level == "Low":
        rec = "Eligible for standard lending terms."
    elif level == "Moderate":
        rec = "Conditional approval recommended."
    else:
        rec = "High risk. Further review required."

    elements.append(Paragraph(rec, normal))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# -----------------------------
# 📤 Upload
# -----------------------------
uploaded_file = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        df.columns = [c.lower().strip().replace(" ", "_") for c in df.columns]

        # simple mapping
        df = df.rename(columns={
            "income": "revenue",
            "cost": "expenses"
        })

        if "debt_payment" not in df.columns:
            df["debt_payment"] = 0

        # calculations
        df["profit"] = df["revenue"] - df["expenses"]
        df["cash_flow"] = df["profit"] - df["debt_payment"]

        dscr = df["cash_flow"].mean() / df["debt_payment"].mean() if df["debt_payment"].mean() else 0
        volatility = np.std(df["revenue"]) / np.mean(df["revenue"]) if np.mean(df["revenue"]) else 0

        score = 100
        explanations = []

        if dscr < 1.2:
            score -= 30
            explanations.append("Low DSCR (cash flow pressure)")

        if volatility > 0.2:
            score -= 20
            explanations.append("High revenue volatility")

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
        # UI Display (YOUR SECTION KEPT)
        # -----------------------------
        st.subheader("📈 Risk Summary")

        col1, col2, col3 = st.columns(3)
        col1.metric("Risk Score", score)
        col2.metric("DSCR", round(dscr, 2))
        col3.metric("Volatility", round(volatility, 2))

        st.markdown(f"### Risk Level: {color} {level}")

        st.subheader("📊 Revenue Trend")
        st.line_chart(df["revenue"])

        st.subheader("⚠️ Risk Factors")
        if explanations:
            for e in explanations:
                st.warning(e)
        else:
            st.success("No major risk signals detected")

        # -----------------------------
        # 📄 CLEAN CREDIT MEMO
        # -----------------------------
        st.subheader("📄 Credit Memo")

        st.markdown(f"""
**Executive Summary**  
The business presents a **{level.lower()} risk profile** with a score of **{score}**.
Based on available financial data, the company's ability to service debt obligations is evaluated through cash flow coverage and revenue stability.

**Financial Analysis**  
- DSCR: {round(dscr,2)}  
- Revenue Volatility: {round(volatility,2)}

**Interpretation**  
""")

        if level == "Low":
            st.success("Strong financial condition and stable cash flow.")
        elif level == "Moderate":
            st.warning("Moderate risk. Some cash flow or stability concerns.")
        else:
            st.error("High risk. Debt repayment capacity may be weak.")

        st.markdown("**Lending Recommendation**")

        if level == "Low":
            st.write("Standard approval likely.")
        elif level == "Moderate":
            st.write("Conditional approval recommended.")
        else:
            st.write("Further review required.")

        # -----------------------------
        # 📥 PDF DOWNLOAD
        # -----------------------------
        pdf = generate_pdf_report(score, level, dscr, volatility, explanations)

        st.download_button(
            "📄 Download Credit Memo (PDF)",
            data=pdf,
            file_name="credit_memo.pdf",
            mime="application/pdf"
        )

    except Exception as e:
        st.error(f"Error: {e}")
