"""
This code is used to scrape ScienceDirect of publication urls and write them to
a text file in the current directory for later use.

To use this code, go to ScienceDirect.com and search for the topic of interest.
Then, copy the URL and paste it into terminal when prompted for user input.

"""

import selenium
from selenium import webdriver
import numpy as np
import pandas as pd
import bs4
from bs4 import BeautifulSoup
import time

def scrape_page(driver):
    """
    This method finds all hrefs on webpage

    Parameters
    ----------
    driver (Selenium webdriver object) : Instance of the webdriver class e.g.
        webdriver.Chrome()


    Returns
    -------
    elems (list) : A list of all scraped hrefs from the page

    """

    elems = driver.find_elements_by_xpath("//a[@href]")
    return elems


def clean(elems):
    """
    This method takes a list of scraped selenium web elements
    and filters/ returns only the hrefs leading to publications.

    Filtering includes removing all urls with keywords that are indicative of
    non-html links.

    Parameters
    ----------
    elems (list) : The list of hrefs to be filtered

    Returns
    -------
    urls (list) : The new list of hrefs, which should be the same as the list
        displayed on gui ScienceDirect

    """

    urls = []
    for elem in elems:
        url = elem.get_attribute("href")
        if 'article' in url and 'pdf' not in url\
                            and 'search' not in url\
                            and 'show=' not in url:
            urls.append(url)
    return urls

def build_annual_urls(first_url,year):
    """
    This method takes the first SD url and creates a list of
    urls which lead to the following pages on SD which will be
    scraped. The page list is for a given year.

    Parameters
    ----------
    first_url (str) : The URL from ScienceDirect after searching for desired
        keywords

    year (str or int) : The given year the URL list is being built for


    Returns
    -------
    page_urls (list) : List of urls the webdriver will use to access all
        available pages for a given year on a given topic

    """

    page_urls = []
    for i in range(20):
        url_100 = first_url.replace('&show=25','&show=100')
        urli = url_100 + '&offset=' + str(i) + '00' + '&articleTypes=REV%2CFLA' + '&years=' + str(year)
        page_urls.append(urli)

    return page_urls

def scrape_all(first_url,driver,year):
    """
    This method takes the first ScienceDirect url and navigates
    through all 60 pages of listed publications, scraping each url
    on each page. Returns a list of the urls. Scrapes all urls for a given year.

    Parameters
    ----------
    first_url (str) : The very first ScienceDirect URL after keyword search

    driver (Selenium webdriver object) : Instance of a selenium webdriver
        e.g. webdrive.Chrome()

    year (str or int) : The current year being scraped

    Returns
    -------
    urls (list) : A list of all collected urls for a given year

    """
    page_list = build_annual_urls(first_url,year)
    urls = []
    for page in page_list:
        driver.get(page)
        time.sleep(1) #must sleep to allow page to load
        elems = scrape_page(driver)
        links = clean(elems)
        if len(links) < 2:
            break
        for link in links:
            urls.append(link)


    return urls


def proxify(scraped_urls,prefix):
    """
    This method takes a list of scraped urls and turns them into urls that
    go through the UW Library proxy so that all of them are full access.

    Parameters
    ----------
    scraped_urls (list) : The list of URLs to be converted

    prefix (str) : The string that all URLs which go through the UW Library
        Proxy start with.

    Returns
    -------
    proxy_urls (list) : The list of converted URLs which go through UW Library
        proxy

    """

    proxy_urls = []
    for url in scraped_urls:
        sd_id = url[-17:]
        newlink = prefix + sd_id
        if sd_id.startswith('S'):
            proxy_urls.append(newlink)

    return proxy_urls

def write_urls(urls,file,year):
    """
    This method takes a list of urls and writes them to a desired text file.

    Parameters
    ----------
    urls (list) : The list of URLs to be saved.

    file (file object) : The opened .txt file which will be written to.

    year (str or int) : The year associated with the publication date.


    Returns
    -------
    Does not return anything

    """
    for link in urls:
        line = str(year) + ',' + link
        file.write(line)
        file.write('\n')



driver = webdriver.Chrome()
prefix = 'https://www-sciencedirect-com.offcampus.lib.washington.edu/science/article/pii/'

first_url = input("Copy/Paste the ScienceDirect URL here: ")
print('\n')
filename = input("Input filename with .txt extension you wish to store urls in: ")

master_list = []
years = np.arange(1990,2021)
file = open(filename,'w')

for year in years:
    year = str(year)
    scraped_urls = scrape_all(first_url,driver,year)
    proxy_urls = proxify(scraped_urls,prefix)
    for link in proxy_urls:
        master_list.append(link)
    print('Number of URLs collected = ',len(master_list))
    print('Year is: ',year)
    write_urls(proxy_urls,file,year)

driver.quit()
