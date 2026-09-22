import pandas as pd


def challan_aging_report(challan_reco_df):
    """
    Generate aging report for unconsumed or partially consumed challans.

    Expected columns in challan_reco_df:
    - Date
    - Balance
    - Status
    """

    df = challan_reco_df.copy()

    if "Date" not in df.columns:
        return pd.DataFrame({
            "Message": [
                "Date column not found. Aging report cannot be generated."
            ]
        })

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

    report_date = pd.Timestamp.today().normalize()

    df["Days Outstanding"] = (
        report_date - df["Date"]
    ).dt.days

    def aging_bucket(days):

        if pd.isna(days):
            return "Unknown"

        if days <= 30:
            return "0-30 Days"

        if days <= 60:
            return "31-60 Days"

        if days <= 90:
            return "61-90 Days"

        if days <= 180:
            return "91-180 Days"

        return "180+ Days"

    df["Aging Bucket"] = (
        df["Days Outstanding"]
        .apply(aging_bucket)
    )

    aging_report = df[
        df["Balance"] > 0
    ].copy()

    aging_report = aging_report.sort_values(
        by="Days Outstanding",
        ascending=False
    )

    return aging_report
