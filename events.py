# define event classes


class XPlayEvent:
  def __init__(self, max_pitches=None, start_time=None, play_result=None,
               inning=None, away_bat=None, away_score=None, home_score=None,
               pitcher_id=None, batter_id=None, men_on=None, pitcher_team=None,
               batter_team=None, pitcher=None, batter=None, batter_score=None,
               pitcher_score=None):
    self.max_pitches = max_pitches
    self.start_time = start_time
    self.play_result = play_result
    self.inning = inning
    self.away_bat = away_bat
    self.away_score = away_score
    self.home_score = home_score
    self.pitcher_id = pitcher_id
    self.batter_id = batter_id
    self.men_on = men_on
    self.pitcher_team = pitcher_team
    self.batter_team = batter_team
    self.pitcher = pitcher
    self.batter = batter
    self.batter_score = batter_score
    self.pitcher_score = pitcher_score


class XPitchEvent:
  def __init__(self, pe=None, balls=None, strikes=None, outs=None,
               pitch_num=None, pitch=None, prior_seq=None):
    self.pe = pe
    self.balls = balls
    self.strikes = strikes
    self.outs = outs
    self.pitch_num = pitch_num
    self.pitch = pitch
    self.prior_seq = prior_seq


class EventsLoader(object):
  def __init__(self, base_dir, game_parser):
    self.base_dir = base_dir
    self.game_parser = game_parser

  def events_filename(self, year):
    return os.path.join(self.base_dir, "data", "events-%d.pkl.bz2" % year)

  def load_year(self, year, ignore_cache=False):
    is_game_file = lambda x: x.startswith("id-")
    filename = self.events_filename(year)
    events = []
    if os.path.exists(filename) and not ignore_cache:
      with open(filename, "rb") as infile:
        events = pickle.load(infile)
    else:
      data_dir = games_dir(year)
      if os.path.exists(data_dir):
        games = {}
        print("File (" + data_dir + ") found.",flush=True)
        entries = os.listdir(data_dir)
        filtered = filter(is_game_file, tqdm(entries, total=len(entries)))
        for entry in filtered:
          try:
            with open(os.path.join(data_dir, entry), "rb") as infile:
              game = pickle.load(infile)
              game_id = game.get('gamePk')
              if game_id is not None:
                games[game_id] = game
              else:
                print("Invalid data for %s" % entry)
          except:
            os.remove(os.path.join(data_dir, entry))
        for game in games.values():
          events.extend(parse(game))
        with open(filename, "wb") as outfile:
          pickle.dump(events, outfile, protocol=4)
        print("DONE")
      else:
        print("File (" + data_dir + ") NOT found.",flush=True)
    return events

  def load_years(self, years, ignore_cache=False):
    valid_years = []
    all_events = []
    for year in years:
      events = self.load_year(year, ignore_cache)
      all_events.extend(events)
      valid_years.append(str(year))
      print("year(%d): %d events loaded" % (year, len(events)))
    print("YEARS LOADED: {}".format(" ".join(valid_years)))
    return (valid_years, all_events)
