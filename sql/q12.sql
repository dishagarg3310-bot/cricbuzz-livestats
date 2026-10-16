USE cricbuzz_livestats;

WITH team_matches AS (
    SELECT m.match_id, m.team1_id AS team_id,
           m.winner_team_id, v.country_id AS venue_country_id
    FROM matches AS m
    LEFT JOIN venues AS v ON v.venue_id = m.venue_id
    WHERE m.state = 'Complete'
    UNION ALL
    SELECT m.match_id, m.team2_id,
           m.winner_team_id, v.country_id
    FROM matches AS m
    LEFT JOIN venues AS v ON v.venue_id = m.venue_id
    WHERE m.state = 'Complete'
)
SELECT
    t.team_name,
    SUM(tm.venue_country_id = t.country_id)                      AS home_matches,
    SUM(tm.venue_country_id = t.country_id
        AND tm.winner_team_id = t.team_id)                       AS home_wins,
    SUM(tm.venue_country_id <> t.country_id)                     AS away_matches,
    SUM(tm.venue_country_id <> t.country_id
        AND tm.winner_team_id = t.team_id)                       AS away_wins
FROM team_matches AS tm
JOIN teams AS t
    ON t.team_id = tm.team_id
GROUP BY t.team_id, t.team_name
ORDER BY home_wins + away_wins DESC, t.team_name;