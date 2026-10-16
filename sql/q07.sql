USE cricbuzz_livestats;

SELECT
    f.format_name      AS format,
    MAX(s.highest_score) AS highest_score
FROM player_career_stats AS s
JOIN formats AS f
    ON f.format_id = s.format_id
WHERE f.format_name IN ('Test', 'ODI', 'T20')
GROUP BY f.format_id, f.format_name
ORDER BY f.format_id;