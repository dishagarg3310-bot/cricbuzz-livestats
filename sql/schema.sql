-- Cricbuzz LiveStats schema (MySQL 8+). Design only: executed in Phase 8.
CREATE DATABASE IF NOT EXISTS cricbuzz_livestats
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE cricbuzz_livestats;

CREATE TABLE countries (
    country_id   INT AUTO_INCREMENT PRIMARY KEY,
    country_name VARCHAR(80) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE formats (
    format_id   TINYINT AUTO_INCREMENT PRIMARY KEY,
    format_name VARCHAR(10) NOT NULL UNIQUE      -- Test, ODI, T20I, T20
) ENGINE=InnoDB;

CREATE TABLE teams (
    team_id     INT PRIMARY KEY,                 -- Cricbuzz team id
    team_name   VARCHAR(100) NOT NULL,
    short_name  VARCHAR(20),
    country_id  INT NULL,
    data_source ENUM('api','sample') NOT NULL DEFAULT 'api',
    CONSTRAINT fk_teams_country FOREIGN KEY (country_id) REFERENCES countries(country_id)
) ENGINE=InnoDB;

CREATE TABLE venues (
    venue_id    INT PRIMARY KEY,
    venue_name  VARCHAR(150) NOT NULL,
    city        VARCHAR(80),
    country_id  INT NULL,
    capacity    INT NULL,
    data_source ENUM('api','sample') NOT NULL DEFAULT 'api',
    CONSTRAINT chk_venue_capacity CHECK (capacity IS NULL OR capacity > 0),
    CONSTRAINT fk_venues_country FOREIGN KEY (country_id) REFERENCES countries(country_id)
) ENGINE=InnoDB;

CREATE TABLE players (
    player_id     INT PRIMARY KEY,
    full_name     VARCHAR(120) NOT NULL,
    country_id    INT NULL,
    playing_role  VARCHAR(20) NULL,
    batting_style VARCHAR(30) NULL,
    bowling_style VARCHAR(40) NULL,
    data_source   ENUM('api','sample') NOT NULL DEFAULT 'api',
    CONSTRAINT chk_player_role CHECK (playing_role IS NULL OR
        playing_role IN ('Batsman','Bowler','All-rounder','Wicket-keeper')),
    CONSTRAINT fk_players_country FOREIGN KEY (country_id) REFERENCES countries(country_id)
) ENGINE=InnoDB;

CREATE TABLE series (
    series_id       INT PRIMARY KEY,
    series_name     VARCHAR(150) NOT NULL,
    host_country_id INT NULL,
    match_type      VARCHAR(20) NULL,            -- International, League, ...
    start_date      DATE NULL,
    end_date        DATE NULL,
    planned_matches INT NULL,
    data_source     ENUM('api','sample') NOT NULL DEFAULT 'api',
    CONSTRAINT chk_series_dates CHECK (start_date IS NULL OR end_date IS NULL OR end_date >= start_date),
    CONSTRAINT fk_series_country FOREIGN KEY (host_country_id) REFERENCES countries(country_id)
) ENGINE=InnoDB;

CREATE TABLE matches (
    match_id            INT PRIMARY KEY,
    series_id           INT NOT NULL,
    format_id           TINYINT NOT NULL,
    match_desc          VARCHAR(100),
    team1_id            INT NOT NULL,
    team2_id            INT NOT NULL,
    venue_id            INT NULL,
    start_time          DATETIME NULL,
    end_time            DATETIME NULL,
    state               VARCHAR(20) NULL,        -- Upcoming, In Progress, Complete
    status_text         VARCHAR(200) NULL,
    toss_winner_team_id INT NULL,
    toss_decision       ENUM('bat','bowl') NULL,
    winner_team_id      INT NULL,
    victory_margin      INT NULL,
    victory_type        ENUM('runs','wickets') NULL,
    data_source         ENUM('api','sample') NOT NULL DEFAULT 'api',
    CONSTRAINT chk_teams_differ  CHECK (team1_id <> team2_id),
    CONSTRAINT chk_winner_valid  CHECK (winner_team_id IS NULL OR winner_team_id IN (team1_id, team2_id)),
    CONSTRAINT chk_toss_valid    CHECK (toss_winner_team_id IS NULL OR toss_winner_team_id IN (team1_id, team2_id)),
    CONSTRAINT chk_margin        CHECK (victory_margin IS NULL OR victory_margin >= 0),
    CONSTRAINT fk_matches_series FOREIGN KEY (series_id) REFERENCES series(series_id),
    CONSTRAINT fk_matches_format FOREIGN KEY (format_id) REFERENCES formats(format_id),
    CONSTRAINT fk_matches_team1  FOREIGN KEY (team1_id)  REFERENCES teams(team_id),
    CONSTRAINT fk_matches_team2  FOREIGN KEY (team2_id)  REFERENCES teams(team_id),
    CONSTRAINT fk_matches_venue  FOREIGN KEY (venue_id)  REFERENCES venues(venue_id),
    CONSTRAINT fk_matches_toss   FOREIGN KEY (toss_winner_team_id) REFERENCES teams(team_id),
    CONSTRAINT fk_matches_winner FOREIGN KEY (winner_team_id)      REFERENCES teams(team_id)
) ENGINE=InnoDB;

CREATE TABLE innings (
    innings_id      INT AUTO_INCREMENT PRIMARY KEY,
    match_id        INT NOT NULL,
    innings_no      TINYINT NOT NULL,
    batting_team_id INT NOT NULL,
    bowling_team_id INT NOT NULL,
    total_runs      INT NULL,
    wickets_lost    TINYINT NULL,
    balls_bowled    INT NULL,
    UNIQUE KEY uq_innings (match_id, innings_no),
    CONSTRAINT chk_innings_teams CHECK (batting_team_id <> bowling_team_id),
    CONSTRAINT fk_innings_match   FOREIGN KEY (match_id) REFERENCES matches(match_id) ON DELETE CASCADE,
    CONSTRAINT fk_innings_batting FOREIGN KEY (batting_team_id) REFERENCES teams(team_id),
    CONSTRAINT fk_innings_bowling FOREIGN KEY (bowling_team_id) REFERENCES teams(team_id)
) ENGINE=InnoDB;

CREATE TABLE batting_scorecards (
    batting_id       INT AUTO_INCREMENT PRIMARY KEY,
    innings_id       INT NOT NULL,
    player_id        INT NOT NULL,
    batting_position TINYINT NOT NULL,
    runs             INT NOT NULL DEFAULT 0,
    balls_faced      INT NOT NULL DEFAULT 0,
    fours            INT NOT NULL DEFAULT 0,
    sixes            INT NOT NULL DEFAULT 0,
    is_not_out       BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE KEY uq_bat_player   (innings_id, player_id),
    UNIQUE KEY uq_bat_position (innings_id, batting_position),
    CONSTRAINT chk_bat_position CHECK (batting_position BETWEEN 1 AND 11),
    CONSTRAINT chk_bat_values   CHECK (runs >= 0 AND balls_faced >= 0),
    CONSTRAINT fk_bat_innings FOREIGN KEY (innings_id) REFERENCES innings(innings_id) ON DELETE CASCADE,
    CONSTRAINT fk_bat_player  FOREIGN KEY (player_id)  REFERENCES players(player_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE bowling_scorecards (
    bowling_id    INT AUTO_INCREMENT PRIMARY KEY,
    innings_id    INT NOT NULL,
    player_id     INT NOT NULL,
    balls_bowled  INT NOT NULL DEFAULT 0,
    maidens       INT NOT NULL DEFAULT 0,
    runs_conceded INT NOT NULL DEFAULT 0,
    wickets       TINYINT NOT NULL DEFAULT 0,
    UNIQUE KEY uq_bowl_player (innings_id, player_id),
    CONSTRAINT chk_bowl_values CHECK (balls_bowled >= 0 AND runs_conceded >= 0 AND wickets BETWEEN 0 AND 10),
    CONSTRAINT fk_bowl_innings FOREIGN KEY (innings_id) REFERENCES innings(innings_id) ON DELETE CASCADE,
    CONSTRAINT fk_bowl_player  FOREIGN KEY (player_id)  REFERENCES players(player_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE player_career_stats (
    player_id       INT NOT NULL,
    format_id       TINYINT NOT NULL,
    matches         INT NOT NULL DEFAULT 0,
    innings_batted  INT NOT NULL DEFAULT 0,
    not_outs        INT NOT NULL DEFAULT 0,
    runs            INT NOT NULL DEFAULT 0,
    balls_faced     INT NOT NULL DEFAULT 0,
    highest_score   INT NOT NULL DEFAULT 0,
    centuries       INT NOT NULL DEFAULT 0,
    fifties         INT NOT NULL DEFAULT 0,
    balls_bowled    INT NOT NULL DEFAULT 0,
    runs_conceded   INT NOT NULL DEFAULT 0,
    wickets         INT NOT NULL DEFAULT 0,
    catches         INT NOT NULL DEFAULT 0,
    stumpings       INT NOT NULL DEFAULT 0,
    data_source     ENUM('api','sample') NOT NULL DEFAULT 'api',
    PRIMARY KEY (player_id, format_id),
    CONSTRAINT chk_career_values CHECK (matches >= 0 AND runs >= 0 AND wickets >= 0),
    CONSTRAINT fk_career_player FOREIGN KEY (player_id) REFERENCES players(player_id) ON DELETE CASCADE,
    CONSTRAINT fk_career_format FOREIGN KEY (format_id) REFERENCES formats(format_id)
) ENGINE=InnoDB;

CREATE TABLE api_call_log (
    log_id             INT AUTO_INCREMENT PRIMARY KEY,
    endpoint           VARCHAR(200) NOT NULL,
    called_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status_code        SMALLINT NULL,
    requests_remaining INT NULL
) ENGINE=InnoDB;

-- Extra indexes (foreign-key columns are indexed automatically)
CREATE INDEX idx_matches_start        ON matches(start_time);
CREATE INDEX idx_matches_state_start  ON matches(state, start_time);
CREATE INDEX idx_players_role         ON players(playing_role);
CREATE INDEX idx_career_format_runs   ON player_career_stats(format_id, runs);
CREATE INDEX idx_series_start         ON series(start_date);