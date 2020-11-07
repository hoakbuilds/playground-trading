__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

from typing import List
from playground import settings
from playground.messaging.producer import WebSocketProducer
from playground.messaging.producer.config import ProducerConfig


class WarehouseSocketProducer(WebSocketProducer):
    """Warehouse WebSocketProducer."""
    

    def __init__(self, config: ProducerConfig = None) -> None:
        """
        Init the producer.
        """
        if config is None:
            raise Exception('WarehouseSocketProducer needs `config` param')

        super().__init__(
            name="WarehouseSocketProducer",
            config=config,
        )


    