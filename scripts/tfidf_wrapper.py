import numpy as np
import pandas as pd
import sklearn
from sklearn.linear_model import SGDClassifier # support vector machine
from sklearn.feature_extraction.text import TfidfVectorizer

class tfidf_model:
    """
    This class creates a tfidf_model object which can be trained to classify the category of
    documents in a corpus.

    Parameters
    ----------
    training_corpus (list, required): The list of documents that will train the tfidf vectorizer.

    training_targets (list, required): Integer values that respectively correspond to the categories
        of the documents in training corpus.


    Attributes
    ----------
    training_corpus: The corpus of documents that are used to train the TF-IDF vectorizer.

    training_targets: List of integer values that represents the respective categories documents are
        meant to be classified in.

    vocab: List of all vocabulary words learned from the training corpus.

    array: The tf-idf matrix printed in array form.

    predictions: The predictions made by the classifier in the most recent call.

    accuracy: The accuracy of the current n-gram tf-idf/SVM model.



    """
    def __init__(self,training_corpus,training_targets):

        self.training_corpus = training_corpus
        self.training_targets = training_targets


    def train(self,ngrams=1):
        """
        This method trains the TF-IDV vectorizer on the training corpus. Creates a TF-IDF matrix,
        master vocabulary, and trains support vector machines to categorize documents based on the
        training target array.

        Parameters
        ----------
        ngrams (int, optional): The size of n-gram tf-idf analysis is done by. 1 = unigrams, 2 = bigrams,
            etc... Default value is 1.

        """


        self.vectorizer = TfidfVectorizer(ngram_range=(ngrams,ngrams))
        self.matrix = self.vectorizer.fit_transform(self.training_corpus)
        self.vocab = self.vectorizer.get_feature_names()
        self.array = self.matrix.toarray()
        self.classifier =  SGDClassifier(max_iter = 1000,tol=1e-3,verbose=1).fit(self.matrix, self.training_targets)

    def predict(self,test_corpus,test_targets = None):

        """
        This method makes category predictions for a test_corpus. It returns an array of prediction values
        for each document in the test corpus.

        Parameters
        ----------
        test_corpus (list, required): The corpus of documents being categorized, list of strings.

        test_targets (list, optional): The list of respective category targets for the test corpus. Only
            functions as an input for model accuracy calculation.
        """
        self.test_corpus = test_corpus
        self.test_targets = test_targets
        X_test = self.vectorizer.transform(test_corpus)
        self.predictions = self.classifier.predict(X_test)

        if test_targets != None:
            numcorrect = len(self.predictions) - np.count_nonzero(self.predictions - test_targets)
            self.accuracy = (float(numcorrect)/len(self.predictions))*100
            print('Accuracy is', self.accuracy, '%')
        else:
            self.accuracy = None

        return self.predictions
