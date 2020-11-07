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

from .config import ProducerConfig, producer_config_from_json
from .websocket_producer import WebSocketProducer
from .producer import Producer


__all__ = [
    ProducerConfig, Producer, WebSocketProducer, producer_config_from_json
]