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

eel.start('index.html')