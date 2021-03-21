import logging
import pandas as pd
from playground.simulation import Period, Account
from playground.notifiers import TwitterNotifier
from playground.models.pair import MarketPair

DELTA_CANDLES = 10

def strategy_v1(
    name: str,
    pair: MarketPair,
    timeframe: str,
    account: Account,
    dataset: pd.DataFrame,
    lookback: pd.DataFrame,
    logger: logging.Logger,
    _tts: str,
    _simple_tts: str,
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
    #tn = TwitterNotifier(logger=logger)

    if account.no != 0 and account.check_delta_since(delta=DELTA_CANDLES):
        strategy_v1_aux(today, name, logger, account, tn=None, _tts=_tts, _simple_tts=_simple_tts)
    elif account.no == 0:
        strategy_v1_aux(today, name, logger, account, tn=None, _tts=_tts, _simple_tts=_simple_tts)

    logger.info('------------'*10 )


def strategy_v1_aux(today, name, logger, account, tn, _tts, _simple_tts):

    signal: bool = False

    if today.ema20_50_cross:
        if tn:
            tn.post_crossover(
                ft_name=_simple_tts, today=today, reason='EMA 20/50 Crossover \n\nRUN-IT-BACK-TURBO-PLEB!', ema1=today.ema20, ema2=today.ema50,
            )
    if today.ema20_100_cross:
        if tn:
            tn.post_crossover(
                    ft_name=_simple_tts, today=today, reason='EMA 20/100 Crossover \n\nRUN-IT-BACK-TURBO-PLEB!', ema1=today.ema20, ema2=today.ema100,
                )
    if today.ema50_100_cross:
        if tn:
            tn.post_crossover(
                    ft_name=_simple_tts, today=today, reason='EMA 50/100 Crossover \n\nRUN-IT-BACK-TURBO-PLEB!', ema1=today.ema50, ema2=today.ema100,
                )
    if today.ema100_200_cross:
        if tn:
            tn.post_crossover(
                ft_name=_simple_tts, today=today, reason='EMA 50/100 Crossover \n\ncome on baby!', ema1=today.ema50, ema2=today.ema100,
            )
    if today.ema100_300_cross:
        if tn:
            tn.post_crossover(
                ft_name=_simple_tts, today=today, reason='EMA 50/100 Crossover \n\nCMON LFG', ema1=today.ema50, ema2=today.ema100,
            )

    
    if today.ema50_20_cross:
        if tn:
            tn.post_crossover(
                ft_name=_simple_tts, today=today, reason='EMA 50/20 Crossover \n\nSPOOL IT DOWN TURBO?!', ema1=today.ema50, ema2=today.ema20,
            )
    if today.ema100_20_cross:
        if tn:
            tn.post_crossover(
                ft_name=_simple_tts, today=today, reason='EMA 100/20 Crossover \n\nSPOOL IT DOWN TURBO?!', ema1=today.ema100, ema2=today.ema20,
            )
    if today.ema100_50_cross:
        if tn:
            tn.post_crossover(
                ft_name=_simple_tts, today=today, reason='EMA 100/50 Crossover \n\nSPOOL IT DOWN TURBO?!', ema1=today.ema100, ema2=today.ema50,
            )
    if today.ema200_100_cross:
        if tn:
            tn.post_crossover(
                ft_name=_simple_tts, today=today, reason='EMA 200/100 Crossover \n\nooo  sh', ema1=today.ema100, ema2=today.ema20,
            )
    if today.ema300_100_cross:
        if tn:
            tn.post_crossover(
                ft_name=_simple_tts, today=today, reason='EMA 300/100 Crossover \n\noH shIT g2g', ema1=today.ema100, ema2=today.ema50,
            )

    # MRFI and SMRFI based logic
    if today.mrfi_ob == 1 and today.smrfi_ob == 1:
        exit_price = today.close
        for position in account.positions:  
            if position.type == 'long':
                signal = True
                reason = 'Long Selling\n\nMRFI: {:.2f}\nSMRFI: {:.2f}'.format(today.mrfi, today.smrfi)
                logger.info(reason)
                if tn:
                    tn.post_tweet_ft(ft_name=_tts, reason=reason, exit_price=exit_price)
                account.close_position(position, 0.5, exit_price)

    if today.mrfi > 75 and today.smrfi > 70:
        risk          = 0.25
        entry_price   = today.open * 0.998
        entry_capital = account.buying_power*risk
        if entry_capital >= 0:
            signal = True
            reason = 'Short Hedge\n\nMRFI: {:.2f}\nSMRFI: {:.2f}'.format(today.mrfi, today.smrfi)
            logger.info(reason)
            if tn:
                tn.post_tweet_ft(
                    ft_name=_tts, reason=reason, entry_price=entry_price, entry_capital=entry_capital, risk=risk,
                )
            account.enter_position('short', entry_capital, entry_price)

    if today.mrfi_os == 1 and today.smrfi_os == 1:
        exit_price = today.close
        for position in account.positions:  
            if position.type == 'short':
                signal = True
                reason = 'Short Covering\n\nMRFI: {:.2f}\nSMRFI: {:.2f}'.format(today.mrfi, today.smrfi)
                logger.info(reason)
                if tn:
                    tn.post_tweet_ft(ft_name=_tts, reason=reason, exit_price=exit_price)
                account.close_position(position, 0.5, exit_price)

    if today.mrfi < 25 and today.smrfi < 30:
        risk          = 0.25
        entry_price   = today.low * 0.998
        entry_capital = account.buying_power*risk
        if entry_capital >= 0:
            signal = True
            reason = 'Long Entry\n\nMRFI: {:.2f}\nSMRFI: {:.2f}'.format(today.mrfi, today.smrfi)
            logger.info(reason)
            if tn:
                tn.post_tweet_ft(
                    ft_name=_tts, reason=reason, entry_price=entry_price, entry_capital=entry_capital, risk=risk,
                )
            account.enter_position('long', entry_capital, entry_price)

    # MFI and RSI based logic
    if today.mfi_ob == 1 and today.rsi_ob == 1:
        exit_price = today.close
        for position in account.positions:  
            if position.type == 'long':
                signal = True
                reason = 'Long Selling\n\nMFI: {:.2f}\nRSI: {:.2f}'.format(today.mfi, today.rsi)
                logger.info(reason)
                if tn:
                    tn.post_tweet_ft(ft_name=_tts, reason=reason, exit_price=exit_price)
                account.close_position(position, 0.35, exit_price)

    if today.mfi > 80 and today.rsi > 70:
        risk          = 0.15
        entry_price   = today.open * 0.998
        entry_capital = account.buying_power*risk
        if entry_capital >= 0:
            signal = True
            reason = 'Short Hedge\n\nMFI: {:.2f}\nRSI:'.format(today.mfi, today.rsi)
            logger.info(reason)
            if tn:
                tn.post_tweet_ft(
                    ft_name=_tts, reason=reason, entry_price=entry_price, entry_capital=entry_capital, risk=risk,
                )
            account.enter_position('short', entry_capital, entry_price)

    if today.mfi_os == 1 and today.rsi_os == 1:
        exit_price = today.close
        for position in account.positions:  
            if position.type == 'short':
                signal = True
                reason = 'Short Covering\n\nMFI: {:.2f}\nRSI: {:.2f}'.format(today.mfi, today.rsi)
                logger.info(reason)
                if tn:
                    tn.post_tweet_ft(ft_name=_tts, reason=reason, exit_price=exit_price)
                account.close_position(position, 0.35, exit_price)

    if today.mfi < 20 and today.rsi < 30:
        risk          = 0.15
        entry_price   = today.low * 0.998
        entry_capital = account.buying_power*risk
        if entry_capital >= 0:
            signal = True
            reason = 'Long Entry\n\nMFI: {:.2f}\nRSI: {:.2f}'.format(today.mfi, today.rsi)
            logger.info(reason)
            if tn:
                tn.post_tweet_ft(
                    ft_name=_tts, reason=reason, entry_price=entry_price, entry_capital=entry_capital, risk=risk,
                )
            account.enter_position('long', entry_capital, entry_price)


    if signal:
        if tn:
            tn.post_indicators(
                ft_name=_simple_tts, rsi=today.rsi, mfi=today.mfi, mrfi=today.mrfi, smrfi=today.smrfi, ema20=today.ema20,
                ema50=today.ema50, ema100=today.ema100,
            )


def chopfucker_v1(
    name: str,
    pair: MarketPair,
    timeframe: str,
    account: Account,
    dataset: pd.DataFrame,
    lookback: pd.DataFrame,
    logger: logging.Logger,
    _tts: str,
    _simple_tts: str,
    last_candle: pd.DataFrame = None,
):
    """
    Chopfucker_v1 logic. HABEMUS!!.
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
    #tn = TwitterNotifier(logger=logger)

    chopfucker_v1_aux(today, name, logger, account, tn=None, _tts=_tts, _simple_tts=_simple_tts)

    logger.info('------------'*10 )


def chopfucker_v1_aux(today, name, logger, account, tn, _tts, _simple_tts):

    signal: bool = False

    if today.ema20_50_cross:
        if tn:
            tn.post_crossover(
                ft_name=_simple_tts, today=today, reason='EMA 20/50 Crossover \n\nRUN-IT-BACK-TURBO-PLEB!', ema1=today.ema20, ema2=today.ema50,
            )
    if today.ema20_100_cross:
        if tn:
            tn.post_crossover(
                ft_name=_simple_tts, today=today, reason='EMA 20/100 Crossover \n\nRUN-IT-BACK-TURBO-PLEB!', ema1=today.ema20, ema2=today.ema100,
            )
    if today.ema50_100_cross:
        if tn:
            tn.post_crossover(
                ft_name=_simple_tts, today=today, reason='EMA 50/100 Crossover \n\nRUN-IT-BACK-TURBO-PLEB!', ema1=today.ema50, ema2=today.ema100,
            )
    if today.ema100_200_cross:
        if tn:
            tn.post_crossover(
                ft_name=_simple_tts, today=today, reason='EMA 50/100 Crossover \n\ncome on baby!', ema1=today.ema50, ema2=today.ema100,
            )
    if today.ema100_300_cross:
        if tn:
            tn.post_crossover(
                ft_name=_simple_tts, today=today, reason='EMA 50/100 Crossover \n\nCMON LFG', ema1=today.ema50, ema2=today.ema100,
            )

    
    if today.ema50_20_cross:
        if tn:
            tn.post_crossover(
                ft_name=_simple_tts, today=today, reason='EMA 50/20 Crossover \n\nSPOOL IT DOWN TURBO?!', ema1=today.ema50, ema2=today.ema20,
            )
    if today.ema100_20_cross:
        if tn:
            tn.post_crossover(
                ft_name=_simple_tts, today=today, reason='EMA 100/20 Crossover \n\nSPOOL IT DOWN TURBO?!', ema1=today.ema100, ema2=today.ema20,
            )
    if today.ema100_50_cross:
        if tn:
            tn.post_crossover(
                ft_name=_simple_tts, today=today, reason='EMA 100/50 Crossover \n\nSPOOL IT DOWN TURBO?!', ema1=today.ema100, ema2=today.ema50,
            )
    if today.ema200_100_cross:
        if tn:
            tn.post_crossover(
                ft_name=_simple_tts, today=today, reason='EMA 200/100 Crossover \n\nooo  sh', ema1=today.ema100, ema2=today.ema20,
            )
    if today.ema300_100_cross:
        if tn:
            tn.post_crossover(
                ft_name=_simple_tts, today=today, reason='EMA 300/100 Crossover \n\noH shIT g2g', ema1=today.ema100, ema2=today.ema50,
            )

    # MRFI and SMRFI based logic
    if today.slow_stoch_crossunder_smrfi and today.smrfi > 65:

        exit_price = today.close
        for position in account.positions:  
            if position.type == 'long':
                signal = True
                reason = 'Long Selling SSXU\n\nSMRFI: {:.2f}\nSS: {:.2f}\nSSSMA14: {:.2f}'.format(today.smrfi, today.slow_stoch, today.slow_stoch_sma14)
                logger.info(reason)
                if tn:
                    tn.post_tweet_ft(ft_name=_tts, reason=reason, exit_price=exit_price)
                account.close_position(position, 1, exit_price)

        risk          = 0.3
        entry_price   = today.upper
        entry_capital = account.buying_power*risk
        if entry_capital >= 0:
            signal = True
            reason = 'Short Hedge SSXU\n\nSMRFI: {:.2f}\nSS: {:.2f}\nSSSMA14: {:.2f}'.format(today.smrfi, today.slow_stoch, today.slow_stoch_sma14)
            logger.info(reason)
            if tn:
                tn.post_tweet_ft(
                    ft_name=_tts, reason=reason, entry_price=entry_price, entry_capital=entry_capital, risk=risk,
                )
            account.enter_position('short', entry_capital, entry_price)

    if (today.slow_stoch_crossover_smrfi and today.smrfi < 35) or (today.slow_stoch < 20 and today.smrfi < 40):

        exit_price = today.close
        for position in account.positions:  
            if position.type == 'short':
                signal = True
                reason = 'Short Covering SSXO\n\nSMRFI: {:.2f}\nSS: {:.2f}\nSSSMA14: {:.2f}'.format(today.smrfi, today.slow_stoch, today.slow_stoch_sma14)
                logger.info(reason)
                if tn:
                    tn.post_tweet_ft(ft_name=_tts, reason=reason, exit_price=exit_price)
                account.close_position(position, 1, exit_price)

        risk          = 0.3
        entry_price   = today.lower
        entry_capital = account.buying_power*risk
        if entry_capital >= 0:
            signal = True
            reason = 'Long Entry SSXO\n\nSMRFI: {:.2f}\nSS: {:.2f}\nSSSMA14: {:.2f}'.format(today.smrfi, today.slow_stoch, today.slow_stoch_sma14)
            logger.info(reason)
            if tn:
                tn.post_tweet_ft(
                    ft_name=_tts, reason=reason, entry_price=entry_price, entry_capital=entry_capital, risk=risk,
                )
            account.enter_position('long', entry_capital, entry_price)

    if signal:
        if tn:
            tn.post_indicators(
                ft_name=_simple_tts, rsi=today.rsi, mfi=today.mfi, mrfi=today.mrfi, smrfi=today.smrfi, ema20=today.ema20,
                ema50=today.ema50, ema100=today.ema100,
            )