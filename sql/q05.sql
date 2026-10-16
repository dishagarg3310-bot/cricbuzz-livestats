USE cricbuzz_livestats;

SELECT
    t.team_name,
    COUNT(m.match_id) AS total_wins
FROM teams AS t
LEFT JOIN matches AS m
    ON m.winner_team_id = t.team_id
GROUP BY t.team_id, t.team_name
ORDER BY total_wins DESC, t.team_name;