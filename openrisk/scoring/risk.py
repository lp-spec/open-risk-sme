import numpy as np

def compute_risk(df):
    avg_cash = df["cash_flow"].mean()
    debt = df["debt_payment"].mean()

    dscr = avg_cash / debt if debt else 0
    volatility = np.std(df["revenue"]) / np.mean(df["revenue"])

    explanations = []

    if dscr < 1.2:
        explanations.append("Low DSCR")

    if volatility > 0.2:
        explanations.append("High revenue volatility")

    score = 100
    if dscr < 1.2:
        score -= 30
    if volatility > 0.2:
        score -= 20

    return {
        "dscr": round(dscr, 2),
        "volatility": round(volatility, 2),
        "risk_score": score,
        "explanations": explanations
    }
