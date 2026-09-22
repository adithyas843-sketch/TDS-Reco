import pandas as pd


def export_reconciliation_pack(
    output_file,
    challan_report,
    books_report,
    duplicate_report,
    aging_report,
    interest_detail=None,
    interest_summary=None
):
    """
    Generate a multi-sheet Excel reconciliation pack.

    Sheets:
    - Dashboard
    - Challan Reconciliation
    - Books vs Challan
    - Duplicate Challans
    - Aging Report
    - Interest Detail
    - Interest Summary
    """

    with pd.ExcelWriter(
        output_file,
        engine="xlsxwriter"
    ) as writer:

        workbook = writer.book

        header_format = workbook.add_format({
            "bold": True,
            "font_color": "white",
            "bg_color": "#1F4E78",
            "border": 1
        })

        dashboard = pd.DataFrame({
            "Metric": [
                "Total Challans",
                "Fully Consumed",
                "Partially Consumed",
                "Excess Utilized"
            ],
            "Value": [
                len(challan_report),
                len(
                    challan_report[
                        challan_report["Status"]
                        == "Fully Consumed"
                    ]
                ),
                len(
                    challan_report[
                        challan_report["Status"]
                        == "Partially Consumed"
                    ]
                ),
                len(
                    challan_report[
                        challan_report["Status"]
                        == "Excess Utilized"
                    ]
                )
            ]
        })

        dashboard.to_excel(
            writer,
            sheet_name="Dashboard",
            index=False
        )

        challan_report.to_excel(
            writer,
            sheet_name="Challan Reco",
            index=False
        )

        books_report.to_excel(
            writer,
            sheet_name="Books vs Challan",
            index=False
        )

        duplicate_report.to_excel(
            writer,
            sheet_name="Duplicates",
            index=False
        )

        aging_report.to_excel(
            writer,
            sheet_name="Aging Report",
            index=False
        )

        if interest_detail is not None:
            interest_detail.to_excel(
                writer,
                sheet_name="Interest Detail",
                index=False
            )

        if interest_summary is not None:
            interest_summary.to_excel(
                writer,
                sheet_name="Interest Summary",
                index=False
            )

        for sheet in writer.sheets.values():
            sheet.set_default_row(20)

        for sheet_name, worksheet in writer.sheets.items():

            worksheet.freeze_panes(1, 0)

            if sheet_name == "Dashboard":
                cols = dashboard.columns
            elif sheet_name == "Challan Reco":
                cols = challan_report.columns
            elif sheet_name == "Books vs Challan":
                cols = books_report.columns
            elif sheet_name == "Duplicates":
                cols = duplicate_report.columns
            elif sheet_name == "Aging Report":
                cols = aging_report.columns
            elif sheet_name == "Interest Detail" and interest_detail is not None:
                cols = interest_detail.columns
            elif sheet_name == "Interest Summary" and interest_summary is not None:
                cols = interest_summary.columns
            else:
                continue

            for col_num, value in enumerate(cols):
                worksheet.write(
                    0,
                    col_num,
                    value,
                    header_format
                )
                worksheet.set_column(
                    col_num,
                    col_num,
                    22
                )

    return output_file
