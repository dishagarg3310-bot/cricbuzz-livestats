USE cricbuzz_livestats;

SELECT 'Q19' AS question, COALESCE(@q19_min_innings, 3) AS min_innings_used;

WITH innings_rows AS (
    SELECT b.player_id, b.runs
    FROM batting_scorecards AS b
    JOIN innings AS i ON i.innings_id = b.innings_id
    JOIN matches AS m ON m.match_id = i.match_id
    WHERE m.state = 'Complete'
      AND m.start_time >= '2022-01-01'
      AND b.balls_faced >= 10
)
SELECT
    p.full_name                       AS batsman,
    COUNT(*)                          AS innings,
    ROUND(AVG(r.runs), 2)             AS avg_runs,
    ROUND(STDDEV_SAMP(r.runs), 2)     AS stddev_runs
FROM innings_rows AS r
JOIN players AS p ON p.player_id = r.player_id
GROUP BY r.player_id, p.full_name
HAVING COUNT(*) >= COALESCE(@q19_min_innings, 3)
ORDER BY stddev_runs ASC, avg_runs DESC;