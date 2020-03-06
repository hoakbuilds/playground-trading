__title__ = "simulation"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

import bokeh.plotting
import pandas as pd
import numpy as np
import warnings
import time
import logging
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
from typing import Callable

# Local imorts
from playground import settings
from playground.notifiers import TwitterNotifier
from playground.simulation import Account, helpers
from playground.util import setup_logger
from playground.util_ops import get_delta_callable_for_tf


class BackTestSession():
    """An object representing a Back Testing Simulation."""
    _name: str
    def __init__(self, data):
        """Initate the BackTestSession.
        :param data: An HLOCV+ pandas dataframe with a datetime index
        :type data: pandas.DataFrame
        :return: A bactesting simulation
        :rtype: BackTestSession
        """  
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Data must be a pandas dataframe")

        missing = set(['high', 'low', 'open', 'close', 'volume'])-set(data.columns)
        if len(missing) > 0:
            msg = "Missing {0} column(s), dataframe must be HLOCV+".format(list(missing))
            warnings.warn(msg)

        self.data = data

    def start(self, initial_capital, logic):
        """Start BackTestSession.
        :param initial_capital: Starting capital to fund account
        :type initial_capital: float
        :param logic: A function that will be applied to each lookback period of the data
        :type logic: function
        :return: A bactesting simulation
        :rtype: BackTestSession
        """
        self.tracker = []
        self.account = Account(initial_capital)

        self._name = '{}-{}'.format(logic.__name__, str(dt.now().isoformat()))

        # Enter BackTestSession ---------------------------------------------  
        for index, today in self.data.iterrows():
    
            date = today['datetime']
            equity = self.account.total_value(today['close'])

            # Handle stop loss
            for p in self.account.positions:
                if p.type == "long":
                    if p.stop_hit(today['low']):
                        self.account.close_position(p, 1.0, today['low'])
                if p.type == "short":
                    if p.stop_hit(today['high']):
                        self.account.close_position(p, 1.0, today['high'])

            self.account.purge_positions()

            # Update account variables
            self.account.date = date
            self.account.equity.append(equity)

            # Equity tracking
            self.tracker.append({'date': date, 
                                 'benchmark_equity' : today['close'],
                                 'strategy_equity' : equity})

            # Execute trading logic
            lookback = self.data[0:index+1]
            logic(self.account, lookback)

            # Cleanup empty positions
            self.account.purge_positions()     
        # ------------------------------------------------------------

        # For pyfolio
        df = pd.DataFrame(self.tracker)
        df['benchmark_return'] = (df.benchmark_equity-df.benchmark_equity.shift(1))/df.benchmark_equity.shift(1)
        df['strategy_return'] = (df.strategy_equity-df.strategy_equity.shift(1))/df.strategy_equity.shift(1)
        df.index = df['date']
        del df['date']
        return df

    def results(self):   
        """Print results"""           
        self.logger.info("-------------- Results ----------------\n")
        being_price = self.data.iloc[0]['open']
        final_price = self.data.iloc[-1]['close']

        pc = helpers.percent_change(being_price, final_price)
        self.logger.info("Buy and Hold : {0}%".format(round(pc*100, 2)))
        self.logger.info("Net Profit   : {0}".format(round(helpers.profit(self.account.initial_capital, pc), 2)))
        
        pc = helpers.percent_change(self.account.initial_capital, self.account.total_value(final_price))
        self.logger.info("Strategy     : {0}%".format(round(pc*100, 2)))
        self.logger.info("Net Profit   : {0}".format(round(helpers.profit(self.account.initial_capital, pc), 2)))

        longs  = len([t for t in self.account.opened_trades if t.type == 'long'])
        sells  = len([t for t in self.account.closed_trades if t.type == 'long'])
        shorts = len([t for t in self.account.opened_trades if t.type == 'short'])
        covers = len([t for t in self.account.closed_trades if t.type == 'short'])

        self.logger.info("Longs        : {0}".format(longs))
        self.logger.info("Sells        : {0}".format(sells))
        self.logger.info("Shorts       : {0}".format(shorts))
        self.logger.info("Covers       : {0}".format(covers))
        self.logger.info("--------------------")
        self.logger.info("Total Trades : {0}".format(longs + sells + shorts + covers))
        self.logger.info("\n---------------------------------------")
    
    def chart(self, show_trades=False, title="Equity Curve"):
        """Chart results.
        :param show_trades: Show trades on plot
        :type show_trades: bool
        :param title: Plot title
        :type title: str
        """     
        bokeh.plotting.output_file("charts/backtests/{}".format(self._name), title=title)
        p = bokeh.plotting.figure(x_axis_type="datetime", plot_width=1000, plot_height=400, title=title)
        p.grid.grid_line_alpha = 0.3
        p.xaxis.axis_label = 'Date'
        p.yaxis.axis_label = 'Equity'
        shares = self.account.initial_capital/self.data.iloc[0]['open']
        base_equity = [price*shares for price in self.data['open']]      
        p.line(self.data['date'], base_equity, color='#CAD8DE', legend='Buy and Hold')
        p.line(self.data['date'], self.account.equity, color='#49516F', legend='Strategy')
        p.legend.location = "top_left"

        if show_trades:
            for trade in self.account.opened_trades:
                try:
                    x = time.mktime(trade.date.timetuple())*1000
                    y = self.account.equity[np.where(self.data['date'] == trade.date.strftime("%Y-%m-%d"))[0][0]]
                    if trade.type == 'long': p.circle(x, y, size=6, color='green', alpha=0.5)
                    elif trade.type == 'short': p.circle(x, y, size=6, color='red', alpha=0.5)
                except:
                    pass

            for trade in self.account.closed_trades:
                try:
                    x = time.mktime(trade.date.timetuple())*1000
                    y = self.account.equity[np.where(self.data['date'] == trade.date.strftime("%Y-%m-%d"))[0][0]]
                    if trade.type == 'long': p.circle(x, y, size=6, color='blue', alpha=0.5)
                    elif trade.type == 'short': p.circle(x, y, size=6, color='orange', alpha=0.5)
                except:
                    pass
        
        bokeh.plotting.show(p)


