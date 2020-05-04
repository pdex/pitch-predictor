import statsapi
import pickle
import os
from os.path import exists
from os import makedirs
from bz2 import open
from tqdm.notebook import tqdm


class Fetcher(object):
  def __init__(self, base_dir):
    self.base_dir = base_dir

  def schedule_filename(self, year):
    return os.path.join(self.base_dir, "data", "schedule-p4-%d.pkl.bz2" % year)

  def game_filename(self, year, game_id):
    return os.path.join(self.base_dir, "data", "games-%d" % year, "id-%d-p4.pkl.bz2" % game_id)

  def create_directories(self, year):
    games_dir = os.path.join("data", "games-%d" % year)
    directories = [
      "data",
      games_dir,
      "models",
      "ckpt"
    ]
    for dir in directories:
      full = os.path.join(self.base_dir, dir)
      if not exists(full):
        try:
          makedirs(full)
        except:
          print("ERROR: Could not create and/or access directory: {}".format(dir))
          raise

  def fetch_schedule(self, year):
    filename = self.schedule_filename(year) 
    print(year, ": ", filename)
    if exists(filename):
      print("{} exists. Loading...".format(filename),end="")
      with open(filename,"rb") as infile:
        schedule = pickle.load(infile)
    else:
      print("{} does not exist. Downloading...".format(filename),end="")
      schedule = statsapi.schedule(start_date='01/01/'+str(year),end_date='12/31/'+str(year))
      with open(filename,"wb") as outfile:
        pickle.dump(schedule, outfile, protocol=4)
    print("DONE.")
    return schedule

  def fetch_game(self, year, game_id):
    filename = self.game_filename(year, game_id) 
    if not exists(filename):
      with open(filename, "wb") as outfile:
        game = statsapi.get("game",{"gamePk":game_id})
        pickle.dump(game, outfile, protocol=4)

  def fetch_games(self, year, schedule):
    game_ids = sorted(set([x['game_id'] for x in schedule]))

    for game_id in tqdm(game_ids):
      self.fetch_game(year, game_id)
    print("DONE.")

  def fetch_year(self, year):
    self.create_directories(year)
    schedule = self.fetch_schedule(year)
    self.fetch_games(year, schedule)


data_years = [2016,2017,2018,2019]


