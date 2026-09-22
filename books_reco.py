import pandas as pd


def books_vs_challan(books_df, challan_df):
    """
    Reconcile TDS liability in books against challans paid.

    Required Columns:

    Books Ledger:
    - Section
    - TDS Payable

    Challan Register:
    - Section
    - Amount
    """

    books_df = books_df.copy()
    challan_df = challan_df.copy()

    books_summary = (
        books_df
        .groupby("Section", as_index=False)["TDS Payable"]
        .sum()
    )

    challan_summary = (
        challan_df
        .groupby("Section", as_index=False)["Amount"]
        .sum()
    )

    reco = books_summary.merge(
        challan_summary,
        on="Section",
        how="outer"
    )

    reco = reco.fillna(0)

    reco = reco.rename(
        columns={
            "Amount": "Challan Paid"
        }
    )

    reco["Difference"] = (
        reco["TDS Payable"]
        - reco["Challan Paid"]
    )

    def get_status(diff):
        if diff == 0:
            return "Matched"
        elif diff > 0:
            return "Short Payment"
        else:
            return "Excess Payment"

    reco["Status"] = (
        reco["Difference"]
        .apply(get_status)
    )

    total_payable = reco["TDS Payable"].sum()
    total_paid = reco["Challan Paid"].sum()

    summary = pd.DataFrame({
        "Metric": [
            "Total TDS Payable",
            "Total Challan Paid",
            "Net Difference"
        ],
        "Value": [
            total_payable,
            total_paid,
            total_payable - total_paid
        ]
    })

    return reco, summary
