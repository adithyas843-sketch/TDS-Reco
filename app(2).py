import streamlit as st
import pandas as pd

from modules.challan_reco import challan_reconciliation
from modules.books_reco import books_vs_challan
from modules.duplicate_check import find_duplicate_challans
from modules.aging import challan_aging_report

st.set_page_config(
    page_title="TDS Challan Reconciliation Tool",
    layout="wide"
)

st.title("TDS Challan Reconciliation Tool")

st.markdown("""
### Upload Files

Required Files:

1. Books Ledger
2. Challan Register
3. Return Utilization File
""")

books_file = st.file_uploader(
    "Books Ledger",
    type=["xlsx", "xls"]
)

challan_file = st.file_uploader(
    "Challan Register",
    type=["xlsx", "xls"]
)

utilization_file = st.file_uploader(
    "Return Utilization",
    type=["xlsx", "xls"]
)

if (
    books_file
    and challan_file
    and utilization_file
):

    with st.spinner("Processing..."):

        books_df = pd.read_excel(books_file)
        challan_df = pd.read_excel(challan_file)
        utilization_df = pd.read_excel(utilization_file)

        challan_report = challan_reconciliation(
            challan_df,
            utilization_df
        )

        books_report = books_vs_challan(
            books_df,
            challan_df
        )

        duplicate_report = find_duplicate_challans(
            challan_df
        )

        aging_report = challan_aging_report(
            challan_report
        )

    st.success("Reconciliation Complete")

    st.subheader("Dashboard")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Challans",
        len(challan_report)
    )

    col2.metric(
        "Fully Consumed",
        len(
            challan_report[
                challan_report["Status"]
                == "Fully Consumed"
            ]
        )
    )

    col3.metric(
        "Partially Consumed",
        len(
            challan_report[
                challan_report["Status"]
                == "Partially Consumed"
            ]
        )
    )

    col4.metric(
        "Excess Utilized",
        len(
            challan_report[
                challan_report["Status"]
                == "Excess Utilized"
            ]
        )
    )

    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs([
        "Challan Reco",
        "Books vs Challan",
        "Duplicates",
        "Aging"
    ])

    with tab1:
        st.dataframe(
            challan_report,
            use_container_width=True
        )

    with tab2:
        st.dataframe(
            books_report,
            use_container_width=True
        )

    with tab3:
        st.dataframe(
            duplicate_report,
            use_container_width=True
        )

    with tab4:
        st.dataframe(
            aging_report,
            use_container_width=True
        )

else:
    st.info(
        "Upload all required files to begin reconciliation."
    )
