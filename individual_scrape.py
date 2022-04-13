# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 16:36:51 2022

@author: martyna1221
"""

from selenium import webdriver
import re
import json
import warnings
from dotenv import load_dotenv
import os

warnings.simplefilter("ignore")

load_dotenv()

chrome_driver = os.getenv('CHROME_DRIVER')
chrome_driver = chrome_driver.replace('\\', '/')

print('\nThis script works by scraping one tiktok url at a time. Please try out '
      'this functionality by either (1) inputting a tiktok url of your choice '
      'when prompted OR (2) by simply hitting ENTER; this option scrapes a '
      'random tiktok that is hardcoded into the attached .env file.')

"""
    get_url() : prompts the user to enter a tiktok url that they wish to scrape
    for metrics; otherwise, if let blank, the url to be scraped is set to a
    hardcoded value which can be seen in the attached .env file
    
"""

def get_url():
    url = input('Enter a valid tiktok url here:\n')
    if url == '':
        url = os.getenv('URL')
    return url

"""
    get_html() : this function, given a tiktok url, continuously creates a 
    headless chrome browser instance and tries to grab the url html until a 
    valid, scrapeable html is collected
    
"""

def get_html(url):
    print('\nscraping ...\n')
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
    parse() : this function, given an html, uses regular expressions to parse
    through the html string; in addition, the urls metrics are printed to the
    console
    
"""

def parse(html):
    print('parsing ...\n')
    # uses a regular expression to find "stats" in the html string
    raw_data_metrics = re.findall(r'"stats":\{(.*?)\}', html)
    raw_data_metrics = raw_data_metrics[0]
    raw_data_metrics = '{' + raw_data_metrics + '}'
    # creates a dictionary out of the data for easier access later on
    raw_data_metrics = json.loads(raw_data_metrics)
    likes = raw_data_metrics['diggCount']
    print(f'likes: {likes}')
    comments = raw_data_metrics['commentCount']
    print(f'comments: {comments}')
    shares = raw_data_metrics['shareCount']
    print(f'shares: {shares}')
    views = raw_data_metrics['playCount']
    print(f'views: {views}')
    # uses a regular expression to find "authorStats" in the html string
    raw_data_metrics_creator = re.findall(r'"authorStats":\{(.*?)\}', html)
    raw_data_metrics_creator = raw_data_metrics_creator[0]
    raw_data_metrics_creator = '{' + raw_data_metrics_creator + '}'
    # creates a dictionary out of the data for easier access later on
    raw_data_metrics_creator = json.loads(raw_data_metrics_creator)
    followers = raw_data_metrics_creator['followerCount'] 
    print(f'followers: {followers}')
    following = raw_data_metrics_creator['followingCount'] 
    print(f'following: {following}\n')

url = get_url()
html = get_html(url)
parse(html)

# opens the url via selenium so that you can cross reference the printed 
# metrics against the metrics that can be viewed on the website
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
browser = webdriver.Chrome(chrome_options = options, executable_path = chrome_driver)
browser.get(url)

print('Now you can cross reference the metrics printed in the console against '
      'the metrics found on the webpage.')
