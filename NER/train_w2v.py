"""
This script is for training word2vec on a corpus of text collected by the elsapy/pyblio modules
"""
import numpy as np
import pandas as pd
import gensim
import gensim, logging
from gensim.models import Word2Vec
import json
import os
import time

from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize

def find_nth(haystack, needle, n):
    """
    This function finds the index of the nth instance of a substring
    in a string
    """
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start

def clean_paper(paper):
    """
    This method takes a single paper and does all the rule-based text preprocessing.

    Parameters:
    ___________
    paper (str): The single paper to be preprocessed

    Returns:
    ________
    paper (str): The cleaned and preprocessed paper
    """
   # this series of statements cuts off the abstract/highlights/references/intro words
   # this method needs to be fixed, the elif sentences don't totally make sense
    if paper.lower().count('highlights') != 0:
        h_index = paper.lower().find('highlights')
        paper = paper[h_index + len('highlights'):] 

    elif paper.lower().count('abstract') != 0:
        a_index = paper.lower().find('abstract')
        paper = paper[a_index + len('abstract'):]

    elif paper.lower().count('introduction') != 0:
        i_index = find_nth(paper.lower(),'introduction',2)
        paper = paper[i_index + len('introduction'):]

    else:
        pass

    r_index = paper.rfind('References')
    paper = paper[:r_index]

    return paper


class SentencesFromJournal():
    """
    This class creates an iterator that can yield sentences from a given journal.
    """

    def __init__(self, journal_directory):
        # this is the path to the directory to the journal that will be iterated through 
        self.journal_directory = journal_directory

    def __iter__(self):
        for filename in os.listdir(self.journal_directory):
        # only open the json file in the directory for the journal
        # this for loop is super quick but there is probably a better way
        # just grab the json
            if '.json' in filename:
                paper_counter = 0
                word_counter = 0
                os.chdir(self.journal_directory)
                with open(filename) as json_file:
                    journal_dict = json.load(json_file)

                for year in journal_dict:
                    #if int(year) >= 1996:
                    # print('number of words is ',word_counter)
                    # break
                    #print('number of papers is ',paper_counter)
                    year_dict = journal_dict[year]

                    for paper_number in year_dict:
                        paper_dict = year_dict[paper_number]

                        fulltext = paper_dict['fulltext']
                        fulltext = clean_paper(fulltext)
                        paper_counter += 1
                        print('Papers is at ',paper_counter)
                        #print('counter is at ', paper_counter, ' papers.')

                        for sentence in sent_tokenize(fulltext):
                            words = word_tokenize(sentence)
                            yield(words)


def main():
    """
    This is the main method to be executed
    """
    generator = SentencesFromJournal('/gscratch/pfaendtner/dacj/nlp/fulltext_pOmOmOo/Carbon')
    model = Word2Vec(generator, min_count=10, workers=1, size=200)
    os.chdir('/gscratch/pfaendtner/dacj/nlp')
    model.save('carbon.model')

main()
