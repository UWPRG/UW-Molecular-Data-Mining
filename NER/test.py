import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

import matplotlib
from matplotlib import pyplot as plt

import gensim
from gensim.models import Word2Vec

import random

torch.manual_seed(1)

# import package

import arch_blocks
import ner
import training

ner_path = '/Volumes/GoogleDrive/Shared drives/ChemE NLP Team Drive/NER_labeling/ner_sheets/'
w2v_model = Word2Vec.load('../models/3j_15e_50D_min1_model/3j_15e_50D_min1_model.model')

data = ner.NerData(ner_path, w2v_model)

lstm = arch_blocks.W2VCharLSTM(7,7,7,data)

bilstm, valset, trainset, bad_train_sentences, vad_val_sentences, fig = training.train_rnn(lstm, data, 55, 0.85)

gpath = '/Volumes/GoogleDrive/Shared drives/ChemE NLP Team Drive/April8/'
model_name = '777_unidirectional_55epoch'
#
torch.save(lstm, gpath+model_name)
plt.show()
fig.show()

#lstm = torch.load(gpath + model_name)
