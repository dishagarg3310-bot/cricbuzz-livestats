USE cricbuzz_livestats;

SELECT 'Q22 part A: head-to-head' AS question, COALESCE(@q22_min_matches, 5) AS min_matches_used;

WITH pair_matches AS (
    SELECT
        m.match_id,
        LEAST(m.team1_id, m.team2_id)    AS team_a,
        GREATEST(m.team1_id, m.team2_id) AS team_b,
        m.winner_team_id,
        m.victory_margin,
        m.victory_type
    FROM matches AS m
    WHERE m.state = 'Complete'
      AND m.start_time >= DATE_SUB(UTC_TIMESTAMP(), INTERVAL 3 YEAR)
)
SELECT
    ta.team_name AS team_a,
    tb.team_name AS team_b,
    COUNT(*)     AS matches,
    SUM(pm.winner_team_id = pm.team_a) AS wins_a,
    SUM(pm.winner_team_id = pm.team_b) AS wins_b,
    ROUND(100 * SUM(pm.winner_team_id = pm.team_a) / COUNT(*), 1) AS win_pct_a,
    ROUND(100 * SUM(pm.winner_team_id = pm.team_b) / COUNT(*), 1) AS win_pct_b,
    ROUND(AVG(CASE WHEN pm.winner_team_id = pm.team_a AND pm.victory_type = 'runs'    THEN pm.victory_margin END), 1) AS a_avg_win_runs,
    ROUND(AVG(CASE WHEN pm.winner_team_id = pm.team_a AND pm.victory_type = 'wickets' THEN pm.victory_margin END), 1) AS a_avg_win_wkts,
    ROUND(AVG(CASE WHEN pm.winner_team_id = pm.team_b AND pm.victory_type = 'runs'    THEN pm.victory_margin END), 1) AS b_avg_win_runs,
    ROUND(AVG(CASE WHEN pm.winner_team_id = pm.team_b AND pm.victory_type = 'wickets' THEN pm.victory_margin END), 1) AS b_avg_win_wkts
FROM pair_matches AS pm
JOIN teams AS ta ON ta.team_id = pm.team_a
JOIN teams AS tb ON tb.team_id = pm.team_b
GROUP BY pm.team_a, pm.team_b, ta.team_name, tb.team_name
HAVING COUNT(*) >= COALESCE(@q22_min_matches, 5)
ORDER BY matches DESC;

SELECT 'Q22 part B: batting first vs bowling first by venue' AS question;

WITH pair_matches AS (
    SELECT
        m.match_id,
        LEAST(m.team1_id, m.team2_id)    AS team_a,
        GREATEST(m.team1_id, m.team2_id) AS team_b,
        m.venue_id,
        m.winner_team_id,
        i1.batting_team_id AS first_bat_team_id
    FROM matches AS m
    JOIN innings AS i1
        ON i1.match_id = m.match_id AND i1.innings_no = 1
    WHERE m.state = 'Complete'
      AND m.start_time >= DATE_SUB(UTC_TIMESTAMP(), INTERVAL 3 YEAR)
),
eligible AS (
    SELECT team_a, team_b
    FROM pair_matches
    GROUP BY team_a, team_b
    HAVING COUNT(*) >= COALESCE(@q22_min_matches, 5)
)
SELECT
    ta.team_name AS team_a,
    tb.team_name AS team_b,
    v.venue_name,
    COUNT(*) AS matches,
    SUM(pm.winner_team_id = pm.first_bat_team_id) AS batting_first_wins,
    SUM(pm.winner_team_id IS NOT NULL AND pm.winner_team_id <> pm.first_bat_team_id) AS bowling_first_wins
FROM pair_matches AS pm
JOIN eligible AS e ON e.team_a = pm.team_a AND e.team_b = pm.team_b
JOIN teams AS ta ON ta.team_id = pm.team_a
JOIN teams AS tb ON tb.team_id = pm.team_b
LEFT JOIN venues AS v ON v.venue_id = pm.venue_id
GROUP BY pm.team_a, pm.team_b, ta.team_name, tb.team_name, pm.venue_id, v.venue_name
ORDER BY ta.team_name, matches DESC, v.venue_name;