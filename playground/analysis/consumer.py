__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

from typing import List
from playground import settings
from playground.messaging.consumer import WebSocketConsumer
from playground.messaging.consumer.config import ConsumerConfig


class AnalysisSocketConsumer(WebSocketConsumer):
    """Analysis WebSocketConsumer."""
    

    def __init__(self, config: ConsumerConfig = None) -> None:
        """
        Init the consumer.
        """
        if config is None:
            raise Exception('WarehouseSocketProducer needs `config` param')

        super().__init__(
            name="AnalysisInternalSocket",
            config=config,
        )


    