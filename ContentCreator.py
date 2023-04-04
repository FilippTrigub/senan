import os

import openai

import numpy as np
import argparse

from Feeder import TwitterFeeder
from GraphContentGenerator import GraphContentGenerator
from SentimentAnalyzer import SentimentAnalyzer
from video_creation.background import download_background, chop_background_video
from video_creation.final_video import make_final_video, make_final_video_with_gpt
from video_creation.voices import save_text_to_mp3
from emoji import emoji_count


class ContentCreator:
    query = 'dummy_query'
    default_config_path = 'config_empty.yaml'
    use_gpt = True

    def __init__(self):
        self.feeder = None

        self.quantity_of_tweets = 10
        arguments = self.parse_arguements()
        self.query = arguments.query
        self.config_path = arguments.config
        self.openai_key = arguments.key

        print(f'Get tweets for {self.query}')
        self.engine = SentimentAnalyzer()

    def create(self):
        self.feeder = TwitterFeeder(self.query, self.quantity_of_tweets, self.config_path)

        tweets = self.feeder.get_query_tweets()

        # convert tweets into a vader-fitting format
        sentences = self.convert_tweets(tweets)

        # analyze with VADER
        vader_scores, vader_scores_as_classes = self.engine.analyze(sentences)

        # get basic statistics
        statistics = self.get_statistics(sentences, vader_scores)

        # create content
        content_object = self.create_content(vader_scores, statistics)

        if self.use_gpt:
            content_object = self.create_content_object_with_gpt(content_object)

        # make the video
        self.make_video(content_object, self.use_gpt)

    def convert_tweets(self, tweets):
        return [tweet.text for tweet in tweets.data]

    def get_statistics(self, sentences, scores):
        """
        Analyzes supplied tweets to retrieve statistics.

        Statistics must have a readable key in plural form.
        Each statistic must be a dict with keys: data, correlation.

        :param sentences: tweets, list of strings
        :param scores: VADER scores, DataFrame
        :return: statistics, dict of dicts
        """
        statistics = {'lengths': self.get_length_statistic(sentences, scores),
                      'emoji counts': self.get_emoji_count_statistic(sentences, scores)}
        return statistics

    def get_length_statistic(self, sentences, scores):
        lengths_of_sentences = [len(sentence) for sentence in sentences]
        correlation_with_scores = np.corrcoef(lengths_of_sentences, scores['compound'])[0][1]
        return {'data': lengths_of_sentences, 'correlation': correlation_with_scores}

    @staticmethod
    def get_emoji_count_statistic(sentences, scores):
        counter_list = [emoji_count(sentence) for sentence in sentences]
        correlation_with_scores = np.corrcoef(counter_list, scores['compound'])[0][1]
        return {'data': counter_list, 'correlation': correlation_with_scores}

    def create_content(self, vader_scores, statistics):
        # todo create more graphs based on analysis
        content_text = self.get_text_for_images(vader_scores, statistics)
        content_object = self.create_content_object_without_gpt(content_text, vader_scores, statistics)

        return content_object

    def make_video(self, content_object, use_gpt):
        total_audio_duration, _ = save_text_to_mp3(content_object)
        download_background()
        chop_background_video(total_audio_duration)
        if use_gpt:
            make_final_video_with_gpt(content_object)
        else:
            make_final_video(content_object)

    def get_text_for_images(self, scores, statistics):
        content_text = dict()
        content_text['intro_text'] = f'What does twitter think about {self.query}? ' \
                                     f'SENAN has analyzed the sentiment of {self.quantity_of_tweets} ' \
                                     f'tweets using Vader and Seaborn. '
        content_text['score_text'] = self.get_score_describtion(scores)
        for key, statistic in statistics.items():
            # todo write about corr with sentiment and disperision of data
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

    def parse_arguements(self):
        parser = argparse.ArgumentParser(
            description=("Searches for flats on Immobilienscout24.de and wg-gesucht.de"
                         " and sends results to Telegram User"),
            epilog="Designed by Trigub"
        )
        parser.add_argument('--query', '-q',
                            type=str,
                            default=self.query,
                            help=f'Query for twitter. If not set, use "{self.query}"'
                            )
        parser.add_argument('--config', '-c',
                            type=str,
                            default=self.default_config_path,
                            help=f'Config file to use. If not set, try to use "{self.default_config_path}"'
                            )
        parser.add_argument('--key', '-k',
                            type=str,
                            default='',
                            help='OpenAI key'
                            )
        return parser.parse_args()

    def create_content_object_without_gpt(self, content_text, vader_scores, statistics):
        content_object = dict()
        for key, content_item in content_text.items():
            if key == 'intro_text':
                content_object['intro_object'] = {'text': content_item}
            elif key == 'score_text':
                basic_score_object = \
                    GraphContentGenerator.get_basic_score_object(content_item, vader_scores)
                content_object['basic_score_object'] = basic_score_object
            elif key == 'lengths':
                compound_vs_length_object = \
                    GraphContentGenerator.get_compound_vs_length_object(content_item, vader_scores, statistics[key])
                content_object['compound_vs_length_object'] = compound_vs_length_object
            elif key == 'emoji counts':
                compound_vs_emoji_count_object = \
                    GraphContentGenerator.get_compound_vs_emoji_count_object(content_item, vader_scores,
                                                                             statistics[key])
                content_object['compound_vs_emoji_count'] = compound_vs_emoji_count_object
                # todo sync all the terminology
        content_object['outro_text'] = {'text': 'Follow to know, what people think!'}
        return content_object

    def create_content_object_with_gpt(self, content_object):
        gpt_prompt = f'Make the following text to sound engaging, enthusiastic and less than 60 seconds long:' \
                     f'\n' \
                     f'Opinions on {self.query}: '
        for key, content_item in content_object.items():
            gpt_prompt += f'{content_item["text"]} '

        openai.api_key = self.openai_key
        content_object['gpt'] = {'text': openai.Completion.create(
            engine="text-davinci-002",
            prompt=gpt_prompt,
            temperature=0.5,
            max_tokens=256,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        ).choices[0].text}
        return content_object


if __name__ == "__main__":
    content_creator = ContentCreator()
    content_creator.create()
