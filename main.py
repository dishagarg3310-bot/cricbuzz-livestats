from pathlib import Path

import plotly.express as px
import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from services import dashboard_service as ds
from services import viz_service as viz
from utils.style import GREEN, apply_theme, hero, kpi_card, match_card, section, style_fig
from utils.ui import show_db_error

st.set_page_config(page_title="Cricbuzz LiveStats", page_icon="🏏", layout="wide")
apply_theme()

hero(
    "Cricbuzz LiveStats",
    "Cricket data from the Cricbuzz API, stored in MySQL and analysed with 25 SQL queries.",
)

try:
    counts = ds.get_counts()
    results = ds.get_recent_results(6)
    wins = viz.team_wins()
except SQLAlchemyError as exc:
    show_db_error(exc)

kpis = [
    ("Series", counts["series"], "🏆"),
    ("Matches", counts["matches"], "🏏"),
    ("Teams", counts["teams"], "🛡️"),
    ("Venues", counts["venues"], "🏟️"),
    ("Players", counts["players"], "👤"),
]
for col, (label, value, icon) in zip(st.columns(5), kpis):
    col.markdown(kpi_card(label, value, icon), unsafe_allow_html=True)

left, right = st.columns([3, 2], gap="large")

with left:
    section("Recent results", "The latest completed matches in the database")
    for _, row in results.iterrows():
        st.markdown(match_card(row.to_dict()), unsafe_allow_html=True)

with right:
    section("Wins per team", "Across all completed matches")
    fig = px.bar(wins, x="wins", y="team_name", orientation="h", text="wins")
    fig.update_traces(marker_color=GREEN, textposition="outside")
    fig.update_layout(yaxis={"categoryorder": "total ascending", "title": None},
                      xaxis={"title": None}, showlegend=False)
    st.plotly_chart(style_fig(fig, height=330), width="stretch")

section("Explore", "Jump to any part of the app")
tiles = [
    ("pages/1_SQL_Analytics.py", "SQL Analytics", "📊"),
    ("pages/2_Top_Players.py", "Top Players", "🏆"),
    ("pages/6_Visualizations.py", "Visualizations", "📈"),
    ("pages/4_Live_Matches.py", "Live Matches", "📡"),
    ("pages/3_CRUD.py", "Manage Players", "🛠️"),
]
available = [t for t in tiles if Path(t[0]).exists()]
for col, (path, label, icon) in zip(st.columns(len(available)), available):
    col.page_link(path, label=label, icon=icon)