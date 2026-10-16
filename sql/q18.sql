USE cricbuzz_livestats;

SELECT 'Q18' AS question, COALESCE(@q18_min_matches, 10) AS min_matches_used;

WITH bowler_match AS (
    SELECT
        w.player_id,
        i.match_id,
        SUM(w.balls_bowled)  AS balls,
        SUM(w.runs_conceded) AS runs,
        SUM(w.wickets)       AS wickets
    FROM bowling_scorecards AS w
    JOIN innings AS i ON i.innings_id = w.innings_id
    JOIN matches AS m ON m.match_id = i.match_id
    WHERE m.state = 'Complete'
      AND m.format_id IN (2, 3)
    GROUP BY w.player_id, i.match_id
)
SELECT
    p.full_name                                         AS bowler,
    COUNT(*)                                            AS matches_bowled,
    SUM(bm.balls)                                       AS total_balls,
    ROUND(SUM(bm.runs) * 6 / NULLIF(SUM(bm.balls), 0), 2) AS economy,
    SUM(bm.wickets)                                     AS total_wickets
FROM bowler_match AS bm
JOIN players AS p ON p.player_id = bm.player_id
GROUP BY bm.player_id, p.full_name
HAVING COUNT(*) >= COALESCE(@q18_min_matches, 10)
   AND SUM(bm.balls) / COUNT(*) >= 12
ORDER BY economy, total_wickets DESC;