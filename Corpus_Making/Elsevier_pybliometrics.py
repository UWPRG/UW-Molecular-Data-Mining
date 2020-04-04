#!/usr/bin/env python
# coding: utf-8

import pybliometrics
from pybliometrics.scopus import ScopusSearch
from pybliometrics.scopus.exception import Scopus429Error
import pandas as pd
import numpy as np
from sklearn.utils import shuffle
import os
import multiprocessing
from os import system, name
import json
import time
from IPython.display import clear_output
from pybliometrics.scopus import config
import click

def make_jlist(jlist_url = 'https://www.elsevier.com/__data/promis_misc/sd-content/journals/jnlactivesubject.xls', 
               journal_strings = ['chemistry','energy','molecular','atomic','chemical','biochem'
                                  ,'organic','polymer','chemical engineering','biotech','colloid']):
    """
    This method creates a dataframe of relevant journals to query. The dataframe contains two columns:
    (1) The names of the Journals
    (2) The issns of the Journals
    
    As inputs, the URL for a journal list and a list of keyword strings to subselect the journals by is required.
    These values currently default to Elsevier's journals and some chemical keywords.
    """
    
    # This creates a dataframe of the active journals and their subjects from elsevier
    active_journals = pd.read_excel(jlist_url)
    # This makes the dataframe column names a smidge more intuitive.
    active_journals.rename(columns = {'Display Category Full Name':'Full_Category','Full Title':'Journal_Title'}, inplace = True)
    
    active_journals.Full_Category = active_journals.Full_Category.str.lower() # lowercase topics for searching
    active_journals = active_journals.drop_duplicates(subset = 'Journal_Title') # drop any duplicate journals
    #Randomize the ordering of the journals so we don't introduce bias
    active_journals = shuffle(active_journals, random_state = 42) 

    # new dataframe full of only journals who's topic description contained the desired keywords
    active_journals = active_journals[active_journals['Full_Category'].str.contains('|'.join(journal_strings))]
    
    #Select down to only the title and the individual identification number called ISSN
    journal_frame = active_journals[['Journal_Title','ISSN']]
    #Remove things that have were present in multiple name searches.
    journal_frame = journal_frame.drop_duplicates(subset = 'Journal_Title')
    
    return journal_frame

def build_search_terms(kwds):
    """
    This builds the keyword search portion of the query string from a list of keywords. 
    The words must be separated by a capital OR or they won't all be searched for.
    """
    combined_keywords = ""
    for i in range(len(kwds)):
        if i != len(kwds)-1:
            combined_keywords += kwds[i] + ' OR '
        else:
            combined_keywords += kwds[i] + ' '
    
    return combined_keywords

def build_query_dict(term_list, issn_list, year_list):
    """
    This method takes the list of journals and creates a nested dictionary
    containing all accessible queries, in each year, for each journal,
    for a given keyword search on sciencedirect.
    
    Parameters
    ----------
    term_list(list, required): the list of search terms looked for in papers by the api.
    
    issn_list(list, required): the list of journal issn's to be queried. Can be created by getting the '.values'
    of a 'journal_list' dataframe that has been created from the 'make_jlist' method.
    
    year_list(list, required): the list of years which will be searched through
    
    """
    search_terms = build_search_terms(term_list)
    dict1 = {}
    #This loop goes through and sets up a dictionary key with an ISSN number
    for issn in issn_list:
        
        issn_terms = ' AND ISSN(' + issn + ')'
        dict2 = {}
        #This loop goes and attaches all the years to the outer loop's key.
        for year in year_list:
            
            year_terms = "AND PUBYEAR IS " + str(year)
            querystring = search_terms + year_terms + issn_terms

            dict2[year] = querystring

        dict1[issn] = dict2

    return dict1


