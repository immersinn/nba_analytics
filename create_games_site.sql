# Create table for storing NBA info: id, date, MDB _id info for components

DROP TABLE IF EXISTS games_mdb_ref;
#@_CREATE_TABLE_
CREATE TABLE games_mdb_ref
(
  game_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (game_id),
  espn_gid INT UNSIGNED NOT NULL,
  game_date DATE NOT NULL,
  pbp_mdb_id VARCHAR(24) NOT NULL,
  box_mdb_id VARCHAR(24) NOT NULL,
  ext_mdb_id VARCHAR(24) NOT NULL,
  season_type VARCHAR(7) NOT NULL,
);
#@_CREATE_TABLE_
