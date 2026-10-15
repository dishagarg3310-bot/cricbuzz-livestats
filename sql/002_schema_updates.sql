USE cricbuzz_livestats;

ALTER TABLE batting_scorecards
  ADD COLUMN dismissal_text VARCHAR(200) NULL,
  ADD COLUMN dismissal_type VARCHAR(20) NULL;

ALTER TABLE bowling_scorecards
  ADD COLUMN dots INT NULL;

ALTER TABLE innings
  ADD COLUMN extras INT NULL;

ALTER TABLE player_career_stats
  ADD COLUMN fours INT NOT NULL DEFAULT 0,
  ADD COLUMN sixes INT NOT NULL DEFAULT 0,
  ADD COLUMN ducks INT NOT NULL DEFAULT 0,
  ADD COLUMN maidens INT NOT NULL DEFAULT 0,
  ADD COLUMN five_wickets INT NOT NULL DEFAULT 0;

CREATE TABLE partnerships (
  partnership_id  INT AUTO_INCREMENT PRIMARY KEY,
  innings_id      INT NOT NULL,
  partnership_no  TINYINT NOT NULL,
  bat1_player_id  INT NOT NULL,
  bat2_player_id  INT NOT NULL,
  bat1_runs       INT NOT NULL DEFAULT 0,
  bat1_balls      INT NOT NULL DEFAULT 0,
  bat2_runs       INT NOT NULL DEFAULT 0,
  bat2_balls      INT NOT NULL DEFAULT 0,
  total_runs      INT NOT NULL DEFAULT 0,
  total_balls     INT NOT NULL DEFAULT 0,
  UNIQUE KEY uq_innings_partnership (innings_id, partnership_no),
  KEY idx_part_bat1 (bat1_player_id),
  KEY idx_part_bat2 (bat2_player_id),
  CONSTRAINT fk_part_innings FOREIGN KEY (innings_id) REFERENCES innings (innings_id),
  CONSTRAINT fk_part_bat1 FOREIGN KEY (bat1_player_id) REFERENCES players (player_id),
  CONSTRAINT fk_part_bat2 FOREIGN KEY (bat2_player_id) REFERENCES players (player_id)
);