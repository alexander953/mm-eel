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

eel.start('index.html')