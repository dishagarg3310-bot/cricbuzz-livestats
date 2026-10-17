from decimal import Decimal
from pathlib import Path

import pandas as pd
import streamlit as st
from sqlalchemy import text

from utils.db_connection import get_engine

SQL_DIR = Path(__file__).resolve().parent.parent / "sql"
LEVELS = ["Beginner", "Intermediate", "Advanced"]


def _q(no, level, title, params=None, labels=None):
    return {
        "no": no,
        "level": level,
        "title": title,
        "params": params or [],
        "labels": labels,
    }


def _p(var, label, default):
    return {"var": var, "label": label, "default": default}


QUESTIONS = [
    _q(1, "Beginner", "Players who represent India"),
    _q(2, "Beginner", "Matches played in the last 30 days"),
    _q(3, "Beginner", "Top 10 ODI run scorers"),
    _q(4, "Beginner", "Venues with capacity above 50,000"),
    _q(5, "Beginner", "Total wins per team"),
    _q(6, "Beginner", "Players per playing role"),
    _q(7, "Beginner", "Highest individual score per format"),
    _q(8, "Beginner", "Series that started in 2024"),
    _q(9, "Intermediate", "All-rounders with 1000+ runs and 50+ wickets"),
    _q(10, "Intermediate", "Last 20 completed matches"),
    _q(11, "Intermediate", "Player runs across formats"),
    _q(12, "Intermediate", "Home vs away wins per team"),
    _q(13, "Intermediate", "Consecutive-batsmen partnerships of 100+"),
    _q(14, "Intermediate", "Bowling performance by venue",
       [_p("min_matches", "Minimum matches at the venue", 3)]),
    _q(15, "Intermediate", "Players in close matches"),
    _q(16, "Intermediate", "Batting performance by year (since 2020)",
       [_p("min_matches_year", "Minimum matches in the year", 5)]),
    _q(17, "Advanced", "Does winning the toss help?",
       labels=["Toss advantage", "Data check"]),
    _q(18, "Advanced", "Most economical limited-overs bowlers",
       [_p("q18_min_matches", "Minimum matches bowled", 10)]),
    _q(19, "Advanced", "Most consistent batsmen",
       [_p("q19_min_innings", "Minimum innings", 3)]),
    _q(20, "Advanced", "Matches and averages per format",
       [_p("q20_min_matches", "Minimum total matches", 20)]),
    _q(21, "Advanced", "Weighted player ranking per format"),
    _q(22, "Advanced", "Team head-to-head",
       [_p("q22_min_matches", "Minimum matches between the two teams", 5)],
       labels=["Head-to-head record", "Batting first vs bowling first by venue"]),
    _q(23, "Advanced", "Recent player form",
       [_p("q23_min_innings", "Minimum innings", 3)]),
    _q(24, "Advanced", "Best batting partnerships",
       [_p("q24_min_partnerships", "Minimum partnerships together", 5)]),
    _q(25, "Advanced", "Career trajectory by quarter",
       [_p("q25_min_quarters", "Minimum quarters of data", 6),
        _p("q25_min_matches", "Minimum matches per quarter", 3)]),
]


def get_sql_text(no: int) -> str:
    return (SQL_DIR / f"q{no:02d}.sql").read_text(encoding="utf-8")


def _statements(sql_text: str) -> list:
    """Split a .sql file into runnable statements (skip USE and header SELECTs)."""
    parts = [p.strip() for p in sql_text.split(";")]
    return [
        p for p in parts
        if p and not p.upper().startswith("USE ") and "AS question" not in p
    ]


def _clean(df: pd.DataFrame) -> pd.DataFrame:
    """Turn Decimal columns into floats so Streamlit shows them as numbers."""
    for col in df.columns:
        if df[col].dtype == object:
            sample = df[col].dropna()
            if not sample.empty and isinstance(sample.iloc[0], Decimal):
                df[col] = df[col].astype(float)
    return df


@st.cache_data(ttl=300, show_spinner=False)
def run_question(no: int, params: tuple = ()) -> list:
    """Run one question and return a list of DataFrames (one per SELECT)."""
    statements = _statements(get_sql_text(no))
    results = []
    with get_engine().connect() as conn:
        for var, value in params:
            conn.execute(text(f"SET @{var} = :v"), {"v": int(value)})
        for stmt in statements:
            results.append(_clean(pd.read_sql(text(stmt), conn)))
    return results