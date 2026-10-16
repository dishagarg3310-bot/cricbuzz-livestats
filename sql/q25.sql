USE cricbuzz_livestats;

SELECT 'Q25' AS question,
       COALESCE(@q25_min_quarters, 6) AS min_quarters_used,
       COALESCE(@q25_min_matches, 3)  AS min_matches_per_quarter_used;

WITH player_match AS (
    SELECT
        b.player_id,
        i.match_id,
        SUM(b.runs)        AS runs,
        SUM(b.balls_faced) AS balls,
        MAKEDATE(YEAR(m.start_time), 1)
            + INTERVAL (QUARTER(m.start_time) - 1) QUARTER AS q_start
    FROM batting_scorecards AS b
    JOIN innings AS i ON i.innings_id = b.innings_id
    JOIN matches AS m ON m.match_id = i.match_id
    WHERE m.state = 'Complete'
    GROUP BY b.player_id, i.match_id, q_start
),
quarterly AS (
    SELECT
        player_id,
        q_start,
        COUNT(*)  AS matches,
        AVG(runs) AS avg_runs,
        SUM(runs) * 100 / NULLIF(SUM(balls), 0) AS strike_rate
    FROM player_match
    GROUP BY player_id, q_start
    HAVING COUNT(*) >= COALESCE(@q25_min_matches, 3)
),
eligible AS (
    SELECT player_id
    FROM quarterly
    GROUP BY player_id
    HAVING COUNT(*) >= COALESCE(@q25_min_quarters, 6)
),
trend AS (
    SELECT
        q.player_id,
        q.q_start,
        q.matches,
        q.avg_runs,
        q.strike_rate,
        LAG(q.avg_runs)    OVER w AS prev_avg,
        LAG(q.strike_rate) OVER w AS prev_sr,
        FIRST_VALUE(q.avg_runs) OVER (
            PARTITION BY q.player_id ORDER BY q.q_start
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS first_avg,
        LAST_VALUE(q.avg_runs) OVER (
            PARTITION BY q.player_id ORDER BY q.q_start
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_avg
    FROM quarterly AS q
    JOIN eligible AS e ON e.player_id = q.player_id
    WINDOW w AS (PARTITION BY q.player_id ORDER BY q.q_start)
)
SELECT
    p.full_name AS player_name,
    CONCAT(YEAR(t.q_start), '-Q', QUARTER(t.q_start)) AS quarter,
    t.matches,
    ROUND(t.avg_runs, 2)    AS avg_runs,
    ROUND(t.strike_rate, 2) AS strike_rate,
    ROUND(t.avg_runs - t.prev_avg, 2)       AS runs_change,
    ROUND(t.strike_rate - t.prev_sr, 2)     AS sr_change,
    CASE
        WHEN t.prev_avg IS NULL THEN 'first quarter'
        WHEN t.avg_runs >= t.prev_avg * 1.10 THEN 'Improving'
        WHEN t.avg_runs <= t.prev_avg * 0.90 THEN 'Declining'
        ELSE 'Stable'
    END AS quarter_trend,
    CASE
        WHEN t.last_avg >= t.first_avg * 1.10 THEN 'Career Ascending'
        WHEN t.last_avg <= t.first_avg * 0.90 THEN 'Career Declining'
        ELSE 'Career Stable'
    END AS career_phase
FROM trend AS t
JOIN players AS p ON p.player_id = t.player_id
ORDER BY p.full_name, t.q_start;