import sys
import numpy as np
import pandas as pd

from elsapy.elsclient import ElsClient
from elsapy.elsprofile import ElsAuthor, ElsAffil
from elsapy.elsdoc import FullDoc, AbsDoc
from elsapy.elssearch import ElsSearch

from mat2vec.processing.process import MaterialsTextProcessor


# client = ElsClient('755e62fd1fafd7376afaa2f5429fa64e')
#
# piis = []
# dois = []
# titles = []
# abstracts = []
# pub_dates = []
# rankings = []
# with open('corrosion_inhib_link_data.txt', 'r') as f:
#     counter = 1
#     for line in f:
#         line = line.split(',')
#         url = line[4]
#         pii = url.split('/')[-1]
#         doc = FullDoc(sd_pii = pii)
#         if doc.read(client):
#             print(counter, doc.title, line[5:11])
#             piis.append(pii)
#             dois.append(doc.data['coredata']['dc:identifier'])
#             titles.append(doc.data['coredata']['dc:title'])
#             abstracts.append(doc.data['coredata']['dc:description'])
#             pub_dates.append(doc.data['coredata']['prism:coverDate'])
#             rankings.append(','.join(line[5:11]))
#             counter += 1
#         else:
#             print('read failed')
#
# df_data = {'title': titles,
#            'pub_date': pub_dates,
#            'doi': dois,
#            'pii': piis,
#            'rankings': rankings,
#            'abstract': abstracts}
# df = pd.DataFrame(df_data)

# ### Make TF-IDF column (all ranks)
# tfidf = []
# for rankings in df.rankings:
#     if '2.0' in rankings:
#         tfidf.append('2')
#     elif '1.0' in rankings:
#         tfidf.append('1')
#     elif '0.0' in rankings:
#         tfidf.append('0')
#     else:
#         tfidf.append('')
# df['tfidf'] = pd.Series(tfidf)
# df.to_pickle('CI_abstracts.pkl')

# ### Remove samples with no abstract
# df = pd.read_pickle('CI_abstracts.pkl')
# df.reset_index(drop=True, inplace=True)
# drop_idxs = []
# for i, row in df.iterrows():
#     if row['abstract'] is None:
#         drop_idxs.append(i)
# df = df.drop(drop_idxs)
# df.reset_index(drop=True, inplace=True)

# ### Rules based cleaning of abstracts
# abstract_types = []
# clean_abstracts = []
# for i, row in df.iterrows():
#     abstract = row['abstract'].split('\n')
#     info = []
#     for line in abstract:
#         line = line.strip()
#         if line != '':
#             info.append(line)
#     if len(info) == 2:
#         abstract_types.append(info[0])
#         clean_abstracts.append(info[1])
#     elif len(info) == 1:
#         if info[0].split()[0].lower() == 'abstract':
#             abstract_types.append('Abstract')
#             clean_abstract = ' '.join(info[0].split()[1:])
#             clean_abstracts.append(clean_abstract)
#         elif info[0].split()[0].lower() == 'summary':
#             abstract_types.append('Summary')
#             clean_abstract = ' '.join(info[0].split()[1:])
#             clean_abstracts.append(clean_abstract)
#         elif 'objective' in info[0].split()[0].lower():
#             abstract_types.append('Objective')
#             clean_abstract = ' '.join(info[0].split()[1:])
#             clean_abstracts.append(clean_abstract)
#         else:
#             abstract_types.append('')
#             clean_abstracts.append(info[0])
#     else:
#         info_lower = [x.lower() for x in info]
#         section_titles = ['introduction',
#                           'purpose',
#                           'background',
#                           'scope and approach',
#                           'objective',
#                           'objectives',
#                           'materials and methods',
#                           'results',
#                           'conclusion',
#                           'conclusions',
#                           'key findings',
#                           'key findings and conclusions',
#                           'methodology',
#                           'methods',
#                           'study Design',
#                           'clinical implications']
#         sectioned = False
#         for section_title in section_titles:
#             if section_title in info_lower:
#                 sectioned = True
#         if sectioned:
#             if info[0].lower() == 'abstract':
#                 abstract_types.append('Abstract')
#                 text = []
#                 for entry in info[1:]:
#                     if entry.lower() in section_titles:
#                         pass
#                     else:
#                         text.append(entry)
#                 clean_abstract = ' '.join(text)
#                 clean_abstracts.append(clean_abstract)
#             elif info[0].lower() == 'summary':
#                 abstract_types.append('Summary')
#                 text = []
#                 for entry in info[1::]:
#                     if entry.lower() in section_titles:
#                         pass
#                     else:
#                         text.append(entry)
#                 clean_abstract = ' '.join(text)
#                 clean_abstracts.append(clean_abstract)
#             else:
#                 abstract_types.append('')
#                 text = []
#                 for entry in info:
#                     if entry.lower() in section_titles:
#                         pass
#                     else:
#                         text.append(entry)
#                 clean_abstract = ' '.join(text)
#                 clean_abstracts.append(clean_abstract)
#         else:
#             if info[0].lower() == 'abstract' or info[0].lower() == 'absract' or info[0].lower() == 'abstact' or info[0].lower() == 'abstractt':
#                 abstract_types.append('Abstract')
#                 clean_abstract = ' '.join(info[1:])
#                 clean_abstracts.append(clean_abstract)
#             elif info[0].lower() == 'summary' or info[0].lower() == 'publisher summary' or info[0].lower() == '1. summary':
#                 abstract_types.append('Summary')
#                 clean_abstract = ' '.join(info[1:])
#                 clean_abstracts.append(clean_abstract)
#             elif info[0] == 'This article has been retracted: please see Elsevier Policy on Article Withdrawal (https://www.elsevier.com/about/our-business/policies/article-withdrawal).':
#                 abstract_types.append('Retracted')
#                 clean_abstracts.append('Retracted')
#             else:
#                 abstract_types.append('')
#                 clean_abstract = ' '.join(info)
#                 clean_abstracts.append(clean_abstract)
#
# df['abstract'] = pd.Series(clean_abstracts)
# df['abstract_type'] = pd.Series(abstract_types)
# df = df[df['abstract_type'] != 'Retracted']
# df.reset_index(drop=True, inplace=True)
#

# ### Make TF-IDF column (Rank 2 or Not Rank 2)
# tfidf_2 = []
# for i, row in df.iterrows():
#     if row['tfidf'] == '2':
#         tfidf_2.append(1)
#     elif row['tfidf'] == '1' or row['tfidf'] == '0':
#         tfidf_2.append(0)
#     else:
#         tfidf_2.append(np.nan)
# df['tfidf_2'] = pd.Series(tfidf_2)

# ### Process abstracts with MaterialsTextProcessor
# processed_abstracts = []
# processor = MaterialsTextProcessor()
# counter = 0
# for abstract in df.abstract:
#     print(counter)
#     abstract, mat_list = processor.process(abstract)
#     abstract = ' '.join(abstract)
#     processed_abstracts.append(abstract)
#     counter += 1
# df['processed_abstract'] = pd.Series(processed_abstracts)

# ### Remove duplicates
# df = df.drop_duplicates(['title'])
# df.to_pickle('CI_abstracts_clean.pkl')
