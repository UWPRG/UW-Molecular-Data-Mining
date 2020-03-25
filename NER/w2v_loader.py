"""
This script is for training word2vec on a corpus of text collected by the elsapy/pyblio modules
"""
"""
@DACB: All functions before SingleLoader class are helper functions for SingleLoader().
    I have successfully used SingleLoader() as a generator for creating word embeddings
    with word2vec. That successful run was done with lines 188-197.

    The goal now is to create MultiLoader(), which, from the perspective of Word2Vec,
    needs to have the exact same functionality as SingleLoader(), except sourcing multiple
    journals instead of just one.

    The important functionality we want to keep is to generate a sequence of sentences via
    the __iter__ function. Each sentence is a sequence of tokens split by whitespace.

    Question is: Does my use of text_loader.__iter__() make sense on line 163, will
        MultiLoader() generate sentences just as SingleLoader() did, just from more journals.
"""
import numpy as np
import pandas as pd
import gensim
import gensim, logging
from gensim.models import Word2Vec
import json
import os
import time
import random

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


class SingleLoader():
    """
    This class creates an iterator that can yield sentences from a given journal
    into gensim's Word2Vec.
    """

    def __init__(self, journal_directory, years='all', retrieval_type='fulltext'):
        """
        This method creates an object, ready to iter through the tokens in a
        journal dictionary's 'fulltext' entry, or 'abstract' entry. This class
        can be used as a sentence generator to train word2vec.

        Parameters:
            journal_directory (str, required): The absolute path to the journal
                .json file being used

            years (list-like, optional): List of years from which to pull publication
                data from. If left as 'all', all the years will be done.

            retrieval_type (str, optional): Produce abstracts, or fulltexts. Use
                'abstract' for the former, and 'fulltext' for the latter.
        """

        self.journal_directory = journal_directory
        self.years = years
        self.retrieval_type = retrieval_type

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

                    year_dict = journal_dict[year]

                    for paper_number in year_dict:
                        paper_dict = year_dict[paper_number]

                        if self.retrieval_type == 'fulltext':
                            text = paper_dict['fulltext']
                        else: # it was 'abstract', this may be dangerous logic, fix soon
                            text = paper_dict['description']

                        text = clean_paper(text)
                        paper_counter += 1
                        print('Papers is at ',paper_counter)

                        for sentence in sent_tokenize(text):
                            words = sentence.split() # don't want word_tokenize
                            yield(words)

class MultiLoader():
    """
    This class creates an object able to iterate through multiple journal-dictionaries
    worth of abstracts/fulltexts.
    """

    def __init__(self, journal_directory_list, years='all', retrieval_type='fulltext'):
        """
        This method initializes the multiloader object

        Parameters:
            journal_directory_list (list, required): list of absolute paths to all journals
                being included in the iterator object.
        """
        self.journal_directory_list = journal_directory_list
        self.years = years
        self.retrieval_type = retrieval_type

    def __iter__(self):
        """
        This method iterates through every sentence of all journals included in the
        journal list. Grabs either abstracts or fulltexts according to retrieval_type. 
        """
        for journal_directory in self.journal_directory_list:
            text_loader = SingleLoader(journal_directory, years = self.years,
                                       retrieval_type = self.retrieval_type)
            text_loader.__iter__()

### DACB, here is the new bit I'm unsure will work
def w2v_main():
    """
    Method to execute training of word2Word2Vec
    """
    corpus_path = '/gscratch/pfaendtner/dacj/nlp/fulltext_pOmOmOo/'
    j_carbon = 'Carbon'
    j_organometallic = 'Journal_of_Organometallic_Chemistry'
    j_inorg_biochem = 'Journal_of_Inorganic_Biochemistry'
    jlist = [corpus_path + j_carbon, corpus_path + j_organometallic, corpus_path + j_inorg_biochem]

    # creating the multiloader iterator object
    multi_j_loader = MultiLoader(multi_j_loader, years='all', retrieval_type='abstract')

    # calling Word2Vec in the same manner I did with a
    model = Word2Vec(multi_j_loader, min_count=10, workers=1, size=200)
    os.chdir('/gscratch/pfaendtner/dacj/nlp/3_journal_model/')
    model.save('3_journal_model.model')

w2v_main()

######################################### For DACB, below is the old call for a single journal that worked

# def w2v_main():
#      """
#      This is the main method to be executed
#      """
#      generator = SingleLoader('/gscratch/pfaendtner/dacj/nlp/fulltext_pOmOmOo/Carbon')
#      model = Word2Vec(generator, min_count=10, workers=1, size=200)
#      os.chdir('/gscratch/pfaendtner/dacj/nlp')
#      model.save('carbon.model')
#
#  w2v_main()
