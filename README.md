# BETO2020

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
