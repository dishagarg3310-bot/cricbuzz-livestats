USE cricbuzz_livestats;

SELECT
    p1.full_name      AS batsman_1,
    p2.full_name      AS batsman_2,
    pt.total_runs     AS partnership_runs,
    m.match_id,
    m.match_desc,
    i.innings_no,
    t.team_name       AS batting_team
FROM partnerships AS pt
JOIN batting_scorecards AS b1
    ON b1.innings_id = pt.innings_id
   AND b1.player_id  = pt.bat1_player_id
JOIN batting_scorecards AS b2
    ON b2.innings_id = pt.innings_id
   AND b2.player_id  = pt.bat2_player_id
JOIN players AS p1
    ON p1.player_id = pt.bat1_player_id
JOIN players AS p2
    ON p2.player_id = pt.bat2_player_id
JOIN innings AS i
    ON i.innings_id = pt.innings_id
JOIN matches AS m
    ON m.match_id = i.match_id
JOIN teams AS t
    ON t.team_id = i.batting_team_id
WHERE pt.total_runs >= 100
  AND ABS(b1.batting_position - b2.batting_position) = 1
ORDER BY pt.total_runs DESC, m.start_time;