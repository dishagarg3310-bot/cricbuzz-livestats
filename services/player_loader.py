import logging
import re
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.engine import Connection

from api.cricbuzz_client import CricbuzzClient
from services.detail_loader import _country_id
from services.parsers import map_role, to_int
from utils.db_connection import get_engine

logger = logging.getLogger(__name__)

STAT_FORMATS = {"Test": 1, "ODI": 2, "T20": 3, "IPL": 4}


def _by_format(table: dict) -> dict:
    """Transpose: rows are stats, columns are formats -> {format: {stat: value}}."""
    headers = table.get("headers", [])[1:]
    result = {h: {} for h in headers}
    for row in table.get("values", []):
        vals = row["values"]
        for header, value in zip(headers, vals[1:]):
            result[header][vals[0]] = value
    return result


def _num(value) -> int:
    """'183*' -> 183. '-' or empty -> 0 (these columns are NOT NULL)."""
    return to_int(str(value).replace("*", "")) or 0


def load_player(conn: Connection, info: dict, batting: dict, bowling: dict) -> None:
    player_id = int(info["id"])
    conn.execute(
        text(
            """UPDATE players SET country_id = :c, playing_role = :r,
                   batting_style = :bat, bowling_style = :bowl
               WHERE player_id = :p"""
        ),
        {
            "c": _country_id(conn, info.get("intlTeam")),
            "r": map_role(info.get("role")),
            "bat": info.get("bat") or None,
            "bowl": info.get("bowl") or None,
            "p": player_id,
        },
    )

    bat_stats = _by_format(batting)
    bowl_stats = _by_format(bowling)
    for fmt_name, fmt_id in STAT_FORMATS.items():
        b = bat_stats.get(fmt_name, {})
        w = bowl_stats.get(fmt_name, {})
        matches = max(_num(b.get("Matches")), _num(w.get("Matches")))
        if matches == 0:
            continue
        conn.execute(
            text(
                """INSERT INTO player_career_stats
                   (player_id, format_id, matches, innings_batted, not_outs, runs,
                    balls_faced, highest_score, centuries, fifties, fours, sixes,
                    ducks, balls_bowled, runs_conceded, wickets, maidens,
                    five_wickets, data_source)
                   VALUES (:p, :f, :m, :inn, :no, :runs, :bf, :hs, :c100, :c50,
                           :fours, :sixes, :ducks, :bb, :rc, :wk, :md, :w5, 'api')
                   ON DUPLICATE KEY UPDATE
                       matches = VALUES(matches), innings_batted = VALUES(innings_batted),
                       not_outs = VALUES(not_outs), runs = VALUES(runs),
                       balls_faced = VALUES(balls_faced),
                       highest_score = VALUES(highest_score),
                       centuries = VALUES(centuries), fifties = VALUES(fifties),
                       fours = VALUES(fours), sixes = VALUES(sixes),
                       ducks = VALUES(ducks), balls_bowled = VALUES(balls_bowled),
                       runs_conceded = VALUES(runs_conceded),
                       wickets = VALUES(wickets), maidens = VALUES(maidens),
                       five_wickets = VALUES(five_wickets)"""
            ),
            {
                "p": player_id,
                "f": fmt_id,
                "m": matches,
                "inn": _num(b.get("Innings")),
                "no": _num(b.get("Not Out")),
                "runs": _num(b.get("Runs")),
                "bf": _num(b.get("Balls")),
                "hs": _num(b.get("Highest")),
                "c100": _num(b.get("100s")),
                "c50": _num(b.get("50s")),
                "fours": _num(b.get("Fours")),
                "sixes": _num(b.get("Sixes")),
                "ducks": _num(b.get("Ducks")),
                "bb": _num(w.get("Balls")),
                "rc": _num(w.get("Runs")),
                "wk": _num(w.get("Wickets")),
                "md": _num(w.get("Maidens")),
                "w5": _num(w.get("5w")),
            },
        )


def load_all_players() -> int:
    ids = sorted(
        int(m.group(1))
        for f in Path("data/raw").glob("stats_v1_player_*.json")
        if (m := re.fullmatch(r"stats_v1_player_(\d+)\.json", f.name))
    )
    client = CricbuzzClient()
    engine = get_engine()
    for player_id in ids:
        info = client.player_info(player_id)
        batting = client.player_batting(player_id)
        bowling = client.player_bowling(player_id)
        with engine.begin() as conn:
            load_player(conn, info, batting, bowling)
        logger.info("Loaded player %s", player_id)

    with engine.begin() as conn:
        conn.execute(
            text(
                """UPDATE teams t JOIN countries c ON c.country_name = t.team_name
                   SET t.country_id = c.country_id"""
            )
        )
    return len(ids)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("players loaded:", load_all_players())