def get_piis(term_list, journal_frame, year_list, cache_path, output_path, keymaster = False, fresh_keys = None, 
             config_path = '/Users/DavidCJ/.scopus/config.ini'):
    """
    This should be a standalone method that recieves a list of journals (issns), a keyword search,
    an output path and a path to clear the cache. It should be mappable to multiple parallel processes. 
    """
    #Double check and make sure that the paths are 
    if output_path[-1] is not '/':
        raise Exception('Output file path must end with /')
    
    if '.scopus/scopus_search' not in cache_path:
        raise Exception('Cache path is not a sub-directory of the scopus_search. Make sure cache path is correct.')
    
    # Separating out the dataframe into individual lists    
    issn_list = journal_frame['ISSN'].values
    journal_list = journal_frame['Journal_Title'].values
    
    # Find and replaces slashes and spaces in names for file saving purposes
    for j in range(len(journal_list)):
        if ':' in journal_list[j]:
            journal_list[j] = journal_list[j].replace(':','')
        elif '/' in journal_list[j]:
            journal_list[j] = journal_list[j].replace('/','_')
        
        elif ' ' in journal_list[j]:
            journal_list[j] = journal_list[j].replace(' ','_')
    
    # Build the dictionary that can be used to sequentially query elsevier for different journals and years
    query_dict = build_query_dict(term_list,issn_list,year_list)
    
    # Must write to memory, clear cache, and clear a dictionary upon starting every new journal
    for i in range(len(issn_list)):
        # At the start of every year, clear the standard output screen
        os.system('cls' if os.name == 'nt' else 'clear')
        paper_counter = 0

        issn_dict = {}
        for j in range(len(year_list)):
            # for every year in every journal, query the keywords
            print(f'{journal_list[i]} in {year_list[j]}.')
            
            # Want the sole 'keymaster' process to handle 429 responses by swapping the key. 
            if keymaster:
                try:
                    query_results = ScopusSearch(verbose = True,query = query_dict[issn_list[i]][year_list[j]])
                except Scopus429Error:
                    print('entered scopus 429 error loop... replacing key')
                    newkey = fresh_keys.pop(0)
                    config["Authentication"]["APIKey"] = newkey
                    time.sleep(5)
                    query_results = ScopusSearch(verbose = True,query = query_dict[issn_list[i]][year_list[j]])
                    print('key swap worked!!')
            # If this process isn't the keymaster, try a query. 
            # If it excepts, wait a few seconds for keymaster to replace key and try again.
            else:
                try:
                    query_results = ScopusSearch(verbose = True,query = query_dict[issn_list[i]][year_list[j]])
                except Scopus429Error:
                    print('Non key master is sleeping for 15... ')
                    time.sleep(15)
                    # at this point, the scopus 429 error should be fixed... 
                    query_results = ScopusSearch(verbose = True,query = query_dict[issn_list[i]][year_list[j]]) 
                    print('Non key master slept, query has now worked.')
            
            # store relevant information from the results into a dictionary pertaining to that query
            year_dict = {}
            if query_results.results is not None:
                # some of the query results might be of type None 
                
                #If the results aren't None, store each of the resultant components in a single dictionary
                for k in range(len(query_results.results)):
                    paper_counter += 1
                    
                    result_dict = {}
                    result = query_results.results[k]

                    result_dict['pii'] = result.pii
                    result_dict['doi'] = result.doi
                    result_dict['title'] = result.title
                    result_dict['num_authors'] = result.author_count
                    result_dict['authors'] = result.author_names
                    result_dict['description'] = result.description
                    result_dict['citation_count'] = result.citedby_count
                    result_dict['keywords'] = result.authkeywords
                    
                    year_dict[k] = result_dict

                # Store all of the results for this year in the dictionary containing to a certain journal
                issn_dict[year_list[j]] = year_dict
            else:
                # if it was a None type, we will just store the empty dictionary as json
                issn_dict[year_list[j]] = year_dict
        
        
        # Store all of the results for this journal in a folder as json file
        os.mkdir(f'{output_path}{journal_list[i]}')
        with open(f'{output_path}{journal_list[i]}/{journal_list[i]}.json','w') as file:
            json.dump(issn_dict, file)
        
        with open(f'{output_path}{journal_list[i]}/{journal_list[i]}.txt','w') as file2:
            file2.write(f'This file contains {paper_counter} publications.')
            
# def multiprocess(term_list, journal_frame, year_list, cache_path, output_path, keymaster = False, fresh_keys = None, config_path = '/Users/Jonathan/.scopus/config.ini', split_ratio = 2):
#     """This call allows the user to multithread if desired. It should speed up scraping, though it'll 
#     likely also take more computational resources."""
    # split_list = np.array_split(journal_frame, split_ratio)
    #     for k in range(split_ratio):
    #         print("Before multiprocessing")
    #         p = multiprocessing.Process(target = get_piis, args = [term_list, split_list[k], year_list, cache_path, output_path, keymaster, fresh_keys, config_path])
    #         print("after multiprocessing")
    #         p.start()    


#Turns out you can't pass lists like this to click. We're not going to be able to use command-line arguments to call this function
@click.command()
@click.option('--terms','-t', required=True,type=list,help='List of search keywords within articles, formatted ["x", "y", "z"]')
@click.option('--jtopics','-jtop', required=True,type=list,help='List of search terms for full journals, formatted ["x", "y", "z"]')
@click.option('--year_list', '-yrs', required=True,type=list,help='List of all years you would like to access journal articles from')
@click.option('--cache', '-ch', required=True, type =str, help='a string that points to the path for the pybiblio cache')
@click.option('--output', '-out', required=True, type=str, help='A string that points to the path you want the metadata saved to')
@click.option('--keymaster', '-key', required=False, type=bool, help='Boolean for if you want keymaster enabled')
@click.option('--apikeylist', '-api', required=False, type=list, help='A list of API keys for Scopus.')
@click.option('--config', '-con', required=False, type = str, help='The path to the config file for pybiblio')
def main(terms, jtopics, year_list, cache, output, keymaster = True, apikeylist = 
         ['646199a6755da12c28f3fdfe59bbfe55'], config = '/Users/Jonathan/.scopus/config.ini'):
    journal_url = 'https://www.elsevier.com/__data/promis_misc/sd-content/journals/jnlactivesubject.xls'
    journal_frame = make_jlist(journal_url, jtopics)
    get_piis(terms, journal_frame, year_list, cache, output, keymaster, apikeylist, config)

if __name__ == "__main__":
    main()
