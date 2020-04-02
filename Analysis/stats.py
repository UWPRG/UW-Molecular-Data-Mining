"""
This module is for calculating stats on a large corpus of text data.
"""
import os
import json
from chemdataextractor.doc import Paragraph
#import pubchempy as pcp

print('Successful imports')

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
    stats = {'papers':0, 'abstracts':0, 'fulltexts':0, 'words':0, 'CDE_mols':0}
    CDE_mols = []

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
                        append_cde_mols(abstract, CDE_mols, ptable)
                        print('Length of CDE mols is ', len(CDE_mols))
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
                        append_cde_mols(fulltext, CDE_mols, ptable)
                        print('Length of CDE mols is ', len(CDE_mols))
                    else:
                        pass
                except KeyError:
                    print('fulltext key error')
                    pass



    CDE_mols = set(CDE_mols)
    stats['CDE_mols'] = len(CDE_mols)

    return ptable, stats, CDE_mols


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


    # try:
    #     ptable[mol.text.lower] += 1
    # except KeyError:
    #     pass


def main(corpus_path, output_dir):
    """
    Main method to be called.

    Parameters:
        output_dir (str, required): Absolute path to a directory

    Returns:
        none
    """

    print('inside of main method')

    ptable, stats, CDE_mols = corpus_stats(corpus_path)

    os.chdir(output_dir)

    with open('ptable2.json', 'w') as fp:
        json.dump(ptable, fp)

    with open('corpus_stats2.json', 'w') as fp:
        json.dump(stats, fp)

    with open('CDE_mols2.txt', 'w') as file:
        for mol in CDE_mols:
            file.write(mol)
            file.write('\n')


output_dir = '/gscratch/pfaendtner/dacj/nlp/stats_pmmo'
corpus_path = '/gscratch/pfaendtner/dacj/nlp/fulltext_pOmOmOo'

main(corpus_path, output_dir)
