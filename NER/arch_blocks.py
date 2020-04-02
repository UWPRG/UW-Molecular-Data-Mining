"""
This module contains architectures for NER. Focus is bidirectional LSTMS at
the character and word level.
"""

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

def prepare_sequence(sequence, to_idx, level):
    """
    This function creates a sequence of words being mapped
    to their respective features

    Parameters:
        seq (list, required): The sequence of single words, or single characters, to be mapped

        to_ix (dict, required): Dictionary of maps for each word/char to their feature

    Returns:
        torch.tensor : A tensor containing the feature mappings for every entry in seq
    """
    if level == 'word':
        idxs = [to_idx[str(word)] for word in sequence] # a list of each word being mapped to it's representation
        return torch.tensor(idxs, dtype=torch.long)

    elif level == 'char':
        char_idxs_for_all_words = []
        for word in sequence:
            idxs = [to_idx[char] for char in str(word)]
            char_idxs_for_all_words.append(idxs)
        return char_idxs_for_all_words

    else:
        pass # Dave Beck taught me this move, among others

class LinearModel(nn.Module):

    def __init__(self, in_reprs, out_reprs):
        super(LinearModel, self).__init__()
        self.in_reprs = in_reprs
        self.out_reprs = out_reprs
        self.linear = nn.Linear(in_reprs, out_reprs)

    def forward(self, input):
        output = self.linear(input)
        return output

class CharLSTM(nn.Module):

    def __init__(self,
                 word_embedding_dim, word_hidden_dim,
                 char_embedding_dim, char_hidden_dim,
                 word_vocab_size, char_vocab_size,
                 tagset_size):

        super(CharLSTM, self).__init__()
        self.word_hidden_dim = word_hidden_dim
        self.char_hidden_dim = char_hidden_dim

        self.word_embeddings = nn.Embedding(word_vocab_size, word_embedding_dim)
        self.char_embeddings = nn.Embedding(char_vocab_size, char_embedding_dim)

        # The LSTM takes word embeddings as inputs, and outputs hidden states
        # with dimensionality hidden_dim.
        self.word_lstm = nn.LSTM(word_embedding_dim + char_embedding_dim, word_hidden_dim)
        self.char_lstm = nn.LSTM(char_embedding_dim, char_hidden_dim)

        # The linear layer that maps from hidden state space to tag space
        self.hidden2tag = nn.Linear(word_hidden_dim, tagset_size)

    def forward(self, sentence_words, sentence_characters):
        # get the word embeddings for each word in sentence
        # print('This is sentence used for word_embeddings(sentence_words)')
        # print(sentence_words)
        word_embeds = self.word_embeddings(sentence_words)
        print('This is word_embeds.shape \n', word_embeds.shape)
        print('This is word_embeds: \n', word_embeds)
        # print('This is word_embeds ', word_embeds)
        char_embeds = [self.char_embeddings(torch.tensor(word, dtype=torch.long)) for word in sentence_characters]


        # send all of the characters through the char_lstm, get out representation
        char_level_reprs_fwd = torch.zeros(len(sentence_words), 6)
        for i, embed_group in enumerate(char_embeds): # remember this is a list of lists
            char_lstm_out, _ = self.char_lstm(embed_group.view(len(embed_group),1, -1))
            last_rep = char_lstm_out[-1][-1]
            char_level_reprs_fwd[i] = last_rep

        # concat the word level and character level representations
        word_embeds = torch.cat((word_embeds, char_level_reprs_fwd), 1)


        word_lstm_out, _ = self.word_lstm(word_embeds.view(len(sentence_words), 1, -1))
        # print('This is word_lstm_out')

        tag_space = self.hidden2tag(word_lstm_out.view(len(sentence_words), -1))


        tag_scores = F.log_softmax(tag_space, dim=1)

        return tag_scores

