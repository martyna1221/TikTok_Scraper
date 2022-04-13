# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 14:45:17 2022

@author: martyna1221
"""

from selenium import webdriver
import re
import json
import warnings
from dotenv import load_dotenv
import os
import pandas as pd

warnings.simplefilter("ignore")

load_dotenv()

chrome_driver = os.getenv('CHROME_DRIVER')
chrome_driver = chrome_driver.replace('\\', '/')

print('\nThis script works by scraping batches of tiktok urls. Please try out '
      'this functionality by either (1) inputting a url to a google sheet '
      'along with its associated sheet name when prompted OR (2) by simply '
      'hitting ENTER; this option scrapes a couple of tiktoks that are '
      'located in a google sheet hardcoded into the attached .env file. If '
      'you make your own sheet please make sure that it can be viewed by '
      'anyone that has a link to it. Also, look at the schema of the example '
      'sheet to see how your data is to be structured.')

"""
    open_google_sheet() : this function, given a sheet_link (i.e. the url) and
    a sheet_name (i.e. the name of the tab you wish to access in Python; a 
    spreadsheets sheet_name can be found in the lower left hand corner and is 
    initialized to 'Sheet1' unless it has been manually changed), returns a 
    dataframe of the data that is housed there
    
"""

def open_google_sheet(sheet_link, sheet_name):
    # searches for the sheet_id given the sheet_link using regular expressions
    match = re.search(r'd/([a-zA-Z0-9-_]+)', sheet_link)
    sheet_id = match.group()
    sheet_id = sheet_id[2:]
    # inserts the searched for sheet_id and the given sheet_name into an f-string
    url_to_open = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
    # opens the google sheet csv and brings it into the Python environment
    google_sheet_df = pd.read_csv(url_to_open)
    return google_sheet_df

"""
    get_google_sheet_info() : this function, based on user input, either
    returns the google sheet that is hardcoded in the .env file as a dataframe
    OR returns a google sheet that is inputted by the user as a dataframe
    
"""

def get_google_sheet_info():
    sheet_link = input('Enter the url to the google sheet here:\n')
    sheet_name = input('Enter the sheet name of the google sheet here:\n')
    if sheet_link == '':
        sheet_link = os.getenv('SHEET_LINK')
        sheet_name = os.getenv('SHEET_NAME')
    df = open_google_sheet(sheet_link, sheet_name)
    return df

"""
    get_html() : this function, given a tiktok url, continuously creates a 
    headless chrome browser instance and tries to grab the url html until a 
    valid, scrapeable html is collected
    
"""

def get_html(url):
    html = ''
    # this counter keeps track of which url htmls have to be recollected
    counter = 0
    # an html length of 26 indicates that the html collected is invalid for our
    # purposes (i.e. no actual information about the video was collected); this 
    # while loop makes sure that a valid html is collected and stored in our 
    # dataframe for future use
    while len(html) <= 26:
        if counter > 0:
            # gives an update regarding the status of the html collection; if 
            # the headless chrome instance has to be launched more than once, 
            # 'trying again' gets printed to the console 
            print('trying again')
        # sets up a headless chrome instance
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        browser = webdriver.Chrome(chrome_options = options, executable_path = chrome_driver)
        browser.get(url)
        # gets a urls html
        html = browser.execute_script('return document.getElementsByTagName(\'html\')[0].innerHTML')
        # print(html)
        browser.close()
        counter = counter + 1
    return html

"""
    get_html() : this function, given a properly formatted dataframe, scrapes 
    metrics by calling the get_html() function; the strings printed give the 
    user a sense of how far along the scrape is
    
"""

def scrape(df):
    print('\nscraping ...\n')
    # gets the shape of the dataframe; used, later, to update the user about 
    # how much of their urls have been processed
    rows, cols = df.shape
    counter = 1
    # iterates through dataframe to grab each individual tiktok url
    for index, row in df.iterrows():
        url = row['url']
        # calls the get_html() function to collect a urls html
        html = get_html(url)
        # inserts the html into the dataframe 
        df.at[index, 'html'] = html
        # gives an update regarding how many of the tiktok urls have been 
        # processed already
        print('%i / %i' % (counter, rows))
        counter = counter + 1
    return df

"""
    parse() : this function, given an dataframe, uses regular expressions to 
    parse through the html string; the 'html' column is dropped beacuse too 
    much information is stored in that column which can cause your editor to 
    crash
    
"""

def parse(df):
    print('\nparsing ...\n')
    for index, row in df.iterrows():  
        html = row['html']
        # uses a regular expression to find "stats" in the html string
        raw_data_metrics = re.findall(r'"stats":\{(.*?)\}', html)
        raw_data_metrics = raw_data_metrics[0]
        raw_data_metrics = '{' + raw_data_metrics + '}'
        # creates a dictionary out of the data for easier access later on
        raw_data_metrics = json.loads(raw_data_metrics)
        df.loc[index, 'likes'] = raw_data_metrics['diggCount']
        df.loc[index, 'comments'] = raw_data_metrics['commentCount']
        df.loc[index, 'shares'] = raw_data_metrics['shareCount']
        df.loc[index, 'views'] = raw_data_metrics['playCount']
        # uses a regular expression to find "authorStats" in the html string
        raw_data_metrics_creator = re.findall(r'"authorStats":\{(.*?)\}', html)
        raw_data_metrics_creator = raw_data_metrics_creator[0]
        raw_data_metrics_creator = '{' + raw_data_metrics_creator + '}'
        # creates a dictionary out of the data for easier access later on
        raw_data_metrics_creator = json.loads(raw_data_metrics_creator)
        df.loc[index, 'followers'] = raw_data_metrics_creator['followerCount'] 
        df.loc[index, 'following'] = raw_data_metrics_creator['followingCount'] 
    df = df.drop(columns = ['html'])
    return df

df = get_google_sheet_info()

# adds some columns to the imported dataframe
df[['html', 'likes', 'comments', 'shares', 'views', 'followers', 'following']] = ''

df = scrape(df)
df = parse(df)

print('RESULTS:\n')
pd.set_option('display.expand_frame_repr', False)
print(df)
