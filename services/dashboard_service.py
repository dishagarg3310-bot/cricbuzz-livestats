import pandas as pd
import streamlit as st
from sqlalchemy import text

from utils.db_connection import get_engine


def _query(sql: str, params: dict | None = None) -> pd.DataFrame:
    """Run a read-only SQL query and return a DataFrame."""
    with get_engine().connect() as conn:
        return pd.read_sql(text(sql), conn, params=params)


@st.cache_data(ttl=300)
def get_counts() -> dict:
    sql = """
        SELECT
            (SELECT COUNT(*) FROM series)  AS series,
            (SELECT COUNT(*) FROM matches) AS matches,
            (SELECT COUNT(*) FROM teams)   AS teams,
            (SELECT COUNT(*) FROM venues)  AS venues,
            (SELECT COUNT(*) FROM players) AS players
    """
    row = _query(sql).iloc[0]
    return {key: int(value) for key, value in row.items()}


@st.cache_data(ttl=300)
def get_recent_results(limit: int = 10) -> pd.DataFrame:
    sql = """
        SELECT
            m.start_time     AS match_date,
            m.match_desc,
            t1.team_name     AS team1,
            t2.team_name     AS team2,
            w.team_name      AS winner,
            m.victory_margin AS margin,
            m.victory_type   AS margin_type,
            v.venue_name
        FROM matches AS m
        JOIN teams AS t1 ON t1.team_id = m.team1_id
        JOIN teams AS t2 ON t2.team_id = m.team2_id
        LEFT JOIN teams AS w ON w.team_id = m.winner_team_id
        LEFT JOIN venues AS v ON v.venue_id = m.venue_id
        WHERE m.state = 'Complete'
        ORDER BY m.start_time DESC
        LIMIT :limit
    """
    return _query(sql, {"limit": int(limit)})