from sqlalchemy import text

from tests.helpers import run_query_file


def test_q01_lists_only_india_players_sorted(db):
    rows = run_query_file(db, 1)[0]
    names = [r["full_name"] for r in rows]
    assert names, "expected at least one India player"
    assert names == sorted(names)
    assert "Virat Kohli" in names


def test_q03_is_sorted_by_runs_and_limited_to_10(db):
    rows = run_query_file(db, 3)[0]
    runs = [r["total_runs"] for r in rows]
    assert 0 < len(rows) <= 10
    assert runs == sorted(runs, reverse=True)


def test_q05_wins_add_up_to_decided_matches(db):
    rows = run_query_file(db, 5)[0]
    total_wins = sum(r["total_wins"] for r in rows)
    with db.connect() as conn:
        decided = conn.execute(
            text("SELECT COUNT(*) FROM matches "
                 "WHERE state = 'Complete' AND winner_team_id IS NOT NULL")
        ).scalar()
    assert total_wins == decided


def test_q14_respects_its_threshold(db):
    rows = run_query_file(db, 14, {"min_matches": 999})[0]
    assert rows == []


def test_q17_percentages_are_valid(db):
    rows = run_query_file(db, 17)[0]
    labels = {r["toss_decision"] for r in rows}
    assert "overall" in labels
    assert all(0 <= r["win_pct"] <= 100 for r in rows)