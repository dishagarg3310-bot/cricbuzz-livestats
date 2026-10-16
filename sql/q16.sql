USE cricbuzz_livestats;

WITH player_match AS (
    SELECT
        b.player_id,
        i.match_id,
        YEAR(m.start_time)  AS yr,
        SUM(b.runs)         AS runs,
        SUM(b.balls_faced)  AS balls
    FROM batting_scorecards AS b
    JOIN innings AS i
        ON i.innings_id = b.innings_id
    JOIN matches AS m
        ON m.match_id = i.match_id
    WHERE m.state = 'Complete'
      AND m.start_time >= '2020-01-01'
    GROUP BY b.player_id, i.match_id, YEAR(m.start_time)
)
SELECT
    p.full_name                                        AS player_name,
    pm.yr                                              AS year,
    COUNT(*)                                           AS matches_played,
    ROUND(AVG(pm.runs), 2)                             AS avg_runs_per_match,
    ROUND(AVG(pm.runs * 100 / NULLIF(pm.balls, 0)), 2) AS avg_strike_rate
FROM player_match AS pm
JOIN players AS p
    ON p.player_id = pm.player_id
GROUP BY pm.player_id, p.full_name, pm.yr
HAVING COUNT(*) >= COALESCE(@min_matches_year, 5)
ORDER BY pm.yr, avg_runs_per_match DESC, p.full_name;