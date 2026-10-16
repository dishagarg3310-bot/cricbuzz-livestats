USE cricbuzz_livestats;

UPDATE teams AS t
JOIN countries AS c
    ON c.country_name = t.team_name
SET t.country_id = c.country_id;

SELECT t.team_name, c.country_name
FROM teams AS t
LEFT JOIN countries AS c ON c.country_id = t.country_id;