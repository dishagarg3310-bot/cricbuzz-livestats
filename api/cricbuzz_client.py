import json
import logging
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import config

logger = logging.getLogger(__name__)

RAW_DIR = Path("data/raw")
TIMEOUT_SECONDS = 20


class CricbuzzAPIError(Exception):
    """Raised when the Cricbuzz API call fails or returns bad data."""


class CricbuzzClient:
    def __init__(self, use_cache: bool = True) -> None:
        if not config.RAPIDAPI_KEY or not config.RAPIDAPI_HOST:
            raise CricbuzzAPIError("RAPIDAPI_KEY / RAPIDAPI_HOST missing in .env")

        self.use_cache = use_cache
        self.base_url = f"https://{config.RAPIDAPI_HOST}"
        self.session = requests.Session()
        self.session.headers.update(
            {
                "x-rapidapi-key": config.RAPIDAPI_KEY,
                "x-rapidapi-host": config.RAPIDAPI_HOST,
            }
        )
        retry = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retry))

    @staticmethod
    def _cache_file(path: str) -> Path:
        name = path.strip("/").replace("/", "_").replace("?", "_") + ".json"
        return RAW_DIR / name

    def get(self, path: str) -> dict:
        cache_file = self._cache_file(path)
        if self.use_cache and cache_file.exists():
            logger.info("Cache hit: %s", cache_file)
            return json.loads(cache_file.read_text(encoding="utf-8"))

        try:
            resp = self.session.get(
                f"{self.base_url}{path}", timeout=TIMEOUT_SECONDS
            )
            resp.raise_for_status()
            data = resp.json()
        except requests.exceptions.HTTPError as exc:
            raise CricbuzzAPIError(f"HTTP error for {path}: {exc}") from exc
        except requests.exceptions.RequestException as exc:
            raise CricbuzzAPIError(f"Network error for {path}: {exc}") from exc
        except ValueError as exc:
            raise CricbuzzAPIError(f"Invalid JSON for {path}") from exc

        remaining = resp.headers.get("x-ratelimit-requests-remaining")
        logger.info("API call %s, remaining this month: %s", path, remaining)

        RAW_DIR.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return data

    def series_list(self) -> dict:
        return self.get("/series/v1/international")

    def series_matches(self, series_id: int) -> dict:
        return self.get(f"/series/v1/{series_id}")

    def match_info(self, match_id: int) -> dict:
        return self.get(f"/mcenter/v1/{match_id}")

    def match_scorecard(self, match_id: int) -> dict:
        return self.get(f"/mcenter/v1/{match_id}/scard")

    def player_info(self, player_id: int) -> dict:
        return self.get(f"/stats/v1/player/{player_id}")

    def player_batting(self, player_id: int) -> dict:
        return self.get(f"/stats/v1/player/{player_id}/batting")

    def player_bowling(self, player_id: int) -> dict:
        return self.get(f"/stats/v1/player/{player_id}/bowling")