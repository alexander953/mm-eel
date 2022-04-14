import eel
import sqlite3 as sql
import configparser as cp
import sys
import traceback
from db_lib import Database
from request_lib import TmdbRequests

database = 'store.db'

class Installer:
  def __init__(self, database):
    con = sql.connect(database)

    with open("install.sql", "r") as setup:
        con.executescript(setup.read())

    con.close()

config = cp.ConfigParser()
config.read('conf.ini')
if config.getboolean('SETUP', 'INSTALL'):
  Installer(database)
  config.set('SETUP', 'INSTALL', 'no')
  with open('conf.ini', 'w') as configFile:
    config.write(configFile)

db = Database()
tmdbRequests = TmdbRequests()

eel.init('web')

# eel functions
@eel.expose
def addMovie(movie):
  db.addMovie(movie)

@eel.expose
def addSeriesByTmdbId(tmdbId):
  db.addSeriesByTmdbId(tmdbId)

@eel.expose
def removeContent(tmdbId):
  db.removeContent(tmdbId)

@eel.expose
def checkIfContentExists(tmdbId, type):
  if type == 'movie':
    isMovie = 1
  else:
    isMovie = 0
  return db.checkIfContentExists(tmdbId, isMovie)

@eel.expose
def getSeasonsById(tmdbId):
  return tmdbRequests.getSeasonsById(tmdbId)

@eel.expose
def checkIfSeasonExists(tmdbId, number):
  return db.checkIfSeasonExists(tmdbId, number)

@eel.expose
def addSeasonByTmdbIdAndNumber(tmdbId, number):
  db.addSeasonByTmdbIdAndNumber(tmdbId, number)

@eel.expose
def getSeasonByIdAndNumber(tmdbId, number):
  return tmdbRequests.getSeasonByIdAndNumber(tmdbId, number)

@eel.expose
def removeSeasonByIdAndNumber(tmdbId, number):
  db.removeSeasonByIdAndNumber(tmdbId, number)

@eel.expose
def getEpisodesByIdAndNumber(tmdbId, number):
  return tmdbRequests.getEpisodesByIdAndNumber(tmdbId, number)

@eel.expose
def checkIfEpisodeExists(tmdbId, seasonNumber, number):
  return db.checkIfEpisodeExists(tmdbId, seasonNumber, number) 

@eel.expose
def addEpisodeByTmdbIdAndNumber(tmdbId, seasonNumber, number):
  db.addEpisodeByTmdbIdAndNumber(tmdbId, seasonNumber, number)

@eel.expose
def removeEpisodeByIdAndNumber(tmdbId, seasonNumber, number):
  db.removeEpisodeByIdAndNumber(tmdbId, seasonNumber, number)

@eel.expose
def addLocation(parentId, name, description):
  db.addLocation(parentId, name, description)

@eel.expose
def getLocationsByParentId(parentId):
  return db.getLocationsByParentId(parentId)

@eel.expose
def removeLocationById(id):
  db.removeLocationById(id)

@eel.expose
def addContentsStorement(tmdbId, isMovie, locationId, amount, recordingDate, notes):
  db.addContentsStorement(tmdbId, isMovie, locationId, amount, recordingDate, notes)

@eel.expose
def addSeasonsStorement(tmdbId, seasonNumber, locationId, amount, recordingDate, notes):
  db.addSeasonsStorement(tmdbId, seasonNumber, locationId, amount, recordingDate, notes)

@eel.expose
def addEpisodesStorement(tmdbId, seasonNumber, episodeNumber, locationId, amount, recordingDate, notes):
  db.addEpisodesStorement(tmdbId, seasonNumber, episodeNumber, locationId, amount, recordingDate, notes)

@eel.expose
def removeContentsStorement(tmdbId, isMovie, locationId):
  db.removeContentsStorement(tmdbId, isMovie, locationId)

@eel.expose
def removeSeasonsStorement(tmdbId, seasonNumber, locationId):
  db.removeSeasonsStorement(tmdbId, seasonNumber, locationId)

@eel.expose
def removeEpisodesStorement(tmdbId, seasonNumber, episodeNumber, locationId):
  db.removeEpisodesStorement(tmdbId, seasonNumber, episodeNumber, locationId)

