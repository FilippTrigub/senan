import re

import chardet as chardet
import pandas as pd
import nltk
from nltk.corpus import stopwords
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score, r2_score
from sklearn.model_selection import train_test_split

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


def convert_labels_to_vader_compound_scores(labels):
    """ VADER scores are valued from -1 to 1 with -1 being negative and 1 being positive. """
    labels_as_scores = []
    for label in labels:
        if label == 'positive':
            labels_as_scores.append(0.66)
        elif label == 'neutral':
            labels_as_scores.append(0)
        elif label == 'negative':
            labels_as_scores.append(-0.66)
    return labels_as_scores


def convert_vader_scores_to_classes(vader_scores):
    """
    VADER scores are valued from -1 to 1 with -1 being negative and 1 being positive.
    This method maps these to negative, neutral and positive.
    """
    scores_as_classes = []
    for score in vader_scores['compound']:
        if score <= -0.05:
            scores_as_classes.append('negative')
        elif score >= 0.05:
            scores_as_classes.append('positive')
        else:
            scores_as_classes.append('neutral')
    return scores_as_classes

class SentimentAnalyzer:
    def __init__(self):
        # VADER
        self.analyzer = SentimentIntensityAnalyzer()

    def analyze(self, sentences):
        vader_scores = pd.DataFrame([self.analyzer.polarity_scores(sentence) for sentence in sentences])
        vader_scores_as_classes = convert_vader_scores_to_classes(vader_scores)
        return vader_scores, vader_scores_as_classes

# print(f'VADER: {accuracy_score(vader_scores_as_classes, labels)}')
#
# # R2 calculation
# vader_compound_scores = [score['compound'] for score in vader_scores]
# labels_as_scores = convert_labels_to_vader_compound_scores(labels)
# print(f'VADER R2: {r2_score(labels_as_scores, vader_compound_scores)}')
#
# print('done')
