"""
This code is used to scrape ScienceDirect of publication urls and write them to
a text file in the current directory for later use.
"""

import selenium
from selenium import webdriver
import numpy as np
import pandas as pd
import bs4
from bs4 import BeautifulSoup
import time
from sklearn.utils import shuffle

def scrape_page(driver):
    """
    This method finds all the publication result web elements on the webpage.
    Parameters
    ----------
    driver (Selenium webdriver object) : Instance of the webdriver class e.g.
        webdriver.Chrome()
    Returns
    -------
    elems (list) : A list of all scraped hrefs from the page
    """

    elems = driver.find_elements_by_class_name('ResultItem')
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

    titles = []
    urls = []
    for elem in elems:
        href_child = elem.find_element_by_css_selector('a[href]')
        url = href_child.get_attribute('href')

        title = href_child.text

        titles.append(title)
        urls.append(url)
    return urls, titles

def build_url_list(gui_prefix,search_terms,journal_list):
    """
    This method takes the list of journals and creates a tiple nested dictionary
    containing all accessible urls to each page, in each year, for each journal,
    for a given search on sciencedirect.
    """

    dict1 = {}
    years = np.arange(1995,2020)
    for journal in journal_list:

        dict2 = {}
        for year in years:

            dict3 = {}
            for i in range(60):
                url = gui_prefix + search_terms + '&show=100'+ '&articleTypes=FLA%2CREV' + '&years='+ str(year)

                if i != 0:
                    url = url + '&offset=' + str(i) +'00'
                url = url + '&pub=' + journal

                dict3[i] = url

            dict2[year] = dict3

        dict1[journal] = dict2

    return dict1

def proxify(scraped_urls,uw_prefix):
    """
    This method takes a list of scraped urls and turns them into urls that
    go through the UW Library proxy so that all of them are full access.
    Parameters
    ----------
    scraped_urls (list) : The list of URLs to be converted
    uw_prefix (str) : The string that all URLs which go through the UW Library
        Proxy start with.
    Returns
    -------
    proxy_urls (list) : The list of converted URLs which go through UW Library
        proxy
    """

    proxy_urls = []
    for url in scraped_urls:
        sd_id = url[-17:]
        newlink = uw_prefix + sd_id
        if sd_id.startswith('S'):
            proxy_urls.append(newlink)

    return proxy_urls

def write_urls(urls,titles,file,journal,year):
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
    for link,title in zip(urls,titles):
        line = link + ',' + title + ',' + journal + ',' + str(year)
        file.write(line)
        file.write('\n')

def find_pubTitle(driver,journal):
    """
    This method finds the identifying number for a specific journal. This
    identifying number is added to the gui query URL to ensure only publciations
    from the desired journal are being found.
    """
    pub_elems = driver.find_elements_by_css_selector('input[id*=publicationTitles]')
    pub_names = []

    for elem in pub_elems:
        pub_name = elem.get_attribute("name")
        if pub_name == journal:
            return elem.get_attribute('id')[-6:] #returns the identifying number
                                                 #for that journal




df = pd.read_excel('elsevier_journals.xls')
df.Full_Category = df.Full_Category.str.lower() # lowercase topics for searching
df = df.drop_duplicates(subset = 'Journal_Title') # drop any duplicate journals
df = shuffle(df,random_state = 42)



# The set of default strings that will be used to sort which journals we want
journal_strings = ['chemistry','energy','molecular','atomic','chemical','biochem'
                  ,'organic','polymer','chemical engineering','biotech','coloid']

name = df.Full_Category.str.contains # making this an easier command to type
# new dataframe full of only journals who's topic description contained the
# desired keywords
df2 = df[name('polymer') | name('chemistry') | name('energy')
        | name('molecular') | name('colloid') | name('biochem')
        | name('organic') | name('biotech') | name('chemical')]

journal_list = df2.Journal_Title # Series of only the journals to be searched


gui_prefix = 'https://www.sciencedirect.com/search/advanced?qs='
search_terms = 'chemistry%20OR%20molecule%20OR%20polymer%20OR%20organic'
url_dict = build_url_list(gui_prefix,search_terms,journal_list)

driver = webdriver.Chrome()
uw_prefix = 'https://www-sciencedirect-com.offcampus.lib.washington.edu/science/article/pii/'

filename = input("Input filename with .txt extension for URL storage: ")

url_counter = 0
master_list = []
file = open(filename,'a+')



for journal in journal_list:
    for year in np.arange(1995,2020):
        for offset in np.arange(60):

            page = url_dict[journal][year][offset]
            print("journal, year, offset =  ",journal,year,offset)
            driver.get(page)

            time.sleep(2)           # need sleep to load the page properly
            if offset == 0:         # if on page 1, we need to grab the publisher number
                try:                # we may be at a page which won't have the item we are looking for
                    pubTitles = find_pubTitle(driver,journal_list[journal_counter])
                    for url in url_dict[journal]:
                        url = url + '&pubTitles=' + pubTitles # update every url in the list
                    driver.get(url_dict[journal][year][0])                         # reload the first page with the new url
                except:
                    pass                                        # if there is an exception, it means we are on the right page

            scraped_elems = scrape_page(driver)                 # scrape the page

            scraped_urls, titles = clean(scraped_elems)
            proxy_urls = proxify(scraped_urls,uw_prefix) # not even sure this is needed

            write_urls(proxy_urls,titles,file,journal,year)
            url_counter += len(proxy_urls)
            print('Total URLs saved is: ',url_counter)

            if len(scraped_elems) < 100:    # after content is saved, go to the next year
                break                       # because we know this is the last page of urls for this year

file.close()
driver.quit()
