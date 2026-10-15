USE cricbuzz_livestats;

CREATE OR REPLACE VIEW v_player_batting_career AS
SELECT
    p.player_id,
    p.full_name,
    f.format_name,
    s.matches,
    s.innings_batted,
    s.not_outs,
    s.runs,
    s.balls_faced,
    s.highest_score,
    s.centuries,
    s.fifties,
    ROUND(s.runs / NULLIF(s.innings_batted - s.not_outs, 0), 2) AS batting_avg,
    ROUND(s.runs * 100 / NULLIF(s.balls_faced, 0), 2) AS strike_rate
FROM player_career_stats s
JOIN players p ON p.player_id = s.player_id
JOIN formats f ON f.format_id = s.format_id;

CREATE OR REPLACE VIEW v_player_bowling_career AS
SELECT
    p.player_id,
    p.full_name,
    f.format_name,
    s.matches,
    s.balls_bowled,
    s.runs_conceded,
    s.wickets,
    ROUND(s.runs_conceded * 6 / NULLIF(s.balls_bowled, 0), 2) AS economy,
    ROUND(s.runs_conceded / NULLIF(s.wickets, 0), 2) AS bowling_avg
FROM player_career_stats s
JOIN players p ON p.player_id = s.player_id
JOIN formats f ON f.format_id = s.format_id;

CREATE OR REPLACE VIEW v_match_summary AS
SELECT
    m.match_id,
    m.match_desc,
    f.format_name,
    m.start_time,
    m.state,
    m.status_text,
    v.venue_name,
    v.city,
    v.capacity
FROM matches m
JOIN formats f ON f.format_id = m.format_id
LEFT JOIN venues v ON v.venue_id = m.venue_id;