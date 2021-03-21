__title__ = "simulation"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

import pandas as pd
import numpy as np
from datetime import datetime as dt
from dateutil.parser import parse
from typing import Callable, List

# Local imorts
from playground import settings
from playground.util import setup_logger
from playground.util_ops import get_delta_callable_for_tf
from playground.simulation.operations import SimulatedOperation


class SimulationEngine():
    """An object representing the Simulation Engine.."""
    
    operations: List[SimulatedOperation]
    backtesting_engine: BacktestEngine = None
    forwardtesting_engine: ForwardtestEngine = None

    def __init__(self, config, yesterday, initial_capital, pair, tf, logic,):
        """Initate the SimulationEngine.
        param: config: An HLOCV+ pandas dataframe with a datetime index
        type: config: pandas.DataFrame
        """

    def update_datasets(self, dataset):
        """Process ForwardTestSession.
        :param dataset: An HLOCV+ pandas dataframe with a datetime index
        :type dataset: pandas.DataFrame
        """
        self.backdata = dataset

    def process(self, today):
        """Process ForwardTestSession.
        :param today: An HLOCV+ pandas dataframe with the last closed candle
        :type today: pandas.DataFrame
        :return: A bactesting simulation
        :rtype: BackTestSession
        """

        current_time = dt.now()

        if current_time > (self.__next_analysis):
            self.logger.info(
                'Processing... %-4s - %-4s - %-4s ' + '------------'*10,
                self.pair, self.tf, today.datetime,
            )
            self.logger.info(
                'O: %-6.6g - H: %-6.6g - L: %-6.6g - C: %-6.6g - V: %-6.6g  - MRFI:' \
                +' %-6.6g  - SMRFI: %-6.6g  - RSI: %-6.6g  - MFI: %-6.6g  - EMA50: %-6.6g  - EMA100: %-6.6g', \
                today.open, today.high, today.low, today.close, today.volumeto, today.mrfi, 
                today.smrfi, today.rsi, today.mfi, today.ema50, today.ema100,
            )
            date = today.get('datetime')
            equity = self.account.total_value(today.close)
            
            self.data = self.data.append(today)
            self.data.sort_index(inplace=True, ascending=False)

            # Handle stop loss
            for p in self.account.positions:
                if p.type == "long":
                    if p.stop_hit(today.get('low')):
                        self.account.close_position(p, 1.0, today.get('low'))
                if p.type == "short":
                    if p.stop_hit(today.get('high')):
                        self.account.close_position(p, 1.0, today.get('high'))

            self.account.purge_positions()

            # Update account variables
            self.account.date = date
            self.account.equity.append(equity)

            # Equity tracking
            self.tracker.append({
                'date': date, 
                'benchmark_equity': today.get('close'),
                'strategy_equity': equity,
            })

            self.logger.info('Executing trading logic... LookbackData: {} :: Data: {}'.format(
                self.backdata.shape, self.data.shape
            ))
            # Execute trading logic and allow full lookback
            self.logic(
                name=self._name,
                pair=self.pair,
                timeframe=self.tf,
                account=self.account,
                dataset=self.backdata,
                lookback=self.data,
                logger=self.logger,
                last_candle=today,
                _tts=self._tts,
                _simple_tts=self._simple_tts
            )

            self.__next_candle = (dt.fromtimestamp(today.time) + self.__analysis_throttle)
            self.__next_analysis = (self.__next_analysis + self.__analysis_throttle)
            self.yesterday = today
            # Cleanup empty positions
            # self.account.purge_positions()     
            # ------------------------------------------------------------

    def print_results(self):   
        """Print results"""
        self.logger.info("-------------- Results ----------------\n")
        being_price = self.data.iloc[0].open
        final_price = self.data.iloc[-1].close

        pc = helpers.percent_change(being_price, final_price)
        tweet_string = "--{}--\n".format(self._name)
        tweet_string += "Begin vs end : {0} {0}\n".format(being_price, final_price)
        tweet_string += "Buy and Hold : {0}%\n".format(round(pc*100, 2))
        tweet_string += "Net Profit   : {0}\n".format(round(helpers.profit(self.account.initial_capital, pc), 2))
        
        pc = helpers.percent_change(self.account.initial_capital, self.account.total_value(final_price))
        tweet_string += "Strategy     : {0}%\n".format(round(pc*100, 2))
        tweet_string += "Net Profit   : {0}\n".format(round(helpers.profit(self.account.initial_capital, pc), 2))

        longs  = len([t for t in self.account.opened_trades if t.type == 'long'])
        sells  = len([t for t in self.account.closed_trades if t.type == 'long'])
        shorts = len([t for t in self.account.opened_trades if t.type == 'short'])
        covers = len([t for t in self.account.closed_trades if t.type == 'short'])

        tweet_string += "Longs        : {0}\n".format(longs)
        tweet_string += "Sells        : {0}\n".format(sells)
        tweet_string += "Shorts       : {0}\n".format(shorts)
        tweet_string += "Covers       : {0}\n".format(covers)
        tweet_string += "--------------------\n"
        tweet_string += "Total Trades : {0}\n".format(longs + sells + shorts + covers)
        tweet_string += "---------------------------------------"

        self.logger.info(tweet_string)
        #tn = TwitterNotifier()
        #tn.post_results_tweet(tweet_string)

    def _get_results(self):
        """
        Return results as dict.
        # TODO: please.... lol
        # """
        longs  = len([t for t in self.account.opened_trades if t.type == 'long'])
        sells  = len([t for t in self.account.closed_trades if t.type == 'long'])
        shorts = len([t for t in self.account.opened_trades if t.type == 'short'])
        covers = len([t for t in self.account.closed_trades if t.type == 'short'])

        if len(self.data) != 0:
            begin_price = self.data.iloc[0].open
            final_price = self.data.iloc[-1].close
            buy_hold_pc = helpers.percent_change(begin_price, final_price)
            strategy_pc = helpers.percent_change(self.account.initial_capital, self.account.total_value(final_price))
            return {
                'name': self._name,
                'begin_price': begin_price,
                'final_price': final_price,
                'buy_and_hold': {
                    'rate_on_equity': round(buy_hold_pc*100, 2),
                    'net_profit': round(helpers.profit(self.account.initial_capital, buy_hold_pc), 2),
                },
                'strategy':{
                    'rate_on_equity': round(strategy_pc*100, 2),
                    'net_profit': round(helpers.profit(self.account.initial_capital, strategy_pc), 2),
                    'long_count': longs,
                    'sell_count': sells,
                    'short_count': shorts,
                    'cover_count': covers,
                    'total': longs + sells + shorts + covers,
                },
                'positions': self.account._get_positions(),
            }
        else:
            begin_price = 'N/A'
            final_price = 'N/A'
            buy_hold_pc = 'N/A'
            strategy_pc = 'N/A'
            return {
                'name': self._name,
                'begin_price': begin_price,
                'final_price': final_price,
                'buy_and_hold': {
                    'rate_on_equity': 0,
                    'net_profit': 0,
                },
                'strategy':{
                    'rate_on_equity': 0,
                    'net_profit': 0,
                    'long_count': longs,
                    'sell_count': sells,
                    'short_count': shorts,
                    'cover_count': covers,
                    'total': longs + sells + shorts + covers,
                },
                'positions': self.account._get_positions(),
            }

    def _get_operations(self):
        """
        TODO: Get operations from the current simulation engine execution
        """
        return self
