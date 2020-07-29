import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import sklearn
from sklearn.linear_model import SGDClassifier # support vector machine
from sklearn.feature_extraction.text import TfidfVectorizer


df = pd.read_pickle('CI_abstracts_clean.pkl')
all_abstracts = df['processed_abstract']
all_rankings = df['tfidf_2'].to_numpy()

vectorizer = TfidfVectorizer(ngram_range=(1,1))
full_tfidf = vectorizer.fit_transform(all_abstracts)
vocab = vectorizer.get_feature_names()

rankings = all_rankings[~np.isnan(all_rankings)]
ranked_tfidf = full_tfidf[~np.isnan(all_rankings)]
unranked_tfidf = full_tfidf[np.isnan(all_rankings)]

train_scores = []
test_scores = []
trial_rankings = np.zeros((1000, all_rankings.shape[0]))
for i in range(1000):
    n_samples = rankings.shape[0]
    n_train = int(n_samples * 0.8)
    n_test = n_samples - n_train
    rand_idxs = np.random.choice(np.arange(n_samples), size=n_samples)
    train_idxs = rand_idxs[:n_train]
    test_idxs = rand_idxs[n_train:]

    train_rankings = rankings[train_idxs]
    test_rankings = rankings[test_idxs]
    train_tfidf = ranked_tfidf[train_idxs,:]
    test_tfidf = ranked_tfidf[test_idxs,:]

    # print(np.sum(train_rankings) / train_rankings.shape[0], np.sum(test_rankings) / test_rankings.shape[0])

    clf = SGDClassifier().fit(train_tfidf, train_rankings)
    train_scores.append(clf.score(train_tfidf, train_rankings))
    test_scores.append(clf.score(test_tfidf, test_rankings))

    predictions = clf.predict(full_tfidf)
    full_rankings = []
    for j, ranking in enumerate(predictions):
        if np.isnan(all_rankings)[j]:
            full_rankings.append(ranking)
        else:
            full_rankings.append(all_rankings[j])
    trial_rankings[i,:] = full_rankings



avg_predictions = np.mean(trial_rankings, axis=0)
rank2_idxs = np.where(avg_predictions > 0.5)[0]
tfidf_predictions = []
sum = 0
for idx in range(all_rankings.shape[0]):
    if idx in rank2_idxs:
        tfidf_predictions.append(1)
        sum += 1
        title = ' '.join(df.iloc[idx].title.strip().split('\n'))
        if np.isnan(all_rankings)[idx]:
            print('\033[0m'+title)
        else:
            print('\033[1m'+title)
    else:
        tfidf_predictions.append(0)
print('\033[0m')

print('Train - ', np.mean(train_scores))
print('Test - ', np.mean(test_scores))
print('Num Rank 2 - ', rank2_idxs.shape[0])
df.reset_index(drop=True, inplace=True)
df['tfidf_predictions'] = pd.Series(tfidf_predictions)
# df.to_pickle('CI_abstracts_clean.pkl')

# df = pd.read_pickle('CI_abstracts_clean.pkl')
# df = df[df.tfidf_predictions == 1]
# df.reset_index(drop=True, inplace=True)
# rank2_abstracts = df.processed_abstract.to_numpy()
#
# f = open('rank2_abstracts.txt', 'w')
# for i, row in df.iterrows():
#     f.write(row.processed_abstract+'SPLITHERE'+row.pii+'SPLITHERE'+row.doi+'\n')
