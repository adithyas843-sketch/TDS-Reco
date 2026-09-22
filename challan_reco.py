import pandas as pd


def challan_reconciliation(challan_df, utilization_df):
    """
    Reconcile challans against utilization.

    Required Columns:

    Challan Register:
    - Challan No
    - Amount

    Utilization File:
    - Challan No
    - Utilized Amount
    """

    challan_df = challan_df.copy()
    utilization_df = utilization_df.copy()

    utilized_summary = (
        utilization_df
        .groupby("Challan No", as_index=False)["Utilized Amount"]
        .sum()
    )

    challan_reco = challan_df.merge(
        utilized_summary,
        on="Challan No",
        how="left"
    )

    challan_reco["Utilized Amount"] = (
        challan_reco["Utilized Amount"]
        .fillna(0)
    )

    challan_reco["Balance"] = (
        challan_reco["Amount"]
        - challan_reco["Utilized Amount"]
    )

    def get_status(balance):
        if balance == 0:
            return "Fully Consumed"
        elif balance > 0:
            return "Partially Consumed"
        else:
            return "Excess Utilized"

    challan_reco["Status"] = (
        challan_reco["Balance"]
        .apply(get_status)
    )

    challan_reco["Consumption %"] = (
        (
            challan_reco["Utilized Amount"]
            / challan_reco["Amount"]
        ) * 100
    ).round(2)

    challan_reco["Consumption %"] = (
        challan_reco["Consumption %"]
        .fillna(0)
    )

    return challan_reco
