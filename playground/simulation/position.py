__title__ = "simulation"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

import copy
import math
from datetime import datetime as dt

class OpenedTrade():
    """An object representing an open trade."""

    def __init__(self, type, date, pos):
        """Initate the trade.
        :param type: Type of trade
        :type type: float
        :param date: When the trade was opened
        :type date: datetime
        :return: A trade
        :rtype: trade
        """  
        self.type = type
        self.opened_date = date
        self.pos = pos

    def __str__(self):
        return "{0}\n{1}".format(self.type, self.date)


class ClosedTrade(OpenedTrade):
    """An object representing a closed trade."""

    def __init__(self, type, opened_date, closed_date, shares, entry, exit, pos):
        """Initate the trade.
        :param type: Type of trade
        :type type: float
        :param date: When the trade was closed
        :type date: datetime
        :param shares: Number of shares
        :type shares: float
        :param entry: Entry price
        :type entry: float
        :param exit: Exit price
        :type exit: float
        :return: A trade
        :rtype: trade
        """  
        super().__init__(type, opened_date, pos)
        self.closed_date = closed_date
        self.shares      = float(shares)
        self.entry       = float(entry)
        self.exit        = float(exit)
    
    def __str__(self):
        return "{0}\n{1}\n{2}\n{3}\n{4}".format(self.type,
                                                self.opened_date,
                                                self.closed_date,
                                                self.shares,
                                                self.entry,
                                                self.exit,)


class Position:
    """A parent object representing a position."""

    def __init__(self, no, pair, tf, entry_price, shares, exit_price, stop_loss):
        """Open the position.
        :param no: A unique position id number
        :type no: float
        :param pair: Market pair operating
        :type pair: MarketPair
        :param tf: Operating timeframe
        :type tf: str
        :param entry_price: Entry price at which shares are longed/shorted
        :type entry_price: float
        :param shares: Number of shares to long/short
        :type shares: float
        :param exit_price: Price at which to take profit
        :type exit_price: float
        :param stop_loss: Price at which to cut losses
        :type stop_loss: float
        :return: A position
        :rtype: position
        """    
        self.no            = no
        self.type          = "None"
        self.pair          = pair
        self.tf            = tf
        self.date          = dt.now()
        self.entry_price   = float(entry_price)
        self.shares        = float(shares)
        self.exit_price    = float(exit_price)
        self.stop_loss     = float(stop_loss)
    
    def __str__(self):
        return "{0}\n{1}\n{2}\n{3}\n{4}\n{5}\n{6}\n{7}\n{8}\n{9}".format(self.type,
                                                self.pair,
                                                self.tf,
                                                self.date,
                                                self.shares,
                                                self.entry_price,
                                                self.exit_price,
                                                self.stop_loss,
                                                self.pos)
    def show(self):
        print("No.     {0}".format(self.no))
        print("Pair:   {0}".format(self.pair))
        print("Type:   {0}".format(self.type))
        print("Entry:  {0}".format(self.entry_price))
        print("Shares: {0}".format(self.shares))
        print("Exit:   {0}".format(self.exit_price))
        print("Stop:   {0}\n".format(self.stop_loss))
    
    def _dict(self):
        return {
            'id': str(self.no),
            'pair': str(self.pair),
            'tf': str(self.tf),
            'type': str(self.type),
            'entry_price': str(self.entry_price),
            'amount': str(self.shares),
            'exit_price': str(self.exit_price),
            'stop_loss': str(self.stop_loss)
        }


class LongPosition(Position):
    """A child object representing a long position."""

    def __init__(self, no, pair, tf, entry_price, shares, exit_price=math.inf, stop_loss=0):
        """Open the position.
        :param no: A unique position id number
        :type no: float
        :param pair: Market pair operating
        :type pair: MarketPair
        :param tf: Operating timeframe
        :type tf: str
        :param entry_price: Entry price at which shares are longed
        :type entry_price: float
        :param shares: Number of shares to long
        :type shares: float
        :param exit_price: Price at which to take profit
        :type exit_price: float
        :param stop_loss: Price at which to cut losses
        :type stop_loss: float
        :return: A long position
        :rtype: LongPosition
        """

        if exit_price is False: exit_price = math.inf
        if stop_loss is False: stop_loss = 0
        super().__init__(no, pair, tf, entry_price, shares, exit_price, stop_loss)
        self.type = 'long'

    def close(self, percent, current_price):
        """Close the position.
        :param percent: Percent of position size to close
        :type percent: float
        :param current_price: Closing price
        :type current_price: float
        :return: Amount of capital gained from closing position
        :rtype: float
        """
        shares = self.shares
        self.shares *= 1.0 - percent
        return shares * percent * current_price

    def stop_hit(self, current_price):
        if current_price <= self.stop_loss:
            return(True)


class ShortPosition(Position):
    """A child object representing a short position."""

    def __init__(self, no,  pair, tf, entry_price, shares, exit_price=0, stop_loss=math.inf):
        """Open the position.
        :param no: A unique position id number
        :type no: int
        :param pair: Market pair operating
        :type pair: MarketPair
        :param tf: Operating timeframe
        :type tf: str
        :param entry_price: Entry price at which shares are shorted
        :type entry_price: float
        :param shares: Number of shares to short
        :type shares: float
        :param exit_price: Price at which to take profit
        :type exit_price: float
        :param stop_loss: Price at which to cut losses
        :type stop_loss: float
        :return: A short position
        :rtype: ShortPosition
        """       
        if exit_price is False: exit_price = 0
        if stop_loss is False: stop_loss = math.inf
        super().__init__(no, pair, tf, entry_price, shares, exit_price, stop_loss)
        self.type = 'short'

    def close(self, percent, current_price):
        """Close the position.
        :param percent: Percent of position size to close
        :type percent: float
        :param current_price: Closing price
        :type current_price: float
        :return: Amount of capital gained from closing position
        :rtype: float
        """
        entry = self.shares * percent * self.entry_price
        exit = self.shares * percent * current_price
        self.shares *= 1.0 - percent
        if entry - exit + entry <= 0: 
            return 0
        else: 
            return entry - exit + entry

    def stop_hit(self, current_price):
        if current_price >= self.stop_loss:
            return(True)
