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
    """Base error: any failure when talking to the Cricbuzz API."""


class AuthError(CricbuzzAPIError):
    """The API key is missing, wrong, or not subscribed to this API."""


class RateLimitError(CricbuzzAPIError):
    """The monthly or hourly request limit has been reached."""


class CricbuzzClient:
    def __init__(self, use_cache: bool = True) -> None:
        if not config.RAPIDAPI_KEY or not config.RAPIDAPI_HOST:
            raise AuthError("RAPIDAPI_KEY / RAPIDAPI_HOST missing in .env")

        self.use_cache = use_cache
        self.last_remaining = None
        self.base_url = f"https://{config.RAPIDAPI_HOST}"
        self.session = requests.Session()
        self.session.headers.update(
            {
                "x-rapidapi-key": config.RAPIDAPI_KEY,
                "x-rapidapi-host": config.RAPIDAPI_HOST,
            }
        )
        # Retry only temporary server problems. 429 is NOT retried, because
        # retrying after the limit is reached only wastes calls.
        retry = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET"],
            raise_on_status=False,
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retry))

    @staticmethod
    def _cache_file(path: str) -> Path:
        name = path.strip("/").replace("/", "_").replace("?", "_") + ".json"
        return RAW_DIR / name

    @staticmethod
    def _raise_for_status(resp: requests.Response, path: str) -> None:
        code = resp.status_code
        if code in (401, 403):
            raise AuthError(
                "The API key was rejected. Check RAPIDAPI_KEY in .env "
                "and your RapidAPI subscription."
            )
        if code == 429:
            raise RateLimitError(
                "The API request limit has been reached. "
                "Wait for it to reset, or use the saved data."
            )
        if code in (404, 410):
            raise CricbuzzAPIError(
                f"The API does not know this endpoint or id ({path}, status {code})."
            )
        if code >= 400:
            raise CricbuzzAPIError(f"The API returned an error ({path}, status {code}).")

    def get(self, path: str, refresh: bool = False) -> dict:
        cache_file = self._cache_file(path)
        if self.use_cache and not refresh and cache_file.exists():
            logger.info("Cache hit: %s", cache_file)
            return json.loads(cache_file.read_text(encoding="utf-8"))

        try:
            resp = self.session.get(f"{self.base_url}{path}", timeout=TIMEOUT_SECONDS)
        except requests.exceptions.Timeout as exc:
            raise CricbuzzAPIError(
                f"The Cricbuzz API did not answer in {TIMEOUT_SECONDS} seconds ({path})."
            ) from exc
        except requests.exceptions.RequestException as exc:
            raise CricbuzzAPIError(
                f"Could not reach the Cricbuzz API ({path}). "
                "Check your internet connection."
            ) from exc

        remaining = resp.headers.get("x-ratelimit-requests-remaining")
        self.last_remaining = (
            int(remaining) if remaining and remaining.isdigit() else None
        )
        self._raise_for_status(resp, path)

        try:
            data = resp.json()
        except ValueError as exc:
            raise CricbuzzAPIError(
                f"The Cricbuzz API returned something that is not JSON ({path})."
            ) from exc
        if not isinstance(data, dict):
            raise CricbuzzAPIError(f"Unexpected response format from {path}.")

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

    def live_matches(self, refresh: bool = False) -> dict:
        return self.get("/matches/v1/live", refresh=refresh)