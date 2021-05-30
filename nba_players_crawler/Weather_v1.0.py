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
DATA_PATH = os.path.join(BASE_PATH, "weather_data")

weather_data_dir = os.path.join(DATA_PATH, "weather")
os.makedirs(weather_data_dir, exist_ok=True)
        
dailyweather_df_2019_2021 = pd.DataFrame()    
dailyweather_df_2019_2021_path = os.path.join(weather_data_dir, "daily_weather_2019_2021.csv")

# <a class="myload" download="" href="S105_201512.csv">CSV</a>
years = ['2019', '2020', '2021']
months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']

download_url = "http://www.weather.gov.sg/files/dailydata/DAILYDATA_"
start_url = "http://www.weather.gov.sg/climate-historical-daily/"
  
r = requests.get(start_url,timeout=60)
r_html = r.text 

soup = BeautifulSoup(r_html, 'html.parser')

station_dropdown = soup.find('ul', {'class': 'dropdown-menu long-dropdown'})
station_tags_list = station_dropdown.find_all('li')
station_name_list = []
station_id_list = []

df_station_dailyweather_2019_2021 = pd.DataFrame(columns = ['station_name', 'station_id', 'month', 'year', 'csv_url'])    
print(df_station_dailyweather_2019_2021)

for station in station_tags_list:
    on_click_value = station.a.get('onclick')
    if on_click_value:
        station_id_extracted = re.findall(r'\(\'.*?\'\)', on_click_value) 
        station_id = re.sub('[()\']', '', station_id_extracted[0])
        station_id_list.append(station_id)
    station_name_list.append(station.a.text)

# 2019
for i in range(len(station_id_list)):
    for year in years:
        for month in months:
            
            start_url_station = start_url + station_id_list[i] + '_' + year + month
            #print(start_url_station)


#for item in (salary_df_0.columns[1:]):
#    salary_df_0[item]=pd.to_numeric(salary_df_0[item])

#salary_df_0.to_csv(salary_df_2009_2020_path, index=None)


