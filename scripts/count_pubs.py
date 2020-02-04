#!/usr/bin/env python
# coding: utf-8

# ## This notebook is for grabbing and viewing information about meta and full corpora.

# In[2]:


import os
import json
import time


# In[3]:


def absoluteFilePaths(directory):
    for dirpath,_,filenames in os.walk(directory):
        for f in filenames:
            yield os.path.abspath(os.path.join(dirpath, f))


# In[14]:


def journal_stats(path,pub_count,j_count,ab_count,ft_count):
    """
    This method gathers the statistics on a single journal directory.
    """
    with open(path) as json_file:
            data = json.load(json_file)
        
            for year in data:
                year_dict = data[year]

                for pub_number in year_dict:
                    pub_count += 1
                    ab_count += 1


                    try:
                        text = data[year][pub_number]['fulltext']
                        ft_count += 1

                    except: # there wasn't a full text retrieved for this doc
                        pass
            json_file.close()
            
            return pub_count,j_count,ab_count,ft_count


# In[5]:


def corpus_stats(corp_path):
    """
    This method loops through a directory which contains either a meta corpus or a full corpus from pybliometrics/Elsevier Fulltext.
    
    Parameters:
    ___________
    corp_path(str, required): 
    """
    pub_count = 0      # number of publications in the corpus
    j_count = 0        # number of journals
    ab_count = 0       # number of abstracts
    ft_count = 0       # number of full-texts
    timestamp = time.time()
    
    for j_name in os.listdir(corp_path):
        j_count += 1   
        
        j_dir_path = f'{corp_path}/{j_name}' # path to the directory corresponding to that journal
        
        for file in absoluteFilePaths(j_dir_path): # make a list of all files in this journal directory
            if '.json' in file and '._' not in file:
                j_json = file
                break
     
        pub_count,j_count,ab_count,ft_count = journal_stats(j_json,pub_count,j_count,ab_count,ft_count)
        
#     with open(j_json) as json_file:
#         data = json.load(json_file)

#         for year in data:
#             year_dict = data[year]

#             for pub_number in year_dict:
#                 pub_count += 1
#                 ab_count += 1


#                 try:
#                     text = data[year][pub_number]['fulltext']
#                     ft_count += 1

#                 except: # there wasn't a full text retrieved for this doc
#                     pass
#         json_file.close()
    return {'num_journals':j_count,'num_abstracts':ab_count,'num_fulltexts':ft_count,'time.time()':timestamp}
        


# In[ ]:


#corpus_stats('/Volumes/My Passport/Davids Stuff/fulltext_pOmOmOo')

