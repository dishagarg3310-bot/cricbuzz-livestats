"""Smoke test: one call to the live matches endpoint, saved to data/."""
import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()  # reads the .env file into environment variables

url = os.getenv("LIVE_MATCHES_URL")
headers = {
    "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
    "x-rapidapi-host": os.getenv("RAPIDAPI_HOST"),
}

if not all([url, headers["x-rapidapi-key"], headers["x-rapidapi-host"]]):
    raise SystemExit("A value is missing in .env - check the three variable names.")

response = requests.get(url, headers=headers, timeout=30)
print("Status code:", response.status_code)
print("Requests remaining:", response.headers.get("x-ratelimit-requests-remaining"))
print("Free-plan requests remaining:",
      response.headers.get("x-rate-limit-rapid-free-plans-hard-limit-remaining"))

if response.status_code == 200:
    out = Path("data") / "sample_live_matches.json"
    out.write_text(json.dumps(response.json(), indent=2), encoding="utf-8")
    print("Saved to", out)
else:
    print("Request failed:", response.text[:300])