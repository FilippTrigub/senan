from datetime import datetime

import openai

from ContentCreator import ContentCreator
from GraphContentGenerator import get_basic_score_object
from utils import misc
from video_creation.background import download_background, chop_background_video
from video_creation.final_video import make_final_video_with_gpt
from video_creation.voices import save_text_to_mp3


class LLMPoweredContentCreator(ContentCreator):
    def __init__(self):
        super().__init__()

    def create_content(self, tweets, vader_scores, statistics):
        plot_object = self._get_plots_without_text(vader_scores, statistics)

        _, most_positive_tweet, _, most_negative_tweet = \
            self.get_most_extreme_tweets(tweets, vader_scores)

        content_object = \
            self.create_content_object_with_gpt(
                plot_object,
                statistics,
                {
                    'positive': misc.remove_anything_but_english_text(
                        most_positive_tweet.text),
                    'negative': misc.remove_anything_but_english_text(
                        most_negative_tweet.text)
                }
            )
        print(content_object['gpt']['text'])
        return content_object

    def create_content_object_with_gpt(self, plot_object, statistics, most_extreme_tweets):
        pre_prompt = \
            f'You are a world class data explainer AI. ' \
            f'You will receive the analysis of {self.quantity_of_tweets} tweets on the topic of {self.query}. '
        statistics_pre_prompt = \
            f'The following are pearson correlation coefficients of the sentiments with several dimensions: {", ".join(self.STATISTICS)}. \n' + \
            f'\n'.join(f"{key}: {statistics['correlation']}" for key, statistics in statistics.items()) + \
            f'\n\n'
        extreme_tweets_pre_prompt = \
            f'You will also receive the texts of the most extreme tweets. \n' + \
            f'\n'.join(f"{key}: {tweet}" for key, tweet in most_extreme_tweets.items()) + \
            f'\n\n'
        task_statement_pre_prompt = \
            f'Describe the analysis in an engaging and enthusiastic way. ' \
            f'Start with the following phrase: <What does twitter think about {self.query}?> ' \
            f'Then quote the most positive and most negative tweet. ' \
            f'Then, for each dimension, describe its correlation with the sentiment of the tweets. ' \
            f'Then infer, what these could say about the authors of the tweets. Be creative and bold.' \
            f'Finally end with the phrase: <Subscribe to know what people tweet!> '

        pre_prompt += statistics_pre_prompt + extreme_tweets_pre_prompt + task_statement_pre_prompt

        openai.api_key = self.openai_api_key

        return {
            'gpt': {
                'text': openai.Completion.create(
                    engine="text-davinci-002",
                    prompt=pre_prompt,
                    temperature=1.0,
                    max_tokens=256,
                    top_p=1.0,
                    frequency_penalty=0.0,
                    presence_penalty=0.0
                ).choices[0].text,
                'graphs': plot_object
            },
            'timestamp': datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        }

    def make_video(self, content_object, use_gpt):
        total_audio_duration, _ = save_text_to_mp3(content_object)
        download_background()
        chop_background_video(total_audio_duration)
        filename = make_final_video_with_gpt(content_object)

        return filename

    def _get_plots_without_text(self, vader_scores, statistics):
        content_object = dict()
        content_object['intro_text'] = {'text': f'What does twitter think about \n{self.query}?'}
        content_object['score_text'] = get_basic_score_object('', vader_scores)
        for key, statistic in statistics.items():
            content_object[key] = self.STATISTICS_OBJECT_MAPPING[key]('', vader_scores, statistics[key])
        return content_object
