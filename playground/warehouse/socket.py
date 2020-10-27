__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

import pandas as pd
from typing import List
from playground import settings
from playground.abstract import SocketServer, SocketEvent
from playground.warehouse.persistence import Warehouse

WAREHOUSE_SOCKET_IP = '0.0.0.0'
WAREHOUSE_SOCKET_PORT = 6677


class WarehouseSocket(SocketServer):
    """Warehouse Socket Server to push events."""
    
    # Warehouse reference to be able to access warehouse info
    # etc
    warehouse = None

    def __init__(self, warehouse: Warehouse = None) -> None:
        """
        Init the api server, and init the super class RPC
        """
        super().__init__(
            name="WarehouseWebSocket",
            socket_ip=WAREHOUSE_SOCKET_IP,
            socket_port=WAREHOUSE_SOCKET_PORT,
        )
        if warehouse is None:
            raise Exception("WarehouseWebSocket needs warehouse object to access data")

        self.warehouse = warehouse

        self.logger.info("Setting up events..")

        # Register application handling
        self.register_warehouse_events()
    
    def Events(self) -> List[SocketEvent]:
        """
        Function that returns the List of Event type objects that this socket pushes.
        """
        return list(
            [
                SocketEvent(
                    name='warehouse_information',
                    handler=self._wh_info,
                    namespace='/'
                ),
                SocketEvent(
                    name='get_dataset',
                    handler=self._get_dataset,
                    namespace='/'
                ),
                SocketEvent(
                    name='get_dataset_limit',
                    handler=self._get_dataset_limit,
                    namespace='/'
                ),
            ]
        )

    def register_warehouse_events(self):
        """
        Registers flask app URLs that are calls to functonality in rpc.rpc.
        First two arguments passed are /URL and 'Label'
        Label can be used as a shortcut when refactoring
        :return:
        """
        self.register_socket_events(self.Events())

    def _wh_info(self):
        """
        Get pairs with available datasets.
        """
        _pairs: list = [str(x) for x in self.warehouse.market_pairs]
        _timeframes: list = [x for x in settings.WAREHOUSE_TIMEFRAMES]
        return self.json_dump({'pairs':_pairs, 'timeframes': _timeframes})
    
    def _get_dataset(self, pair=None, timeframe=None):
        """
        Get pairs with available datasets.
        """
        tf: str = timeframe.replace('_', ' ')

        dataset = self.warehouse.get_dataset(pair=pair, timeframe=tf, analysed=True).to_json()

        return self.json_dump({'data': dataset})

    def _get_dataset_limit(self, pair=None, timeframe=None, limit=None):
        """
        Get pairs with available datasets. Optional limit parameter for smaller dataset.
        """
        tf: str = timeframe.replace('_', ' ')

        dataset: pd.DataFrame = None
        
        if int(limit) == 1:
            dataset = self.warehouse.get_latest_candle(pair=pair, timeframe=tf, analysed=True, closed=True).to_json()
        else:
            dataset = self.warehouse.get_dataset(pair=pair, timeframe=tf, analysed=True, limit=int(limit)).to_json()

        return self.json_dump({'data': dataset})