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
from io import StringIO

## Paths 
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_PATH, "weather_data")

weather_data_dir = os.path.join(DATA_PATH, "weather")
os.makedirs(weather_data_dir, exist_ok=True)
           
dailyweather_download_urls_df_2018_2021_path = os.path.join(weather_data_dir, "daily_weather_2018_2021_download_urls.csv")
dailyweather_all_df_2018_2021_path = os.path.join(weather_data_dir, "daily_weather_2018_2021_all.csv")


years = ['2018', '2019', '2020', '2021']
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

dailyweather_row = {}
df_station_dailyweather_2018_2021_download_urls = pd.DataFrame(columns = ['station_name', 'station_id', 'month', 'year', 'csv_url'])    
df_station_dailyweather_2018_2021_all = pd.DataFrame(columns = ['Station', 'Year', 'Month', 'Day', 'Daily Rainfall Total (mm)', 'Highest 30 Min Rainfall (mm)',
                                                                'Highest 60 Min Rainfall (mm)', 'Highest 120 Min Rainfall (mm)', 'Mean Temperature (°C)', 'Maximum Temperature (°C)',
                                                                'Minimum Temperature (°C)', 'Mean Wind Speed (km/h)', 'Max Wind Speed (km/h)','Station ID'])
df_station_dailyweather_2018_2021_all.columns = map(str.lower, df_station_dailyweather_2018_2021_all.columns)


for station in station_tags_list:
    on_click_value = station.a.get('onclick')
    if on_click_value:
        station_id_extracted = re.findall(r'\(\'.*?\'\)', on_click_value) 
        station_id = re.sub('[()\']', '', station_id_extracted[0])
        station_id_list.append(station_id)
        
    station_name_list.append(station.a.text)

# 2018 - 2021
LAST_MONTH = '02'
LAST_YEAR = '2021'
counter = 0
for i in range(len(station_id_list)):
    for year in years:
        for month in months:
            if(year == LAST_YEAR and month > LAST_MONTH):
                #print('test')
                #print(year)
                #print(month)
                pass
            else:
                counter += 1
                #print(counter)
                dailyweather_row['station_name'] = station_name_list[i]
                dailyweather_row['station_id'] = station_id_list[i]
                dailyweather_row['year'] = year
                dailyweather_row['month'] = month
            
                start_url_station = download_url + station_id_list[i] + '_' + year + month + '.csv'
                
                dailyweather_row['csv_url'] = start_url_station
                #df_station_dailyweather_2018_2021_download_urls = df_station_dailyweather_2018_2021_download_urls.append(dailyweather_row, ignore_index=True)

                # append to main daily record dataframe
                # request.get(url).content delivers a byte stream
                headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:66.0) Gecko/20100101 Firefox/66.0"}
                #print(start_url_station)
                req = requests.get(start_url_station, headers=headers)
                s = StringIO(req.text)

                #s=requests.get(dailyweather_row['csv_url']).content
                try:          
                    dailyweather_records = pd.read_csv(s)
                    dailyweather_records['Station ID'] = station_id_list[i]
                    dailyweather_records.columns = map(str.lower, dailyweather_records.columns)
                    df_station_dailyweather_2018_2021_all = df_station_dailyweather_2018_2021_all.append(dailyweather_records, ignore_index=True)
                    df_station_dailyweather_2018_2021_download_urls = df_station_dailyweather_2018_2021_download_urls.append(dailyweather_row, ignore_index=True)
                except:
                    #print('no data')
                    pass									

# print(df_station_dailyweather_2018_2021_all.head()) 

# save the csv urls
df_station_dailyweather_2018_2021_download_urls.to_csv(dailyweather_download_urls_df_2018_2021_path, index=None)
df_station_dailyweather_2018_2021_all.to_csv(dailyweather_all_df_2018_2021_path, index=None)


