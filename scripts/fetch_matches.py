import logging

from sqlalchemy import text

from api.cricbuzz_client import CricbuzzClient
from utils.db_connection import get_engine

logging.basicConfig(level=logging.INFO)

with get_engine().connect() as conn:
    match_ids = [
        r[0]
        for r in conn.execute(
            text("SELECT match_id FROM matches WHERE state = 'Complete' ORDER BY start_time")
        )
    ]

client = CricbuzzClient()
for match_id in match_ids:
    client.match_info(match_id)
    client.match_scorecard(match_id)

print("done:", len(match_ids), "matches")