import tweepy


class TwitterFeeder:
    key = '3WUh5iiia2hKFOhD2kFvC6hk7'
    secret = 'hksle58dXcT38bzJNwUdHmTs8LP7FRoFjQaPPFAFrfDjiavB8o'
    access_token = '1257688956428341249-tcbkjpwgjSZgOoe6FTs7ZXdvyReLrB'
    access_token_secret = '1jO9akCleUU8hNOnqcia5v94mnhdRsiMsykBWc0VmVbC6'

    bearer_token = 'AAAAAAAAAAAAAAAAAAAAALEDeQEAAAAAnfu%2FhYBVPHHDi1P7d%2FRnCLhKKMA%3DmzjGpnypKzdkBYTsYUszmxzcioN3JXEgqUPM0VogTZKvNSE75U'

    QUERY = ' -is:retweet -is:quote -has:mentions lang:en'

    def __init__(self, query, quantity_of_tweets):
        self.QUERY = query + self.QUERY
        self.quantity_of_tweets = quantity_of_tweets
        self.client = tweepy.Client(self.bearer_token)

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