class W2VCharLSTM(nn.Module):

    def __init__(self,
                 word_hidden_dim, char_hidden_dim, char_embedding_dim,
                 ner_data_obj):
        """
        Create a unidirectional, character+word level LSTM.

        Parameters:
            word_hidden_dim (int, required): Dimensionality of hidden layer in the
                word-level lstm. Also the input dimenstionality of the hidden2tag
                linear layer.

            char_hidden_dim (int, required): Dimensionality of the hidden layer in the
                char LSTM

            char_embedding_dim (int, required): Dimenstionality of the randomized
                character embeddings

            ner_data_obj (ner.NerData, required): Data container housing the BESIO
                training data
        """

        super(W2VCharLSTM, self).__init__()
        self.word_hidden_dim = word_hidden_dim
        self.char_hidden_dim = char_hidden_dim
        self.char_embedding_dim = char_embedding_dim

        self.w2v_model = ner_data_obj.w2v_model

        self.char_embeddings = nn.Embedding(len(ner_data_obj.char_set), char_embedding_dim)

        # The LSTM takes word embeddings as inputs, and outputs hidden states
        # with dimensionality hidden_dim.
        # the w2v model vector size is the size of the word embedding
        self.word_lstm = nn.LSTM(self.w2v_model.wv.vector_size + char_embedding_dim, word_hidden_dim,
                                 bidirectional=False)
        self.char_lstm = nn.LSTM(char_embedding_dim, char_hidden_dim,
                                 bidirectional=False)

        # The linear layer that maps from hidden state space to tag space
        self.hidden2tag = nn.Linear(word_hidden_dim, len(ner_data_obj.label_set))

    def forward(self, sentence_words, sentence_characters):
        """
        This method does a forward pass through the network.

        Parameters:
            sentence_words (list of strings): The list of words in the incoming sentence

            sentence_characters (list of ints): The list of characters, but mapped to their
                integer identifier
        """
        # get the word embeddings for each word in sentence
        # print('This is sentence used for word_embeddings(sentence_words)')
        # print(sentence_words)
        word_embeds = self.word_embeddings(sentence_words) # this gets the embeddings from w2v

        char_embeds = [self.char_embeddings(torch.tensor(word, dtype=torch.long)) for word in sentence_characters]


        # send all of the characters through the char_lstm, get out representation
        char_level_reprs_fwd = torch.zeros(len(sentence_words), self.char_embedding_dim)
        for i, embed_group in enumerate(char_embeds): # remember this is a list of lists
            char_lstm_out, _ = self.char_lstm(embed_group.view(len(embed_group),1, -1))
            last_rep = char_lstm_out[-1][-1]
            char_level_reprs_fwd[i] = last_rep

        # concat the word level and character level representations
        word_embeds = torch.cat((word_embeds, char_level_reprs_fwd), 1)


        word_lstm_out, _ = self.word_lstm(word_embeds.view(len(sentence_words), 1, -1))
        # print('This is word_lstm_out')

        tag_space = self.hidden2tag(word_lstm_out.view(len(sentence_words), -1))


        tag_scores = F.log_softmax(tag_space, dim=1)

        return tag_scores

    def word_embeddings(self, sentence_words):
        """
        This method grabs the w2v word_embeddings for every word in a sentence

        Parameters:
            sentence_words (list of strings): The words to grab w2v embeddings for
        """
        embeddings = torch.zeros(len(sentence_words), self.w2v_model.wv.vector_size)
        try:
            for i, word in enumerate(sentence_words):
                embedding = self.w2v_model.wv[word]             # this is a np array
                embeddings[i] = torch.from_numpy(embedding)  # append the pytorch tensor

        except:
            #print('This is sentence_words ', sentence_words)
            pass

        return embeddings


    def translate(self, sentence, data):
        """
        This function takes the output of a forward pass, and outputs what the human-readable predictions are.

        Paramters:
            output (pytorch tensor, required): Tensor predictions from the neural network, 2 dimensional

            data (ner.NerData, required): Ner data object

        Returns:
            tuple: Tuple of the human readable predictions for words in a sentence
        """
        # prepare the character sequence to go into lstm
        chars_in = prepare_sequence(sentence, data.char2ix, level='char')
        output = self.forward(sentence, chars_in)
        ix2label = data.ix2label

        labels = []
        for word in output:
            maxval, idx = torch.max(word, 0) # get the max value, and the index of the max value
            labels.append(ix2label[idx.item()])

        return labels



class WordLSTM(nn.Module):

    def __init__(self,
                 word_embedding_dim, word_hidden_dim,
                 word_vocab_size, tagset_size):

        super(WordLSTM, self).__init__()
        self.word_hidden_dim = word_hidden_dim

        self.word_embeddings = nn.Embedding(word_vocab_size, word_embedding_dim)

        # The LSTM takes word embeddings as inputs, and outputs hidden states
        # with dimensionality hidden_dim.
        self.word_lstm = nn.LSTM(word_embedding_dim, word_hidden_dim)

        # The linear layer that maps from hidden state space to tag space
        self.hidden2tag = nn.Linear(word_hidden_dim, tagset_size)

    def forward(self, sentence_words, sentence_characters):
        # get the word embeddings for each word in sentence
        word_embeds = self.word_embeddings(sentence_words)

        word_lstm_out, _ = self.word_lstm(word_embeds.view(len(sentence_words), 1, -1))

        tag_space = self.hidden2tag(word_lstm_out.view(len(sentence_words), -1))


        tag_scores = F.log_softmax(tag_space, dim=1)

        return tag_scores
