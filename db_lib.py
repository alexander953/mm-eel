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
        self.contentValues = ['title', '', '', 'description', 'release_date', 'age_restricted', 'rating', 'notes', 'amount', 'recording_date', 'notes', 'location_id']
        self.contentSubValues = ['title', '', '', 'description', 'air_date', '', 'rating', 'notes', 'amount', 'recording_date', 'notes', 'location_id']

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
            name = req.getSeriesById(tmdbId)['name']
            season = req.getSeasonByIdAndNumber(tmdbId, number)
            seasonName = season['name']
            season.update({ 'tmdbId': tmdbId, 'name': name + ' / ' + seasonName })
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
        name = req.getSeriesById(tmdbId)['name']
        seasonName = req.getSeasonByIdAndNumber(tmdbId, seasonNumber)['name']
        episode = req.getEpisodeByIdAndNumber(tmdbId, seasonNumber, number)
        episodeName = episode["name"]
        if not episode['still_path']:
            episode['still_path'] = ""
        episode.update({ "tmdbId": tmdbId, "seasonNumber": seasonNumber, "name": name + " / " + seasonName + " / " + episodeName })
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
                """SELECT co.title, '', '', co.description, co.release_date, co.age_restricted, co.rating, co.notes, st.amount, st.recording_date, st.notes, st.location_id, co.tmdb_id, co.is_movie FROM contents co
                    INNER JOIN
                    contents_storement st
                    ON co.tmdb_id = st.tmdb_id AND co.is_movie = st.is_movie
                    UNION ALL
                    SELECT se.title, se.number, '', se.description, se.air_date, '', se.rating, se.notes, st.amount, st.recording_date, st.notes, st.location_id, se.tmdb_id, 0 FROM
                    seasons se
                    INNER JOIN
                    seasons_storement st
                    ON se.tmdb_id = st.tmdb_id AND se.number = st.season_number
                    UNION ALL
                    SELECT ep.title, ep.season_number, ep.number, ep.description, ep.air_date, '', ep.rating, ep.notes, st.amount, st.recording_date, st.notes, st.location_id, ep.tmdb_id, 0 FROM
                    episodes ep
                    INNER JOIN
                    episodes_storement st
                    ON ep.tmdb_id = st.tmdb_id AND ep.season_number = st.season_number AND ep.number = st.episode_number;"""
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
        print(err)
        print("SQLite error: %s" % (" ".join(err.args)))
        print("Exception class is: ", err.__class__)
        print("SQLite traceback: ")
        exc_type, exc_value, exc_tb = sys.exc_info()
        print(traceback.format_exception(exc_type, exc_value, exc_tb))

    def getLocations(self):
        self.__init__()
        try:
            self.cur.execute(
                """SELECT id FROM locations;"""
            )
            return self.cur.fetchall()
        except sqlite3.Error as err:
            self.handleError(err)
        return None
    
    def updateContent(self, tmdbId, isMovie, index, data):
        self.__init__()
        try:
            self.cur.execute(
                """UPDATE contents
                    SET {0} = :data
                    WHERE tmdb_id = :tmdbId
                    AND is_movie = :isMovie""".format(self.contentValues[index]),
                {
                    "data": data,
                    "tmdbId": tmdbId,
                    "isMovie": isMovie
                }
            )
            self.con.commit()
        except sqlite3.Error as err:
            self.handleError(err)
        return None

    def updateSeason(self, tmdbId, seasonNumber, index, data):
        self.__init__()
        try:
            self.cur.execute(
                """UPDATE seasons
                    SET {0} = :data
                    WHERE tmdb_id = :tmdbId
                    AND number = :seasonNumber""".format(self.contentSubValues[index]),
                {
                    "data": data,
                    "tmdbId": tmdbId,
                    "seasonNumber": seasonNumber
                }
            )
            self.con.commit()
        except sqlite3.Error as err:
            self.handleError(err)
        return None

    def updateEpisode(self, tmdbId, seasonNumber, episodeNumber, index, data):
        self.__init__()
        try:
            self.cur.execute(
                """UPDATE episodes
                    SET {0} = :data
                    WHERE tmdb_id = :tmdbId
                    AND season_number = :seasonNumber
                    AND number = :episodeNumber""".format(self.contentSubValues[index]),
                {
                    "data": data,
                    "tmdbId": tmdbId,
                    "seasonNumber": seasonNumber,
                    "episodeNumber": episodeNumber
                }
            )
            self.con.commit()
        except sqlite3.Error as err:
            self.handleError(err)
        return None

    def updateContentsStorement(self, tmdbId, isMovie, locationId, index, data):
        self.__init__()
        try:
            self.cur.execute(
                """UPDATE contents_storement
                    SET {0} = :data
                    WHERE tmdb_id = :tmdbId
                    AND is_movie = :isMovie
                    AND location_id = :locationId""".format(self.contentValues[index]),
                {
                    "data": data,
                    "tmdbId": tmdbId,
                    "isMovie": isMovie,
                    "locationId": locationId
                }
            )
            self.con.commit()
        except sqlite3.Error as err:
            self.handleError(err)
        return None

    def updateSeasonsStorement(self, tmdbId, seasonNumber, locationId, index, data):
        self.__init__()
        try:
            self.cur.execute(
                """UPDATE seasons_storement
                    SET {0} = :data
                    WHERE tmdb_id = :tmdbId
                    AND season_number = :seasonNumber
                    AND location_id = :locationId""".format(self.contentSubValues[index]),
                {
                    "data": data,
                    "tmdbId": tmdbId,
                    "seasonNumber": seasonNumber,
                    "locationId": locationId
                }
            )
            self.con.commit()
        except sqlite3.Error as err:
            self.handleError(err)
        return None

    def updateEpisodesStorement(self, tmdbId, seasonNumber, episodeNumber, locationId, index, data):
        self.__init__()
        try:
            self.cur.execute(
                """UPDATE episodes_storement
                    SET {0} = :data
                    WHERE tmdb_id = :tmdbId
                    AND season_number = :seasonNumber
                    AND episode_number = :episodeNumber
                    AND location_id = :locationId""".format(self.contentSubValues[index]),
                {
                    "data": data,
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
    
    def getPossessions(self):
        self.__init__()
        try:
            self.cur.execute(
                """SELECT tmdb_id, is_movie, '', '', title from contents
                    UNION ALL
                    SELECT tmdb_id, '', number, '', title from seasons
                    UNION ALL
                    SELECT tmdb_id, '', season_number, number, title from episodes"""
            )
            return self.cur.fetchall()
        except sqlite3.Error as err:
            self.handleError(err)
        return None
    
    # def getTvTitleByTmdbId(self, tmdbId):
    #     self.__init__()
    #     try:
    #         self.cur.execute(
    #             """SELECT title FROM contents
    #                 WHERE tmdb_id = :tmdbId AND is_movie = 0;""",
    #             {
    #                 "tmdbId": tmdbId
    #             }
    #         )
    #         result = self.cur.fetchone()
    #         if result:
    #             return result[0]
    #         else:
    #             return '...'
    #     except sqlite3.Error as err:
    #         self.handleError(err)
    #     return None
    
    # def getSeasonTitleByTmdbIdAndNumber(self, tmdbId, number):
    #     self.__init__()
    #     try:
    #         self.cur.execute(
    #             """SELECT title FROM seasons
    #                 WHERE tmdb_id = :tmdbId AND number = :number;""",
    #             {
    #                 "tmdbId": tmdbId,
    #                 "number": number
    #             }
    #         )
    #         result = self.cur.fetchone()
    #         if result:
    #             return result[0]
    #         else:
    #             return '...'
    #     except sqlite3.Error as err:
    #         self.handleError(err)
    #     return None
    
    # def getEpisodeTitleByTmdbIdAndSeasonNumberAndNumber(self, tmdbId, seasonNumber, number):
    #     self.__init__()
    #     try:
    #         self.cur.execute(
    #             """SELECT title FROM episodes
    #                 WHERE tmdb_id = :tmdbId AND season_number = :seasonNumber AND number = :number;""",
    #             {
    #                 "tmdbId": tmdbId,
    #                 "seasonNumber": seasonNumber,
    #                 "number": number
    #             }
    #         )
    #         result = self.cur.fetchone()
    #         if result:
    #             return result[0]
    #         else:
    #             return '...'
    #     except sqlite3.Error as err:
    #         self.handleError(err)
    #    return None
    
    def getPossessionsCount(self):
        self.__init__()
        try:
            self.cur.execute("""
                SELECT COUNT(*) AS contents_count FROM contents
                UNION ALL
                SELECT COUNT(*) AS seasons_count FROM seasons
                UNION ALL
                SELECT COUNT(*) AS episodes_count FROM episodes;
            """)
            return self.cur.fetchall()
        except sqlite3.Error as err:
            self.handleError(err)
        return None
    
    def getLocationsCount(self):
        self.__init__()
        try:
            self.cur.execute(
                """
                SELECT COUNT(*) AS locations_count FROM locations;"""
            )
            return self.cur.fetchone()
        except sqlite3.Error as err:
            self.handleError(err)
        return None
    
    def getAssignedPossessionsCount(self):
        self.__init__()
        try:
            self.cur.execute(
                """
                    SELECT COUNT(DISTINCT tmdb_id || '' || is_movie) FROM contents_storement
                    UNION ALL
                    SELECT COUNT(DISTINCT tmdb_id || '' || season_number) FROM seasons_storement
                    UNION ALL
                    SELECT COUNT(DISTINCT tmdb_id || '' || season_number || '' || episode_number) FROM episodes_storement;
                """
            )
            return self.cur.fetchall()
        except sqlite3.Error as err:
            self.handleError(err)
        return None