import logging

from sqlalchemy import text

from api.cricbuzz_client import CricbuzzClient
from utils.db_connection import get_engine

logging.basicConfig(level=logging.INFO)

TOP_BATTERS = 10
TOP_BOWLERS = 6

with get_engine().connect() as conn:
    batters = [
        r[0]
        for r in conn.execute(
            text(
                "SELECT player_id FROM batting_scorecards "
                "GROUP BY player_id ORDER BY SUM(runs) DESC LIMIT :n"
            ),
            {"n": TOP_BATTERS},
        )
    ]
    bowlers = [
        r[0]
        for r in conn.execute(
            text(
                "SELECT player_id FROM bowling_scorecards "
                "GROUP BY player_id ORDER BY SUM(wickets) DESC LIMIT :n"
            ),
            {"n": TOP_BOWLERS},
        )
    ]

player_ids = list(dict.fromkeys(batters + bowlers))
print("players:", len(player_ids), player_ids)

client = CricbuzzClient()
for player_id in player_ids:
    client.player_info(player_id)
    client.player_batting(player_id)
    client.player_bowling(player_id)

print("done:", len(player_ids), "players")