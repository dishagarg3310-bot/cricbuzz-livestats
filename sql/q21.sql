USE cricbuzz_livestats;

SELECT 'Q21' AS question;

WITH bat_stats AS (
    SELECT m.format_id, b.player_id,
           SUM(b.runs) AS runs,
           SUM(b.balls_faced) AS balls,
           SUM(b.dismissal_type <> 'not_out') AS outs
    FROM batting_scorecards AS b
    JOIN innings AS i ON i.innings_id = b.innings_id
    JOIN matches AS m ON m.match_id = i.match_id
    WHERE m.state = 'Complete'
    GROUP BY m.format_id, b.player_id
),
bowl_stats AS (
    SELECT m.format_id, w.player_id,
           SUM(w.wickets) AS wickets,
           SUM(w.runs_conceded) AS runs,
           SUM(w.balls_bowled) AS balls
    FROM bowling_scorecards AS w
    JOIN innings AS i ON i.innings_id = w.innings_id
    JOIN matches AS m ON m.match_id = i.match_id
    WHERE m.state = 'Complete'
    GROUP BY m.format_id, w.player_id
),
fielding_raw AS (
    SELECT m.format_id, b.dismissal_type,
           TRIM(CASE b.dismissal_type
                  WHEN 'caught' THEN SUBSTRING(b.dismissal_text, 3, LOCATE(' b ', b.dismissal_text) - 3)
                  WHEN 'stumped' THEN SUBSTRING(b.dismissal_text, 4, LOCATE(' b ', b.dismissal_text) - 4)
                  WHEN 'caught_and_bowled' THEN SUBSTRING(b.dismissal_text, LOCATE(' b ', b.dismissal_text) + 3)
                END) AS fielder_name
    FROM batting_scorecards AS b
    JOIN innings AS i ON i.innings_id = b.innings_id
    JOIN matches AS m ON m.match_id = i.match_id
    WHERE m.state = 'Complete'
      AND b.dismissal_type IN ('caught', 'stumped', 'caught_and_bowled')
),
field_stats AS (
    SELECT fr.format_id, p.player_id,
           SUM(fr.dismissal_type IN ('caught', 'caught_and_bowled')) AS catches,
           SUM(fr.dismissal_type = 'stumped') AS stumpings
    FROM fielding_raw AS fr
    JOIN players AS p ON p.full_name = fr.fielder_name
    GROUP BY fr.format_id, p.player_id
),
roster AS (
    SELECT format_id, player_id FROM bat_stats
    UNION
    SELECT format_id, player_id FROM bowl_stats
    UNION
    SELECT format_id, player_id FROM field_stats
),
scored AS (
    SELECT
        r.format_id,
        r.player_id,
        ROUND(COALESCE(bt.runs * 0.01, 0)
            + COALESCE(bt.runs / NULLIF(bt.outs, 0) * 0.5, 0)
            + COALESCE(bt.runs * 100 / NULLIF(bt.balls, 0) * 0.3, 0), 2) AS batting_points,
        ROUND(COALESCE(bw.wickets * 2, 0)
            + COALESCE((50 - bw.runs / NULLIF(bw.wickets, 0)) * 0.5, 0)
            + COALESCE((6 - bw.runs * 6 / NULLIF(bw.balls, 0)) * 2, 0), 2) AS bowling_points,
        COALESCE(fs.catches * 3, 0) + COALESCE(fs.stumpings * 5, 0) AS fielding_points
    FROM roster AS r
    LEFT JOIN bat_stats   AS bt ON bt.format_id = r.format_id AND bt.player_id = r.player_id
    LEFT JOIN bowl_stats  AS bw ON bw.format_id = r.format_id AND bw.player_id = r.player_id
    LEFT JOIN field_stats AS fs ON fs.format_id = r.format_id AND fs.player_id = r.player_id
),
ranked AS (
    SELECT
        sc.format_id,
        sc.player_id,
        sc.batting_points,
        sc.bowling_points,
        sc.fielding_points,
        sc.batting_points + sc.bowling_points + sc.fielding_points AS total_points,
        RANK() OVER (
            PARTITION BY sc.format_id
            ORDER BY sc.batting_points + sc.bowling_points + sc.fielding_points DESC
        ) AS rnk
    FROM scored AS sc
)
SELECT
    f.format_name,
    rk.rnk,
    p.full_name AS player_name,
    rk.batting_points,
    rk.bowling_points,
    rk.fielding_points,
    ROUND(rk.total_points, 2) AS total_points
FROM ranked AS rk
JOIN players AS p ON p.player_id = rk.player_id
JOIN formats AS f ON f.format_id = rk.format_id
WHERE rk.rnk <= 5
ORDER BY f.format_id, rk.rnk, p.full_name;