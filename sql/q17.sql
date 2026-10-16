USE cricbuzz_livestats;

SELECT 'Q17' AS question;

SELECT
    IF(GROUPING(m.toss_decision) = 1, 'overall', m.toss_decision) AS toss_decision,
    COUNT(*) AS matches,
    SUM(m.toss_winner_team_id = m.winner_team_id) AS toss_winner_won,
    ROUND(100 * SUM(m.toss_winner_team_id = m.winner_team_id) / COUNT(*), 1) AS win_pct
FROM matches AS m
WHERE m.state = 'Complete'
  AND m.toss_winner_team_id IS NOT NULL
  AND m.winner_team_id IS NOT NULL
  AND m.toss_decision IS NOT NULL
GROUP BY m.toss_decision WITH ROLLUP;

SELECT COUNT(*) AS complete_matches, SUM(toss_decision IS NULL) AS toss_missing
FROM matches
WHERE state = 'Complete';