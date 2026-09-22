import streamlit as st
import pandas as pd
import plotly.express as px

from challan_reco import challan_reconciliation
from books_reco import books_vs_challan
from duplicate_check import find_duplicate_challans
from aging import challan_aging_report

st.set_page_config(page_title="TDS Compliance Copilot", layout="wide")

st.markdown("""
<style>
.main-title{font-size:36px;font-weight:700;}
.metric-box{
padding:15px;border-radius:12px;border:1px solid #ddd;
background:#f8f9fa;
}
</style>
""", unsafe_allow_html=True)

if "results" not in st.session_state:
    st.session_state.results = None

st.markdown('<div class="main-title">TDS Compliance Copilot</div>', unsafe_allow_html=True)
st.caption("Challan reconciliation, utilization analysis, liability matching and audit-ready reporting.")

with st.sidebar:
    st.header("📁 Upload Files")

    books_file = st.file_uploader("Books Ledger", type=["xlsx","xls"])
    challan_file = st.file_uploader("Challan Register", type=["xlsx","xls"])
    utilization_file = st.file_uploader("Return Utilization", type=["xlsx","xls"])

    st.divider()

    st.header("📥 Templates")

    st.info("Keep books_template.xlsx, challan_template.xlsx and utilization_template.xlsx in repo root.")

    st.divider()

    st.header("Upload Status")

    st.write("🟢 Books Uploaded" if books_file else "⚪ Books Pending")
    st.write("🟢 Challan Uploaded" if challan_file else "⚪ Challan Pending")
    st.write("🟢 Utilization Uploaded" if utilization_file else "⚪ Utilization Pending")

    run_reco = st.button("▶ Run Reconciliation", use_container_width=True)

col_a, col_b, col_c = st.columns(3)

with col_a:
    if st.button("Clear Results"):
        st.session_state.results = None

with col_b:
    if st.button("Reset Application"):
        st.session_state.clear()
        st.rerun()

with col_c:
    st.button("Data Management")

if run_reco:

    if not all([books_file, challan_file, utilization_file]):
        st.error("Please upload all files.")
        st.stop()

    books_df = pd.read_excel(books_file)
    challan_df = pd.read_excel(challan_file)
    utilization_df = pd.read_excel(utilization_file)

    challan_report = challan_reconciliation(challan_df, utilization_df)
    books_report, books_summary = books_vs_challan(books_df, challan_df)
    duplicate_report = find_duplicate_challans(challan_df)
    aging_report = challan_aging_report(challan_report)

    st.session_state.results = {
        "challan": challan_report,
        "books": books_report,
        "books_summary": books_summary,
        "duplicates": duplicate_report,
        "aging": aging_report
    }

if st.session_state.results:

    challan_report = st.session_state.results["challan"]
    books_report = st.session_state.results["books"]
    books_summary = st.session_state.results["books_summary"]
    duplicate_report = st.session_state.results["duplicates"]
    aging_report = st.session_state.results["aging"]

    total = len(challan_report)
    full = len(challan_report[challan_report["Status"]=="Fully Consumed"])
    partial = len(challan_report[challan_report["Status"]=="Partially Consumed"])
    excess = len(challan_report[challan_report["Status"]=="Excess Utilized"])

    unconsumed = len(challan_report[challan_report["Balance"]>0])
    health = round((full/max(total,1))*100)

    c1,c2,c3,c4,c5,c6 = st.columns(6)

    c1.metric("Total Challans", total)
    c2.metric("Fully Consumed", full)
    c3.metric("Partially Consumed", partial)
    c4.metric("Unconsumed", unconsumed)
    c5.metric("Excess Utilized", excess)
    c6.metric("Health Score", f"{health}/100")

    st.warning(
        f"Exceptions: Excess Utilized={excess} | Unconsumed={unconsumed} | Duplicate Records={len(duplicate_report)}"
    )

    tabs = st.tabs([
        "Dashboard",
        "Challan Reconciliation",
        "Books vs Challan",
        "Books Summary",
        "Duplicates",
        "Aging",
        "Exports"
    ])

    with tabs[0]:
        status_counts = challan_report["Status"].value_counts().reset_index()
        status_counts.columns = ["Status","Count"]

        fig = px.pie(
            status_counts,
            names="Status",
            values="Count",
            title="Challan Status Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(books_summary, use_container_width=True)

    with tabs[1]:
        st.dataframe(challan_report, use_container_width=True)

    with tabs[2]:
        st.dataframe(books_report, use_container_width=True)

    with tabs[3]:
        st.dataframe(books_summary, use_container_width=True)

    with tabs[4]:
        st.dataframe(duplicate_report, use_container_width=True)

    with tabs[5]:
        st.dataframe(aging_report, use_container_width=True)

    with tabs[6]:
        st.success("Connect exporter.py here for Excel download pack.")

else:
    st.info("Upload files from sidebar and click Run Reconciliation.")
