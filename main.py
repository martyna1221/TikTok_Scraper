# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 14:45:17 2022

@author: martyna1221
"""

"""

    HELLO

    Follow the prompts to scrape some tiktoks. You can scrape an individual 
    tiktok url and batches of tiktok urls. 
    
    Somethings to keep in mind:
        (1) Download chromedriver : 
            (a) Download chromedriver from https://chromedriver.chromium.org/downloads
            (b) Download chrome from https://www.google.com/chrome/downloads/
            (c) Download the chromedriver specific to your OS & chrome browser
                version
        (2) Input path to chromedriver executable in the .env file
        (3) Input 'pip install -r requirements.txt' into your console; this
            installs the required packages to run the program
            
"""

c = 1

# prompts user for input until they wish to exit the program
while c == 1:
    
    # prompts user for selection
    selection = input('Enter :\n'
                      '1 --- individual scraper\n'
                      '2 --- batch scraper\n\n')

    selection = int(selection)
    
    if selection == 1:
        exec(open('individual_scrape.py').read())
    if selection == 2:
        exec(open('batch_scrape.py').read())
        
    selection = input('Enter :\n'
                      '1 --- continue scraping\n'
                      '2 --- exit scraping\n\n')
    selection = int(selection)
    
    c = selection
    

