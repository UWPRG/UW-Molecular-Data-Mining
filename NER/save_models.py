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

ner_path = '/gscratch/pfaendtner/dacj/nlp/ner_sheets_backup2'
w2v_path = '/gscratch/pfaendtner/dacj/nlp/w2v_models/3j_15e_50D_min1_model/3j_15e_50D_min1_model.model'

# load the Word2Vec model to be referenced for word embeddings
w2v_model = Word2Vec.load(w2v_path)

# create the NerData object, referencing the ner_sheets and the nerData object
data = ner.NerData(ner_path, w2v_model)

# create the RNN model
bilstm = arch_blocks.BiW2VCharLSTM(7,7,7,data)

save_epochs = [5,10,20,30,40,50,60,70]
name = '777_BiW2VCharLSTM'
dirname = '/gscratch/pfaendtner/dacj/nlp/pytorch_models/777_BiW2VCharLSTM'

training.train_save_rnn(bilstm, data, 50, save_epochs, 0.85, dirname, name)
