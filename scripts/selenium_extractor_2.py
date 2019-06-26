import numpy as np
import pandas as pd
import time
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# Some global variables
first_link = "https://scholar.google.com/scholar?start=0&q=flame+retardant&hl=en&as_sdt=0,48&as_ylo=2015"
our_html_links = []
pg_counter = 1
wait_time = 6   # changes how long you'd like to wait between flipping pages on Google

def first_page(link,output):
    driver = webdriver.Chrome()                             # opens the chrome webdriver
    driver.get(link)                                        # heads to chrome, goes to page
    elems = scrape(driver)                                  # grabs all elements with an href
    clean_elems = clean(elems)
    for item in clean_elems:
        if type(link) is str:
            output.write(link)
            output.write('\n')
    return driver, clean_elems

def clean(raw_elems):                                       # input the list of raw xpath elements, filters bad links, returns updated html list
    hits = []
    for index, elem in enumerate(raw_elems):
        link = elem.get_attribute("href")

        if 'scholar' not in link and 'void' not in link and\
                                     'pdf' not in link and\
                                     'php' not in link and\
                                     'google' not in link and\
                                     'utm' not in link:
            hits.append(index)
            if len(hits) > 1:                               #after filtering for 'scholar' and 'void' we get the two main links of each article,
                if index - hits[-2] > 5:                    #the page links and the full article links, which appear w/in 5 indices (usually)
                    our_html_links.append(link)

    return our_html_links

def n_pages(driver,max_iters,counter,pg_start,output):              # This method navigates through a desired number of pages on google, scrapes each one
    pg_counter = pg_start                                           # After scraping, the newly scraped htmls are written to the output file
    while counter <= max_iters:
        time.sleep(wait_time)                                       # throttle so Google doesn't think we're robots
        counter += 1
        pgs = driver.find_elements_by_class_name('gs_nma')          # finds a list of the buttons which navigate through the pages

        if pg_counter < 7:                                          # google scholar page format changes slightly upon reaching page 7
            nxt_link = str(pgs[pg_counter].get_attribute('href'))   # grabs the link to the very next page
            driver.get(nxt_link)
            elems = scrape(driver)
            clean_elems = clean(elems)
            our_html_links.append(clean_elems)
            for link in clean_elems:                                # loops through cleaned link list, writes to output file
                if type(link) is str:
                    output.write(link)
                    output.write('\n')
            pg_counter += 1
            print('Size HTML list:  ',len(our_html_links))          # only do this if you want to keep track of the master list size

        else:
            nxt_link = str(pgs[6].get_attribute('href'))
            driver.get(nxt_link)
            elems = scrape(driver)
            clean_elems = clean(elems)
            our_html_links.append(clean_elems)
            for link in clean_elems:                                # loops through cleaned link list, writes to output file
                if type(link) is str:
                    output.write(link)
                    output.write('\n')
            pg_counter += 1
            print('Size HTML list:  ',len(our_html_links))          # only do this if you want to keep track of the master list size

    return our_html_links

def scrape(driver):
    elems = driver.find_elements_by_xpath("//a[@href]")
    return elems

####### Actual executed code is below ######

file = open('html_list.txt','w')                                    # a file with that name must be already located in current dir (I think)

driver,our_html_links = first_page(first_link,file)
our_html_links = n_pages(driver,10,0,1,file)                         # method takes (a) the driver (b) maximum pages to scrape (c) counter start, and (d) page start

driver.quit()
