def generate_report(metrics):
    risk_level = "Low"

    if metrics["risk_score"] < 70:
        risk_level = "Moderate"
    if metrics["risk_score"] < 50:
        risk_level = "High"

    return {
        "risk_level": risk_level,
        "summary": f"Risk Score: {metrics['risk_score']}",
        "details": metrics
    }
