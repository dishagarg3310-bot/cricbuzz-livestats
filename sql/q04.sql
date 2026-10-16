USE cricbuzz_livestats;

SELECT
    v.venue_name,
    v.city,
    c.country_name AS country,
    v.capacity
FROM venues AS v
LEFT JOIN countries AS c
    ON c.country_id = v.country_id
WHERE v.capacity > 50000
ORDER BY v.capacity DESC;