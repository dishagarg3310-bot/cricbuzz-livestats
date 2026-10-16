USE cricbuzz_livestats;

SELECT
    m.match_desc,
    t1.team_name  AS team1,
    t2.team_name  AS team2,
    v.venue_name,
    v.city,
    m.start_time  AS match_date
FROM matches AS m
JOIN teams AS t1
    ON t1.team_id = m.team1_id
JOIN teams AS t2
    ON t2.team_id = m.team2_id
LEFT JOIN venues AS v
    ON v.venue_id = m.venue_id
WHERE m.state = 'Complete'
  AND m.start_time >= DATE_SUB(UTC_TIMESTAMP(), INTERVAL 30 DAY)
  AND m.start_time <= UTC_TIMESTAMP()
ORDER BY m.start_time DESC;