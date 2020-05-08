from pitchpredictor.events import EventsLoader
from pitchpredictor.events import XPlayEvent
from pitchpredictor.events import XPitchEvent
from pitchpredictor.getdata import Fetcher
from pitchpredictor.parser import GameParser
import random


def setup_parameters(years=(2016, 2017, 2018, 2019), epochs=50, testing=True):
  shuffled_years = list(years)
  random.shuffle(shuffled_years)
  result = ()
  if testing:
    num_epochs = 1
    result = (shuffled_years[:1], num_epochs)
  else:
    num_epochs = epochs
    result = (shuffled_years, num_epochs)
  return result 
