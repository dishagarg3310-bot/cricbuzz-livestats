USE cricbuzz_livestats;

SELECT 'Q24' AS question, COALESCE(@q24_min_partnerships, 5) AS min_partnerships_used;

WITH pairs AS (
    SELECT
        LEAST(pt.bat1_player_id, pt.bat2_player_id)    AS player_1,
        GREATEST(pt.bat1_player_id, pt.bat2_player_id) AS player_2,
        pt.total_runs
    FROM partnerships AS pt
    JOIN batting_scorecards AS b1
        ON b1.innings_id = pt.innings_id AND b1.player_id = pt.bat1_player_id
    JOIN batting_scorecards AS b2
        ON b2.innings_id = pt.innings_id AND b2.player_id = pt.bat2_player_id
    WHERE ABS(b1.batting_position - b2.batting_position) = 1
),
agg AS (
    SELECT
        player_1,
        player_2,
        COUNT(*)                                      AS partnerships,
        ROUND(AVG(total_runs), 1)                     AS avg_runs,
        SUM(total_runs > 50)                          AS over_50,
        MAX(total_runs)                               AS highest,
        ROUND(100 * SUM(total_runs > 50) / COUNT(*), 1) AS success_rate_pct
    FROM pairs
    GROUP BY player_1, player_2
    HAVING COUNT(*) >= COALESCE(@q24_min_partnerships, 5)
)
SELECT
    RANK() OVER (ORDER BY a.success_rate_pct DESC, a.avg_runs DESC) AS rnk,
    p1.full_name AS player_1,
    p2.full_name AS player_2,
    a.partnerships,
    a.avg_runs,
    a.over_50,
    a.highest,
    a.success_rate_pct
FROM agg AS a
JOIN players AS p1 ON p1.player_id = a.player_1
JOIN players AS p2 ON p2.player_id = a.player_2
ORDER BY rnk, a.avg_runs DESC;