class ForwardTestSession():
    """An object representing a Forward Testing Simulation."""

    backdata: pd.DataFrame = None
    data: pd.DataFrame = pd.DataFrame()
    initial_capital: float = 1.0
    pair: dict = None
    tf: dict = None
    tracker: list = None
    logic: Callable = None
    logger: logging.Logger
    _name: str = ''
    __last_analysis: dt = None
    __analysis_throttle: rd = None

    def __init__(self, data, initial_capital, pair, tf, logic,):
        """Initate the ForwardTestSession.
        :param data: An HLOCV+ pandas dataframe with a datetime index
        :type data: pandas.DataFrame
        :param initial_capital: Starting capital to fund account
        :type initial_capital: float
        :param pair: Operating market pair
        :type pair: MarketPair obj
        :param tf: Operating timeframe
        :type tf: str
        :param logic: A function that will be applied to each lookback period of the data
        :type logic: function
        :return: A forwardtesting simulation
        :rtype: ForwardTestSession
        """  
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Data must be a pandas dataframe")

        missing = set(['high', 'low', 'open', 'close', 'volume'])-set(data.columns)
        if len(missing) > 0:
            msg = "Missing {0} column(s), dataframe must be HLOCV+".format(list(missing))
            warnings.warn(msg)

        self.tracker = []
        self.backdata = data.copy()
        self.backdata = self.backdata.set_index('datetime').sort_index(inplace=True, ascending=False)
        self.account = Account(initial_capital=initial_capital, pair=pair, tf=tf)
        self.logic = logic
        self.pair = pair
        self.tf = tf
        self._tts = __name__+'\n\n{} - {}\n :: {}\n\n'.format(
            self.pair, self.tf, logic.__name__,
        )
        self._name = __name__+'. {} - {} :: {} :: {}'.format(
            self.pair, self.tf, logic.__name__, str(dt.now().date()),
        ).replace(' ', '')
        self.logger = setup_logger(name=self._name)
        self.__last_analysis = dt.now()
        self.logger.info('Forwardtesting session started for: {}-{} using {} at {} '.format(
            self.pair, self.tf, self.logic.__name__, self.__last_analysis,
            ),
        )
        # rd stands for relativedelta
        rd_call: Callable = None
        rd_args: dict = None
        rd_call, rd_args = get_delta_callable_for_tf(tf=self.tf)
        self.__analysis_throttle = rd_call(**rd_args)

    def update_dataset(self, dataset):
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

        if current_time > (self.__last_analysis + self.__analysis_throttle):
            self.__last_analysis = dt.now()
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
            )

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

    def _get_longs(self):
        return self.account._get_longs()

    def _get_shorts(self):
        return self.account._get_shorts()
       

    def chart(self, show_trades=False, title="Equity Curve"):
        """Chart results.
        :param show_trades: Show trades on plot
        :type show_trades: bool
        :param title: Plot title
        :type title: str
        """     
        bokeh.plotting.output_file("charts/forwardtests/chart-{0}.html".format(self._name), title=title)
        p = bokeh.plotting.figure(x_axis_type="datetime", plot_width=1000, plot_height=400, title=title)
        p.grid.grid_line_alpha = 0.3

        p.xaxis.axis_label = 'Date'
        p.yaxis.axis_label = 'Equity'

        shares = self.account.initial_capital/self.data.iloc[-1].open
        base_equity = [price*shares for price in self.data.open]

        p.line(self.data.datetime, base_equity, color='#CAD8DE', legend_label='Buy and Hold')
        p.line(self.data.datetime, self.account.equity, color='#49516F', legend_label='Strategy')
        p.legend.location = "top_left"

        if show_trades:
            for trade in self.account.opened_trades:
                try:
                    x = time.mktime(trade.date.timetuple())*1000
                    y = self.account.equity[np.where(self.data.datetime == trade.date)[0][0]]
                    if trade.type == 'long': p.circle(x, y, size=6, color='green', alpha=0.5)
                    elif trade.type == 'short': p.circle(x, y, size=6, color='red', alpha=0.5)
                except:
                    pass

            for trade in self.account.closed_trades:
                try:
                    x = time.mktime(trade.date.timetuple())*1000
                    y = self.account.equity[np.where(self.data.datetime == trade.date)[0][0]]
                    if trade.type == 'long': p.circle(x, y, size=6, color='blue', alpha=0.5)
                    elif trade.type == 'short': p.circle(x, y, size=6, color='orange', alpha=0.5)
                except:
                    pass
        
        bokeh.plotting.show(p)