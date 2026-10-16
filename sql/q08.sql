USE cricbuzz_livestats;

SELECT
    s.series_name,
    c.country_name AS host_country,
    s.match_type,
    s.start_date,
    s.planned_matches
FROM series AS s
LEFT JOIN countries AS c
    ON c.country_id = s.host_country_id
WHERE s.start_date >= '2024-01-01'
  AND s.start_date <  '2025-01-01'
ORDER BY s.start_date;