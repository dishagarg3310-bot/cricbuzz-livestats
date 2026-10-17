import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from services import dashboard_service as ds

st.set_page_config(page_title="Cricbuzz LiveStats", page_icon="🏏", layout="wide")

st.title("🏏 Cricbuzz LiveStats")
st.caption("Cricket data from the Cricbuzz API, stored in MySQL and analysed with SQL.")

try:
    counts = ds.get_counts()
    results = ds.get_recent_results(10)
except SQLAlchemyError:
    st.error("Could not read the database. Check that MySQL is running and .env is correct.")
    st.stop()

cols = st.columns(5)
cols[0].metric("Series", counts["series"])
cols[1].metric("Matches", counts["matches"])
cols[2].metric("Teams", counts["teams"])
cols[3].metric("Venues", counts["venues"])
cols[4].metric("Players", counts["players"])

st.subheader("Recent results")
st.dataframe(results, width="stretch", hide_index=True)