@eel.expose
def getContentsStorement():
  results = db.getContentsStorement()
  contentsStorementHeaders = ['tmdb_id', 'is_movie', 'location_id', 'amount', 'recording_date', 'notes', 'created_on', 'updated_on']
  dictResults = [dict(zip(contentsStorementHeaders, result)) for result in results]
  return dictResults

@eel.expose
def getContentByTmdbIdAndIsMovie(tmdbId, isMovie):
  result = db.getContentByTmdbIdAndIsMovie(tmdbId, isMovie)
  contentsHeaders = ["tmdb_id", "is_movie", "title", "description", "backdrop_path", "release_date", "age_restricted", "rating", "notes", "created_on", "updated_on"]
  return dict(zip(contentsHeaders, result))

@eel.expose
def getRecordings():
  result = db.getRecordings()
  return result

@eel.expose
def getFullLocationById(id):
  fullLocation = ''
  if not fullLocation:
    return ''
  # TODO: Move this to config
  separator = ' / '
  location = db.getLocationById(id)
  fullLocation = location[1]
  parentLocationId = location[0]
  while parentLocationId:
    location = db.getLocationById(parentLocationId)
    fullLocation = location[1] + separator + fullLocation
    parentLocationId = location[0]
  return fullLocation

@eel.expose
def getFullLocations():
  fullLocations = []
  locationIds = db.getLocations()
  for locationId in locationIds:
    id = locationId[0]
    name = getFullLocationById(id)
    fullLocations.append((id, name))
  return fullLocations

@eel.expose
def updateStorement(data):
  tmdbId = data['tmdb_id']
  seasonNumber = data['season_number']
  episodeNumber = data['episode_number']
  print(data)
  index = data['index']
  value = data['data']
  locationId = data['location_id']

  if seasonNumber:
    if episodeNumber:
      if index < 8:
        db.updateEpisode(tmdbId, seasonNumber, episodeNumber, index, value)
      else:
        db.updateEpisodesStorement(tmdbId, seasonNumber, episodeNumber, locationId, index, value)
    else:
      if index < 8:
        db.updateSeason(tmdbId, seasonNumber, index, value)
      else:
        db.updateSeasonsStorement(tmdbId, seasonNumber, locationId, index, value)
  else:
    isMovie = data['is_movie']
    if index < 8:
      db.updateContent(tmdbId, isMovie, index, value)
    else:
      db.updateContentsStorement(tmdbId, isMovie, locationId, index, value)

@eel.expose
def getPossessions():
  return db.getPossessions()

@eel.expose
def addRecording(recording, locationId, amount, recordingDate, notes):
  tmdbId = recording[0]
  isMovie = recording[1]
  seasonNumber = recording[2]
  episodeNumber = recording[3]

  if seasonNumber:
    if episodeNumber:
      db.addEpisodesStorement(tmdbId, seasonNumber, episodeNumber, locationId, amount, recordingDate, notes)
    else:
      db.addSeasonsStorement(tmdbId, seasonNumber, locationId, amount, recordingDate, notes)
  else:
    db.addContentsStorement(tmdbId, isMovie, locationId, amount, recordingDate, notes)

@eel.expose
def deleteRecording(data):
  tmdbId = data['tmdb_id']
  isMovie = data['is_movie']
  seasonNumber = data['season_number']
  episodeNumber = data['episode_number']
  locationId = data['location_id']

  if seasonNumber:
    if episodeNumber:
      db.removeEpisodesStorement(tmdbId, seasonNumber, episodeNumber, locationId)
    else:
      db.removeSeasonsStorement(tmdbId, seasonNumber, locationId)
  else:
    db.removeContentsStorement(tmdbId, isMovie, locationId)

# @eel.expose
# def getFullTitle(tmdbId, seasonNumber, episodeNumber):
#   contentTitle = db.getTvTitleByTmdbId(tmdbId)
#   seasonTitle = ''
#   episodeTitle = ''
#   if seasonNumber:
#     seasonTitle = ' / ' + db.getSeasonTitleByTmdbIdAndNumber(tmdbId, seasonNumber)
#     if episodeNumber:
#       episodeTitle = ' / ' + db.getEpisodeTitleByTmdbIdAndSeasonNumberAndNumber(tmdbId, seasonNumber, episodeNumber)
#   fullTitle = contentTitle + seasonTitle + episodeTitle
#   return fullTitle

# print(getRecordings())
# quit()

eel.start('index.html')