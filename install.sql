/* Create tables */
CREATE TABLE IF NOT EXISTS contents (
    tmdb_id INTEGER NOT NULL,
    is_movie BOOLEAN NOT NULL,
    title TEXT NOT NULL DEFAULT '',
    `description` TEXT NOT NULL DEFAULT '',
    backdrop_path TEXT NOT NULL DEFAULT '',
    release_date DATE NULL DEFAULT NULL,
    age_restricted BOOLEAN NULL,
    rating REAL NULL,
    notes TEXT NOT NULL DEFAULT '',
    created_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    CHECK (is_movie IN (0, 1)),
    CHECK (age_restricted IN (0, 1)),
    PRIMARY KEY (tmdb_id, is_movie)
);

CREATE TABLE IF NOT EXISTS seasons (
    tmdb_id INTEGER NOT NULL,
    number INTEGER NOT NULL,
    title TEXT NOT NULL DEFAULT '',
    `description` TEXT NOT NULL DEFAULT '',
    backdrop_path TEXT NOT NULL DEFAULT '',
    air_date DATE NULL DEFAULT NULL,
    rating REAL NULL DEFAULT NULL,
    notes TEXT NOT NULL DEFAULT '',
    created_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tmdb_id) REFERENCES contents(tmdb_id),
    PRIMARY KEY (tmdb_id, number)
);

CREATE TABLE IF NOT EXISTS episodes (
    tmdb_id INTEGER NOT NULL,
    season_number INTEGER NOT NULL,
    number INTEGER NOT NULL,
    title TEXT NOT NULL DEFAULT '',
    `description` TEXT NOT NULL DEFAULT '',
    backdrop_path TEXT NOT NULL DEFAULT '',
    air_date DATE NULL DEFAULT NULL,
    rating REAL NULL,
    notes TEXT NOT NULL DEFAULT '',
    created_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tmdb_id, season_number) REFERENCES seasons(tmdb_id, number),
    PRIMARY KEY (tmdb_id, season_number, number)
);

CREATE TABLE IF NOT EXISTS locations (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    parent_id INTEGER NULL,
    `name` TEXT NOT NULL DEFAULT '',
    `description` TEXT NOT NULL DEFAULT '',
    created_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    CHECK (`name` <> ''),
    FOREIGN KEY (parent_id) REFERENCES locations(id) ON DELETE CASCADE
);

/* Create relations */

CREATE TABLE IF NOT EXISTS contents_storement (
    tmdb_id INTEGER NOT NULL,
    is_movie BOOLEAN NOT NULL,
    location_id INTEGER NOT NULL,
    amount INTEGER NOT NULL DEFAULT 1,
    recording_date DATE DEFAULT NULL,
    notes TEXT NOT NULL DEFAULT '',
    created_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tmdb_id, is_movie) REFERENCES contents(tmdb_id, is_movie),
    FOREIGN KEY (location_id) REFERENCES locations(id),
    PRIMARY KEY (tmdb_id, is_movie, location_id)
);

CREATE TABLE IF NOT EXISTS seasons_storement (
    tmdb_id INTEGER NOT NULL,
    season_number INTEGER NOT NULL,
    location_id INTEGER NOT NULL,
    amount INTEGER NOT NULL DEFAULT 1,
    recording_date DATE DEFAULT NULL,
    notes TEXT NOT NULL DEFAULT '',
    created_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tmdb_id, season_number) REFERENCES seasons(tmdb_id, number),
    FOREIGN KEY (location_id) REFERENCES locations(id),
    PRIMARY KEY (tmdb_id, season_number, location_id)
);

CREATE TABLE IF NOT EXISTS episodes_storement (
    tmdb_id INTEGER NOT NULL,
    season_number INTEGER NOT NULL,
    episode_number INTEGER NOT NULL,
    location_id INTEGER NOT NULL,
    amount INTEGER NOT NULL DEFAULT 1,
    recording_date DATE DEFAULT NULL,
    notes TEXT NOT NULL DEFAULT '',
    created_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tmdb_id, season_number, episode_number) REFERENCES episodes(tmdb_id, season_number, number),
    FOREIGN KEY (location_id) REFERENCES locations(id),
    PRIMARY KEY (tmdb_id, season_number, episode_number, location_id)
);

