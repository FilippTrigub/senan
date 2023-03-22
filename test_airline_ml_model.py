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
    for score in vader_scores:
        if score['compound'] <= -0.05:
            scores_as_classes.append('negative')
        elif score['compound'] >= 0.05:
            scores_as_classes.append('positive')
        else:
            scores_as_classes.append('neutral')
    return scores_as_classes

nltk.download('stopwords')

data_source_path = "C:/coding_challanges/sentimental_twitter/data-Airline/all_tweets_with_long_labels.csv"
with open(data_source_path, 'rb') as rawdata:
    guessed_encoding = chardet.detect(rawdata.read(10000))
airline_tweets = pd.read_csv(data_source_path, encoding=guessed_encoding['encoding'], delimiter=',',
                             encoding_errors='ignore')

features = airline_tweets['text'].values
labels = airline_tweets['airline_sentiment'].values

processed_features = []

for sentence in range(0, len(features)):
    # Remove all the special characters
    processed_feature = re.sub(r'/W', ' ', str(features[sentence]))

    # remove all single characters
    processed_feature = re.sub(r'/s+[a-zA-Z]/s+', ' ', processed_feature)

    # Remove single characters from the start
    processed_feature = re.sub(r'/^[a-zA-Z]/s+', ' ', processed_feature)

    # Substituting multiple spaces with single space
    processed_feature = re.sub(r'/s+', ' ', processed_feature, flags=re.I)

    # Removing prefixed 'b'
    processed_feature = re.sub(r'^b/s+', '', processed_feature)

    # Converting to Lowercase
    processed_feature = processed_feature.lower()

    processed_features.append(processed_feature)

vectorizer = TfidfVectorizer(max_features=2500, min_df=7, max_df=0.8, stop_words=stopwords.words('english'))
vectorized_features = vectorizer.fit_transform(processed_features).toarray()

X_train, X_test, y_train, y_test = train_test_split(vectorized_features, labels, test_size=0.2, random_state=0)

# fitted classfier
text_classifier = RandomForestClassifier(n_estimators=200, random_state=0)
text_classifier.fit(X_train, y_train)

predictions = text_classifier.predict(X_test)

# print(confusion_matrix(y_test, predictions))
# print(classification_report(y_test, predictions))
print(f'Trained model: {accuracy_score(y_test, predictions)}')

# VADER
analyzer = SentimentIntensityAnalyzer()
vader_scores = [analyzer.polarity_scores(sentence) for sentence in processed_features]
vader_scores_as_classes = convert_vader_scores_to_classes(vader_scores)
print(f'VADER: {accuracy_score(vader_scores_as_classes, labels)}')

# R2 calculation
vader_compound_scores = [score['compound'] for score in vader_scores]
labels_as_scores = convert_labels_to_vader_compound_scores(labels)
print(f'VADER R2: {r2_score(labels_as_scores, vader_compound_scores)}')

print('done')
