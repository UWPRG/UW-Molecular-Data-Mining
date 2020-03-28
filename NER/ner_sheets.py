import json
import os
import time
import random
import math

from openpyxl import load_workbook

from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize

import numpy as np
import pandas as pd

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

def make_ner_sheet(journal_directory, retrieval_type='description', years='all', scramble=True,
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
            abstracts worth of NER data
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
        pubs_per_year = int(round(num_papers / num_years)) # round to nearest whole
    else:
        # the first layer of dictionaries in journal_dict corresponds to all the
        # years, so the number of keys will tell us how many pubs for each year
        num_years = len(journal_dict.keys())
        pubs_per_year = int(round(num_papers / num_years))

    if years == 'all':
        year_list = journal_dict.keys()
    else:
        year_list = years

    pubs = []
    pub_infos = []
    for year in year_list:


        year_dict = journal_dict[year]
        pubs_from_year = 0

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
                if retrieval_type == 'description':
                    text = year_dict[pub_idx]['description'] # need to change this to 'abstract' in pyblio
                else:
                    text = year_dict[pub_idx]['fulltext']

                if text == None: # some abstracts and fulltexts just aren't there
                    continue
                text = clean_paper(text)
                sent_list = sent_tokenize(text)
                sent_endings = [] # will be built to track the index of sentence endings

                for i, sentence in enumerate(sent_list):
                    length = len(sentence.split())
                    sent_endings.append(length)
                    for word in sentence.split():
                        pub_tokens.append(word)

                pubs.append(pub_tokens)

                # edit sent_endings so it actually corresponds to tokens in pub_tokens
                # before this point, it's just a list of lengths, so doesn't work
                # for indexing
                for i, num in enumerate(sent_endings):
                    if i == 0:
                        pass
                    else:
                        sent_endings[i] = sent_endings[i] + sent_endings[i-1]
                sent_endings = np.array(sent_endings) - 1
                # at this point, sent_endings needs to be stored for later access
                # we will append them to info_tup, so they get carried with
                # the associated publication through the scramble


                info_tup = (year, pub_idx, year_dict[pub_idx]['doi'], year_dict[pub_idx]['pii'], sent_endings.tolist())
                pub_infos.append(info_tup)

            except:
                break

#     # grab the relevant text corresponding to the random index #########
#     if retrieval_type == 'description':
#         text = year_dict[pub_idx]['description'] # need to change this to 'abstract' in pyblio
#     else:
#         text = year_dict[pub_idx]['fulltext']
#
#     if text == None: # some abstracts and fulltexts just aren't there
#         continue
#     text = clean_paper(text)
#     for sentence in sent_tokenize(text):
#         for word in sentence.split():
#             pub_tokens.append(word)
#
#     pubs.append(pub_tokens)
#     info_tup = (year, pub_idx, year_dict[pub_idx]['doi'], year_dict[pub_idx]['pii'])
#     pub_infos.append(info_tup)
#
# except:
#     break ##########
    ########################### at this point, all pub tokens are made and stored
    np.random.seed(42)
    np.random.shuffle(pubs)

    np.random.seed(42)
    np.random.shuffle(pub_infos)

    longest = find_longest_paper(pubs)

    pubs_in_excel = 0
    sheet_number = 0
    pub_counter = 0
    master_endings_dict = {}


    while pubs_in_excel < len(pubs) - 1:

        pubs_in_sheet = 0
        dynamic_endings_dict = {}
        while pubs_in_sheet < pubs_per_sheet:
            try:
                data = pubs[pub_counter]
            except IndexError:
                break
            while len(data) < longest:
                data.append('')
            data = np.array(data)

            # create dataframe
            name   = ['' for x in range(len(data))]
            besio  = np.array(['' for x in range(len(data))])
            entity = besio
            mol_class = besio
            name[1] = pub_infos[pub_counter][0] # put the year in the second entry
            name[2] = pub_infos[pub_counter][1] # put the pub index within the year as third entry
            name[3] = pub_infos[pub_counter][2] # put the pub doi as fourth entry

            name = np.array(name) # now turn it into np array

            columns = ['name', 'tokens', 'BESIO', 'entity', 'mol_class']

            df = pd.DataFrame(np.array([name, data, besio, entity, mol_class]).transpose(), columns=columns)

            # write the damn thing to excel in the propper column
            sheet_name = json_filename[:-5]
            filename = f'{sheet_name}_{sheet_number}.xlsx'
            append_df_to_excel(filename, df, sheet_name=f'Sheet1', startcol = 6 * pubs_in_sheet)

            # append the sentence_endings lists into the dict
            dynamic_endings_dict[pubs_in_sheet] = pub_infos[pub_counter][4]

            pubs_in_sheet += 1
            pubs_in_excel += 1
            pub_counter += 1

        sheet_number += 1
        master_endings_dict[filename] = dynamic_endings_dict

    with open('sentence_endings.json', 'w') as fp:
        json.dump(master_endings_dict, fp)

def append_df_to_excel(filename, df, sheet_name='Sheet1', startrow=0, startcol=None,
                       truncate_sheet=False,
                       **to_excel_kwargs):
    """
    Append a DataFrame [df] to existing Excel file [filename]
    into [sheet_name] Sheet.
    If [filename] doesn't exist, then this function will create it.

    Parameters:
      filename : File path or existing ExcelWriter
                 (Example: '/path/to/file.xlsx')
      df : dataframe to save to workbook
      sheet_name : Name of sheet which will contain DataFrame.
                   (default: 'Sheet1')
      startrow : upper left cell row to dump data frame.
                 Per default (startrow=None) calculate the last row
                 in the existing DF and write to the next row...

      startcol : upper left cell column to dump data frame.


      truncate_sheet : truncate (remove and recreate) [sheet_name]
                       before writing DataFrame to Excel file
      to_excel_kwargs : arguments which will be passed to `DataFrame.to_excel()`
                        [can be dictionary]

    Returns: None
    """

    print('On dataframe ', startcol/6)
    # ignore [engine] parameter if it was passed
    if 'engine' in to_excel_kwargs:
        to_excel_kwargs.pop('engine')

    writer = pd.ExcelWriter(filename, engine='openpyxl')

    # Python 2.x: define [FileNotFoundError] exception if it doesn't exist
    try:
        FileNotFoundError
    except NameError:
        FileNotFoundError = IOError


    try:
        # try to open an existing workbook
        writer.book = load_workbook(filename)

        if startcol is None and sheet_name in writer.book.sheetnames:
            startcol = writer.book[sheet_name].max_col

        # truncate sheet
        if truncate_sheet and sheet_name in writer.book.sheetnames:
            # index of [sheet_name] sheet
            idx = writer.book.sheetnames.index(sheet_name)
            # remove [sheet_name]
            writer.book.remove(writer.book.worksheets[idx])
            # create an empty sheet [sheet_name] using old index
            writer.book.create_sheet(sheet_name, idx)

        # copy existing sheets
        writer.sheets = {ws.title:ws for ws in writer.book.worksheets}
    except FileNotFoundError:
        # file does not exist yet, we will create it
        pass


    if startcol is None:
        startcol = 0

    # write out the new sheet
    df.to_excel(writer, sheet_name, startrow=startrow, startcol=startcol, **to_excel_kwargs)

    # save the workbook
    writer.save()




def find_longest_paper(pubs):
    """
    This function finds the longest paper in a year_dict, in terms of how many
    tokens are in the paper.

    Parameters:
        pubs (list-like, required): The year_dict to be searched

    Returns:
        longest (int): The length of the longest paper in the year dict
    """
    longest = 0
    for paper in pubs:
        if len(paper) > longest:
            longest = len(paper)

    return longest


def find_labeled(df):
    """
    This function takes in a labeled NER sheet, and finds the columns that have been labeled.

    Parameters:
        df (pandas DataFrame, required): The dataframe containing the labeled NER information

    Returns:
        pandas DataFrame: Dataframe containing only labeled abstracts, and their labels.
    """

    labeled = []
    columns = df.columns

    new_df = pd.DataFrame()

    for idx, column in enumerate(columns):
        # skip the columns that say Unnamed.x
        if column.startswith('Unnamed'):
            continue
        else:
            pass

        # find every column that starts with 'name'
        if column.startswith('name'):

            # check if the entry in 'name' cell is a str
            if isinstance(df[column][0], str):
                # put the name column in new_df
                new_df[column] = df[column]

                tokens = df[columns[idx + 1]].values
                new_df[columns[idx + 1]] = tokens # put the tokens in new_df

                # assume there is at least one label column after
                # start at 2 because first label column is +2 ahead of 'name' col
                nextcol = columns[idx + 2]

                # also start this at 2, increment in while-loop to look further into frame
                fwd_idx = 2

                while not (nextcol.startswith('Unnamed')):

                    labels = df[nextcol].values
                    new_df[nextcol] = labels
                    fwd_idx += 1
                    nextcol = columns[idx + fwd_idx]

    return new_df

def collect_ner_data(folder_path):
    """
    This function collects all the labeled NER training data from a folder holding
    any number of ner_sheet folders from different journals.

    Parameters:
        folder_path (str, required): The path to a folder containing other folders.
            Those "other folders" correspond to different journals, and contain
            filled out excel spreadsheets with NER training data.

    Returns:
        array: array of tuples. Each tuple contains one list of tokens, and the
            corresponding NER labels for each token.
    """
    # ensure we start with the same format every time
    if not folder_path.endswith('/'):
        folder_path += '/'

    ner_folders = os.listdir(folder_path)

    # iter through all NER data folders corresponding to a single journal
    for journal in ner_folders:
        journal_path = folder_path + journal + '/'

        for sheet in journal_path:

            if sheet.endswith('xlsx'): # don't want to open google sheets
                df = pd.read_excel(sheet)
                clean_df = find_labeled(df)
            else:
                pass

def recover_sentences(tokens, sentence_endings):
    """
    Reconstructs the original sentences from an token list.

    Parameters:
        tokens (list, required): list of tokens from which to construct sentences


    """

def label_main():
    """
    This is the main method for the paper label exection.
    """
    carbon_path = '/gscratch/pfaendtner/dacj/nlp/fulltext_pOmOmOo/Carbon'
    j_in_bio = '/gscratch/pfaendtner/dacj/nlp/fulltext_pOmOmOo/Journal_of_Inorganic_Biochemistry'
    j_o_metallic = '/gscratch/pfaendtner/dacj/nlp/fulltext_pOmOmOo/Journal_of_Organometallic_Chemistry'
    #make_ner_sheet(carbon_path, num_papers = 300, pubs_per_sheet = 50)
    make_ner_sheet(j_in_bio, num_papers = 300, pubs_per_sheet = 50)
    make_ner_sheet(j_o_metallic, num_papers = 300, pubs_per_sheet = 50)

label_main()
