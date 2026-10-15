import logging

from sqlalchemy import text
from sqlalchemy.engine import Engine

from api.cricbuzz_client import CricbuzzClient
from services.parsers import epoch_ms_to_datetime, parse_result
from utils.db_connection import get_engine

logger = logging.getLogger(__name__)

FORMAT_IDS = {"TEST": 1, "ODI": 2, "T20": 3}


def _match_infos(data: dict) -> list:
    """Collect every matchInfo dict. Items without matchDetailsMap are skipped."""
    infos = []
    for item in data.get("matchDetails", []):
        for entry in item.get("matchDetailsMap", {}).get("match", []):
            if "matchInfo" in entry and "warm" not in str(entry["matchInfo"].get("matchDesc", "")).lower():
                infos.append(entry["matchInfo"])
    return infos


def load_series_matches(engine: Engine, data: dict) -> dict:
    infos = _match_infos(data)

    teams, venues = {}, {}
    for m in infos:
        for key in ("team1", "team2"):
            t = m[key]
            teams[t["teamId"]] = (t["teamName"], t.get("teamSName"))
        v = m.get("venueInfo")
        if v:
            venues[v["id"]] = (v["ground"], v.get("city"))

    name_to_id = {}
    for tid, (name, short) in teams.items():
        name_to_id[name.lower()] = tid
        if short:
            name_to_id[short.lower()] = tid

    match_rows = []
    for m in infos:
        start = epoch_ms_to_datetime(m.get("startDate"))
        end = epoch_ms_to_datetime(m.get("endDate"))
        winner_name, margin, kind = parse_result(m.get("status", ""))
        match_rows.append(
            {
                "id": m["matchId"],
                "series": m["seriesId"],
                "fmt": FORMAT_IDS.get(str(m.get("matchFormat", "")).upper()),
                "desc": m.get("matchDesc"),
                "t1": m["team1"]["teamId"],
                "t2": m["team2"]["teamId"],
                "venue": (m.get("venueInfo") or {}).get("id"),
                "start": start,
                "end": end,
                "state": m.get("state"),
                "status": m.get("status"),
                "winner": name_to_id.get(winner_name.lower()) if winner_name else None,
                "margin": margin,
                "kind": kind,
            }
        )

    with engine.begin() as conn:
        conn.execute(
            text(
                """INSERT INTO teams (team_id, team_name, short_name, data_source)
                   VALUES (:id, :name, :short, 'api')
                   ON DUPLICATE KEY UPDATE team_name = VALUES(team_name),
                                           short_name = VALUES(short_name)"""
            ),
            [{"id": i, "name": n, "short": s} for i, (n, s) in teams.items()],
        )
        conn.execute(
            text(
                """INSERT INTO venues (venue_id, venue_name, city, data_source)
                   VALUES (:id, :name, :city, 'api')
                   ON DUPLICATE KEY UPDATE venue_name = VALUES(venue_name),
                                           city = VALUES(city)"""
            ),
            [{"id": i, "name": n, "city": c} for i, (n, c) in venues.items()],
        )
        conn.execute(
            text(
                """INSERT INTO matches
                   (match_id, series_id, format_id, match_desc, team1_id, team2_id,
                    venue_id, start_time, end_time, state, status_text,
                    winner_team_id, victory_margin, victory_type, data_source)
                   VALUES (:id, :series, :fmt, :desc, :t1, :t2, :venue, :start, :end,
                           :state, :status, :winner, :margin, :kind, 'api')
                   ON DUPLICATE KEY UPDATE
                       state = VALUES(state), status_text = VALUES(status_text),
                       end_time = VALUES(end_time),
                       winner_team_id = VALUES(winner_team_id),
                       victory_margin = VALUES(victory_margin),
                       victory_type = VALUES(victory_type)"""
            ),
            match_rows,
        )
    return {"teams": len(teams), "venues": len(venues), "matches": len(match_rows)}


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)
    series_id = int(sys.argv[1]) if len(sys.argv) > 1 else 11902
    result = load_series_matches(get_engine(), CricbuzzClient().series_matches(series_id))
    print(result)