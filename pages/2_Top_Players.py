import plotly.express as px
import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from services import player_stats_service as ps

st.set_page_config(page_title="Top Players", page_icon="🏆", layout="wide")

st.title("🏆 Top Players")
st.caption("Career stats of the players loaded in the database (not every player in the world).")

try:
    formats = ps.get_formats()
    roster = ps.players_with_stats()
except SQLAlchemyError:
    st.error("Could not read the database. Check that MySQL is running.")
    st.stop()

tab_board, tab_compare = st.tabs(["Leaderboard", "Compare players"])

with tab_board:
    c1, c2, c3 = st.columns(3)
    fmt = c1.selectbox("Format", formats, index=formats.index("ODI") if "ODI" in formats else 0)
    kind = c2.radio("Show", ["Batting", "Bowling"], horizontal=True)
    top_n = c3.slider("Players to show", 3, 15, 10)

    if kind == "Batting":
        df = ps.top_batters(fmt, top_n)
        x_col, title = "runs", f"Top {top_n} run scorers in {fmt}"
    else:
        df = ps.top_bowlers(fmt, top_n)
        x_col, title = "wickets", f"Top {top_n} wicket takers in {fmt}"

    if df.empty:
        st.info("No data for this selection.")
    else:
        fig = px.bar(df, x=x_col, y="player", orientation="h", title=title, text=x_col)
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=450)
        st.plotly_chart(fig, width="stretch")
        st.dataframe(df, width="stretch", hide_index=True)

with tab_compare:
    names = roster["full_name"].tolist()
    default = [n for n in ("Virat Kohli", "Rohit Sharma") if n in names]
    chosen = st.multiselect("Players (pick 2 to 5)", names, default=default, max_selections=5)
    metric = st.selectbox("Metric", ["runs", "batting_avg", "strike_rate", "centuries"])

    if len(chosen) < 2:
        st.info("Pick at least 2 players to compare.")
    else:
        ids = tuple(int(i) for i in roster.loc[roster["full_name"].isin(chosen), "player_id"])
        cmp_df = ps.compare_players(ids)
        fig = px.bar(
            cmp_df, x="format", y=metric, color="player", barmode="group",
            title=f"{metric} by format",
        )
        st.plotly_chart(fig, width="stretch")
        st.dataframe(cmp_df, width="stretch", hide_index=True)