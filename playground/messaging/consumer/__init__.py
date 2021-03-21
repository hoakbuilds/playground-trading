__name__ = "messaging"
__title__ = "playground"
__author__ = "github.com/murlokito"
__description__ = __title__ + " Not your typical trading bot."
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "GPL"
__email__ = "murlux@protonmail.com"
__status__ = "Prototype"

__version__ = "0.0.1"

from .config import ConsumerConfig, consumer_config_from_json
from .websocket_consumer import WebSocketConsumer
from .consumer import Consumer


__all__ = [
    ConsumerConfig, Consumer, WebSocketConsumer, consumer_config_from_json,
]