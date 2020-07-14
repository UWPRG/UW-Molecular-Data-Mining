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

import ner
import arch_blocks
import training

ner_path = '../labeled_data'
w2v_model = Word2Vec.load('../w2v_models/3j_15e_50D_min1_model/3j_15e_50D_min1_model.model')

data = ner.NerData(ner_path, w2v_model)

all_words = []
all_chars = []
all_tags = []
mol_words = []
for journal_data in data.training_dict.keys():
    for sheet_data in data.training_dict[journal_data]:
        for xy in sheet_data:
            sentence_list = xy[0]
            tags = xy[1]

            for word, tag in zip(sentence_list, tags):
                all_words.append(word)
                if tag != 'O':
                    all_tags.append(tag)
                    if 'MOL' in tag:
                        mol_words.append(word)
                try:
                    for char in word:
                        all_chars.append(char)
                except TypeError:
                    pass
unique_words = set(all_words)
unique_chars = set(all_chars)
mol_words = np.array(list(set(mol_words)))
print('-- Our Corpus Stats --')
print('# training abstracts - ', 193)
print('# total words - ', len(all_words))
print('# unique words - ', len(unique_words))
print('# unique characters - ', len(unique_chars))
print('# labeled words - ', len(all_tags))
print('# percent labeled - ', '{}%'.format(round(len(all_tags) / len(all_words) * 100, 2)), '\n')

all_words = []
all_chars = []
all_tags = []
mat_words = []
with open('../../persson_data/train.txt', 'r') as f:
    for line in f:
        line = line.split()
        if len(line) > 1:
            all_words.append(line[0])
            if line[1] != 'O':
                all_tags.append(line[1])
                if 'MAT' in line[1]:
                    mat_words.append(line[0])
            for char in line[0]:
                all_chars.append(char)
unique_words = set(all_words)
unique_chars = set(all_chars)
mat_words = np.array(list(set(mat_words)))
print('-- Perrson Corpus Stats --')
print('# training abstracts - ', 640)
print('# total words - ', len(all_words))
print('# unique words - ', len(unique_words))
print('# unique characters - ', len(unique_chars))
print('# labeled words - ', len(all_tags))
print('# percent labeled - ', '{}%'.format(round(len(all_tags) / len(all_words) * 100, 2)), '\n')


print('-- W2V Stats --')
print('# unique words - ', len(data.word_set))
print('# unique characters - ', len(data.char_set))

mol_idxs = np.random.choice(np.arange(len(mol_words)), size=25, replace=False)
mat_idxs = np.random.choice(np.arange(len(mat_words)), size=25, replace=False)
print(mol_words[mol_idxs])
print(mat_words[mat_idxs])
