USE cricbuzz_livestats;

SELECT
    p.full_name   AS player_name,
    f.format_name AS format,
    s.runs        AS total_runs,
    s.wickets     AS total_wickets
FROM player_career_stats AS s
JOIN players AS p
    ON p.player_id = s.player_id
JOIN formats AS f
    ON f.format_id = s.format_id
WHERE p.playing_role = 'All-rounder'
  AND s.runs    > 1000
  AND s.wickets > 50
ORDER BY s.runs DESC, p.full_name;