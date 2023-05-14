import os
from typing import Dict, Tuple

import numpy as np

from dotenv import load_dotenv
from tweepy import Tweet

from Feeder import TwitterFeeder
from GraphContentGenerator import get_basic_score_object, get_compound_vs_length_object, \
    get_compound_vs_emoji_count_object, get_compound_vs_average_word_length_object, \
    get_compound_vs_lexical_diversity_object
from SentimentAnalyzer import SentimentAnalyzer
from tweet_statistics import get_length_statistic, get_emoji_count_statistic, get_lexical_diversity_statistic, \
    get_average_word_length_statistic
from utils import misc
from video_creation.background import download_background, chop_background_video
from video_creation.final_video import make_final_video
from video_creation.voices import save_text_to_mp3
from emoji import emoji_count


class ContentCreator:
    query = 'dummy_query'
    use_gpt = False
    STATISTICS = ['lengths', 'emoji counts', 'lexical diversity', 'average word length']
    STATISTICS_GETTER_MAPPING = {STATISTICS[0]: get_length_statistic,
                                 STATISTICS[1]: get_emoji_count_statistic,
                                 STATISTICS[2]: get_lexical_diversity_statistic,
                                 STATISTICS[3]: get_average_word_length_statistic}
    STATISTICS_OBJECT_MAPPING = {STATISTICS[0]: get_compound_vs_length_object,
                                 STATISTICS[1]: get_compound_vs_emoji_count_object,
                                 STATISTICS[2]: get_compound_vs_lexical_diversity_object,
                                 STATISTICS[3]: get_compound_vs_average_word_length_object}

    def __init__(self):
        self.feeder = None
        self.quantity_of_tweets = 100

        load_dotenv()
        self.query = os.getenv('QUERY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')

        print(f'Get tweets for {self.query}')
        self.engine = SentimentAnalyzer()

    def create(self):
        self.feeder = TwitterFeeder(self.query, self.quantity_of_tweets)

        # clean up
        misc.remove_files_in_dir('assets/png')

        # get tweets
        tweets = self.feeder.get_query_tweets()

        # convert tweets into a vader-fitting format
        sentences = self.convert_tweets(tweets)

        # analyze with VADER
        vader_scores, vader_scores_as_classes = self.engine.analyze(sentences)

        # get basic statistics
        statistics = self.get_statistics(sentences, vader_scores)

        # create content
        content_object = self.create_content(tweets, vader_scores, statistics)

        # make the video
        filename = self.make_video(content_object, self.use_gpt)

        return filename

    def convert_tweets(self, tweets):
        tweet_texts = [tweet.text for tweet in tweets.data if self.tweet_is_valid(tweet.text)]
        return tweet_texts

    def get_statistics(self, sentences, scores):
        """
        Analyzes supplied tweets to retrieve statistics.

        Statistics must have a readable key in plural form.
        Each statistic must be a dict with keys: data, correlation.

        :param sentences: tweets, list of strings
        :param scores: VADER scores, DataFrame
        :return: statistics, dict of dicts
        """
        return {key: self.STATISTICS_GETTER_MAPPING[key](sentences, scores) for key in self.STATISTICS}

    def create_content(self, tweets, vader_scores, statistics):
        content_text = self.get_text_for_images(vader_scores, statistics)
        content_object = self.create_content_object(content_text, vader_scores, statistics)
        content_object = self.add_most_controversial_tweets(content_object, tweets, vader_scores)

        # add outro
        content_object['outro_text'] = {'text': 'Follow to know, what people think!'}

        return content_object

    def make_video(self, content_object, use_gpt):
        total_audio_duration, _ = save_text_to_mp3(content_object)
        download_background()
        chop_background_video(total_audio_duration)
        filename = make_final_video(content_object)
        return filename

    def get_text_for_images(self, scores, statistics):
        content_text = dict()
        content_text['intro_text'] = f'What does twitter think about {self.query}? ' \
                                     f'SENAN has analyzed the sentiment of {self.quantity_of_tweets} ' \
                                     f'tweets using Vader and Seaborn. '
        content_text['score_text'] = self.get_score_describtion(scores)
        for key, statistic in statistics.items():
            content_text[key] = self.get_correlation_statement(key, statistic)

        return content_text

    def get_score_describtion(self, scores):
        description = scores.describe()
        if description.loc['mean']['compound'] < 0.025:
            average_statement = 'negative '
        elif description.loc['mean']['compound'] > 0.025:
            average_statement = 'positive '
        else:
            average_statement = 'neutral '
        if abs(description.loc['mean']['compound'] > 0.075):
            average_statement = 'very ' + average_statement
        elif 0.05 > abs(description.loc['mean']['compound'] > 0.025):
            average_statement = 'rather ' + average_statement

        spread = description.loc['std']['compound'] / (
            abs(description.loc['min']['compound'] + abs(description.loc['max']['compound'])))
        if spread < 0.25:  # todo decide on better numbers
            spread_statement = 'are clustered around the mean'
        elif spread > 0.75:
            spread_statement = 'are very polarized'
        else:
            spread_statement = 'show a healthy spread'
        score_statement = f'Opinions are on average {average_statement} and {spread_statement}.'

        return score_statement

    def get_correlation_statement(self, key, statistic):
        correlation_statement = f'The {key} of the tweets '
        absolute_correlation_factor = abs(statistic['correlation'])
        if absolute_correlation_factor >= 0.75:
            correlation_statement += 'correlate strongly '
        elif 0.75 > absolute_correlation_factor >= 0.5:
            correlation_statement += 'correlate moderately '
        elif 0.5 > absolute_correlation_factor >= 0.25:
            correlation_statement += 'correlate weakly '
        else:
            correlation_statement += 'do not correlate '
        correlation_statement = correlation_statement + 'with their scores. '

        if absolute_correlation_factor >= 0.25:
            direction_statement = 'positive ' if np.sign(statistic['correlation']) > 0 else 'negative '
            correlation_statement = correlation_statement \
                                    + f'Higher values mean a more {direction_statement} sentiment. '

        return correlation_statement

    def create_content_object(self, content_text, vader_scores, statistics) -> Dict[str, Dict[str, str]]:
        content_object = dict()
        for key, content_item in content_text.items():
            if key == 'intro_text':
                content_object[key] = {'text': content_item}
            elif key == 'score_text':
                content_object[key] = get_basic_score_object(content_item, vader_scores)
            elif key in statistics.keys():
                content_object[key] = self.STATISTICS_OBJECT_MAPPING[key](content_item, vader_scores, statistics[key])
            return content_object

    def add_most_controversial_tweets(self, content_object, tweets, vader_scores):
        most_positive_index, most_positive_tweet, most_negative_index, most_negative_tweet = \
            self.get_most_extreme_tweets(tweets, vader_scores)

        image_data_dict = self.feeder.extract_tweet_images(keys=['most_negative_tweet', 'most_positive_tweet'],
                                                           tweet_id=[most_negative_tweet.id, most_positive_tweet.id],
                                                           usernames=[
                                                               tweets[1]['users'][most_positive_index].data['username'],
                                                               tweets[1]['users'][most_negative_index].data[
                                                                   'username']])

        content_object['most_negative_tweet'] = {
            'text': misc.remove_urls_and_emojis_and_leave_only_english_text(most_negative_tweet.text),
            'image': image_data_dict[most_negative_tweet.id]}
        content_object['most_positive_tweet'] = {
            'text': misc.remove_urls_and_emojis_and_leave_only_english_text(most_positive_tweet.text),
            'image': image_data_dict[most_positive_tweet.id]}
        return content_object

    @staticmethod
    def tweet_is_valid(text):
        if emoji_count(text) > 9:
            return False
        return True

    @staticmethod
    def get_most_extreme_tweets(tweets, vader_scores: Dict) -> Tuple[int, Tweet, int, Tweet]:
        most_negative_index, most_positive_index = misc.find_min_and_max_float_index(vader_scores['compound'])
        most_negative_tweet = tweets.data[most_negative_index]
        most_positive_tweet = tweets.data[most_positive_index]
        return most_positive_index, most_positive_tweet, most_negative_index, most_negative_tweet


if __name__ == "__main__":
    content_creator = ContentCreator()
    content_creator.create()
