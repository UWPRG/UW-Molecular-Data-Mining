"""
This module is for abstracting training processes with the models in arch blocks
"""
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

import matplotlib
from matplotlib import pyplot as plt

import arch_blocks

import random

torch.manual_seed(1)



def train_rnn(model, data, epochs, train_frac, plot=True):
    """
    This function is an abstraction for a training loop to train the W2VCharLSTM model.


    """
    loss_function = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=0.1)

    train_losses = []
    val_losses = []


    # split the data into training and validation data
    # fraction of data for training
    num_train = int(round(train_frac*len(data.list),0)) # calculate the number of training samples
    random.shuffle(data.list)                           # shuffle data set

    train_set = data.list[:num_train]
    val_set = data.list[num_train:]


    for epoch in range(epochs):
        print('On epoch ', epoch)
        train_loss = 0
        val_loss = 0

        model.train()
        for sentence, tags in train_set: # run through the training set

            model.zero_grad()

            # ready the x's and y's
            try:
                sentence_in = sentence
                chars_in = arch_blocks.prepare_sequence(sentence, data.char2ix, level='char')
                targets = arch_blocks.prepare_sequence(tags, data.label2ix, level='word')
            except:
                continue

            #send the words and characters (x) through model and get tag_scores (y)
            try:
                tag_scores = model(sentence_in, chars_in)
            except KeyError:
                continue


            loss = loss_function(tag_scores, targets)
            #loss /= len(sentence)
            train_loss += loss

            loss.backward()
            optimizer.step()
        train_losses.append(train_loss/len(train_set))

        # set to eval mode, no backprop,
        model.eval()
        with torch.no_grad():
            for sentence, tags in val_set: # run through the validation set



                # ready the x's and y's
                try:
                    sentence_in = sentence
                    chars_in = arch_blocks.prepare_sequence(sentence, data.char2ix, level='char')
                    targets = arch_blocks.prepare_sequence(tags, data.label2ix, level='word')
                except:
                    continue

                #send the words and characters (x) through model and get tag_scores (y)
                try:
                    tag_scores = model(sentence_in, chars_in)
                except KeyError:
                    continue


                loss = loss_function(tag_scores, targets)
                #loss /= len(sentence)
                val_loss += loss

            val_losses.append(train_loss/len(val_set))

    if plot:
        plt.figure(dpi=100)
        plt.plot(range(epochs), train_losses, label='training')
        plt.plot(range(epochs), val_losses,   label='validation')
        plt.title('Char+Word Level LSTM Training Curve', fontsize=15)
        plt.xlabel('Epoch', fontsize=14)
        plt.ylabel('Normalized X-entropy Loss', fontsize=14)
        plt.legend()
    else:
        pass

    return model
