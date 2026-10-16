USE cricbuzz_livestats;

SELECT
    full_name   AS player_name,
    runs        AS total_runs,
    batting_avg,
    centuries
FROM v_player_batting_career
WHERE format_name = 'ODI'
ORDER BY runs DESC
LIMIT 10;