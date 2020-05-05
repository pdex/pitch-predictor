from __init__ import EventsLoader
from __init__ import XPlayEvent
from __init__ import XPitchEvent
from __init__ import Fetcher
from __init__ import GameParser
from __init__ import setup_parameters


def main():
  data_years = [2016,2017,2018,2019]
  base_dir = "./tmp"
  fetcher = Fetcher(base_dir)
  for year in data_years:
    fetcher.fetch_year(year)
  loader = EventsLoader(base_dir, GameParser(XPitchEvent, XPlayEvent))
  years, num_epocs = setup_parameters(data_years, testing=True)
  valid_years, all_events = loader.load_years(years)


if __name__ == '__main__':
  main()
