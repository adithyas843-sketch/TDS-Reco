import pandas as pd


def find_duplicate_challans(challan_df):
    """
    Detect duplicate challans.

    Preferred matching columns:
    - BSR Code
    - Challan No
    - Date

    Fallback:
    - Challan No
    """

    df = challan_df.copy()

    preferred_cols = ["BSR Code", "Challan No", "Date"]

    available_cols = [
        col for col in preferred_cols
        if col in df.columns
    ]

    if len(available_cols) >= 2:

        duplicates = df[
            df.duplicated(
                subset=available_cols,
                keep=False
            )
        ].copy()

    else:

        duplicates = df[
            df.duplicated(
                subset=["Challan No"],
                keep=False
            )
        ].copy()

    if duplicates.empty:

        return pd.DataFrame({
            "Message": [
                "No duplicate challans found."
            ]
        })

    duplicates["Duplicate Count"] = (
        duplicates
        .groupby(available_cols)["Challan No"]
        .transform("count")
        if len(available_cols) >= 2
        else duplicates
        .groupby(["Challan No"])["Challan No"]
        .transform("count")
    )

    duplicates = duplicates.sort_values(
        by="Duplicate Count",
        ascending=False
    )

    return duplicates
