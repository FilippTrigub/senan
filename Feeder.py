import os
from typing import List

import tweepy
import yaml as yaml
from dotenv import load_dotenv

from utils import misc


class TwitterFeeder:
    key = None
    secret = None
    access_token = None
    access_token_secret = None
    bearer_token = None

    QUERY = ' -is:retweet -is:quote -has:mentions lang:en'

    def __init__(self, query, quantity_of_tweets):
        self.QUERY = query + self.QUERY
        self.set_config()
        self.quantity_of_tweets = quantity_of_tweets
        self.client = tweepy.Client(self.bearer_token)

        # Authenticate with Twitter API
        auth = tweepy.OAuthHandler(self.key, self.secret)
        auth.set_access_token(self.access_token, self.access_token_secret)
        self.api = tweepy.API(auth)

    # get tweets
    def get_query_tweets(self):
        self.query_tweets = self.client.search_recent_tweets(query=self.QUERY,
                                                             max_results=self.quantity_of_tweets,
                                                             expansions=['referenced_tweets.id',
                                                                         'in_reply_to_user_id', 'author_id'])
        return self.query_tweets

    # take first tweet that is not retweet
    def get_selected_ukraine_tweet(self):
        self.selected_tweet = None
        while not self.selected_tweet and len(self.query_tweets) > 0:
            if (not self.query_tweets.data[-1].referenced_tweets
                or self.query_tweets.data[-1].referenced_tweets and self.query_tweets.data[-1].referenced_tweets[
                    0].type != 'retweeted') \
                    and 'RT @' not in self.query_tweets.data[-1].text:
                self.selected_tweet = self.query_tweets.data.pop()
        if not self.selected_tweet:
            raise ValueError("No tweet found")

    def get_username_and_id(self):
        self.user_name = \
            self.client.get_users(ids=[self.selected_tweet.author_id]).data[0].username
        self.user_screenname = \
            self.client.get_users(ids=[self.selected_tweet.author_id]).data[0].name
        self.tweet_id = self.selected_tweet.id

    def get_replies(self):
        # WARNING: this method is not used because it requires elevated permissions for the Twitter API
        self.replies_full_text = []
        self.query_tweets = self.get_query_tweets()
        while len(self.query_tweets) > 0 and len(self.replies_full_text) == 0:
            self.get_selected_ukraine_tweet()
            self.get_username_and_id()
            paginator = tweepy.Paginator(self.client.search_recent_tweets,
                                         query='to:{} is:reply'.format(self.user_name),
                                         since_id=self.tweet_id, max_results=100)
            for page in paginator:
                if not page.data:
                    continue
                try:
                    while len(page.data) > 0:
                        self.replies_full_text.append(page.data.pop().text)
                except tweepy.errors.TooManyRequests as e:
                    # break
                    print("Twitter api rate limit reached".format(e))
                    break
                except tweepy.errors.TweepyException as e:
                    print("TweepyException occured:{}".format(e))
                    break
                except StopIteration:
                    break
                except Exception as e:
                    print("Failed while fetching replies {}".format(e))
                    break

    def extract_tweet_images(self, keys, tweet_id: List, usernames: List) -> dict:
        # Get tweet data from Twitter API and Selenium
        image_paths = dict()
        for key, tweet_id, username in zip(keys, tweet_id, usernames):
            # Check if tweet has media
            media_url = f'https://twitter.com/{username}/status/{tweet_id}'
            path = f'assets/png/{key}.png'
            misc.html_to_png(media_url, path)
            image_paths[tweet_id] = path

        return image_paths

    def set_config(self):
        load_dotenv()
        self.key = os.getenv('TWITTER_KEY')
        self.secret = os.getenv('TWITTER_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')

