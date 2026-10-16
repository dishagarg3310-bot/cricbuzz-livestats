USE cricbuzz_livestats;

SELECT 'Q23' AS question, COALESCE(@q23_min_innings, 3) AS min_innings_used;

WITH recent AS (
    SELECT
        b.player_id,
        b.runs,
        b.balls_faced,
        ROW_NUMBER() OVER (
            PARTITION BY b.player_id
            ORDER BY m.start_time DESC, i.innings_no DESC
        ) AS rn
    FROM batting_scorecards AS b
    JOIN innings AS i ON i.innings_id = b.innings_id
    JOIN matches AS m ON m.match_id = i.match_id
    WHERE m.state = 'Complete'
),
last10 AS (
    SELECT * FROM recent WHERE rn <= 10
),
summary AS (
    SELECT
        player_id,
        COUNT(*) AS innings_used,
        ROUND(AVG(CASE WHEN rn <= 5 THEN runs END), 2) AS avg_runs_last5,
        ROUND(AVG(runs), 2) AS avg_runs_last10,
        ROUND(SUM(CASE WHEN rn <= 5 THEN runs END) * 100
              / NULLIF(SUM(CASE WHEN rn <= 5 THEN balls_faced END), 0), 2) AS sr_last5,
        ROUND(SUM(runs) * 100 / NULLIF(SUM(balls_faced), 0), 2) AS sr_last10,
        SUM(runs >= 50) AS scores_50_plus,
        ROUND(STDDEV_SAMP(runs), 2) AS consistency_sd
    FROM last10
    GROUP BY player_id
)
SELECT
    p.full_name AS player_name,
    s.innings_used,
    s.avg_runs_last5,
    s.avg_runs_last10,
    s.sr_last5,
    s.sr_last10,
    ROUND(s.sr_last5 - s.sr_last10, 2) AS sr_trend,
    s.scores_50_plus,
    s.consistency_sd,
    CASE
        WHEN s.avg_runs_last5 >= 50 AND s.avg_runs_last5 >= s.avg_runs_last10 THEN 'Excellent Form'
        WHEN s.avg_runs_last5 >= 35 THEN 'Good Form'
        WHEN s.avg_runs_last5 >= 20 THEN 'Average Form'
        ELSE 'Poor Form'
    END AS form_category
FROM summary AS s
JOIN players AS p ON p.player_id = s.player_id
WHERE s.innings_used >= COALESCE(@q23_min_innings, 3)
ORDER BY s.avg_runs_last5 DESC, p.full_name;