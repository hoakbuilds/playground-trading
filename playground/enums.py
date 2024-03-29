__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

from enum import Enum

"""
This file is used to define state constants for the systems operation.
"""

class State(Enum):
    """
    Bot application states
    """
    EXIT = -1
    STARTING = 0
    READY = 1
    STOPPED = 2
    RUNNING = 3
    RELOAD_CONF = 4


class RunMode(Enum):
    """
    Bot running mode (backtest, dry-run, ...)
    can be "live", "dry-run", "backtest"
    """
    LIVE = "live"
    PAPER = "paper"
    FORDWARDTEST = "forwardtest"
    BACKTEST = "backtest"
    PLOT = "plot"
    OTHER = "other"


class TradingMode(Enum):
    """
    Specification of different trading modes (spot, margin)
    """
    SPOT = 1
    MARGIN = 2
    FUTURES = 3
    OPTIONS = 4


class QuoteCurrency(Enum):
    """
    Specification of different wallet types
    """
    USD = "USD"
    EUR = "EUR"


class Timeframe(Enum):
    """
    Specification of different timeframes
    """
    MINUTE = "1 m"
    THREE_MINUTES = "3 m"
    FIVE_MINUTES = "5 m"
    FIFTEEN_MINUTES = "15 m"
    THIRTY_MINUTES = "30 m"
    HOURLY = "1 h"
    TWO_HOURS = "2 h"
    FOUR_HOURS = "4 h"
    SIX_HOURS = "6 h"
    TWELVE_HOURS = "12 h"
    DAILY = "1 D"
    THREE_DAYS = "3 D"
    WEEKLY = "1 W"
    BIWEEKLY = "2 W"
    MONTHLY = "1 M"
    TRIMESTRAL = "3 M"
    SEMESTRAL = "6 M"
    YEARLY = "1 Y"


TRADING_MODES = [
    RunMode.LIVE,
    RunMode.PAPER,
]
SIMULATION_MODES = [
    RunMode.BACKTEST,
    RunMode.FORDWARDTEST,
]

LOW_TIMEFRAMES = [
    Timeframe.MINUTE,
    Timeframe.THREE_MINUTES,
    Timeframe.FIVE_MINUTES,
    Timeframe.FIFTEEN_MINUTES,
    Timeframe.THIRTY_MINUTES,
]

MEDIUM_TIMEFRAMES = [
    Timeframe.HOURLY,
    Timeframe.TWO_HOURS,
    Timeframe.FOUR_HOURS,
    Timeframe.SIX_HOURS,
    Timeframe.TWELVE_HOURS,
]

MACRO_TIMEFRAMES = [
    Timeframe.DAILY,
    Timeframe.THREE_DAYS,
    Timeframe.WEEKLY,
    Timeframe.BIWEEKLY,
    Timeframe.MONTHLY,
    Timeframe.TRIMESTRAL,
    Timeframe.SEMESTRAL,
    Timeframe.YEARLY,
]