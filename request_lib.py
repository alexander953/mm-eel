import requests as req
import configparser as cp

# TODO: Write api parameters to seperate variable
class TmdbRequests:
    def __init__(self):
        config = cp.ConfigParser()
        config.read("conf.ini")

        self.baseUri = config["ENVIRONMENT"]["tmdb_base_uri"]
        self.apiKey = config["ENVIRONMENT"]["api_key"]
        self.backdropUri = config["ENVIRONMENT"]["tmdb_backdrop_uri"]
        self.language = config["SETTINGS"]["language"]
        # TODO: Change settings -> get configuration via API
        self.posterSize = config["SETTINGS"]["poster_size"]

    def getSeriesById(self, id):
        res = req.get(
            self.baseUri
            + "/tv/"
            + str(id)
            + "?api_key="
            + self.apiKey
            + "&language="
            + self.language
        )
        if res.status_code == 200:
            return res.json()
        else:
            return []
    
    def getSeasonsById(self, id):
        res = self.getSeriesById(id)
        if res:
            return res['seasons']
        else:
            return []
    
    def getSeasonByIdAndNumber(self, id, number):
        res = req.get(self.baseUri + "/tv/" + str(id) + "/season/" + str(number)+ "?api_key="
            + self.apiKey
            + "&language="
            + self.language)
        if res.status_code == 200:
            return res.json()
        else:
            return {}
    
    def getEpisodeByIdAndNumber(self, id, seasonNumber, number):
        res = req.get(self.baseUri + "/tv/" + str(id) + "/season/" + str(seasonNumber) + "/episode/" + str(number)+ "?api_key="
            + self.apiKey
            + "&language="
            + self.language)
        if res.status_code == 200:
            return res.json()
        else:
            return {}
    
    def getEpisodesByIdAndNumber(self, id, seasonNumber):
        res = req.get(self.baseUri + "/tv/" + str(id) + "/season/" + str(seasonNumber)+ "?api_key="
            + self.apiKey
            + "&language="
            + self.language)
        if res.status_code == 200:
            return res.json()['episodes']
        else:
            return []

    def getPopularMovies(self):
        res = req.get(
            self.baseUri
            + "/movie/popular?api_key="
            + self.apiKey
            + "&language="
            + self.language
        )
        if res.status_code == 200:
            return res.json()["results"]
        else:
            return []

    def getPopularSeries(self):
        res = req.get(
            self.baseUri
            + "/tv/popular?api_key="
            + self.apiKey
            + "&language="
            + self.language
        )
        if res.status_code == 200:
            return res.json()["results"]
        else:
            return []

    def getImage(self, backdropPath, posterSize=None):
        if not posterSize:
            posterSize = self.posterSize
        res = req.get(self.backdropUri + self.posterSize + str(backdropPath))
        if res.status_code == 200:
            return res.content
        else:
            return None

    def searchMovie(self, term):
        res = req.get(
            self.baseUri
            + "/search/movie?api_key="
            + self.apiKey
            + "&language="
            + self.language
            + "&query="
            + term
        )
        if res.status_code == 200:
            return res.json()["results"]
        else:
            return []

    def searchSeries(self, term):
        res = req.get(
            self.baseUri
            + "/search/tv?api_key="
            + self.apiKey
            + "&language="
            + self.language
            + "&query="
            + term
        )
        if res.status_code == 200:
            return res.json()["results"]
        else:
            return []