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

def teams_basic_information():
  teams_data_dir = os.path.join(DATA_PATH, "teams")
  os.makedirs(teams_data_dir, exist_ok=True)
  all_teams_09_path = os.path.join(teams_data_dir, "all_teams_info.csv")
  teams = pd.read_csv(all_teams_09_path)
  teams = teams[teams['team_url'].notna()] # Filter to get the franchises URL only
  teams = teams[(teams['From'] >= '2009-10') | (teams['To'] >= '2009-10')]
  
  for idx in teams.index:
    info = {}
    print("Scraping franchise for ", teams.loc[idx,'Franchise'], "||", teams.loc[idx,'Lg'])

    # Backing Off #

    team_url = teams.loc[idx,'team_url']
    team_id = team_url.strip().split('/')[-2]

    t0_request = time.time()

    response = requests.get(team_url)

    response_delay = time.time() - t0_request
    if(response_delay > 10):
      time.sleep(5*response_delay)
      print('sleep')

    ##################  
      
    html_doc = response.text
    soup = BeautifulSoup(html_doc, 'html.parser')
    delay()

    _div = soup.find(name="div", attrs = {'id': 'info'})
    _h1 = _div.h1.span.text
    print(_h1)
    info['Franchise Name'] = _h1.strip()
    
    for _ptag in _div.find_all('p'):
      
      row = [text for text in _ptag.stripped_strings]

      # Location     
      if(row[0] == 'Location:'):
        info['Location'] = row[1].strip('\n\n\n  \n  ▪')
        #print(info['Location'])
        
      # Championships   
      elif(row[0] == 'Championships:'):
        championships_list = row[1].split(';\n  \n  ')
        championships_nba_aba = re.findall(r"\((.+)\)", championships_list[0])

        if(championships_nba_aba):
          championships_total = championships_list[0].split()[0]
          info['Championships Total'] = int(championships_total)

          championships_nba_aba_list = championships_nba_aba[0].split(' & ')
          nba_championships_number = championships_nba_aba_list[0].split(' ')[0]
          aba_championships_number = championships_nba_aba_list[1].split(' ')[0]
          info['Championships NBA'] = int(nba_championships_number)
          info['Championships ABA'] = int(aba_championships_number)
        
        else:
          championships_total = championships_list[0]
          info['Championships Total'] = int(championships_total)
          info['Championships NBA'] = int(championships_total)
          info['Championships ABA'] = np.nan
        
        print(info['Championships Total'])
        print(info['Championships NBA'])
        print(info['Championships ABA'])

      # Team Name
      elif(row[0] == 'Team Names:'):
        info['Team'] = row[1]
        print(info['Team'])

      # Playoff Appearances
      elif(row[0] == 'Playoff Appearances:'):
        playoff_list = row[1].split(';\n  \n  ')
        playoff_nba_aba = re.findall(r"\((.+)\)", playoff_list[0])

        if(playoff_nba_aba):
          playoff_total = playoff_list[0].split()[0]
          info['Playoff Apprearances Total'] = int(playoff_total)

          playoff_nba_aba_list = playoff_nba_aba[0].split(' & ')
          nba_playoff_number = playoff_nba_aba_list[0].split(' ')[0]
          aba_playoff_number = playoff_nba_aba_list[1].split(' ')[0]
          info['Playoff NBA'] = int(nba_playoff_number)
          info['Playoff ABA'] = int(aba_playoff_number)
        
        else:
          playoff_total = playoff_list[0]
          info['Playoff Apprearances Total'] = int(playoff_total)
          info['Playoff NBA'] = int(playoff_total)
          info['Playoff ABA'] = np.nan
        
        print(info['Playoff Apprearances Total'])
        print(info['Playoff NBA'])
        print(info['Playoff ABA'])

      # Seasons
      elif(row[0] == 'Seasons:'):
        season_list = row[1].split(';\n  \n  ')

        # Season from & to 
        season_from = season_list[1].split(' to ')[0]
        season_to = season_list[1].split(' to ')[1]
        
        season_nba_aba = re.findall(r"\((.+)\)", season_list[0])

        if(season_nba_aba):
          season_total = season_list[0].split()[0]
          info['Season Total'] = season_total
          info['Season From'] = season_from
          info['Season To'] = season_to

          season_nba_aba_list = season_nba_aba[0].split(' & ')
          nba_season_number = season_nba_aba_list[0].split(' ')[0]
          aba_season_number = season_nba_aba_list[1].split(' ')[0]
          info['Season NBA'] = int(nba_season_number)
          info['Season ABA'] = int(aba_season_number)
        
        else:
          season_total = season_list[0]
          info['Season Total'] = season_total
          info['Season From'] = season_from
          info['Season To'] = season_to
          info['Season NBA'] = int(season_total)
          info['Season ABA'] = np.nan
          
        print(info['Season From'])
        print(info['Season To'])
        print(info['Season Total'])
        print(info['Season NBA'])
        print(info['Season ABA'])

      # Record
      elif(row[0] == 'Record:'):
        record_win_loss_total = row[1].split(',')[0].split('-')
        record_win_total = record_win_loss_total[0]
        record_loss_total = record_win_loss_total[1]
        record_nba_aba = re.findall(r"\((.+)\)", row[1].split(',')[1])
        
        if(record_nba_aba):
          record_win_loss_percentage_list = row[1].split(' ')[1].split('\n  \n    ')
          record_win_loss_percentage = float('0' + record_win_loss_percentage_list[0])
          record_win_nba = int(record_nba_aba[0].split(' & ')[0].split()[0].split('-')[0])
          record_loss_nba = int(record_nba_aba[0].split(' & ')[0].split()[0].split('-')[1])
          record_win_aba = int(record_nba_aba[0].split(' & ')[1].split()[0].split('-')[0])
          record_loss_aba = int(record_nba_aba[0].split(' & ')[1].split()[0].split('-')[1])

          info['Win Total'] = record_win_total
          info['Loss Total'] = record_loss_total
          info['Total Win Loss Percentage'] = record_win_loss_percentage
          
          info['Win Total NBA'] = record_win_nba
          info['Loss Total NBA'] = record_loss_nba
          info['NBA Win Loss Percentage'] = round(record_win_nba/(record_win_nba+record_loss_nba),3)
          
          info['Win Total ABA'] = record_win_aba
          info['Loss Total ABA'] = record_loss_aba
          info['ABA Win Loss Percentage'] = round(record_win_aba/(record_win_aba+record_loss_aba),3)
          
        else:
          record_win_loss_percentage = float('0' + row[1].split(',')[1].split()[0])
          info['Win Total'] = record_win_total
          info['Loss Total'] = record_loss_total
          info['Total Win Loss Percentage'] = record_win_loss_percentage
          
          info['Win Total NBA'] = record_win_total
          info['Loss Total NBA'] = record_loss_total
          info['NBA Win Loss Percentage'] = record_win_loss_percentage
          
          info['Win Total ABA'] = np.nan
          info['Loss Total ABA'] = np.nan
          info['ABA Win Loss Percentage'] = np.nan
          
          
    df_basic_info = pd.DataFrame(info, index=[0])
    # print(df_basic_info)
    
  return None

teams_basic_information()
