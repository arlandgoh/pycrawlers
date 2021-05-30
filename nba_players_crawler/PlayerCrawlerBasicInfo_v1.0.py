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

def players_basic_information():
  players_data_dir = os.path.join(DATA_PATH, "players")
  os.makedirs(players_data_dir, exist_ok=True)
  all_players_09_path = os.path.join(players_data_dir, "all_players_from_2009.csv")
  players = pd.read_csv(all_players_09_path)
  
  for idx in players.index:
    info = {}
    print("Scraping players for ", players.loc[idx,'Player'], "||", players.loc[idx,'Franchise'])
    
    # Backing Off # 
    
    t0_request = time.time()

    response = requests.get(MAIN_URL + players.loc[idx,'player_url'])

    response_delay = time.time() - t0_request
    if(response_delay > 10):
      time.sleep(5*response_delay)
      print('sleep')

    ##################  
      
    
    html_doc = response.text
    soup = BeautifulSoup(re.sub("<!--|-->","", html_doc), "lxml")
    delay()

    _div = soup.find(name="div", attrs = {'itemtype':"https://schema.org/Person"})
    _h1 = _div.h1.text
    
    info['Name'] = _h1.strip()
    info['player_url'] = players.loc[idx,'player_url']

    for _ptag in _div.find_all('p'):
      
      row = [text for text in _ptag.stripped_strings]
      print(row)
      # Full Name
      if(_ptag.strong):
        if(_ptag.strong.strong):
          info['Full Name'] = _ptag.strong.strong.text.replace(":", "")
          #print(info['Full Name'])

      # Additional Information: Shoots
      if(len(row) > 3):
        if(row[2] == 'Shoots:'):
          info['Shoots'] = row[3]
          #print(info['Shoots'])
          
      # Position     
      if(row[0] == 'Position:'):
        info['Position'] = row[1].strip('\n\n\n  \n  ▪')
        #print(info['Position'])
        
      # Pronuniciation   
      elif(row[0] == 'Pronunciation'):
        info['Pronunciation'] = row[1].strip(': ')
        #print(info['Pronunciation'])

      # Experience 
      elif(row[0] == 'Experience:'):
        info['Experience'] = row[1].strip(' years')
        #print(info['Experience'])

        
      # Team
      elif(row[0] == 'Team'):
        info['Team'] = row[2]
        print(info['Team'])

      # Recruiting Rank
      elif(row[0] == 'Recruiting Rank:'):
        
        #info['Recruiting Rank Year'] = row[1].strip()
        #print(info['Recruiting Rank Year'])

        #info['Recruiting Rank'] = int(re.sub('[()]', '', row[2].strip()))
        #print(info['Recruiting Rank'])
        if len(row) > 3:
          info['Recruiting Rank Year'] = row[1].strip() + "," + row[3].strip()
          info['Recruiting Rank'] = re.findall(r'[0-9]+', row[2].strip())[0] \
                                                            + "," + re.findall(r'[0-9]+', row[4].strip())[0]
        else:
          info['Recruiting Rank Year'] = row[1].strip()
          info['Recruiting Rank'] = int(re.findall(r'[0-9]+', row[2].strip())[0])
          
      # Draft Team
      elif(row[0] == 'Draft:'):
        info['Draft Team'] = row[1]
        
        if(len(row)>2):
          draft_round = re.findall(r"\((.+)\)", row[2])

          if(draft_round):
            info['Draft Detail'] = row[2].strip(', ')
            info['Draft Round'] = row[2].strip(', ')[0]
            print(info['Draft Detail'])
            
        else:
          info['Draft Round'] = np.nan
          
        if(len(row)>3):
          info['Draft Year'] = int(row[3].strip().split(' ')[0])
          print(info['Draft Year'])

        else:
          info['Draft Year'] = np.nan

      # Nickname
      elif(len(row) == 1):
        nickname = re.findall(r"\((.+)\)", row[0])
        # check for nickname
        if(nickname):
          info['Nickname'] = nickname[0]
          #print(info['Nickname'])
                
      # Additional Information: College
      elif(row[0] == 'College:'):
        
        info['College'] = row[1]
        #print(info['College'])
        
      # Additional Information: High School  
      elif(row[0] == 'High School:'):
        info['High School'] = row[1]+row[2]
        #print(info['High School'])

      # Additional Information: NBA Debut 
      elif(row[0] == 'NBA Debut:'):
        date_list = row[1].split()
        _dd = date_list[1].strip(',')
        _mmm = date_list[0][0:3]
        _yyyy = date_list[2]
        _ddmmmyyyy = '-'.join((_yyyy, _mmm,_dd))
        _ddmmmyyyy_obj = datetime.strptime(_ddmmmyyyy, '%Y-%b-%d') # date object with yyyy-mon-dd format
        
        _ddmmyyyy_obj = datetime.strftime(_ddmmmyyyy_obj, '%Y-%m-%d') # date object with yyyy-mm-dd format
        
        info['NBA Debut'] = _ddmmyyyy_obj
        #print(info['NBA Debut'])

      elif(len(row) > 3):
        # Additional Information: Twitter 
        if(row[2] == 'Twitter'):
          info['Twitter'] = 'https://twitter.com/' + row[4]
          #print(info['Twitter'])
          
      # Additional Information: Career Length   
      elif(row[0] == 'Career Length:'):
        info['Career Length'] = row[1].strip(' years')
        #print(info['Career Length'])
        
      # Additional Information: Hall of Fame
      elif(row[0] == 'Hall of Fame:'):
        info['Hall of Fame'] = row[1].strip()
        print(info['Hall of Fame'])
          
      if(_ptag.span):
        
        # height - > feet and inches
        if(_ptag.find('span', attrs={"itemprop": "height"})):
          height = _ptag.find('span', attrs={"itemprop": "height"})
          info['Height Feet Inches'] = height.text
          height = height.text.split('-')

          # Convert height (in feet and inches to centimeters)
          h_ft = int(height[0])
          h_inch = int(height[1])
          h_inch += h_ft * 12
          h_cm = round(h_inch * 2.54)
          info['Height Centimeters'] = h_cm
          
          #print(info['Height Feet Inches'])
          #print(info['Height Centimeters'])
      
        # weight -> Pounds (lb)
        if(_ptag.find('span', attrs={"itemprop": "weight"})):
          weight = _ptag.find('span', attrs={"itemprop": "weight"})
          info['Weight lb'] = int(weight.text.strip('lb'))
     
          w_lb = info['Weight lb']
          w_kg = w_lb / 2.2

          # truncate the decimal point
          info['Weight kg'] = int(w_kg)
          
          #print(info['Weight kg'])
          #print(info['Weight lb'])
          
        # birthdate
        if(_ptag.find('span', attrs={"itemprop": "birthDate"})):
          birthdate = _ptag.find('span', attrs={"itemprop": "birthDate"})
          info['Birthday'] = birthdate['data-birth']
          #print(info['Birthday'])
          
        # birthdate  
        if(_ptag.find('span', attrs={"itemprop": "birthPlace"})):
          birthPlace = _ptag.find('span', attrs={"itemprop": "birthPlace"})
          
          # remove \xa0 from string
          birthPlace = birthPlace.get_text(strip=True).replace(u'\xa0', u' ')
          birthPlace = birthPlace.replace('in ', '')
          #print(birthPlace)
          info['Birth Place'] = birthPlace
          #print(info['Birth Place'])
          
    df_basic_info = pd.DataFrame(info, index=[0])
    #print(df_basic_info)
    
  return None

players_basic_information()
