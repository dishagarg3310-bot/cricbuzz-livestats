USE cricbuzz_livestats;

INSERT IGNORE INTO countries (country_id, country_name)
SELECT COALESCE(MAX(country_id), 0) + 1, 'Australia' FROM countries;

INSERT INTO venues (venue_id, venue_name, city, country_id, capacity, data_source)
VALUES
  (2000000001, 'Narendra Modi Stadium', 'Ahmedabad',
   (SELECT country_id FROM countries WHERE country_name = 'India'), 132000, 'sample'),
  (2000000002, 'Melbourne Cricket Ground', 'Melbourne',
   (SELECT country_id FROM countries WHERE country_name = 'Australia'), 100024, 'sample'),
  (2000000003, 'Eden Gardens', 'Kolkata',
   (SELECT country_id FROM countries WHERE country_name = 'India'), 66000, 'sample')
ON DUPLICATE KEY UPDATE
  venue_name = VALUES(venue_name),
  city = VALUES(city),
  country_id = VALUES(country_id),
  capacity = VALUES(capacity);