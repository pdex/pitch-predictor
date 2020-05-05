from events import EventsLoader
from events import XPlayEvent
from events import XPitchEvent
from getdata import Fetcher
from parser import GameParser
import random


def setup_parameters(years=(2016, 2017, 2018, 2019), epochs=50, testing=True):
  shuffled_years = list(years)
  random.shuffle(shuffled_years)
  result = ()
  if testing:
    num_epochs = 1
    result = (shuffled_years[:1], num_epochs)
  else:
    num_epochs = epocs
    result = (shuffled_years, num_epochs)
  return result 
