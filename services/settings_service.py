import pandas as pd
import streamlit as st
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

import config
from utils.db_connection import get_engine

TABLES = (
    "series", "teams", "venues", "players", "matches", "innings",
    "batting_scorecards", "bowling_scorecards", "partnerships",
    "player_career_stats", "countries", "formats", "api_call_log",
)
SOURCE_TABLES = (
    "series", "teams", "venues", "players", "matches", "player_career_stats",
)


def db_status() -> dict:
    try:
        with get_engine().connect() as conn:
            version, database = conn.execute(
                text("SELECT VERSION(), DATABASE()")
            ).one()
        return {"ok": True, "version": version, "database": database}
    except SQLAlchemyError as exc:
        return {"ok": False, "error": type(exc).__name__}


def config_status() -> dict:
    """Never returns secrets, only whether they are set."""
    return {
        "RapidAPI key set": bool(config.RAPIDAPI_KEY),
        "RapidAPI host": config.RAPIDAPI_HOST or "missing",
        "Database user set": bool(config.DB_USER),
        "Database password set": bool(config.DB_PASSWORD),
        "Database name": config.DB_NAME or "missing",
    }


@st.cache_data(ttl=60)
def table_counts() -> pd.DataFrame:
    sql = " UNION ALL ".join(
        f"SELECT '{t}' AS table_name, COUNT(*) AS row_count FROM {t}" for t in TABLES
    )
    with get_engine().connect() as conn:
        return pd.read_sql(text(sql), conn)


@st.cache_data(ttl=60)
def data_sources() -> pd.DataFrame:
    sql = " UNION ALL ".join(
        f"SELECT '{t}' AS table_name, data_source, COUNT(*) AS row_count "
        f"FROM {t} GROUP BY data_source"
        for t in SOURCE_TABLES
    )
    with get_engine().connect() as conn:
        df = pd.read_sql(text(sql), conn)
    return (
        df.pivot_table(
            index="table_name", columns="data_source",
            values="row_count", fill_value=0,
        )
        .reset_index()
        .rename_axis(columns=None)
    )