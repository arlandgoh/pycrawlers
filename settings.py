'''
Defining all the settings here
'''

import sys
import time
import os

## Main url for crawling
MAIN_URL = "https://basketball-reference.com"

## Paths 
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_PATH, "data")

## Site settings 

DOWNLOAD_DELAY = 3 
ROBOTSTXT_OBEY = True

def delay() -> None:
    time.sleep(DOWNLOAD_DELAY)
    return None


# defining state
TESTING = True
MULTIPROCESSING = False
