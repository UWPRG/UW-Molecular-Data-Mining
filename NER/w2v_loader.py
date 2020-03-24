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


class Loader():
    """
    This class creates an iterator that can yield sentences from a given journal
    into gensim's Word2Vec.
    """

    def __init__(self, journal_directory, years='all', retrieval_type='fulltext', mode='w2v'):
        """
        This method creates an object, ready to iter through the tokens in a
        journal dictionary's 'fulltext' entry, or 'abstract' entry. This class
        can be used as a sentence generator to train word2vec, or to produce
        training data for labeling.

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
                        else: # it was 'abstract'
                            text = paper_dict['abstract']

                        text = clean_paper(text)
                        paper_counter += 1
                        print('Papers is at ',paper_counter)
                        #print('counter is at ', paper_counter, ' papers.')

                        for sentence in sent_tokenize(text):
                            words = word_tokenize(sentence)
                            yield(words)


def make_ner_sheet(journal_directory, retrieval_type='abstract', years='all', scramble=True,
                   pick_random=True, num_papers=1000, seed=42, pubs_per_sheet=100):
    """
    This function prepares text data to be labeled for NER training in excel spreadsheet.
    Attempts to pull papers from all years as equally as possible.

    Parameters:
        journal_directory (str, required): The absolute path to the journal directory

        retrieval_type (str, optional): Produce abstracts, or fulltexts. Use
            'abstract' for the former, and 'fulltext' for the latter.

        years (list-like, optional): List of years to collect papers from. If left
            as 'all', will grab papers from all years possible.

        scramble (bool, optional): Whether to scramble the papers year-wise throughout
            the excel spreadsheets, so the years from which the labeled data come from
            end up reasonably homogenous

        num_papers (int, optional): How many papers to put in the spreadsheets.
            Ceder et al stopped improving training accuracy after about 600-650
            abstracts worth of NER data.
    """
    files = os.listdir(journal_directory)

    # find the .json file, containing all the publication data
    for filename in files:
        if filename.endswith('.json'):
            json_filename = filename
            break

    # find the jounal .json and make a dictionary from it
    paper_counter = 0
    os.chdir(journal_directory)
    with open(json_filename) as json_file:
        journal_dict = json.load(json_file)

    # calculate the publications per year we need
    if years != 'all':
        num_years = len(years)
        pubs_per_year = num_papers / num_years
    else:
        # the first layer of dictionaries in journal_dict corresponds to all the
        # years, so the number of keys will tell us how many pubs for each year
        num_years = len(journal_dict.keys())
        pubs_per_year = num_papers / num_years

    if years == 'all':
        year_list = journal_dict.keys()
    else:
        year_list = years

    pubs = []
    pub_infos = []
    for year in year_list:


        year_dict = journal_dict[year]
        pubs_from_year = 0
        longest_paper = find_longest_paper(year_dict, text_type = retrieval_type)

        random.seed(seed)
        pub_idxs = random.sample(range(len(year_dict)), pubs_per_year)

        while pubs_from_year < pubs_per_year:
            pubs_from_year += 1

            # going to try/except because we don't know if pubs_per_year will
            # be greater than the number of publications in any of the years
            try:
                pub_tokens = []
                pub_idx = str(pub_idxs.pop()) # have to access the dictionary with strings. Yes, I suck

                # grab the relevant text corresponding to the random index
                if retrieval_type == 'abstract':
                    text = year_dict[pub_idx]['description'] # need to change this to 'abstract' in pyblio
                else:
                    text = year_dict[pub_idx]['fulltext']

                for sentence in sent_tokenize(text):
                    for word in word_tokenize(sentence):
                        pub_tokens.append(word)

                pubs.append(pub_tokens)
                info_tup = (year, pub_idx, year_dict[pub_idx]['doi'], year_dict[pub_idx]['pii'])
                pub_infos.append(info_tup)

            except:
                break

    print('This is pub_infos[0]', pub_infos[0])
    print('This is pubs[0] ', pubs[0])
    print('This is len(pubs) ', len(pubs))
    print('This is len(pub_infos) ', len(pub_infos))
                ###########################################

                # # make sure pub_tokens is as long as the longest paper
                # while len(pub_tokens) < longest_paper:
                #     pub_tokens.append(np.nan)
                #
                # pubdict[year][pub_idx] =
                #
                #
                # # here's the stuff we're actually going to put in a dataframe
                # pub_tokens = np.array(pub_tokens)
                # doi = year_dict[pub_idx]['doi']
                # name   = np.array(['' for range(len(pub_tokens))])
                # besio  = np.array(['' for range(len(pub_tokens))])
                # entity = np.array(['' for range(len(pub_tokens))])
                #
                # data = np.array([name, pub_tokens, besio, entity]).transpose()
                # columns = ['name', 'tokens', 'BESIO', 'entity']
                # pubs_df = pd.DataFrame(data, columns=columns)
                #
                # if pubs_on_sheet < pubs_per_sheet:
                #     with pd.ExcelWriter('label_carbon.xlsx') as writer:
                #         df.to_excel(writer, sheet_name = f'Sheet{}', startcol = 6*pubs_on_sheet)
                #         pubs_on_sheet += 1
                #
                # else: # pubs_on_sheet was >= pubs_per_sheet
                #
                #
                #
                #
                #
                #
                #
                #
                # except: # there weren't enough publications in this year, move on
                #     break




def find_longest_paper(year_dict, text_type='description'):
    """
    This function finds the longest paper in a year_dict, in terms of how many
    tokens are in the paper.

    Parameters:
        year_dict (dict, required): The year_dict to be searched

        text_type (str, optional): 'abstract' or 'fulltext'

    Returns:
        longest (int): The length of the longest paper in the year dict
    """
    longest = 0
    for paper_idx in year_dict:
        paper_wds = 0
        text = year_dict[paper_idx][text_type]
        for sentence in sent_tokenize(text):
            for word in word_tokenize(sentence):
                paper_wds += 1

        if paper_wds > longest:
            longest = paper_wds
        else:
            pass # dave beck taught me this move

    return longest




def label_main():
    """
    This is the main method for the paper label exection.
    """
    carbon_path = '/gscratch/pfaendtner/dacj/nlp/fulltext_pOmOmOo/Carbon'
    make_ner_sheet(carbon_path, num_papers = 50)

label_main()




# def w2v_main():
#     """
#     This is the main method to be executed
#     """
#     generator = Loader('/gscratch/pfaendtner/dacj/nlp/fulltext_pOmOmOo/Carbon')
#     model = Word2Vec(generator, min_count=10, workers=1, size=200)
#     os.chdir('/gscratch/pfaendtner/dacj/nlp')
#     model.save('carbon.model')
#
# main()
