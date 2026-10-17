import pytest
import requests

import config
from api import cricbuzz_client as cb
from api.cricbuzz_client import (
    AuthError,
    CricbuzzAPIError,
    CricbuzzClient,
    RateLimitError,
)

SECRET = "test-secret-key"


class FakeResponse:
    def __init__(self, status=200, payload=None, headers=None, bad_json=False):
        self.status_code = status
        self._payload = {"ok": True} if payload is None else payload
        self.headers = headers or {}
        self._bad_json = bad_json

    def json(self):
        if self._bad_json:
            raise ValueError("not json")
        return self._payload


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "RAPIDAPI_KEY", SECRET)
    monkeypatch.setattr(config, "RAPIDAPI_HOST", "example.test")
    monkeypatch.setattr(cb, "RAW_DIR", tmp_path)
    return CricbuzzClient()


def fake_get(client, monkeypatch, response=None, error=None):
    """Replace the network call. Returns a list that records every call."""
    calls = []

    def _get(url, timeout):
        calls.append(url)
        if error:
            raise error
        return response

    monkeypatch.setattr(client.session, "get", _get)
    return calls


def test_success_is_cached_and_remaining_is_read(client, monkeypatch, tmp_path):
    resp = FakeResponse(payload={"a": 1}, headers={"x-ratelimit-requests-remaining": "150"})
    calls = fake_get(client, monkeypatch, resp)

    assert client.get("/series/v1/1") == {"a": 1}
    assert client.last_remaining == 150
    assert (tmp_path / "series_v1_1.json").exists()
    assert len(calls) == 1


def test_second_call_uses_cache(client, monkeypatch):
    calls = fake_get(client, monkeypatch, FakeResponse())
    client.get("/x/1")
    client.get("/x/1")
    assert len(calls) == 1


def test_refresh_forces_a_new_call(client, monkeypatch):
    calls = fake_get(client, monkeypatch, FakeResponse())
    client.get("/x/1")
    client.get("/x/1", refresh=True)
    assert len(calls) == 2


@pytest.mark.parametrize("status", [401, 403])
def test_bad_key_raises_auth_error(client, monkeypatch, status):
    fake_get(client, monkeypatch, FakeResponse(status=status))
    with pytest.raises(AuthError) as info:
        client.get("/x/1")
    assert SECRET not in str(info.value)


def test_limit_reached_raises_rate_limit_error(client, monkeypatch):
    fake_get(client, monkeypatch, FakeResponse(status=429))
    with pytest.raises(RateLimitError):
        client.get("/x/1")


@pytest.mark.parametrize("status", [404, 410, 500])
def test_other_http_errors(client, monkeypatch, status):
    fake_get(client, monkeypatch, FakeResponse(status=status))
    with pytest.raises(CricbuzzAPIError) as info:
        client.get("/x/1")
    assert not isinstance(info.value, (AuthError, RateLimitError))


def test_timeout_message(client, monkeypatch):
    fake_get(client, monkeypatch, error=requests.exceptions.Timeout())
    with pytest.raises(CricbuzzAPIError, match="did not answer"):
        client.get("/x/1")


def test_connection_error_message(client, monkeypatch):
    fake_get(client, monkeypatch, error=requests.exceptions.ConnectionError())
    with pytest.raises(CricbuzzAPIError, match="Could not reach"):
        client.get("/x/1")


def test_invalid_json(client, monkeypatch):
    fake_get(client, monkeypatch, FakeResponse(bad_json=True))
    with pytest.raises(CricbuzzAPIError, match="not JSON"):
        client.get("/x/1")


def test_unexpected_json_shape(client, monkeypatch):
    fake_get(client, monkeypatch, FakeResponse(payload=[1, 2, 3]))
    with pytest.raises(CricbuzzAPIError, match="Unexpected"):
        client.get("/x/1")


def test_failed_call_is_not_cached(client, monkeypatch, tmp_path):
    fake_get(client, monkeypatch, FakeResponse(status=429))
    with pytest.raises(RateLimitError):
        client.get("/x/1")
    assert list(tmp_path.iterdir()) == []


def test_missing_key_raises_auth_error(monkeypatch):
    monkeypatch.setattr(config, "RAPIDAPI_KEY", None)
    with pytest.raises(AuthError):
        CricbuzzClient()