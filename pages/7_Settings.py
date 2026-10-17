import streamlit as st

from services import live_service as live
from services import settings_service as ss

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")

st.title("⚙️ Settings and status")
st.caption("Health check for the app. Secrets are never shown here.")

status = ss.db_status()
col1, col2, col3 = st.columns(3)
if status["ok"]:
    col1.metric("Database", "Connected")
    col2.metric("MySQL version", status["version"])
    col3.metric("Database name", status["database"])
else:
    st.error(f"Cannot connect to the database ({status['error']}). Check MySQL and .env.")
    st.stop()

st.subheader("Configuration")
cfg = ss.config_status()
for name, value in cfg.items():
    shown = ("Yes" if value else "No") if isinstance(value, bool) else value
    st.write(f"- **{name}:** {shown}")

left = live.calls_left()
st.metric("API calls left this month (from the last logged call)", left if left is not None else "-")

st.subheader("Rows per table")
st.dataframe(ss.table_counts(), width="stretch", hide_index=True)

st.subheader("Data source (API vs sample)")
st.caption("'sample' rows were added by hand or by the CRUD page, 'api' rows came from Cricbuzz.")
st.dataframe(ss.data_sources(), width="stretch", hide_index=True)

st.subheader("Maintenance")
if st.button("Clear cached query results"):
    st.cache_data.clear()
    st.success("Cache cleared. Pages will read fresh data from MySQL.")