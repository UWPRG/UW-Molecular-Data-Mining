import numpy as np
import gensim
from gensim.models import Word2Vec

path = '/gscratch/pfaendtner/dacj/nlp/3_journal_model/3_journal_model.model'
model = Word2Vec.load(path)

print(model.most_similar('nitrogen'))
