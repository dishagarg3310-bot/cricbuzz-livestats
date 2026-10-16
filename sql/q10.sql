USE cricbuzz_livestats;

SELECT
    m.match_desc,
    t1.team_name AS team1,
    t2.team_name AS team2,
    w.team_name  AS winning_team,
    m.victory_margin,
    m.victory_type,
    v.venue_name
FROM matches AS m
JOIN teams AS t1
    ON t1.team_id = m.team1_id
JOIN teams AS t2
    ON t2.team_id = m.team2_id
LEFT JOIN teams AS w
    ON w.team_id = m.winner_team_id
LEFT JOIN venues AS v
    ON v.venue_id = m.venue_id
WHERE m.state = 'Complete'
ORDER BY m.start_time DESC
LIMIT 20;