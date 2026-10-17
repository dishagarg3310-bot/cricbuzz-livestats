from pathlib import Path

import pytest
from sqlalchemy import text
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parent.parent


def run_page(script: Path) -> AppTest:
    return AppTest.from_file(str(script), default_timeout=30).run()


def test_home_page_shows_five_metrics(db):
    at = run_page(ROOT / "main.py")
    assert not at.exception
    assert [m.label for m in at.metric] == [
        "Series", "Matches", "Teams", "Venues", "Players"
    ]
    with db.connect() as conn:
        series = conn.execute(text("SELECT COUNT(*) FROM series")).scalar()
    assert int(at.metric[0].value) == series


def test_settings_page_reports_connected(db):
    script = next(ROOT.glob("pages/*Settings.py"))
    at = run_page(script)
    assert not at.exception
    assert at.metric[0].value == "Connected"


def test_sql_analytics_page_renders_first_question(db):
    script = next(ROOT.glob("pages/*SQL_Analytics.py"))
    at = run_page(script)
    assert not at.exception
    assert len(at.dataframe) >= 1