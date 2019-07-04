import selenium
from selenium import webdriver
import numpy as np
import pandas as pd
import bs4
from bs4 import BeautifulSoup
import time

'''
This code is used to scrape ScienceDirect of publication urls and write them to
a text file in the current directory for later use.

Before running this code you must:

(1) Go to sciencedirect.com and search for the publication keywords you're
    interested in (i.e. 'organic flame retardant').

(2) Once the page is loaded, there is a 'Refine By' section on the left where you
    select the years you would like publications from.

(3) In the same 'Refine By' section you must select 'Review articles' and
    'Research articles'

(4) *Important: Scroll to the bottom of the page as click the option to display
    100 links at a time.

An examplary link for 'corrosion inhibitor synthesis'is shown here:

'https://www.sciencedirect.com/search?qs=corrosion%20inhibitor%20synthesis&show=100&sortBy=relevance&origin=home&zone=qSearch&years=2021%2C2020%2C2019%2C2018%2C2017%2C2016%2C2015%2C2014%2C2013%2C2012%2C2011%2C2010&articleTypes=REV%2CFLA'
'''

def scrape_page(driver):
    '''
    This method finds all hrefs on webpage
    '''

    elems = driver.find_elements_by_xpath("//a[@href]")
    return elems


def clean(elems):
    '''
    This method takes a list of scraped selenium web elements
    and filters/ returns only the hrefs leading to publications.
    '''

    urls = []
    for elem in elems:
        url = elem.get_attribute("href")
        if 'article' in url and 'pdf' not in url\
                            and 'search' not in url\
                            and 'show=' not in url:
            urls.append(url)
    return urls

def get_pages(first_url):
    '''
    This method takes the first SD url and creates a list of
    urls which lead to the following pages on SD which will be
    scraped.
    '''

    page_urls = []
    for i in range(60):
        urli = first_url + '&offset=' + str(i) + '00'
        page_urls.append(urli)

    return page_urls

def scrape_all(first_url,driver):
    '''
    This method takes the first ScienceDirect url and navigates
    through all 60 pages of listed publications, scraping each url
    on each page. Returns a list of the urls.
    '''
    page_list = get_pages(first_url)
    urls = []
    for page in page_list:
        driver.get(page)
        time.sleep(1.5) #must sleep to allow page to load
        elems = scrape_page(driver)
        links = clean(elems)
        for link in links:
            urls.append(link)


    return urls


def proxify(scraped_urls,prefix):
    '''
    This method takes a list of scraped urls and turns them into urls that
    go through the UW Library proxy so that all of them are full access.
    '''

    proxy_urls = []
    for url in scraped_urls:
        sd_id = url[-17:]
        newlink = prefix + sd_id
        proxy_urls.append(newlink)

    return proxy_urls

def write_urls(urls,filename):
    '''
    This method takes a list of urls and writes them to a desired text file.
    '''
    file = open(filename,'w')
    for link in urls:
        file.write(link)
        file.write('\n')


driver = webdriver.Chrome()
prefix = 'https://www-sciencedirect-com.offcampus.lib.washington.edu/science/article/pii/'

first_url = input("Copy/Paste the ScienceDirect URL here: ")
filename = input("Input filename with .txt extension you wish to store urls in: ")

scraped_urls = scrape_all(first_url,driver)
proxy_urls = proxify(scraped_urls,prefix)
write_urls(proxy_urls,filename)

driver.quit()
