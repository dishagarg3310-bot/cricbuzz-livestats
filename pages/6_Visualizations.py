import plotly.express as px
import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from services import viz_service as viz

st.set_page_config(page_title="Visualizations", page_icon="📈", layout="wide")

st.title("📈 Visualizations")
st.caption("Charts built from the MySQL data. Only the matches in the database are included.")

try:
    wins = viz.team_wins()
    roles = viz.role_counts()
except SQLAlchemyError:
    st.error("Could not read the database. Check that MySQL is running.")
    st.stop()

tab_teams, tab_bat, tab_form, tab_venue = st.tabs(
    ["Teams and roles", "Batters", "Form trend", "Venues"]
)

with tab_teams:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Wins per team")
        st.caption("Bar chart: the easiest way to compare categories side by side.")
        fig = px.bar(wins, x="team_name", y="wins", text="wins",
                     labels={"team_name": "Team", "wins": "Wins"})
        st.plotly_chart(fig, width="stretch")
    with c2:
        st.subheader("Players by role")
        st.caption("Donut chart: shows each role's share of the whole. "
                   "'Unknown' is large because role is only loaded for 16 players.")
        fig = px.pie(roles, names="role", values="players", hole=0.45)
        st.plotly_chart(fig, width="stretch")

with tab_bat:
    st.subheader("Batting average vs strike rate")
    st.caption("Scatter plot: two measures at once. Bigger bubble = more career runs. "
               "Players towards the top right are both consistent and fast.")
    c1, c2 = st.columns(2)
    fmt = c1.selectbox("Format", ["ODI", "T20", "Test", "IPL"])
    min_runs = c2.slider("Minimum career runs", 0, 5000, 300, step=100)
    scatter = viz.batting_scatter(fmt, min_runs)
    if scatter.empty:
        st.info("No players match this filter. Lower the minimum runs.")
    else:
        fig = px.scatter(scatter, x="batting_avg", y="strike_rate", size="runs",
                         hover_name="player", text="player",
                         labels={"batting_avg": "Batting average", "strike_rate": "Strike rate"})
        fig.update_traces(textposition="top center")
        fig.update_layout(height=500)
        st.plotly_chart(fig, width="stretch")

    st.subheader("Career runs by player and format")
    st.caption("Heatmap: darker colour = more runs, so you can see each player's strongest format.")
    top_n = st.slider("Players to show", 5, 15, 10)
    heat = viz.runs_heatmap(top_n)
    fig = px.imshow(heat, text_auto=True, aspect="auto", color_continuous_scale="Blues",
                    labels={"x": "Format", "y": "Player", "color": "Runs"})
    fig.update_layout(height=450)
    st.plotly_chart(fig, width="stretch")

with tab_form:
    st.subheader("Runs per match")
    st.caption("Line chart (trend analysis): follow one player's runs match by match "
               "to see if form is rising or falling.")
    roster = viz.players_with_innings()
    names = roster["full_name"].tolist()
    default = names.index("Shai Hope") if "Shai Hope" in names else 0
    who = st.selectbox("Player", names, index=default)
    pid = int(roster.loc[roster["full_name"] == who, "player_id"].iloc[0])
    trend = viz.player_trend(pid)
    if trend.empty:
        st.info("No batting data for this player.")
    else:
        fig = px.line(trend, x="match_name", y="runs", markers=True,
                      labels={"match_name": "Match", "runs": "Runs"})
        fig.update_layout(height=420)
        st.plotly_chart(fig, width="stretch")
        st.dataframe(trend[["match_date", "match_name", "runs", "balls", "strike_rate"]],
                     width="stretch", hide_index=True)

with tab_venue:
    st.subheader("Average first-innings score by venue")
    st.caption("Bar chart: a high average suggests a batting-friendly ground. "
               "With only a few matches per venue, treat this as an illustration.")
    vfmt = st.selectbox("Format", ["ODI", "T20", "Test"], key="venue_fmt")
    venues = viz.venue_scores(vfmt)
    if venues.empty:
        st.info("No completed matches in this format.")
    else:
        fig = px.bar(venues, x="avg_first_innings", y="venue_name", orientation="h",
                     text="avg_first_innings", hover_data=["matches"],
                     labels={"avg_first_innings": "Average first-innings runs", "venue_name": "Venue"})
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=450)
        st.plotly_chart(fig, width="stretch")