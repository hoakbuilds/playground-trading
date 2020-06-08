import tweepy

from playground import settings as s


class TwitterNotifier:
    """
    Twitter Notifier class for the Twitter API
    """

    def __init__(self, logger):
        self.auth = tweepy.OAuthHandler(s.CONSUMER_KEY, s.CONSUMER_SECRET)
        self.auth.set_access_token(s.ACCESS_TOKEN, s.ACCESS_TOKEN_SECRET)
        self.api = tweepy.API(self.auth)
        self.logger = logger

    def post_test_tweet(self):
        self.api.update_status("Henlo this is test")

    def post_fear_greed_update(self, yesterday, today):
        self.api.update_status("Yesterday's F&G: {}\nToday's F&G: {}".format(yesterday, today))

    def post_results_tweet(self, tweet_string: str = ''):
        self.api.update_status("{}".format(tweet_string))

    def post_crossover(self, ft_name, today, reason, ema1=None, ema2=None):
        result = None
        try:
            if ema1 > 1 and ema2 > 1:
                result = self.api.update_status("{} Crossee: {:.3f}\n Crossed: {:3f}\n Open: {:3f}\n Close: {:3f}\n\n {}".format(
                    ft_name, ema1, ema2, today.open, today.close, reason,
                    ),
                )
            else:
                result = self.api.update_status("{} Crossee: {:.8f}\n Crossed: {:8f}\n Open: {:8f}\n Close: {:8f}\n\n {}".format(
                    ft_name, ema1, ema2, today.open, today.close, reason,
                    ),
                )
        except:
            pass
        if result:
            self.logger.info('TweepyError: {}'.format(result))

    def post_indicators(
        self, ft_name, mrfi=None, smrfi=None, mfi=None, rsi=None, ema20=None, ema50=None, ema100=None,
    ):
        result = None
        try:
            if ema20 > 1:
                result = self.api.update_status("{}RSI: {:.2f}\nMFI: {:.2f}\nMRFI: {:.2f}\nSMRFI: {:.2f}\nEMA20: {:.3f}\nEMA50: {:.3f}\nEMA100: {:.3f}".format(
                    ft_name, round(rsi, 2), round(mfi, 2), round(mrfi, 2), round(smrfi, 2), ema20, ema50, ema100, 
                ))
            else:
                result = self.api.update_status("{}RSI: {:.2f}\nMFI: {:.2f}\nMRFI: {:.2f}\nSMRFI: {:.2f}\nEMA20: {:.8f}\nEMA50: {:.8f}\nEMA100: {:.8f}".format(
                    ft_name, round(rsi, 2), round(mfi, 2), round(mrfi, 2), round(smrfi, 2), ema20, ema50, ema100, 
                ))
        except:
            pass
        if result:
            self.logger.info('TweepyError: {}'.format(result))


    def post_tweet_ft(
        self, ft_name, reason, exit_price=None, entry_price=None, entry_capital=None, risk=None,
    ):
        result = None
        try:
            if exit_price:
                if exit_price > 1:
                    result = self.api.update_status("{}  {}\nExit Price: {:.3f}".format(
                        ft_name, reason, round(exit_price, 3), 
                    ))
                else:
                    result = self.api.update_status("{}  {}\nExit Price: {:.8f}".format(
                        ft_name, reason, round(exit_price, 8), 
                    ))
            elif entry_price and entry_capital and risk:
                if entry_price > 1:
                    result = self.api.update_status("{}  {}\nEntry Price: {:.3f}\nEntry Capital: {:.2f}\nRisk: {:.2f} (static)".format(
                        ft_name, reason, entry_price, entry_capital, risk,
                    ))
                else:
                    result = self.api.update_status("{}  {}\nEntry Price: {:.8f}\nEntry Capital: {:.2f}\nRisk: {:.2f} (static)".format(
                        ft_name, reason, entry_price, entry_capital, risk,
                    ))
        except:
            pass
        if result:
            self.logger.info('TweepyError: {}'.format(result))
