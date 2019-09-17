# BETO2020

### September 16 Meeting (Taking stock, regroup, what's everyone up to?)
Summary of this meeting is that Wes T + Alex are building a word2vec classifier based on a cumulative cosine distance of a paper to keywords/phrases like 'corrosion inhibition' or 'flame retardant polymer.' Dave J has established one resource for full text publications that can yield at least 10^4 papers on a given topic. Also building TF-IDF classifier. Jon will investigate methods for large JSON datastructures to start storing our data in an organized fashion. We agreed we need the ability to create a living breathing database offline that is easily added to and accessed. 

#### Where is everyone at?

##### Alex/ West T
Working on a text classifier using Word2Vec. Strategy is to train Word2Vec on papers that are mannually graded as really good (score of 2) so it can learn the context of relevant words. Then cumulative cosine similarity scores will be given to papers, and a threshold will be established to accept/reject if a paper is relevant. 

##### Dave J
Working on a text classifier using TF-IDF and support vector machines. Strategy is to vectorize documents using the TF-IDF formula, then create classification boundaries with support vector machines. Also might investigate n-gram optimization (i.e. is Tf-IDF most successful with unigrams, bigrams, trigrams, etc...) 

#### Next steps for everyone

##### Dave J
Keep figuring out how to gain access to large volumes of full text publications via APIs. Also keep building TF-IDF classifier. Maybe test out on some real papers. 

##### Jon et. al.
Database/JSON formatting investigation. How can we format our papers/metadata? 

##### Wes T et. al.
Keep building the Word2Vec classifier


### July 31st (List of important data/scripts and their locations)

#### Important Scripts and iPython Notebooks:
1. 'scrape_sciencedirect_urls.py' - BETO2020/scripts/ - Use this script to scrape large volumes of Science Direct publication URLs on any topic from any series of years. 

2. 'Elsevier_fulltext_api.ipynb' - BETO2020/data/ScienceDirect URLS/ - Use this notebook to retrive the full texts of publications from a list of Science Direct URLS. Creates a text file full of the raw corpus, and can create a dataframe that records exactly which URLs successfully yielded a fulltext that went into the corpus. 

3. 'tfidf_wrapper.py' - BETO2020/scripts/ - This script can be used to train a document classifier. It is written as a class and its use will require looking at the documentation within. Classification is a two step process (1) vectorization of the dodument into TF-IDF vectors (2) Classification via support vector machines. 

4. 'SD_paper_cleaner.ipynb' - BETO2020/ipynb/ - This notebook is able to clean the full text output from the Science Direct API. Removes unusable text from the front and back of the publication, leaving only the body of text in the publication. 

#### Important Data:
1. 'keyword_organic_corrosion_inhibitor.txt' - Located in 'BETO2020/data/ScienceDirect URLS/' and the ChemE NLP team drive. The current master list of corrosion inhibitor publication URLs from Science Direct. This is the file that was used to create the raw corpus of corrosion inhibitor papers. 

2. 'keyword_organic_flame_retardant.txt' - Located in 'BETO2020/data/ScienceDirect URLS/'. The current master list of flame retardant publication URLs from Science Direct. this is the file that was used to create the raw corpus of flame retardant papers.

3. 'corrinhib_success.txt' - Located in 'BETO2020/data/ScienceDirect URLS/' and the ChemE NLP team drive. This is the same list of URLs as above, except the rightmost column has a binary indicator of whether or not the API was successful at retrieving the full text. This can be used to link the papers in the raw corpus of corrosion inhibitor publications to their URLs, and PII numbers. There is a header. 

4. 'corrosion_inhibitor_texts.txt' - Located in the ChemE NLP team drive. The first raw corpus of corrosion inhibitor texts. Texts are separated by a '\n' delimiter, and can be loaded into a dataframe. There is no header. 

5. 'flame_retardant_texts.txt' - Locateed in the ChemE NLP team drive. The first raw corpus of flame retardant texts. Texts are separated by a '\n' delimiter, and can be loaded into a dataframe. There is no header. 

6. 'corrosion_inhib_splits.xlsx' - Located in the ChemE NLP team drive. The scrambled and split list of corrosion inhibitor URLs that will be used to train a document classifier after the URLs are ranked. 

7. 'flame_retardant_splits.xlsx' - Located in the ChemE NLP team drive. The scrambled and split list of flame retardant URLs that will be used to train a document classifer after the URLs are ranked. 

### July 3rd
Meeting notes:
- dropbox for database location (may or may not take format of sql database)
- set meeting for **July 17 Hackathon** with Luscombe summer students (UnitTests, Travis CI, pypi, readthedocs/sphinx/ghpages/pep8)
- July 5th Wes+David hacky hack establish how/what we are going to store (abstracts/text/figures/tables). So far David has been using beautiful soup. He's taken an algorithmic approach to parsing science direct (where the text is saved each time, etc.)

## Overview
This repository describes how to identify organic chemical candidates that can function as flame retardants or corrosion inhibitors from published papers.
## Process
#### STEP 1: Clone the github repository
#### STEP 2: Installation
Python package ChemDataExtractor,bs4 and pandas are required for running the
count_chemical_occurrences.ipynb
#### STEP 3: Data collection
1.Search at [web of science](https://apps.webofknowledge.com/WOS_GeneralSearch_input.do?product=WOS&search_mode=GeneralSearch&SID=7CDbc95VnqxjeigJW9S&preferencesSaved=) using keyword "organic corrosion inhibitor" and "organic flame retardant" .

2.Click "Export" at the top of result page, choose "Other File Formats" and then select "Author, Title, Source, Abstract" for Record Content and "HTML" for File Format.

3.Save the HTML files under the data folder.
#### STEP 4: Output chemical candidates
Run count_chemical_occurrences.ipynb. Two csv files respectively named as "corrosion_inhibitor_list.csv" and "flame_retardant_list.csv" are generated, listing candidates for each category.
#### STEP 5: Visualize molecules
Import csv files to [ChemAxon](https://chemaxon.com/products/jchem-for-office), generate and download molecular representations.
