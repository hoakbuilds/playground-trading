__title__ = "simulation"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

import copy
from datetime import datetime as dt
from playground.simulation.position import (
    OpenedTrade, ClosedTrade, LongPosition, ShortPosition, 
)
from playground.pair import MarketPair
from playground.util_ops import get_delta_callable_for_tf


class Account():
    """An object representing an exchange Account."""

    no: int
    initial_capital: float
    buying_power: float
    positions: list
    opened_trades: list
    closed_trades: list
    equity: list
    date: dt
    pair: MarketPair
    tf: str

    def __init__(self, initial_capital, pair, tf):
        """Initiate an Account.
        :param initial_capital: Starting capital to fund Account
        :type initial_capital: float
        :return: An Account object
        :rtype: Account
        """ 

        self.initial_capital = float(initial_capital)
        self.buying_power    = float(initial_capital)
        self.no              = 0
        self.date            = None
        self.equity          = []
        self.positions       = []
        self.opened_trades   = []
        self.closed_trades   = []
        self.pair            = pair
        self.tf              = tf

    def get_last_by_pair(self, pair: MarketPair):
        """Get last position by pair...
        :param pair: Market pair operating
        :type pair: MarketPair
        """

        for position in self.positions:
            if str(position.pair) == str(pair):
                return position

        return None

    def check_delta_since(self, delta: int):
        """Get last position by pair...
        :param pair: Market pair operating
        :type pair: MarketPair
        """

        # rd stands for relativedelta
        rd_call: Callable = None
        rd_args: dict = None
        rd_call, rd_args = get_delta_callable_for_tf(tf=self.tf)
        relativedelta = rd_call(**rd_args)
        current_time = dt.now()

        tmplist = copy.deepcopy(self.positions)
        tmplist = tmplist[::-1]
        if tmplist is not None:
            if len(tmplist) != 0:
                for position in tmplist:
                    if (((str(position.pair) == str(self.pair)) and (str(position.tf) == str(self.tf))) and
                        (current_time > (position.date + (delta*relativedelta)))):
                            return True

        return False

    def enter_position(self, type, entry_capital, entry_price, exit_price=False, stop_loss=False, commission=0):
        """Open a position.
        :param type: Type of position e.g. ("long, short")
        :type type: float
        :param entry_capital: Amount of capital invested into position
        :type entry_capital: float
        :param entry_price: Entry price at which shares are longed/shorted
        :type entry_price: float
        :param exit_price: Price at which to take profit
        :type exit_price: float
        :param stop_loss: Price at which to cut losses
        :type stop_loss: float
        :param commision: Percent commission subtracted from position size
        :type commision: float
        """ 

        entry_capital = float(entry_capital)
        
        if entry_capital < 0: 
            raise ValueError("Error: Entry capital must be positive")          
        elif entry_price < 0: 
            raise ValueError("Error: Entry price cannot be negative.")
        elif self.buying_power < entry_capital: 
            raise ValueError("Error: Not enough buying power to enter position")          
        else: 
            self.buying_power -= entry_capital
            if commission > 0:
                shares = entry_capital / (entry_price + commission * entry_price)
            else:
                shares = entry_capital / entry_price

            pos = None
            if type == 'long':
                pos = LongPosition(self.no,
                    self.pair,
                    self.tf,
                    entry_price,
                    shares,
                    exit_price,
                    stop_loss)
                self.positions.append(pos)
            elif type == 'short':
                pos = ShortPosition(self.no,
                    self.pair,
                    self.tf,
                    entry_price,
                    shares,
                    exit_price,
                    stop_loss)
                self.positions.append(pos)
            else: 
                raise TypeError("Error: Invalid position type.")

            self.opened_trades.append(OpenedTrade(type, self.date, pos))
            self.no += 1

    def close_position(self, position, percent, current_price, commission=0):
        """Close a position.
        :param position: Position id number
        :type position: int
        :param percent: Percent of position size to close
        :type percent: float
        :param current_price: Price at which position is closed
        :type current_price: float
        :param commision: Percent commission subtracted from capital returned
        :type commision: float
        """ 

        if percent > 1 or percent < 0: 
            raise ValueError("Error: Percent must range between 0-1.")
        elif current_price < 0:
            raise ValueError("Error: Current price cannot be negative.")                
        else: 
            self.closed_trades.append(ClosedTrade(position.type, 
                                                   position.date,
                                                   self.date,
                                                   position.shares * percent, 
                                                   position.entry_price, 
                                                   current_price,
                                                   position))
            
            if commission > 0:
                closing_position_price = position.close(percent, current_price)
                self.buying_power += (closing_position_price - closing_position_price * commission)
            else:
                self.buying_power += position.close(percent, current_price)

    def purge_positions(self):
        """Delete all empty positions.""" 
        self.positions = [p for p in self.positions if p.shares > 0]        

    def show_positions(self):
        """Show all Account positions.""" 
        for p in self.positions: p.show()

    def _get_positions(self):
        """Return all positions as a dict."""

        longs  = [t.pos._dict() for t in self.opened_trades if t.type == 'long']
        sells  = [t.pos._dict() for t in self.closed_trades if t.type == 'long']
        shorts = [t.pos._dict() for t in self.opened_trades if t.type == 'short']
        covers = [t.pos._dict() for t in self.closed_trades if t.type == 'short']
        return {
            'longs': longs,
            'sells': sells,
            'shorts': shorts,
            'covers': covers,
        }

    def _get_longs(self):
        """Return all longs as a dict."""

        longs  = [t.pos._dict() for t in self.opened_trades if t.type == 'long']
        sells  = [t.pos._dict() for t in self.closed_trades if t.type == 'long'] 
        return {
            'longs': longs,
            'sells': sells, 
        }

    def _get_shorts(self):
        """Return all shorts as a dict."""
 
        shorts = [t.pos._dict() for t in self.opened_trades if t.type == 'short']
        covers = [t.pos._dict() for t in self.closed_trades if t.type == 'short']
        return {
            'shorts': shorts,
            'covers': covers,
        }

    def total_value(self, current_price):
        """Calculate total value of Account
        :param current_price: Price used to value open position sizes
        :type current_price: float
        :return: Total value of acocunt
        :rtype: float
        """ 

        temporary = copy.deepcopy(self)
        for position in temporary.positions:
            temporary.close_position(position, 1.0, current_price)
        return temporary.buying_power