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

    # create the training and val sets
    train_set = data.list[:num_train]
    val_set = data.list[num_train:]

    bad_train_sentences = 0
    bad_val_sentences = 0

    for epoch in range(epochs):
        print('On epoch ', epoch)
        train_loss = 0
        val_loss = 0

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
                    bad_val_sentences += 1
                    continue


                loss = loss_function(tag_scores, targets)
                loss /= len(sentence)
                val_loss += loss

            val_losses.append(val_loss/len(val_set))

        model.train()
        for sentence, tags in train_set: # run through the training set

            model.zero_grad()

            # ready the x's and y's
            try:
                sentence_in = sentence
                chars_in = arch_blocks.prepare_sequence(sentence, data.char2ix, level='char')
                targets = arch_blocks.prepare_sequence(tags, data.label2ix, level='word')
            except:
                bad_train_sentences += 1
                continue

            #send the words and characters (x) through model and get tag_scores (y)
            try:
                tag_scores = model(sentence_in, chars_in)
            except KeyError:
                continue


            loss = loss_function(tag_scores, targets)
            loss /= len(sentence)
            train_loss += loss

            loss.backward()
            optimizer.step()

        train_losses.append(train_loss/len(train_set))

    if plot:
        fig, ax = plt.subplots(dpi=100)
        ax.plot(range(epochs), train_losses, label='training')
        ax.plot(range(epochs), val_losses,   label='validation')
        ax.set_title('Char+Word Level LSTM Training Curve', fontsize=15)
        ax.set_xlabel('Epoch', fontsize=14)
        ax.set_ylabel('Normalized X-entropy Loss', fontsize=14)
        ax.legend()
        return model, val_set, train_set, bad_train_sentences, bad_val_sentences, fig
    else:
        return model, val_set, train_set, bad_train_sentences, bad_val_sentences

def train_save_rnn(model, data, epochs, save_epochs, train_frac, save_dir, model_name):
    """
    This function loops through a desired number of epochs training a model, and saves
    information about the model (parameters, loss, etc)

    Parameters:
        model (pytorch nn.Module subclass, required): The model to be trained

        data (ner.NerData object, required): The NerData object to be trained

        epochs (int, required): Total number of epochs to train model

        save_epochs (list/iterable of ints, required): List of epochs at which to save
            model info

        train_frac (float, required): The fraction of data from the data object to use
            for training

        save_dir (str, required): Path to the directory where info about model will be saved

        model_name (str, required): Name for your model. Best to provide info about
            the architecture. bidirectional, unidirectional, char level, etc..
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

    bad_train_sentences = 0
    bad_val_sentences = 0

    for epoch in range(epochs):
        print('On epoch ', epoch)
        train_loss = 0
        val_loss = 0
        if epoch in save_epochs:
            save_dict = {
            'epoch':epoch,
            'state_dict':model.state_dict(),
            'train_losses':train_losses,
            'val_losses':val_losses
            }

            path = save_dir + model_name + '_epoch' + epoch + '.pt'
            torch.save(save_dict, path)

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
                    bad_val_sentences += 1
                    continue


                loss = loss_function(tag_scores, targets)
                loss /= len(sentence)
                val_loss += loss

            val_losses.append(val_loss/len(val_set))

        model.train()
        for sentence, tags in train_set: # run through the training set

            model.zero_grad()

            # ready the x's and y's
            try:
                sentence_in = sentence
                chars_in = arch_blocks.prepare_sequence(sentence, data.char2ix, level='char')
                targets = arch_blocks.prepare_sequence(tags, data.label2ix, level='word')
            except:
                bad_train_sentences += 1
                continue

            #send the words and characters (x) through model and get tag_scores (y)
            try:
                tag_scores = model(sentence_in, chars_in)
            except KeyError:
                continue


            loss = loss_function(tag_scores, targets)
            loss /= len(sentence)
            train_loss += loss

            loss.backward()
            optimizer.step()

        train_losses.append(train_loss/len(train_set))
