import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("RAPIDAPI_HOST")
KEY = os.getenv("RAPIDAPI_KEY")


def fetch(path: str) -> None:
    url = f"https://{HOST}{path}"
    headers = {"x-rapidapi-key": KEY, "x-rapidapi-host": HOST}
    resp = requests.get(url, headers=headers, timeout=20)

    print("Status:", resp.status_code)
    print("Remaining this month:", resp.headers.get("x-ratelimit-requests-remaining"))

    resp.raise_for_status()

    out_dir = Path("data/raw")
    out_dir.mkdir(parents=True, exist_ok=True)
    name = path.strip("/").replace("/", "_").replace("?", "_") + ".json"
    out_file = out_dir / name
    out_file.write_text(json.dumps(resp.json(), indent=2), encoding="utf-8")
    print("Saved:", out_file)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit('Usage: python scripts/fetch_one.py "/path/here"')
    fetch(sys.argv[1])