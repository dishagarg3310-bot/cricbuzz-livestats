USE cricbuzz_livestats;

SELECT 'Q20' AS question, COALESCE(@q20_min_matches, 20) AS min_matches_used;

SELECT
    p.full_name AS player_name,
    SUM(CASE WHEN f.format_name = 'Test' THEN s.matches END) AS test_matches,
    SUM(CASE WHEN f.format_name = 'ODI'  THEN s.matches END) AS odi_matches,
    SUM(CASE WHEN f.format_name = 'T20'  THEN s.matches END) AS t20_matches,
    ROUND(SUM(CASE WHEN f.format_name = 'Test' THEN s.runs END)
        / NULLIF(SUM(CASE WHEN f.format_name = 'Test' THEN s.innings_batted - s.not_outs END), 0), 2) AS test_avg,
    ROUND(SUM(CASE WHEN f.format_name = 'ODI' THEN s.runs END)
        / NULLIF(SUM(CASE WHEN f.format_name = 'ODI' THEN s.innings_batted - s.not_outs END), 0), 2) AS odi_avg,
    ROUND(SUM(CASE WHEN f.format_name = 'T20' THEN s.runs END)
        / NULLIF(SUM(CASE WHEN f.format_name = 'T20' THEN s.innings_batted - s.not_outs END), 0), 2) AS t20_avg
FROM player_career_stats AS s
JOIN players AS p ON p.player_id = s.player_id
JOIN formats AS f ON f.format_id = s.format_id
WHERE f.format_name IN ('Test', 'ODI', 'T20')
GROUP BY p.player_id, p.full_name
HAVING SUM(s.matches) >= COALESCE(@q20_min_matches, 20)
ORDER BY SUM(s.matches) DESC, p.full_name;