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
            print("SQLite error: %s" % (" ".join(err.args)))
            print("Exception class is: ", err.__class__)
            print("SQLite traceback: ")
            exc_type, exc_value, exc_tb = sys.exc_info()
            print(traceback.format_exception(exc_type, exc_value, exc_tb))
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
            print("SQLite error: %s" % (" ".join(err.args)))
            print("Exception class is: ", err.__class__)
            print("SQLite traceback: ")
            exc_type, exc_value, exc_tb = sys.exc_info()
            print(traceback.format_exception(exc_type, exc_value, exc_tb))
        self.con.close()

     
    def addSeasonByTmdbIdAndNumber(self, tmdbId, number):
        self.__init__()
        try:
            req = TmdbRequests()
            season = req.getSeasonByIdAndNumber(tmdbId, number)
            season.update({ 'tmdbId': tmdbId })
            self.cur.execute(
                """INSERT INTO seasons (tmdb_id, number, title, `description`, backdrop_path, air_date)
                    VALUES (:tmdbId, :season_number, :name, :overview, :poster_path, :air_date)""", season
            )
        except sqlite3.Error as err:
            print("SQLite error: %s" % (" ".join(err.args)))
            print("Exception class is: ", err.__class__)
            print("SQLite traceback: ")
            exc_type, exc_value, exc_tb = sys.exc_info()
            print(traceback.format_exception(exc_type, exc_value, exc_tb))
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
                """INSERT INTO episodes (tmdb_id, season_numbmer, number, title, `description`, backdrop_path, air_date, rating)
                    VALUES (:tmdbId, :seasonNumber, :episode_number, :name, :overview, :still_path, :air_date, :vote_average)""", episode
            )
        except sqlite3.Error as err:
            print("SQLite error: %s" % (" ".join(err.args)))
            print("Exception class is: ", err.__class__)
            print("SQLite traceback: ")
            exc_type, exc_value, exc_tb = sys.exc_info()
            print(traceback.format_exception(exc_type, exc_value, exc_tb))
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
            print("SQLite error: %s" % (" ".join(err.args)))
            print("Exception class is: ", err.__class__)
            print("SQLite traceback: ")
            exc_type, exc_value, exc_tb = sys.exc_info()
            print(traceback.format_exception(exc_type, exc_value, exc_tb))
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
            print("SQLite error: %s" % (" ".join(err.args)))
            print("Exception class is: ", err.__class__)
            print("SQLite traceback: ")
            exc_type, exc_value, exc_tb = sys.exc_info()
            print(traceback.format_exception(exc_type, exc_value, exc_tb))
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
            print("SQLite error: %s" % (" ".join(err.args)))
            print("Exception class is: ", err.__class__)
            print("SQLite traceback: ")
            exc_type, exc_value, exc_tb = sys.exc_info()
            print(traceback.format_exception(exc_type, exc_value, exc_tb))
        return None
    
    def removeContent(self, tmdbId):
      self.__init__()
      try:
        self.cur.execute(
          """DELETE FROM contents WHERE tmdb_id = :tmdbId""", { "tmdbId": tmdbId }
        )
        self.con.commit()
      except sqlite3.Error as err:
        print("SQLite error: %s" % (" ".join(err.args)))
        print("Exception class is: ", err.__class__)
        print("SQLite traceback: ")
        exc_type, exc_value, exc_tb = sys.exc_info()
        print(traceback.format_exception(exc_type, exc_value, exc_tb))
      return None