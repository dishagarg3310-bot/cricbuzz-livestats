"""Explore the saved live-matches JSON. Reads a local file, makes no API calls."""
import json
from pathlib import Path

import pandas as pd

data = json.loads(Path("data/sample_live_matches.json").read_text(encoding="utf-8"))
print("Top-level keys:", list(data.keys()))

rows = []
first_match = None
for type_block in data.get("typeMatches", []):
    match_type = type_block.get("matchType")
    for series_block in type_block.get("seriesMatches", []):
        wrapper = series_block.get("seriesAdWrapper")
        if wrapper is None:  # some entries are ads, not series
            continue
        for match in wrapper.get("matches", []):
            first_match = first_match or match
            info = match.get("matchInfo", {})
            venue = info.get("venueInfo", {})
            rows.append({
                "match_type": match_type,
                "series_id": wrapper.get("seriesId"),
                "series_name": wrapper.get("seriesName"),
                "match_id": info.get("matchId"),
                "description": info.get("matchDesc"),
                "format": info.get("matchFormat"),
                "team1": info.get("team1", {}).get("teamName"),
                "team2": info.get("team2", {}).get("teamName"),
                "venue": venue.get("ground"),
                "city": venue.get("city"),
                "state": info.get("state"),
            })

df = pd.DataFrame(rows)
print("\nMatches found:", len(df))
print(df.to_string())

if first_match:
    print("\nKeys in one match:", list(first_match.keys()))
    print("Keys in matchInfo:", list(first_match.get("matchInfo", {}).keys()))