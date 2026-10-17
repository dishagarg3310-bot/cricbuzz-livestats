import pandas as pd
import streamlit as st
from sqlalchemy import bindparam, text

from utils.db_connection import get_engine


def _query(statement, params: dict | None = None) -> pd.DataFrame:
    with get_engine().connect() as conn:
        return pd.read_sql(statement, conn, params=params)


@st.cache_data(ttl=300)
def get_formats() -> list:
    df = _query(text("SELECT format_name FROM formats ORDER BY format_id"))
    return df["format_name"].tolist()


@st.cache_data(ttl=300)
def top_batters(format_name: str, limit: int) -> pd.DataFrame:
    sql = text(
        """
        SELECT full_name AS player, runs, batting_avg, strike_rate, centuries
        FROM v_player_batting_career
        WHERE format_name = :f
        ORDER BY runs DESC
        LIMIT :n
        """
    )
    return _query(sql, {"f": format_name, "n": int(limit)})


@st.cache_data(ttl=300)
def top_bowlers(format_name: str, limit: int) -> pd.DataFrame:
    sql = text(
        """
        SELECT full_name AS player, wickets, economy, bowling_avg, matches
        FROM v_player_bowling_career
        WHERE format_name = :f AND wickets > 0
        ORDER BY wickets DESC
        LIMIT :n
        """
    )
    return _query(sql, {"f": format_name, "n": int(limit)})


@st.cache_data(ttl=300)
def players_with_stats() -> pd.DataFrame:
    sql = text(
        """
        SELECT DISTINCT p.player_id, p.full_name
        FROM players AS p
        JOIN player_career_stats AS s ON s.player_id = p.player_id
        ORDER BY p.full_name
        """
    )
    return _query(sql)


@st.cache_data(ttl=300)
def compare_players(player_ids: tuple) -> pd.DataFrame:
    sql = text(
        """
        SELECT full_name AS player, format_name AS format,
               runs, batting_avg, strike_rate, centuries
        FROM v_player_batting_career
        WHERE player_id IN :ids
        ORDER BY full_name, format_name
        """
    ).bindparams(bindparam("ids", expanding=True))
    return _query(sql, {"ids": list(player_ids)})