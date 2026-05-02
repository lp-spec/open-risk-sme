def normalize(df):
    df["profit"] = df["revenue"] - df["expenses"]
    df["cash_flow"] = df["profit"] - df["debt_payment"]
    return df
