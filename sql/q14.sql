USE cricbuzz_livestats;

WITH bowler_match AS (
    SELECT
        w.player_id,
        i.match_id,
        m.venue_id,
        SUM(w.balls_bowled)   AS balls,
        SUM(w.runs_conceded)  AS runs,
        SUM(w.wickets)        AS wickets
    FROM bowling_scorecards AS w
    JOIN innings AS i
        ON i.innings_id = w.innings_id
    JOIN matches AS m
        ON m.match_id = i.match_id
    GROUP BY w.player_id, i.match_id, m.venue_id
    HAVING SUM(w.balls_bowled) >= 24
)
SELECT
    p.full_name                          AS bowler,
    v.venue_name,
    v.city,
    COUNT(*)                             AS matches_played,
    ROUND(AVG(bm.runs * 6 / bm.balls), 2) AS avg_economy,
    SUM(bm.wickets)                      AS total_wickets
FROM bowler_match AS bm
JOIN players AS p
    ON p.player_id = bm.player_id
JOIN venues AS v
    ON v.venue_id = bm.venue_id
GROUP BY bm.player_id, p.full_name, bm.venue_id, v.venue_name, v.city
HAVING COUNT(*) >= COALESCE(@min_matches, 3)
ORDER BY avg_economy, total_wickets DESC;