# Create table for storing NBA players names, webpages(ESPN), ESPN IDs

DROP TABLE IF EXISTS players_site;
#@_CREATE_TABLE_
CREATE TABLE players_site
(
  player_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (player_id),
  espn_id INT UNSIGNED NOT NULL,
  last_name VARCHAR(30) NOT NULL,
  first_name VARCHAR(30) NOT NULL,
  pbp_name VARCHAR(50) NOT NULL,
  espn_web_page VARCHAR(150) NOT NULL
);
#@_CREATE_TABLE_
