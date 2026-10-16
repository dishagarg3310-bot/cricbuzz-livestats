USE cricbuzz_livestats;

SELECT
    p.full_name AS player_name,
    SUM(CASE WHEN f.format_name = 'Test' THEN s.runs END) AS test_runs,
    SUM(CASE WHEN f.format_name = 'ODI'  THEN s.runs END) AS odi_runs,
    SUM(CASE WHEN f.format_name = 'T20'  THEN s.runs END) AS t20_runs,
    ROUND(
        SUM(s.runs) / NULLIF(SUM(s.innings_batted - s.not_outs), 0),
        2
    ) AS overall_batting_avg
FROM player_career_stats AS s
JOIN players AS p
    ON p.player_id = s.player_id
JOIN formats AS f
    ON f.format_id = s.format_id
WHERE f.format_name IN ('Test', 'ODI', 'T20')
GROUP BY p.player_id, p.full_name
HAVING COUNT(DISTINCT f.format_id) >= 2
ORDER BY SUM(s.runs) DESC, p.full_name;