import re
from pathlib import Path

import pytest
from sqlalchemy import text
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parent.parent


def run_page(script: Path) -> AppTest:
    return AppTest.from_file(str(script), default_timeout=30).run()


def test_home_page_shows_five_kpi_cards(db):
    at = run_page(ROOT / "main.py")
    assert not at.exception
    html = " ".join(block.value for block in at.markdown)

    labels = re.findall(r'<div class="label">(.*?)</div>', html)
    assert labels == ["Series", "Matches", "Teams", "Venues", "Players"]

    values = re.findall(r'<div class="value">(.*?)</div>', html)
    with db.connect() as conn:
        series = conn.execute(text("SELECT COUNT(*) FROM series")).scalar()
    assert int(values[0]) == series


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