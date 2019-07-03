import numpy as np
import pandas as pd
import selenium
from selenium import webdriver
import bs4
from bs4 import BeautifulSoup
import time

def extract(url,driver,wait_time):
    '''
    This method takes a url, webdriver, and a desired wait time for loading
    pages. It saves html source code from site as BeautifulSoup object, then

    '''


    driver.get(url)
    time.sleep(wait_time) # important


    source = driver.page_source
    soup = BeautifulSoup(source,'html.parser')

    title = soup.title.text
    abstract = soup.find('div', {'class':"Abstracts u-font-serif"}).text

    try:
        doi = soup.find('div', {'id':"doi-link"}).text
    except:
        print('Oops, no DOI for some reason.')
        doi = None

    try:
        body = soup.find('div', {'id' :"body"}).text
    except:
        print('Oops, no html body.')
        body = None

    try:
        refs = soup.find('div' > 'dl', {'class' : "references"})
        children = refs.findChildren("dd" , recursive=False)
    except:
        print('Oops, no references.')
        refs = None
        children = None

    #list = [title,abstract,doi,body,children]
    return body

def parse_all(df,max_iters,driver,file):
    title1 = extract(df.iloc[1,0], driver,10)
    file.write(title1)
    file.write('\n')

    for i in range(2,max_iters):
        print('On page ',i)
        try:
            title = extract(df.iloc[i,0],driver,2)
            file.write(title)
            file.write('\n')
        except:
            print('Oops, page refresh should do the trick.')
            driver.refresh()
            time.sleep(2)
            title = extract(df.iloc[i,0],driver,2)
            file.write(title)
            file.write('\n')



df = pd.read_csv('organic_sd_urls.txt',header = None, names = ['url'])
driver = webdriver.Chrome()

file = open('organic_body.txt','w')

parse_all(df,3,driver,file)






driver.quit()
