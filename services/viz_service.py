import pandas as pd
import streamlit as st
from sqlalchemy import text

from utils.db_connection import get_engine


def _query(sql: str, params: dict | None = None) -> pd.DataFrame:
    with get_engine().connect() as conn:
        return pd.read_sql(text(sql), conn, params=params)


def _to_float(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    for col in cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype(float)
    return df


@st.cache_data(ttl=300)
def team_wins() -> pd.DataFrame:
    return _query(
        """
        SELECT t.team_name, COUNT(m.match_id) AS wins
        FROM teams AS t
        LEFT JOIN matches AS m ON m.winner_team_id = t.team_id
        GROUP BY t.team_id, t.team_name
        ORDER BY wins DESC, t.team_name
        """
    )


@st.cache_data(ttl=300)
def role_counts() -> pd.DataFrame:
    return _query(
        """
        SELECT COALESCE(playing_role, 'Unknown') AS role, COUNT(*) AS players
        FROM players
        GROUP BY COALESCE(playing_role, 'Unknown')
        ORDER BY players DESC
        """
    )


@st.cache_data(ttl=300)
def batting_scatter(format_name: str, min_runs: int) -> pd.DataFrame:
    df = _query(
        """
        SELECT full_name AS player, runs, batting_avg, strike_rate
        FROM v_player_batting_career
        WHERE format_name = :f AND runs >= :r
          AND batting_avg IS NOT NULL AND strike_rate IS NOT NULL
        """,
        {"f": format_name, "r": int(min_runs)},
    )
    return _to_float(df, ["runs", "batting_avg", "strike_rate"])


@st.cache_data(ttl=300)
def runs_heatmap(top_n: int) -> pd.DataFrame:
    df = _query(
        """
        SELECT full_name, format_name, runs
        FROM v_player_batting_career
        WHERE format_name IN ('Test', 'ODI', 'T20')
        """
    )
    pivot = df.pivot_table(
        index="full_name", columns="format_name", values="runs", fill_value=0
    )
    pivot = pivot.reindex(columns=[c for c in ("Test", "ODI", "T20") if c in pivot.columns])
    pivot["total"] = pivot.sum(axis=1)
    pivot = pivot.sort_values("total", ascending=False).head(int(top_n))
    return pivot.drop(columns="total").astype(float)


@st.cache_data(ttl=300)
def players_with_innings() -> pd.DataFrame:
    return _query(
        """
        SELECT DISTINCT p.player_id, p.full_name
        FROM batting_scorecards AS b
        JOIN players AS p ON p.player_id = b.player_id
        ORDER BY p.full_name
        """
    )


@st.cache_data(ttl=300)
def player_trend(player_id: int) -> pd.DataFrame:
    df = _query(
        """
        SELECT m.start_time AS match_date,
               CONCAT(m.match_desc, ' (', f.format_name, ')') AS match_name,
               SUM(b.runs) AS runs,
               SUM(b.balls_faced) AS balls
        FROM batting_scorecards AS b
        JOIN innings AS i ON i.innings_id = b.innings_id
        JOIN matches AS m ON m.match_id = i.match_id
        JOIN formats AS f ON f.format_id = m.format_id
        WHERE b.player_id = :p AND m.state = 'Complete'
        GROUP BY m.match_id, m.start_time, m.match_desc, f.format_name
        ORDER BY m.start_time
        """,
        {"p": int(player_id)},
    )
    df = _to_float(df, ["runs", "balls"])
    df["strike_rate"] = (df["runs"] * 100 / df["balls"]).where(df["balls"] > 0).round(1)
    return df


@st.cache_data(ttl=300)
def venue_scores(format_name: str) -> pd.DataFrame:
    df = _query(
        """
        SELECT v.venue_name,
               COUNT(*) AS matches,
               ROUND(AVG(i.total_runs), 1) AS avg_first_innings
        FROM innings AS i
        JOIN matches AS m ON m.match_id = i.match_id
        JOIN formats AS f ON f.format_id = m.format_id
        JOIN venues AS v ON v.venue_id = m.venue_id
        WHERE i.innings_no = 1 AND m.state = 'Complete' AND f.format_name = :f
        GROUP BY v.venue_id, v.venue_name
        ORDER BY avg_first_innings DESC
        """,
        {"f": format_name},
    )
    return _to_float(df, ["avg_first_innings"])