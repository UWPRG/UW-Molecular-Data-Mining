"""
This module is for calculating stats on a large corpus of text data.
"""
import os
import json
from chemdataextractor.doc import Paragraph
import sys
import random
#import pubchempy as pcp

print('Successful imports')


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


def read_ptable():
    """
    This function reads the periodic table file 'periodic_table.txt' and sets up a
    dictionary of values for each element.

    Parameters:
        none

    Returns:
        dict: dictionary of element names and symbols as keys, integers = 0 as all
            values
    """
    ptable = {}

    with open('periodic_table.txt', 'r') as file:
        for line in file:

            tokens = line.split()

            element = tokens[1].lower
            symbol = tokens[2].lower

            ptable[element] = 0
            ptable[symbol] = 0

    return ptable


def corpus_stats(corpus_path):
    """
    This function runs through an entire literature corpus and calculates many
    statistics about the corpus.

    Parameters:
        corpus_path (str, required): The path to the master corpus.

        level (str, optional): Whether to gather stats from the 'abstract' level,
            'fulltext', or 'both'.

    Returns:
        dict: Dictionary with each key corresponding to an element, and each value
            equal to the number of times that element/symbol was seen

        dict: Dictionary of various other corpus stats.
    """
    ptable = read_ptable() # create dictionary of periodic table elements
    stats = {'papers':0, 'abstracts':0, 'fulltexts':0, 'words':0}

    # make sure we have consistent endings
    if not corpus_path.endswith('/'):
        corpus_path += '/'

    # get a list of all the journal directories and remove the README
    journals = os.listdir(corpus_path)
    journals.remove('README.txt')

    # iterate through every journal in corpus
    for journal_name in journals:
        journal_path = corpus_path + journal_name +'/'

        journal_json = journal_path + journal_name + '.json'

        print('On journal ', journal_name)

        # open the entire dictionary corresponding to a single jornal
        with open(journal_json) as json_file:
            journal_dict = json.load(json_file)

        # iterate through the journal years
        for year in journal_dict:
            year_dict = journal_dict[year]
            print(year)

            # iterate through every paper number in that year
            for paper in year_dict:
                stats['papers'] += 1                        #increment paper stat
                paper_dict = year_dict[paper]

                # in the paper dict there are,
                # 'description', 'fulltext', 'doi', 'pii'...
                try:
                    abstract = paper_dict['description']
                    if abstract != None:
                        stats['abstracts'] += 1                 #increment abs stat
                        stats['words'] += len(abstract.split())
                    else:
                        pass
                except KeyError:
                    print('Abstract key error')
                    pass

                try:
                    fulltext = paper_dict['fulltext']
                    if fulltext != None:
                        stats['fulltexts'] += 1                 #increment ft stat
                        stats['words'] += len(fulltext.split())
                    else:
                        pass
                except KeyError:
                    print('fulltext key error')
                    pass


    return ptable, stats

def get_CDE_mols(corpus_path, years, ppy, output_path, mode='fulltext'):
    """
    This function grabs

    Parameters:
        corpus_path (str, required): Path to the corpus

        years (list, required): List of years to find mols for

        ppy (int, required): Papers per year. How many papers to get mols from per
            year

        output_path (str, required): path to place output data to be furher analyzed

        mode (str, optional): Either 'fulltext' or 'abstract' or 'both'
    """
    paper_count = 0
    # make sure we have consistent endings
    if not corpus_path.endswith('/'):
        corpus_path += '/'

    # get a list of all the journal directories and remove the README
    journals = os.listdir(corpus_path)
    journals.remove('README.txt')

    random.seed(42)
    random.shuffle(journals)

    # iterate through every journal in corpus
    for journal_name in journals:
        journal_path = corpus_path + journal_name +'/'

        journal_json = journal_path + journal_name + '.json'

        print('On journal ', journal_name)

        # open the entire dictionary corresponding to a single jornal
        with open(journal_json) as json_file:
            journal_dict = json.load(json_file)

        # iterate through the specified years in parameter
        for year in years:
            year_dict = journal_dict[year]
            print(year)
            try:
                # don't know if there will be enough papers in this year for this pub
                paper_idxs = random.sample(range(len(year_dict)), ppy)
            except:
                continue
            for num in paper_idxs:
                paper_count += 1
                print('On paper ', paper_count, ' of ', len(journals)*len(years)*ppy)
                # grab the paper from this year corresponding to the 'numth' paper
                paper_dict = year_dict[str(num)]

                # get the fulltext out
                try:
                    text = paper_dict['fulltext']
                except:
                    continue
                if type(text) != str:
                    continue
                # remove nonsense information
                text = clean_paper(text)

                para = Paragraph(text)
                mols = para.cems # find all molecules in the text

                mols = ['<<NEW_PAPER>>'] + [mol.text for mol in mols]
                with open(output_path, 'a') as file:
                    for entry in mols:
                        file.write(entry + '\n')
                    file.write('\n')

def append_cde_mols(text, mol_list, ptable):
    """
    This function uses ChemDataExtractor to find all molecules in a chunk of text.

    Parameters:
        text (str, required): The text to find molecules in

    Returns:
        list: list of all molecules in the text
    """
    para = Paragraph(text)
    new_mols = para.cems # find all molecules in the text

    for mol in new_mols:
        mol_list.append(mol.text)
        print('appended ', mol)

def main(corpus_path, output_path):
    """
    Main method to be called.

    Parameters:
        output_dir (str, required): Absolute path to a directory

    Returns:
        none
    """
    ppy = 5
    years = ['2019']
    get_CDE_mols(corpus_path, years, ppy, output_path, mode='fulltext')


output_path = '/gscratch/pfaendtner/dacj/nlp/stats_pmmo/2015_5ppy_CDE_mols.txt'
corpus_path = '/gscratch/pfaendtner/dacj/nlp/fulltext_pOmOmOo'

main(corpus_path, output_path)
