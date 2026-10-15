import logging

from sqlalchemy import text
from sqlalchemy.engine import Connection, Engine

from api.cricbuzz_client import CricbuzzClient
from services.parsers import (
    overs_to_balls,
    parse_dismissal_type,
    parse_toss,
    to_int,
)
from utils.db_connection import get_engine

logger = logging.getLogger(__name__)


def _team_map(conn: Connection) -> dict:
    ids = {}
    rows = conn.execute(text("SELECT team_id, team_name, short_name FROM teams"))
    for team_id, name, short in rows:
        ids[name.lower()] = team_id
        if short:
            ids[short.lower()] = team_id
    return ids


def _team_id(teams: dict, name) -> int:
    team_id = teams.get((name or "").lower())
    if team_id is None:
        raise ValueError(f"Unknown team: {name!r}")
    return team_id


def _country_id(conn: Connection, name):
    if not name:
        return None
    row = conn.execute(
        text("SELECT country_id FROM countries WHERE country_name = :n"), {"n": name}
    ).first()
    if row:
        return row[0]
    new_id = conn.execute(
        text("SELECT COALESCE(MAX(country_id), 0) + 1 FROM countries")
    ).scalar()
    conn.execute(
        text("INSERT INTO countries (country_id, country_name) VALUES (:i, :n)"),
        {"i": new_id, "n": name},
    )
    return new_id