/* Create updated_on triggers */
CREATE TRIGGER IF NOT EXISTS updated_contents
AFTER UPDATE ON contents
BEGIN
   UPDATE contents SET updated_on = CURRENT_TIMESTAMP WHERE tmdb_id = NEW.tmdb_id AND is_movie = NEW.is_movie;
END;

CREATE TRIGGER IF NOT EXISTS updated_seasons
AFTER UPDATE ON seasons
BEGIN
   UPDATE seasons SET updated_on = CURRENT_TIMESTAMP WHERE tmdb_id = NEW.tmdb_id AND number = NEW.number;
END;

CREATE TRIGGER IF NOT EXISTS updated_episodes
AFTER UPDATE ON episodes
BEGIN
   UPDATE episodes SET updated_on = CURRENT_TIMESTAMP WHERE tmdb_id = NEW.tmdb_id AND season_number = NEW.season_number AND number = NEW.number;
END;

CREATE TRIGGER IF NOT EXISTS updated_locations
AFTER UPDATE ON locations
BEGIN
   UPDATE locations SET updated_on = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS updated_contents_storement
AFTER UPDATE ON contents_storement
BEGIN
   UPDATE contents_storement SET updated_on = CURRENT_TIMESTAMP WHERE tmdb_id = NEW.tmdb_id AND is_movie = NEW.is_movie AND location_id = NEW.location_id;
END;

CREATE TRIGGER IF NOT EXISTS updated_seasons_storement
AFTER UPDATE ON seasons_storement
BEGIN
   UPDATE seasons_storement SET updated_on = CURRENT_TIMESTAMP WHERE tmdb_id = NEW.tmdb_id AND number = NEW.number AND location_id = NEW.location_id;
END;

CREATE TRIGGER IF NOT EXISTS updated_episodes_storement
AFTER UPDATE ON episodes_storement
BEGIN
   UPDATE episodes_storement SET updated_on = CURRENT_TIMESTAMP WHERE tmdb_id = NEW.tmdb_id AND season_number = NEW.season_number AND number = NEW.number AND location_id = NEW.location_id;
END;

/* Make created_on read-only */
CREATE TRIGGER IF NOT EXISTS ro_contents
BEFORE UPDATE OF created_on ON contents
BEGIN
    SELECT raise(abort, 'Field "created_on" cannot be changed.');
END;

CREATE TRIGGER IF NOT EXISTS ro_seasons
BEFORE UPDATE OF created_on ON seasons
BEGIN
    SELECT raise(abort, 'Field "created_on" cannot be changed.');
END;

CREATE TRIGGER IF NOT EXISTS ro_episodes
BEFORE UPDATE OF created_on ON episodes
BEGIN
    SELECT raise(abort, 'Field "created_on" cannot be changed.');
END;

CREATE TRIGGER IF NOT EXISTS ro_locations
BEFORE UPDATE OF created_on ON locations
BEGIN
    SELECT raise(abort, 'Field "created_on" cannot be changed.');
END;

CREATE TRIGGER IF NOT EXISTS ro_contents_storement
BEFORE UPDATE OF created_on ON contents_storement
BEGIN
    SELECT raise(abort, 'Field "created_on" cannot be changed.');
END;

CREATE TRIGGER IF NOT EXISTS ro_seasons_storement
BEFORE UPDATE OF created_on ON seasons_storement
BEGIN
    SELECT raise(abort, 'Field "created_on" cannot be changed.');
END;

CREATE TRIGGER IF NOT EXISTS ro_episodes_storement
BEFORE UPDATE OF created_on ON episodes_storement
BEGIN
    SELECT raise(abort, 'Field "created_on" cannot be changed.');
END;