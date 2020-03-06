import logging
import pandas as pd
from playground.simulation import Period, Account
from playground.notifiers import TwitterNotifier
from playground.pair import MarketPair

DELTA_CANDLES = 25

def strategy_v1(
    name: str,
    pair: MarketPair,
    timeframe: str,
    account: Account,
    dataset: pd.DataFrame,
    lookback: pd.DataFrame,
    logger: logging.Logger,
    _tts: str,
    last_candle: pd.DataFrame = None,
):
    """
    Strategy_v1 logic.
    :param name: str
    :param account: Account
    :param dataset: pd.DataFrame
    :param lookback: pd.DataFrame
    :param _tts: str
    :param logger: logging.Logger
    """
    yesterday: period = None
    today: period = None
    lookback_period: period = None

    try:
        # Load into period class to simplify indexing
        lookback_period = Period(lookback)
    except ValueError:
        pass

    if last_candle is not None:
        try:
            today = lookback_period.loc(0) # Current candle
            yesterday = lookback_period.loc(-1) # Previous candle
        except ValueError:
            today = lookback.iloc[0] # Current candle
            yesterday = lookback.iloc[-1] # Previous candle
            pass
    else:
        today = last_candle

    logger.info('Processing logic...')
    tn = TwitterNotifier()

    if account.no != 0 and account.check_delta_since(delta=DELTA_CANDLES):
        strategy_v1_aux(today, name, logger, account, tn, tweet_string=_tts)
    elif account.no == 0:
        strategy_v1_aux(today, name, logger, account, tn, tweet_string=_tts)

    logger.info('------------'*10 )


def strategy_v1_aux(today, name, logger, account, tn, tweet_string):
    if today.mrfi_ob == 1 and today.smrfi_ob == 1:
        exit_price = today.close
        for position in account.positions:  
            if position.type == 'long':
                reason = 'Long Selling'
                logger.info(reason)
                if tn:
                    tn.post_tweet_ft(ft_name=tweet_string, reason=reason, exit_price=exit_price)
                account.close_position(position, 0.5, exit_price)

    if today.mrfi > 75 and today.smrfi > 70:
        risk          = 0.25
        entry_price   = today.open * 0.998
        entry_capital = account.buying_power*risk
        if entry_capital >= 0:
            reason = 'Short Hedge'
            logger.info(reason)
            if tn:
                tn.post_tweet_ft(
                    ft_name=tweet_string, reason=reason, entry_price=entry_price, entry_capital=entry_capital, risk=risk,
                )
            account.enter_position('short', entry_capital, entry_price)

    if today.mrfi_os == 1 and today.smrfi_os == 1:
        exit_price = today.close
        for position in account.positions:  
            if position.type == 'short':
                reason = 'Short Covering'
                logger.info(reason)
                if tn:
                    tn.post_tweet_ft(ft_name=tweet_string, reason=reason, exit_price=exit_price)
                account.close_position(position, 0.5, exit_price)

    if today.mrfi < 25 and today.smrfi < 30:
        risk          = 0.25
        entry_price   = today.low * 0.998
        entry_capital = account.buying_power*risk
        if entry_capital >= 0:
            reason = 'Long Entry'
            logger.info(reason)
            if tn:
                tn.post_tweet_ft(
                    ft_name=tweet_string, reason=reason, entry_price=entry_price, entry_capital=entry_capital, risk=risk,
                )
            account.enter_position('long', entry_capital, entry_price)