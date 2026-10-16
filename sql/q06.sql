USE cricbuzz_livestats;

SELECT
    COALESCE(playing_role, 'Unknown') AS playing_role,
    COUNT(*) AS player_count
FROM players
GROUP BY COALESCE(playing_role, 'Unknown')
ORDER BY player_count DESC, playing_role;