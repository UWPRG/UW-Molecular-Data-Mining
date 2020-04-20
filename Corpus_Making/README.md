For some guidance:

To do fulltext extraction on journals published by Wiley, check out the `WileyFullExtractor.ipynb`, within which are functions for
both metadata collection (through a Crossref API) and fulltext extraction (through the Wiley API). 

To do fulltext extraction on journals published by Elsevier, you'll want the tools `Pybliometrics` in either its .py or .ipynb formats
depending on your preference. That tool will allow you to collect a metadata corpus quickly.
Once you have the metadata corpus, to get fulltext you will then need to invoke the tool `Elsevier_fulltext_api` in either its
.py or .ipynb format. 
