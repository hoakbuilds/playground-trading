import tweepy

from playground.settings import (
    CONSUMER_KEY, 
    CONSUMER_SECRET,
    ACCESS_TOKEN,
    ACCESS_TOKEN_SECRET,
)


class TwitterNotifier:
    """
    Twitter Notifier class for the Twitter API
    """

    def __init__(self):
        self.auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        self.auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        self.api = tweepy.API(self.auth)

    def post_test_tweet(self):
        self.api.update_status("Henlo this is test")

    def post_fear_greed_update(self, yesterday, today):
        self.api.update_status("Yesterday's F&G: {}\nToday's F&G: {}".format(yesterday, today))

    def post_results_tweet(self, tweet_string: str = ''):
        self.api.update_status("{}".format(tweet_string))

    def post_tweet_ft(
        self, ft_name, reason, exit_price=None, entry_price=None, entry_capital=None, risk=None,
    ):
        if exit_price:
            self.api.update_status("{} - {}\nExit Price: {}".format(
                ft_name, reason, exit_price, 
            ))
        elif entry_price and entry_capital and risk:
            self.api.update_status("{} - {}\nEntry Price: {}\nEntry Capital: {}\nRisk: {} (static)".format(
                ft_name, reason, entry_price, entry_capital, risk,
            ))