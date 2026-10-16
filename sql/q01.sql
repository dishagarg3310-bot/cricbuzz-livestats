USE cricbuzz_livestats;

SELECT
    p.full_name,
    p.playing_role,
    p.batting_style,
    p.bowling_style
FROM players AS p
JOIN countries AS c
    ON c.country_id = p.country_id
WHERE c.country_name = 'India'
ORDER BY p.full_name;