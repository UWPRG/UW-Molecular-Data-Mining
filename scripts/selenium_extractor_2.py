#!/usr/bin/env python

import time

import click
import numpy as np
import pandas as pd
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

pg_counter = 1

def get_first_page(url, output):
    # opens the chrome webdriver
    driver = webdriver.Chrome()
    # heads to chrome, goes to page
    driver.get(url)
    # grabs all elements with an href
    elems = scrape(driver)
    clean_elems = clean(elems)
    for item in clean_elems:
        if type(url) is str:
            output.write(url)
            output.write('\n')
    return driver, clean_elems


def clean(raw_elems):
    """
    input the list of raw xpath elements, filters bad urls, returns updated html list
    """
    hits = []
    urls = []
    for index, elem in enumerate(raw_elems):
        url = elem.get_attribute("href")

        if 'scholar' not in url and 'void' not in url and\
                                     'pdf' not in url and\
                                     'php' not in url and\
                                     'google' not in url and\
                                     'utm' not in url:
            hits.append(index)
            # after filtering for 'scholar' and 'void' we get the two main urls of each article,
            if len(hits) > 1:
                # the page urls and the full article urls, which appear w/in 5 indices (usually)
                if index - hits[-2] > 5:
                    urls.append(url)

    return urls


def n_pages(driver, max_iters, counter, pg_start, output, wait_time):
    """
    This method navigates through a desired number of pages on google, scrapes each one
    After scraping, the newly scraped htmls are written to the output file
    """
    pg_counter = pg_start
    urls = []
    while counter <= max_iters:
        # throttle so Google doesn't think we're robots
        time.sleep(wait_time)
        counter += 1
        # finds a list of the buttons which navigate through the pages
        pgs = driver.find_elements_by_class_name('gs_nma')

        # google scholar page format changes slightly upon reaching page 7
        if pg_counter < 7:
            # grabs the url to the very next page
            nxt_url = str(pgs[pg_counter].get_attribute('href'))
        else:
            nxt_url = str(pgs[6].get_attribute('href'))

        driver.get(nxt_url)
        elems = scrape(driver)
        clean_elems = clean(elems)
        urls.append(clean_elems)
        # loops through cleaned url list, writes to output file
        for url in clean_elems:
            if type(url) is str:
                output.write(url)
                output.write('\n')
        pg_counter += 1

    return urls


def scrape(driver):
    elems = driver.find_elements_by_xpath("//a[@href]")
    return elems


@click.command()
@click.option('-o', '--output_file', 'output_file', type=str, required=True,
            help='name of the output file to contant the list of HTML urls')
@click.option('-f', '--first_url', 'first_url', type=str, required=False,
            default='https://scholar.google.com/scholar?start=0&q=flame+retardant&hl=en&as_sdt=0,48&as_ylo=2015',
            show_default=True,
            help='URL that the crawler should use as the search base')
@click.option('-w', '--wait_time', 'wait_time', type=int, required=False,
            default=6, show_default=True,
            help='time in second between page fetches')
@click.option('-m', '--max_iters', 'max_iters', type=int, required=False,
            default=10, show_default=True,
            help='maximum number of iterations (pages to fetch)')
def selenium_extractor(output_file, first_url, wait_time, max_iters):
    # NOTE, urls is constructed but nothing is done with it
    with open(output_file, 'w') as f:
        driver, urls = get_first_page(first_url, f)
        # NOTE, subsequent calls to this, in a loop would increment ocunter and pg_start
        urls.extend(
                n_pages(driver, max_iters=10, counter=0, pg_start=1, 
                        output=f, wait_time=wait_time)
            )

    print('collected %d total URLS' % (len(urls)))
    print(urls)

    driver.quit()


if __name__ == '__main__':
    selenium_extractor()
