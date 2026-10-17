import config

config.RAPIDAPI_HOST = "no-such-host.invalid"

from api.cricbuzz_client import CricbuzzAPIError, CricbuzzClient

client = CricbuzzClient(use_cache=False)
try:
    client.get("/series/v1/999999")
except CricbuzzAPIError as exc:
    print(type(exc).__name__, "-", exc)