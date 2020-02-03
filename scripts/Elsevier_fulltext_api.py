#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
from elsapy.elsclient import ElsClient
from elsapy.elsprofile import ElsAuthor, ElsAffil
from elsapy.elsdoc import FullDoc, AbsDoc
from elsapy.elssearch import ElsSearch
import os
import json
import shutil
import click


def load_journal_json(absolute_path):
    """
    This method loads data collected on a single journal by the pybliometrics metadata collection module into a dictionary.

    Parameters
    ----------
    absolute_path(str, required) - The path to the .json file containing metadata procured by the pybliometrics module.
    """
    with open(absolute_path) as json_file:
        data = json.load(json_file)

    return data


def create_json_list(metacorpus_path):
    """
    The purpose of this method is to create a list of .json files present in a meta corpus directory.

    Parameters:
    -----------
    metacorpus_filepath(str, required): Path to the folder containing all metadata json files from the pybliometrics module.
    """

    dir_list = os.listdir(metacorpus_path) # get a list of all the directories

    json_list = []
    for directory in dir_list:
        j_filename = f'{metacorpus_path}/{directory}/{directory}.json' # this is the format that pybliometrics module puts out files in
        json_list.append(j_filename)

    return json_list


def get_doc(dtype,identity,client):
    """
    This method retrieves a 'Doc' object from the Elsevier API. The doc object contains metadata and full-text information
    about a publication associated with a given PII.

    Parameters:
    -----------
    dtype(str,required): The type of identification string being used to access the document. (Almost always PII in our case.)

    identity: The actual identification string/ PII that will be used to query.
    """
    if dtype == 'pii':
        doc = FullDoc(sd_pii = identity)
    elif dtype == 'doi':
        doc= FullDoc(doi = identity)

    if doc.read(client):
            #print ("doc.title: ", doc.title)
            doc.write()
    else:
        print ("Read document failed.")

    return doc


def get_docdata(doc):
    """
    This method attempts to get certain pieces of metadata from an elsapy doc object.

    Parameters:
    -----------

    doc(elsapy object, required): elsapy doc object being searched for

    Returns:
    --------
    text(str): The full text from the original publciation.

    auths(list): The list of authors from the publication.
    """
    try:
        text = doc.data['originalText']                          # grab original full text
    except:
        text = 'no text in doc'

    try:
        auths = authorize(doc) # a list of authors
    except:
        auths = []

    return text, auths


def authorize(doc):
    #this method takes a doc object and returns a list of authors for the doc
    auths = []
    for auth in doc.data['coredata']['dc:creator']:
        auths.append(auth['$'])

    return auths

def meta2full_corpus(metacorpus_path,output_path,jobs,job_id,client):
    """
    This method creates a full text corpus in dictionary/json format from a metadata corpus which has been procured by the pybliometrics module.
    A new copy of the metacorpus is first created, and that version is operated on by this method.
    Duplication of the metacorpus is to avoid partial alteration of the corpus in the event of a program crash.

    Parameters
    __________
    metacorpus_filepath(str, required): Absolute path to the folder containing all metadata json files from the pybliometrics module.

    output_path(str, required): Absolute path (including the file name) in which the full text corpus folder will be placed.

    output_name(str, required): The desired name of the output folder where the full text corpus will be placed.

    """
    if os.path.isdir(output_path):
        pass
    else:
        shutil.copytree(metacorpus_path,output_path)

    directory_list = os.listdir(output_path)                # get a list of all the directories
    print(f'about to slice directory_list into {jobs} slice(s), {jobs} has type {type(jobs)}')

    dir_array = np.array_split(directory_list,jobs)     # split directory list into equal parts if parallel downloading is desired

    print('Calling get_fulltexts')
    get_fulltexts(dir_array[job_id-1],output_path,job_id,client)


def get_fulltexts(directory_list,output_path,pnum,client):
    """
    This method takes a list of directories containing 'meta' corpus information from the pybliometrics module and adds full-text information to those files.

    Parameters:
    ___________
    directory_list(list, required): A list of directories which this method will enter and add full-text information to.

    output_path(str, required): The folder in which the new full text corpus will be placed.

    api_keys(list, required): A list of valid API keys from Elsevier developer. One key needed per process being started.
    """

    for directory in directory_list:
        print(f'Process {pnum} on directory {directory}')
        if os.path.exists(f'{output_path}/{directory}/marker.txt'): # If we've already been to this directory, skip it
            print(f'skipping {output_path}/{directory} because it has a marker.')
            continue
        else:
            pass # Dave Beck taught me this move


        info = open(f'{output_path}/{directory}/info.csv','w') # a file to keep track of errors
        info.write('type,file,year,pub') # header

        #print(f'made marker and errors in {directory}')

        json_file = f'{output_path}/{directory}/{directory}.json'
        j_dict = load_journal_json(json_file) # now we have a dictionary of information in our hands. Access it via journal_dict['year']['pub_number']

        for year in j_dict:

            if j_dict[year] is not {}:

                for pub in j_dict[year]:

                    pii = j_dict[year][pub]['pii'] # the pii identification number used to get the full text

                    try:
                        doc = get_doc('pii',pii,client) # don't know if doc retrieval will fail
                        print(f'Process {pnum} got doc in {directory}')
                    except Exception as e:
                        print(f'EXCEPTION: DOC RETRIEVAL. Process {pnum} in directory {directory} year {year}')
                        print(f'Exception was {e}')
                        doc = None
                        info.write(f'doc retrieval,{json_file},{year},{pub}')

                    text, auths = get_docdata(doc) # doesn't crash even if doc = None


                    if text is 'no text in doc':
                        info.write(f'no text in doc,{json_file},{year},{pub}')
                    elif auths is []:
                        info.write(f'no auths in doc,{json_file},{year},{pub}')

                    j_dict[year][pub]['authors'] = auths
                    j_dict[year][pub]['fulltext'] = text # the real magic

            else:
                # the year was empty
                info.write(f'year empty,{json_file},{year},{np.nan}')
        print(f'Making marker for {output_path}/{directory}')
        marker = open(f'{output_path}/{directory}/marker.txt','w+') # put a file in the directory that lets us know we've been in that directory
        marker.close()
        info.close()
        with open(json_file,'w') as file:
            json.dump(j_dict,file)

@click.command()
@click.option('--jobs','-j', required=True,type=int,help='Total number of processes')
@click.option('--job_id','-jid', required=True,type=int,help='Integer label for this process')
def main(jobs,job_id):
    client = ElsClient("5c3e44d3231b7ef83bbd46a1fca5fe0d")
    meta_filepath = '/Volumes/My Passport/davids_stuff/fulltext_pOmOmOo'
    output_filepath = '/Volumes/My Passport/Davids Stuff/fulltext_pOmOmOo'
    meta2full_corpus(meta_filepath,output_filepath,jobs,job_id,client)


if __name__ == "__main__":
    main()
