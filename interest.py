import pandas as pd


def calculate_tds_interest(df):
    """
    Estimate TDS interest under Section 201(1A).

    Expected Columns:
    - Section
    - TDS Amount
    - Due Date
    - Deposit Date

    Interest Rate Assumption:
    - 1.5% per month or part thereof
      for late deposit.
    """

    data = df.copy()

    required_columns = [
        "Section",
        "TDS Amount",
        "Due Date",
        "Deposit Date"
    ]

    missing = [
        col for col in required_columns
        if col not in data.columns
    ]

    if missing:
        return pd.DataFrame({
            "Error": [
                f"Missing columns: {', '.join(missing)}"
            ]
        })

    data["Due Date"] = pd.to_datetime(
        data["Due Date"],
        errors="coerce"
    )

    data["Deposit Date"] = pd.to_datetime(
        data["Deposit Date"],
        errors="coerce"
    )

    data["Delay Days"] = (
        data["Deposit Date"]
        - data["Due Date"]
    ).dt.days

    data["Delay Days"] = (
        data["Delay Days"]
        .clip(lower=0)
    )

    def months_or_part(days):
        if pd.isna(days) or days <= 0:
            return 0
        return ((days - 1) // 30) + 1

    data["Interest Months"] = (
        data["Delay Days"]
        .apply(months_or_part)
    )

    data["Interest Rate"] = 0.015

    data["Estimated Interest"] = (
        data["TDS Amount"]
        * data["Interest Months"]
        * data["Interest Rate"]
    ).round(2)

    summary = (
        data.groupby("Section", as_index=False)
        .agg({
            "TDS Amount": "sum",
            "Estimated Interest": "sum",
            "Delay Days": "max"
        })
        .rename(columns={
            "TDS Amount": "Total TDS",
            "Estimated Interest": "Total Interest",
            "Delay Days": "Max Delay Days"
        })
    )

    return data, summary
