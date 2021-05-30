import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import sys
import re
import pdb
from datetime import datetime

## Paths 
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_PATH, "data")

players_data_dir = os.path.join(DATA_PATH, "players")
os.makedirs(players_data_dir, exist_ok=True)
        
salary_df_2009_2020 = pd.DataFrame()    
salary_df_2009_2020_path = os.path.join(players_data_dir, "players_salary_2009_2020.csv")

url="https://hoopshype.com/salaries/players/"
# '1999-2000','2000-2001','2001-2002','2002-2003','2003-2004','2004-2005','2005-2006','2006-2007','2007-2008','2008-2009',
list_season =['2009-2010','2010-2011','2011-2012','2012-2013','2013-2014',
              '2014-2015','2015-2016','2016-2017','2017-2018','2018-2019',
              '2019-2020']

# '1999-00','2000-01','2001-02','2002-03','2003-04','2004-05','2005-06','2006-07','2007-08','2008-09',
year_column =[ '2009-10','2010-11','2011-12','2012-13','2013-14',
              '2014-15','2015-16','2016-17','2017-18','2018-19',
              '2019-20']

for season in range(len(list_season)):
  
    r = requests.get(url+list_season[season],timeout=60)
    r_html = r.text 

    soup = BeautifulSoup(r_html, 'html.parser')

    salary_table = soup.find('table')

    length=len(salary_table.find_all("td"))

    player_names=[salary_table.find_all("td")[i].text.strip() for i in range(5,length, 4)]

    column1=[salary_table.find_all("td")[i].text.strip() for i in range(6,length,4)]

    df_dict={'player_names':player_names,
            year_column[season]:column1,
             }
    
    if(season == 0):
      salary_df_0 = pd.DataFrame(df_dict).set_index('player_names')

    else:
      salary_df = pd.DataFrame(df_dict).set_index('player_names')
      salary_df_0 = salary_df_0.join(salary_df, how='outer')

    print(list_season[season] + ' Done')

salary_df_0.replace({'\$':''}, regex = True,inplace=True)
salary_df_0.replace(',','', regex=True, inplace=True)
salary_df_0.reset_index(inplace=True)

for item in (salary_df_0.columns[1:]):
    salary_df_0[item]=pd.to_numeric(salary_df_0[item])

salary_df_0.to_csv(salary_df_2009_2020_path, index=None)


