from datetime import datetime

import pytest

from services.parsers import (
    epoch_ms_to_datetime,
    map_role,
    overs_to_balls,
    parse_dismissal_type,
    parse_height_cm,
    parse_result,
    parse_toss,
    to_float,
    to_int,
)


def test_epoch_ms_to_datetime():
    assert epoch_ms_to_datetime("1790497800000") == datetime(2026, 9, 27, 8, 30)


@pytest.mark.parametrize("bad", [None, "", "abc", 0, -5])
def test_epoch_ms_to_datetime_bad_input(bad):
    assert epoch_ms_to_datetime(bad) is None


def test_to_int():
    assert to_int("50000") == 50000
    assert to_int("1,234") == 1234
    assert to_int(" 7 ") == 7


@pytest.mark.parametrize("bad", ["-", "", None, "x"])
def test_to_int_returns_none_not_zero(bad):
    assert to_int(bad) is None


def test_to_float():
    assert to_float("58.79") == 58.79
    assert to_float("-") is None


@pytest.mark.parametrize(
    "overs, balls",
    [(41.4, 250), ("41.4", 250), (0.3, 3), (10, 60), ("0.0", 0)],
)
def test_overs_to_balls(overs, balls):
    assert overs_to_balls(overs) == balls


def test_overs_to_balls_missing():
    assert overs_to_balls(None) is None
    assert overs_to_balls("") is None


def test_parse_toss():
    assert parse_toss("India opt to bowl") == ("India", "bowl")
    assert parse_toss("West Indies elected to bat") == ("West Indies", "bat")


def test_parse_toss_unknown_format():
    assert parse_toss("") == (None, None)
    assert parse_toss("Toss delayed by rain") == (None, None)


def test_parse_result_wickets_and_runs():
    assert parse_result("India won by 8 wkts") == ("India", 8, "wickets")
    assert parse_result("Australia won by 214 runs") == ("Australia", 214, "runs")


def test_parse_result_no_winner():
    assert parse_result("Match tied") == (None, None, None)
    assert parse_result("") == (None, None, None)


@pytest.mark.parametrize(
    "text, expected",
    [
        ("", "did_not_bat"),
        ("not out", "not_out"),
        ("batting", "not_out"),
        ("b Prasidh Krishna", "bowled"),
        ("c Jewel Andrew b Alzarri Joseph", "caught"),
        ("c & b Starc", "caught_and_bowled"),
        ("lbw b Kuldeep Yadav", "lbw"),
        ("st Carey b Zampa", "stumped"),
        ("run out (Hope)", "run_out"),
        ("hit wicket b Jansen", "hit_wicket"),
        ("retired hurt", "other"),
    ],
)
def test_parse_dismissal_type(text, expected):
    assert parse_dismissal_type(text) == expected


def test_parse_height_cm():
    assert parse_height_cm("5 ft 9 in (175 cm) ") == 175
    assert parse_height_cm("") is None


def test_map_role_matches_database_constraint():
    allowed = {"Batsman", "Bowler", "All-rounder", "Wicket-keeper"}
    for api_role in ["Batsman", "Bowler", "WK-Batsman",
                     "Batting Allrounder", "Bowling Allrounder"]:
        assert map_role(api_role) in allowed
    assert map_role("Coach") is None
    assert map_role(None) is None