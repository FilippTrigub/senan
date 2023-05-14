import numpy as np
from emoji import emoji_count


def get_length_statistic(sentences, scores):
    lengths_of_sentences = [len(sentence) for sentence in sentences]
    correlation_with_scores = np.corrcoef(lengths_of_sentences, scores['compound'])[0][1]
    return {'data': lengths_of_sentences, 'correlation': correlation_with_scores}


def get_emoji_count_statistic(sentences, scores):
    counter_list = [emoji_count(sentence) for sentence in sentences]
    correlation_with_scores = np.corrcoef(counter_list, scores['compound'])[0][1]
    return {'data': counter_list, 'correlation': correlation_with_scores}


def _unique_word_ratio(sentence):
    words = sentence.split()
    unique_words = set(words)
    return len(unique_words) / len(words)


def get_lexical_diversity_statistic(sentences, scores):
    lexical_diversity = [_unique_word_ratio(sentence) for sentence in sentences]
    correlation_with_scores = np.corrcoef(lexical_diversity, scores['compound'])[0][1]
    return {'data': lexical_diversity, 'correlation': correlation_with_scores}


def _average_word_length(sentence):
    words = sentence.split()
    return sum(len(word) for word in words) / len(words)


def get_average_word_length_statistic(sentences, scores):
    average_word_length = [_average_word_length(sentence) for sentence in sentences]
    correlation_with_scores = np.corrcoef(average_word_length, scores['compound'])[0][1]
    return {'data': average_word_length, 'correlation': correlation_with_scores}
