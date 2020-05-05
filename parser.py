import copy
import os


# Category classes

class PlayResultCategory(object):
  FIELD_OUT = tuple([
    'balk',
    'batter_interference',
    'catcher_interf',
    'caught_stealing_2b',
    'caught_stealing_3b',
    'caught_stealing_home',
    'double_play',
    'fan_interference',
    'field_error',
    'field_out',
    'fielders_choice',
    'fielders_choice_out',
    'force_out',
    'game_advisory',
    'grounded_into_double_play',
    'hit_by_pitch',
    'other_out',
    'passed_ball',
    'pickoff_1b',
    'pickoff_2b',
    'pickoff_3b',
    'pickoff_caught_stealing_2b',
    'pickoff_caught_stealing_3b',
    'pickoff_caught_stealing_home',
    'pickoff_error_1b',
    'runner_double_play',
    'stolen_base_2b',
    'triple_play',
    'wild_pitch',
    'sac_bunt',
    'sac_bunt_double_play',
    'sac_fly',
    'sac_fly_double_play'
  ])
  WALK = tuple([
    'intent_walk',
    'walk'
  ])
  STRIKEOUT = tuple([
    'strikeout',
    'strikeout_double_play'
  ])
  HIT = tuple([
    'home_run',
    'single',
    'double',
    'triple'
  ])
  def __call__(self, play_result):
    if play_result in self.WALK:
      return 'walk'
    if play_result in self.STRIKEOUT:
      return 'strikeout'
    if play_result in self.HIT:
      return 'hit'
    return 'field_out'


# Parsing classes

class PlayerParser(object):
  '''Parse a game and return a dict of player_id to fullname'''
  def __call__(self, game):
    player_db = {}
    players = game['gameData']['players']
    for elt in players.values():
      player_db[elt['id']] = elt['fullName']
    return player_db


class TeamParser(object):
  '''Parse a game and return a dict of player_id to team_name'''
  SIDES = tuple([
    'home',
    'away'                 
  ])
  def __call__(self, game):
    team_db = {}
    for side in self.SIDES:
      team_name = game['liveData']['boxscore']['teams'][side]['team']['name']
      for player in game['liveData']['boxscore']['teams'][side]['players'].values():
        team_db[player['person']['id']] = team_name
    return team_db


class PlayEventParser(object):
  '''Parse a play and return a XPlayEvent'''
  def __init__(self, PlayEventClass):
    self.PlayEventClass = PlayEventClass
    self.play_result_category = PlayResultCategory()

  def batter_score(self, away_bat, away_score, home_score):
    if away_bat:
      return away_score
    return home_score

  def pitcher_score(self, away_bat, away_score, home_score):
    if not away_bat:
      return away_score
    return home_score

  def __call__(self, team_db, player_db, play):
    away_bat = play['about']['isTopInning'] # bool
    away_score = play['result']['awayScore'] # num
    home_score = play['result']['homeScore'] # num
    pitcher_id = play['matchup']['pitcher']['id']
    batter_id = play['matchup']['batter']['id']

    return self.PlayEventClass(
      max_pitches=len(play['pitchIndex']),
      start_time=play['about'].get('startTime'),
      play_result=self.play_result_category(play['result']['eventType']), # string from vocab
      inning=play['about']['inning'], # num
      away_bat=away_bat,
      away_score=away_score,
      home_score=home_score,
      pitcher_id=pitcher_id,
      batter_id=batter_id,
      men_on=(0 if "Empty" == play['matchup']['splits']['menOnBase'] else 1),
      pitcher_team=team_db[pitcher_id],
      batter_team=team_db[batter_id],
      pitcher=player_db[pitcher_id],
      batter=player_db[batter_id],
      batter_score=self.batter_score(away_bat, away_score, home_score),
      pitcher_score=self.pitcher_score(away_bat, away_score, home_score),
    )


class PitchEvenParser(object):
  '''Parse a game and return a list of play events'''
  def __init__(self, PitchEventClass, play_event_parser):
    self.PitchEventClass = PitchEventClass
    self.play_event_parser = play_event_parser

  def filtered_pitches(self, play, play_event):
    is_pitch = (
      lambda i : play['playEvents'][i]["isPitch"]
      and "type" in play['playEvents'][i]['details']
    )
    return list(filter(is_pitch, range(play_event.max_pitches)))

  def parse(self, play, playevent, pitch_num, pitch_seq):
    return self.PitchEventClass(
      pe=playevent,
      balls=play['playEvents'][pitch_num]['count']['balls'],
      strikes=play['playEvents'][pitch_num]['count']['strikes'],
      outs=play['count']['outs'],
      pitch_num=pitch_num,
      pitch=play['playEvents'][pitch_num]['details']['type']['code'],
      prior_seq=pitch_seq,
    )

  def __call__(self, team_db, player_db, game):
    output = []
    number_of_plays = len(game['liveData']['plays']['allPlays'])
    for play_number in range(number_of_plays):
      play = game['liveData']['plays']['allPlays'][play_number]
      if ('event' in play['result']):
        play_event = self.play_event_parser(team_db, player_db, play)
        filtered_pitch_indices = self.filtered_pitches(play, play_event)
        pitch_seq = []
        for i in filtered_pitch_indices:
          pitch_event = self.parse(play, play_event, i, copy.deepcopy(pitch_seq))
          pitch_seq.append(pitch_event.pitch)
          output.append(pitch_event)
    return output


class GameParser(object):
  def __init__(self, PitchEventClass, PlayEventClass):
    self.team_parser = TeamParser()
    self.player_parser = PlayerParser()
    self.pitch_event_parser = PitchEvenParser(PitchEventClass, PlayEventParser(PlayEventClass))

  def __call__(self, game):
    team_db = self.team_parser(game)
    player_db = self.player_parser(game)
    return self.pitch_event_parser(team_db, player_db, game)
