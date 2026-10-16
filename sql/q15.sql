USE cricbuzz_livestats;

WITH close_matches AS (
    SELECT match_id, winner_team_id
    FROM matches
    WHERE state = 'Complete'
      AND winner_team_id IS NOT NULL
      AND (
            (victory_type = 'runs'    AND victory_margin < 50)
         OR (victory_type = 'wickets' AND victory_margin < 5)
          )
),
player_match AS (
    SELECT
        b.player_id,
        cm.match_id,
        SUM(b.runs) AS runs,
        MAX(i.batting_team_id = cm.winner_team_id) AS team_won
    FROM batting_scorecards AS b
    JOIN innings AS i
        ON i.innings_id = b.innings_id
    JOIN close_matches AS cm
        ON cm.match_id = i.match_id
    GROUP BY b.player_id, cm.match_id
)
SELECT
    p.full_name                  AS player_name,
    ROUND(AVG(pm.runs), 2)       AS avg_runs,
    COUNT(*)                     AS close_matches_played,
    SUM(pm.team_won)             AS close_matches_won
FROM player_match AS pm
JOIN players AS p
    ON p.player_id = pm.player_id
GROUP BY pm.player_id, p.full_name
ORDER BY avg_runs DESC, close_matches_won DESC, p.full_name;