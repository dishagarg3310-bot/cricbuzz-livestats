import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from api.cricbuzz_client import CricbuzzClient
from services.parsers import epoch_ms_to_datetime
from utils.db_connection import get_engine

ROOT = Path(__file__).resolve().parent.parent
SAVED = ROOT / "data" / "raw" / "matches_v1_live.json"
SAMPLE = ROOT / "data" / "sample" / "sample_live_matches.json"
LIVE_PATH = "/matches/v1/live"


def load_saved() -> tuple:
    """Return (data, label). Never calls the API."""
    if SAVED.exists():
        saved_at = datetime.fromtimestamp(SAVED.stat().st_mtime)
        label = f"Last refreshed {saved_at:%d %b %Y, %H:%M}"
        return json.loads(SAVED.read_text(encoding="utf-8")), label
    if SAMPLE.exists():
        return (
            json.loads(SAMPLE.read_text(encoding="utf-8")),
            "Sample data (not live). Press Refresh to fetch live data.",
        )
    return {}, "No saved data yet. Press Refresh to fetch live data."


def _score_text(team_score) -> str:
    parts = []
    for key in sorted(team_score or {}):
        inn = team_score[key]
        if inn.get("runs") is None:
            continue
        parts.append(f"{inn['runs']}/{inn.get('wickets', 0)} ({inn.get('overs', 0)} ov)")
    return "  &  ".join(parts)


def parse_matches(data: dict) -> list:
    records = []
    for type_block in data.get("typeMatches", []):
        for series_block in type_block.get("seriesMatches", []):
            wrapper = series_block.get("seriesAdWrapper")
            if not wrapper:
                continue
            for item in wrapper.get("matches", []):
                info = item.get("matchInfo") or {}
                score = item.get("matchScore") or {}
                venue = info.get("venueInfo") or {}
                team1 = info.get("team1") or {}
                team2 = info.get("team2") or {}
                start = epoch_ms_to_datetime(info.get("startDate"))
                records.append(
                    {
                        "match_id": info.get("matchId"),
                        "series": info.get("seriesName"),
                        "desc": info.get("matchDesc"),
                        "format": info.get("matchFormat"),
                        "state": info.get("state") or "Unknown",
                        "status": info.get("status"),
                        "team1": team1.get("teamName"),
                        "team2": team2.get("teamName"),
                        "team1_short": team1.get("teamSName"),
                        "team2_short": team2.get("teamSName"),
                        "score1": _score_text(score.get("team1Score")),
                        "score2": _score_text(score.get("team2Score")),
                        "venue": venue.get("ground"),
                        "city": venue.get("city"),
                        "start": f"{start:%d %b %Y, %H:%M} UTC" if start else "",
                    }
                )
    return records


def _log_call(endpoint: str, status: int, remaining) -> None:
    """Best effort: a logging failure must never break the page."""
    try:
        with get_engine().begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO api_call_log (endpoint, called_at, status_code, requests_remaining) "
                    "VALUES (:e, UTC_TIMESTAMP(), :s, :r)"
                ),
                {"e": endpoint, "s": status, "r": remaining},
            )
    except SQLAlchemyError:
        pass


def refresh_live() -> None:
    """Spend exactly one API call and save the response."""
    client = CricbuzzClient()
    client.live_matches(refresh=True)
    _log_call(LIVE_PATH, 200, getattr(client, "last_remaining", None))


def calls_left():
    try:
        with get_engine().connect() as conn:
            return conn.execute(
                text(
                    "SELECT requests_remaining FROM api_call_log "
                    "WHERE requests_remaining IS NOT NULL "
                    "ORDER BY called_at DESC, log_id DESC LIMIT 1"
                )
            ).scalar()
    except SQLAlchemyError:
        return None


@st.cache_data(ttl=300)
def upcoming_from_db() -> pd.DataFrame:
    sql = text(
        """
        SELECT m.start_time AS start_utc, m.match_desc,
               t1.team_name AS team1, t2.team_name AS team2,
               v.venue_name, v.city
        FROM matches AS m
        JOIN teams AS t1 ON t1.team_id = m.team1_id
        JOIN teams AS t2 ON t2.team_id = m.team2_id
        LEFT JOIN venues AS v ON v.venue_id = m.venue_id
        WHERE m.state = 'Upcoming'
        ORDER BY m.start_time
        """
    )
    with get_engine().connect() as conn:
        return pd.read_sql(sql, conn)