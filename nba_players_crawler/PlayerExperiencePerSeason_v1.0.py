import settings
from settings import delay
from settings import DATA_PATH, MAIN_URL

import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import sys
import re
import pdb
from datetime import datetime
import time
import numpy as np
import re


def players_experiences_information():

  season_list = ['2010.html',
                 '2011.html',
                 '2012.html',
                 '2013.html',
                 '2014.html',
                 '2015.html',
                 '2016.html',
                 '2017.html',
                 '2018.html',
                 '2019.html',
                 '2020.html']

  season_mapper = {'2010.html': '2009-10',
                 '2011.html': '2010-11',
                 '2012.html': '2011-12',
                 '2013.html': '2012-13',
                 '2014.html': '2013-14',
                 '2015.html': '2014-15',
                 '2016.html': '2015-16',
                 '2017.html': '2016-17',
                 '2018.html': '2017-18',
                 '2019.html': '2018-19',
                 '2020.html': '2019-20'}
  
  
  teams_data_dir = os.path.join(DATA_PATH, "teams")
  os.makedirs(teams_data_dir, exist_ok=True)
  all_teams_09_path = os.path.join(teams_data_dir, "all_teams_info.csv")
  teams = pd.read_csv(all_teams_09_path)
  teams = teams[teams['team_url'].notna()] # Filter to get the franchises URL only
  teams = teams[(teams['From'] >= '2009-10') | (teams['To'] >= '2009-10')]
  
  players_data_dir = os.path.join(DATA_PATH, "players")
  os.makedirs(players_data_dir, exist_ok=True)
  players_experiences = pd.DataFrame()
  players_experiences_path = os.path.join(players_data_dir, "players_experiences.csv")
  
  for idx in teams.index:
    info = {}
    print("Scraping franchise for ", teams.loc[idx,'Franchise'], "||", teams.loc[idx,'Lg'])

    # Backing Off #

    team_url = teams.loc[idx,'team_url']
    team_id = team_url.strip().split('/')[-2]

    for season in season_list:
      print("Scraping season for ", season)
      t0_request = time.time()
      response = requests.get(team_url+season)
      response_delay = time.time() - t0_request
      if(response_delay > 10):
        time.sleep(5*response_delay)
        print('sleep')

    ##################  
      
      html_doc = response.text
      #soup = BeautifulSoup(html_doc, 'html.parser')
      soup = BeautifulSoup(re.sub("<!--|-->","", html_doc), "lxml")
      delay()
      try:
        _table = soup.find("table", {"id" :  "roster"})
        cols = []
        _ = [cols.append(head.text.replace(u'\xa0', u'flag')) for head in _table.thead.tr.findAll('th')]
        rows = _table.tbody.findAll('tr')
        player_experiences = [[td.getText() for td in rows[i].findAll(re.compile(r'(th|td)'))] for i in range(len(rows))]

        _experiences = pd.DataFrame(player_experiences, columns = cols)

        # franchise
        _experiences['Franchise'] = teams.loc[idx,'Franchise']

        # season
        _experiences['Season'] = season_mapper[season]

        # player urls        
        player_college_urls = [atag['href'] for atag in _table.tbody.findAll('a')]
        player_urls = [ s for s in player_college_urls if 'players' in s ]   
        _experiences['player_url'] = player_urls
        
        players_experiences = pd.concat([players_experiences, _experiences], ignore_index=True)

      except Exception as e:
        print(e)
        
  #save all player's experience per season
  players_experiences.to_csv(players_experiences_path, index=None)
  print("Scraping players for players' experience completed!")

  return None 


players_experiences_information()
