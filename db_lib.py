import sqlite3

# for debugging purpuse
import traceback
import sys
from request_lib import TmdbRequests


# TODO: return boolean values or None to check if the queries are successful
# TODO: Remove not null constraint from backdrop_path
class Database:
    def __init__(self):
        self.con = sqlite3.connect("store.db")
        self.cur = self.con.cursor()

    def addMovie(self, movie):
        self.__init__()
        try:
            if not movie["backdrop_path"]:
                movie["backdrop_path"] = ""
            self.cur.execute(
                """INSERT INTO contents (tmdb_id, is_movie, title, `description`, backdrop_path, release_date, age_restricted, rating)
                                VALUES (:id, 1, :title, :overview, :backdrop_path, :release_date, :adult, :vote_average);""",
                movie,
            )
            self.con.commit()
        except sqlite3.Error as err:
            self.handleError(err)
        self.con.close()

    def addSeriesByTmdbId(self, tmdbId):
        self.__init__()
        req = TmdbRequests()
        series = req.getSeriesById(tmdbId)
        if not series["backdrop_path"]:
            series["backdrop_path"] = ""
        try:
            self.cur.execute(
                """INSERT INTO contents (tmdb_id, is_movie, title, `description`, backdrop_path, release_date, age_restricted, rating)
                                    VALUES (:id, 0, :name, :overview, :backdrop_path, :first_air_date, :adult, :vote_average);""",
                series,
            )
            self.con.commit()
        except sqlite3.Error as err:
            self.handleError(err)
        self.con.close()

     
    def addSeasonByTmdbIdAndNumber(self, tmdbId, number):
        self.__init__()
        try:
            req = TmdbRequests()
            season = req.getSeasonByIdAndNumber(tmdbId, number)
            season.update({ 'tmdbId': tmdbId })
            if not season['poster_path']:
              season['poster_path'] = ''
            self.cur.execute(
                """INSERT INTO seasons (tmdb_id, number, title, `description`, backdrop_path, air_date)
                    VALUES (:tmdbId, :season_number, :name, :overview, :poster_path, :air_date)""", season
            )
            self.con.commit()
        except sqlite3.Error as err:
            self.handleError(err)
        return None

    def addEpisodeByTmdbIdAndNumber(self, tmdbId, seasonNumber, number):
        self.__init__()
        req = TmdbRequests()
        episode = req.getEpisodeByIdAndNumber(tmdbId, seasonNumber, number)
        if not episode['still_path']:
            episode['still_path'] = ""
        episode.update({ "tmdbId": tmdbId, "seasonNumber": seasonNumber })
        try:
            self.cur.execute(
                """INSERT INTO episodes (tmdb_id, season_number, number, title, `description`, backdrop_path, air_date, rating)
                    VALUES (:tmdbId, :seasonNumber, :episode_number, :name, :overview, :still_path, :air_date, :vote_average)""", episode
            )
            self.con.commit()
        except sqlite3.Error as err:
            self.handleError(err)
        return None
        

    def checkIfContentExists(self, tmdbId, isMovie):
        self.__init__()
        try:
            self.cur.execute(
                """SELECT COUNT(*) FROM contents WHERE tmdb_id = :tmdbId AND is_movie = :isMovie""",
                {"tmdbId": tmdbId, "isMovie": isMovie},
            )
            return bool(self.cur.fetchone()[0])
        except sqlite3.Error as err:
            self.handleError(err)
        return None

    def checkIfSeasonExists(self, tmdbId, number):
        self.__init__()
        try:
            self.cur.execute(
                """SELECT COUNT(*) FROM seasons WHERE tmdb_id = :tmdbId AND number = :number""",
                {"tmdbId": tmdbId, "number": number},
            )
            return bool(self.cur.fetchone()[0])
        except sqlite3.Error as err:
            self.handleError(err)
        return None
   
    def checkIfEpisodeExists(self, tmdbId, seasonNumber, number):
        self.__init__()
        try:
            self.cur.execute(
                """SELECT COUNT(*) FROM episodes WHERE tmdb_id = :tmdbId AND season_number = :seasonNumber AND number = :number""",
                { "tmdbId": tmdbId, "seasonNumber": seasonNumber, "number": number },
            )
            return bool(self.cur.fetchone()[0])
        except sqlite3.Error as err:
            self.handleError(err)
        return None
    
    def removeContent(self, tmdbId):
      self.__init__()
      try:
        self.cur.execute(
          """DELETE FROM contents WHERE tmdb_id = :tmdbId""", { "tmdbId": tmdbId }
        )
        self.con.commit()
      except sqlite3.Error as err:
        self.handleError(err)
      return None
  
    def removeSeasonByIdAndNumber(self, tmdbId, number):
      self.__init__()
      try:
        self.cur.execute(
            """DELETE FROM seasons WHERE tmdb_id = :tmdbId AND number = :number""",
            {"tmdbId": tmdbId, "number": number},
        )
        self.con.commit()
      except sqlite3.Error as err:
        self.handleError(err)
      return None
    
    def removeEpisodeByIdAndNumber(self, tmdbId, seasonNumber, number):
        self.__init__()
        try:
            self.cur.execute(
                """DELETE FROM episodes WHERE tmdb_id = :tmdbId AND season_number = :seasonNumber AND number = :number""",
                { "tmdbId": tmdbId, "seasonNumber": seasonNumber, "number": number },
            )
            self.con.commit()
        except sqlite3.Error as err:
            self.handleError(err)
        return None
    
    def addLocation(self, parentId, name, description):
        self.__init__()
        try:
            if parentId:
                self.cur.execute(
                    """INSERT INTO locations (parent_id, name, description)
                        VALUES (:parentId, :name, :description)""",
                    {
                        "parentId": parentId,
                        "name": name,
                        "description": description
                    }
                )
            else:
                self.cur.execute(
                    """INSERT INTO locations (name, description)
                        VALUES (:name, :description)""",
                    {
                        "name": name,
                        "description": description
                    }
                )
            self.con.commit()
        except sqlite3.Error as err:
            self.handleError(err)
        return None
    
    def getLocationsByParentId(self, parentId):
        self.__init__()
        try:
            self.cur.execute(
                """SELECT id, `name`, `description` FROM locations
                    WHERE parent_id IS :parentId""",
                {
                    "parentId": parentId
                }
            )
            return self.cur.fetchall()
        except sqlite3.Error as err:
            self.handleError(err)
        return None
    
    def removeLocationById(self, id):
        self.__init__()
        try:
            self.cur.execute(
                """DELETE FROM locations
                    WHERE id = :id""",
                {
                    "id": id
                }
            )
            self.con.commit()
            toDelete = self.getLocationIdsForParentId(id)
            while (len(toDelete) > 0):
                for delId in toDelete:
                    self.__init__()
                    self.cur.execute(
                        """DELETE FROM locations
                            WHERE id = :id""",
                        {
                            "id": delId
                        }
                    )
                    self.con.commit()
                toDelete = self.getLocationIdsForParentId(delId)
        except sqlite3.Error as err:
            self.handleError(err)
        return None
    
    def getLocationIdsForParentId(self, parentId):
        self.__init__()
        try:
            self.cur.execute(
                """SELECT id FROM locations
                    WHERE parent_id = :parentId;""",
                {
                    "parentId": parentId
                }
            )
            return [id[0] for id in self.cur.fetchall()]
        except sqlite3.Error as err:
            self.handleError(err)
        return None
    
    def addContentsStorement(self, tmdbId, isMovie, locationId, amount = 1, recordingDate = None, notes = ''):
        self.__init__()
        try:
            self.cur.execute(
                """INSERT INTO contents_storement (tmdb_id, is_movie, location_id, amount, recording_date, notes)
                        VALUES (:tmdbId, :isMovie, :locationId, :amount, :recordingDate, :notes)""",
                {
                    "tmdbId": tmdbId,
                    "isMovie": isMovie,
                    "locationId": locationId,
                    "amount": amount,
                    "recordingDate": recordingDate,
                    "notes": notes
                }
            )
            self.con.commit()
        except sqlite3.Error as err:
            self.handleError(err)
        return None
    
    def addSeasonsStorement(self, tmdbId, seasonNumber, locationId, amount = 1, recordingDate = None, notes = ''):
        self.__init__()
        try:
            self.cur.execute(
                """INSERT INTO seasons_storement (tmdb_id, season_number, location_id, amount, recording_date, notes)
                        VALUES (:tmdbId, :seasonNumber, :locationId, :amount, :recordingDate, :notes)""",
                {
                    "tmdbId": tmdbId,
                    "seasonNumber": seasonNumber,
                    "locationId": locationId,
                    "amount": amount,
                    "recordingDate": recordingDate,
                    "notes": notes
                }
            )
            self.con.commit()
        except sqlite3.Error as err:
            self.handleError(err)
        return None
    
    def addEpisodesStorement(self, tmdbId, seasonNumber, episodeNumber, locationId, amount = 1, recordingDate = None, notes = ''):
        self.__init__()
        try:
            self.cur.execute(
                """INSERT INTO episodes_storement (tmdb_id, season_number, episode_number, location_id, amount, recording_date, notes)
                        VALUES (:tmdbId, :seasonNumber, :episodeNumber, :locationId, :amount, :recordingDate, :notes)""",
                {
                    "tmdbId": tmdbId,
                    "seasonNumber": seasonNumber,
                    "episodeNumber": episodeNumber,
                    "locationId": locationId,
                    "amount": amount,
                    "recordingDate": recordingDate,
                    "notes": notes
                }
            )
            self.con.commit()
        except sqlite3.Error as err:
            self.handleError(err)
        return None
    
    def removeContentsStorement(self, tmdbId, isMovie, locationId):
        self.__init__()
        try:
            self.cur.execute(
                """DELETE FROM contents_storement WHERE tmdb_id = :tmdbId AND is_movie = :isMovie AND location_id = :locationId""",
                {
                    "tmdbId": tmdbId,
                    "isMovie": isMovie,
                    "locationId": locationId
                }
            )
            self.con.commit()
        except sqlite3.Error as err:
            self.handleError(err)
        return None
    
    def removeSeasonsStorement(self, tmdbId, seasonNumber, locationId):
        self.__init__()
        try:
            self.cur.execute(
                """DELETE FROM seasons_storement WHERE tmdb_id = :tmdbId AND season_number = :seasonNumber AND location_id = :locationId""",
                {
                    "tmdbId": tmdbId,
                    "seasonNumber": seasonNumber,
                    "locationId": locationId
                }
            )
            self.con.commit()
        except sqlite3.Error as err:
            self.handleError(err)
        return None
    
    def removeEpisodesStorement(self, tmdbId, seasonNumber, episodeNumber, locationId):
        self.__init__()
        try:
            self.cur.execute(
                """DELETE FROM episodes_storement WHERE tmdb_id = :tmdbId AND season_number = :seasonNumber AND episode_number = :episodeNumber AND location_id = :locationId""",
                {
                    "tmdbId": tmdbId,
                    "seasonNumber": seasonNumber,
                    "episodeNumber": episodeNumber,
                    "locationId": locationId
                }
            )
            self.con.commit()
        except sqlite3.Error as err:
            self.handleError(err)
        return None
    
    def getRecordings(self):
        self.__init__()
        try:
            self.cur.execute(
                """SELECT c.title, '', '', c.description, c.release_date, c.age_restricted, c.rating, c.notes, s.notes, s.location_id FROM contents c
                    INNER JOIN
                    contents_storement s
                    ON c.tmdb_id = s.tmdb_id AND c.is_movie = s.is_movie
                    UNION ALL
                    SELECT c.title, c.number, '', c.description, c.air_date, '', c.rating, c.notes, s.notes, s.location_id FROM seasons c
                    INNER JOIN
                    seasons_storement s
                    ON c.tmdb_id = s.tmdb_id AND c.number = s.season_number
                    UNION ALL
                    SELECT e.title, e.season_number, e.number, e.description, e.air_date, '', e.rating, e.notes, s.notes, s.location_id FROM episodes e
                    INNER JOIN
                    episodes_storement s
                    ON e.tmdb_id = s.tmdb_id AND e.season_number = s.season_number AND e.number = s.episode_number;"""
            )
            return self.cur.fetchall()
        except sqlite3.Error as err:
            self.handleError(err)
        return None
    
    def getLocationById(self, id):
        self.__init__()
        try:
            self.cur.execute(
                """SELECT parent_id, name FROM locations
                    WHERE id = :id""",
                {
                    "id": id
                }
            )
            return self.cur.fetchone()
        except sqlite3.Error as err:
            self.handleError(err)
        return None
    
    def handleError(self, err):
        print("SQLite error: %s" % (" ".join(err.args)))
        print("Exception class is: ", err.__class__)
        print("SQLite traceback: ")
        exc_type, exc_value, exc_tb = sys.exc_info()
        print(traceback.format_exception(exc_type, exc_value, exc_tb))