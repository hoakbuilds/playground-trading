__name__ = "commands"
__title__ = "playground"
__author__ = "github.com/murlokito"
__description__ = __title__ + " Not your typical trading bot."
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "GPL"
__email__ = "murlux@protonmail.com"
__status__ = "Prototype"

__version__ = "0.0.1"


from .operation import Operation
from .pair import MarketPair, Currency

__all__ = [
    Operation, MarketPair, Currency,
]