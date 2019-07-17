import numpy as np
import pandas as pd
import selenium
from selenium import webdriver
import bs4
from bs4 import BeautifulSoup
import time

def extract(url,driver,wait_time):
    """
    This method saves html source code from site as a BeautifulSoup object, then
    parses through the source code to extract information from the html.

    Parameters
    ----------
    url (str) : The url Selenium will navigate to.

    driver (Selenium webdriver object) : Instance of webdriver e.g.
        webdriver.Chrome()

    wait_time (int or float) : The desired wait time between pages, usually
        don't go below ~1-1.5 seconds to ensure page can load

    Returns
    -------
    Can return Title, Abstract, Body, References, DOI

    If one of the above texts is unnavailable within the souce code, return
    type for that text is changed to None
    """


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
    """
    This method loops through the list of URLs in a dataframe to extract all
    import aspects of a paper (located at each url).

    Parameters
    ----------
    df (Pandas dataframe) : The dataframe containing all URLs to be parsed.
        The urls must be located in the first column of the dataframe.

    max_iters (int) : The number of URLs in the data frame you would like to
        parse through

    driver (Selenium webdriver object) : e.g. webdriver.Chrome()

    file (file object) : The file where text from the paper is to be stored

    Returns
    -------
    No returns

    """
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
