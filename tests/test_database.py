from sqlalchemy import text

EXPECTED_TABLES = {
    "api_call_log", "batting_scorecards", "bowling_scorecards", "countries",
    "formats", "innings", "matches", "partnerships", "player_career_stats",
    "players", "series", "teams", "venues",
}


def test_all_tables_exist(db):
    with db.connect() as conn:
        found = {
            row[0]
            for row in conn.execute(
                text("SELECT table_name FROM information_schema.tables "
                     "WHERE table_schema = DATABASE()")
            )
        }
    assert EXPECTED_TABLES <= found


def test_views_exist(db):
    with db.connect() as conn:
        views = {
            row[0]
            for row in conn.execute(
                text("SELECT table_name FROM information_schema.views "
                     "WHERE table_schema = DATABASE()")
            )
        }
    assert {"v_player_batting_career", "v_player_bowling_career", "v_match_summary"} <= views


def test_innings_total_equals_batsmen_runs_plus_extras(db):
    sql = text(
        """
        SELECT i.innings_id
        FROM innings AS i
        LEFT JOIN batting_scorecards AS b ON b.innings_id = i.innings_id
        GROUP BY i.innings_id, i.total_runs, i.extras
        HAVING i.total_runs <> COALESCE(SUM(b.runs), 0) + COALESCE(i.extras, 0)
        """
    )
    with db.connect() as conn:
        assert conn.execute(sql).fetchall() == []


def test_every_winner_played_in_the_match(db):
    sql = text(
        """
        SELECT match_id FROM matches
        WHERE winner_team_id IS NOT NULL
          AND winner_team_id NOT IN (team1_id, team2_id)
        """
    )
    with db.connect() as conn:
        assert conn.execute(sql).fetchall() == []


def test_toss_decision_only_bat_or_bowl(db):
    with db.connect() as conn:
        bad = conn.execute(
            text("SELECT COUNT(*) FROM matches "
                 "WHERE toss_decision IS NOT NULL AND toss_decision NOT IN ('bat', 'bowl')")
        ).scalar()
    assert bad == 0


def test_players_have_valid_roles(db):
    with db.connect() as conn:
        roles = {
            row[0]
            for row in conn.execute(
                text("SELECT DISTINCT playing_role FROM players WHERE playing_role IS NOT NULL")
            )
        }
    assert roles <= {"Batsman", "Bowler", "All-rounder", "Wicket-keeper"}