def load_match_detail(conn: Connection, match_id: int, info: dict, card: dict) -> None:
    teams = _team_map(conn)
    team1, team2 = conn.execute(
        text("SELECT team1_id, team2_id FROM matches WHERE match_id = :m"),
        {"m": match_id},
    ).one()

    venue = info.get("venueinfo") or {}
    conn.execute(
        text("UPDATE venues SET country_id = :c, capacity = :cap WHERE venue_id = :v"),
        {
            "c": _country_id(conn, venue.get("country")),
            "cap": to_int(venue.get("capacity")),
            "v": venue.get("id"),
        },
    )

    toss_team, decision = parse_toss(info.get("tossstatus", ""))
    conn.execute(
        text(
            "UPDATE matches SET toss_winner_team_id = :t, toss_decision = :d "
            "WHERE match_id = :m"
        ),
        {"t": teams.get((toss_team or "").lower()), "d": decision, "m": match_id},
    )

    for number, inn in enumerate(card.get("scorecard", []), start=1):
        batting = _team_id(teams, inn.get("batteamname"))
        if batting not in (team1, team2):
            raise ValueError(f"Batting team {batting} not in match {match_id}")
        bowling = team2 if batting == team1 else team1

        conn.execute(
            text(
                """INSERT INTO innings
                   (match_id, innings_no, batting_team_id, bowling_team_id,
                    total_runs, wickets_lost, balls_bowled, extras)
                   VALUES (:m, :n, :bat, :bowl, :runs, :wkts, :balls, :extras)
                   ON DUPLICATE KEY UPDATE
                       total_runs = VALUES(total_runs),
                       wickets_lost = VALUES(wickets_lost),
                       balls_bowled = VALUES(balls_bowled),
                       extras = VALUES(extras)"""
            ),
            {
                "m": match_id,
                "n": number,
                "bat": batting,
                "bowl": bowling,
                "runs": inn.get("score"),
                "wkts": inn.get("wickets"),
                "balls": overs_to_balls(inn.get("overs")),
                "extras": (inn.get("extras") or {}).get("total"),
            },
        )
        innings_id = conn.execute(
            text("SELECT innings_id FROM innings WHERE match_id = :m AND innings_no = :n"),
            {"m": match_id, "n": number},
        ).scalar()

        partners = (inn.get("partnership") or {}).get("partnership", [])

        people = {}
        for b in inn.get("batsman", []):
            people[b["id"]] = b["name"]
        for b in inn.get("bowler", []):
            people[b["id"]] = b["name"]
        for p in partners:
            people[p["bat1id"]] = p["bat1name"]
            people[p["bat2id"]] = p["bat2name"]
        if people:
            conn.execute(
                text(
                    "INSERT IGNORE INTO players (player_id, full_name, data_source) "
                    "VALUES (:i, :n, 'api')"
                ),
                [{"i": i, "n": n} for i, n in people.items()],
            )

        bat_rows, position = [], 0
        for b in inn.get("batsman", []):
            kind = parse_dismissal_type(b.get("outdec"))
            if kind == "did_not_bat":
                continue
            position += 1
            bat_rows.append(
                {
                    "inn": innings_id,
                    "p": b["id"],
                    "pos": position,
                    "runs": b.get("runs", 0),
                    "balls": b.get("balls", 0),
                    "fours": b.get("fours", 0),
                    "sixes": b.get("sixes", 0),
                    "no": 1 if kind == "not_out" else 0,
                    "dtext": b.get("outdec") or None,
                    "dtype": kind,
                }
            )
        if bat_rows:
            conn.execute(
                text(
                    """INSERT INTO batting_scorecards
                       (innings_id, player_id, batting_position, runs, balls_faced,
                        fours, sixes, is_not_out, dismissal_text, dismissal_type)
                       VALUES (:inn, :p, :pos, :runs, :balls, :fours, :sixes,
                               :no, :dtext, :dtype)
                       ON DUPLICATE KEY UPDATE
                           runs = VALUES(runs), balls_faced = VALUES(balls_faced),
                           fours = VALUES(fours), sixes = VALUES(sixes),
                           is_not_out = VALUES(is_not_out),
                           dismissal_text = VALUES(dismissal_text),
                           dismissal_type = VALUES(dismissal_type)"""
                ),
                bat_rows,
            )

        bowl_rows = [
            {
                "inn": innings_id,
                "p": b["id"],
                "balls": overs_to_balls(b.get("overs")),
                "maidens": b.get("maidens", 0),
                "runs": b.get("runs", 0),
                "wkts": b.get("wickets", 0),
                "dots": b.get("dots"),
            }
            for b in inn.get("bowler", [])
        ]
        if bowl_rows:
            conn.execute(
                text(
                    """INSERT INTO bowling_scorecards
                       (innings_id, player_id, balls_bowled, maidens,
                        runs_conceded, wickets, dots)
                       VALUES (:inn, :p, :balls, :maidens, :runs, :wkts, :dots)
                       ON DUPLICATE KEY UPDATE
                           balls_bowled = VALUES(balls_bowled),
                           maidens = VALUES(maidens),
                           runs_conceded = VALUES(runs_conceded),
                           wickets = VALUES(wickets), dots = VALUES(dots)"""
                ),
                bowl_rows,
            )

        part_rows = [
            {
                "inn": innings_id,
                "no": idx,
                "b1": p["bat1id"],
                "b2": p["bat2id"],
                "r1": p.get("bat1runs", 0),
                "ba1": p.get("bat1balls", 0),
                "r2": p.get("bat2runs", 0),
                "ba2": p.get("bat2balls", 0),
                "tr": p.get("totalruns", 0),
                "tb": p.get("totalballs", 0),
            }
            for idx, p in enumerate(partners, start=1)
        ]
        if part_rows:
            conn.execute(
                text(
                    """INSERT INTO partnerships
                       (innings_id, partnership_no, bat1_player_id, bat2_player_id,
                        bat1_runs, bat1_balls, bat2_runs, bat2_balls,
                        total_runs, total_balls)
                       VALUES (:inn, :no, :b1, :b2, :r1, :ba1, :r2, :ba2, :tr, :tb)
                       ON DUPLICATE KEY UPDATE
                           bat1_runs = VALUES(bat1_runs), bat1_balls = VALUES(bat1_balls),
                           bat2_runs = VALUES(bat2_runs), bat2_balls = VALUES(bat2_balls),
                           total_runs = VALUES(total_runs),
                           total_balls = VALUES(total_balls)"""
                ),
                part_rows,
            )


def load_all(engine: Engine) -> int:
    client = CricbuzzClient()
    with engine.connect() as conn:
        match_ids = [
            r[0]
            for r in conn.execute(
                text("SELECT match_id FROM matches WHERE state = 'Complete' ORDER BY start_time")
            )
        ]
    for match_id in match_ids:
        info = client.match_info(match_id)
        card = client.match_scorecard(match_id)
        with engine.begin() as conn:
            load_match_detail(conn, match_id, info, card)
        logger.info("Loaded match %s", match_id)
    return len(match_ids)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("matches loaded:", load_all(get_engine()))