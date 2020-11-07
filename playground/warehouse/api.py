__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

import pandas as pd
from typing import List
from flask import request
from playground import settings
from playground.abstract import APIServer, Endpoint
from playground.warehouse.persistence import Warehouse

WAREHOUSE_BASE_URI = '/api/v1/warehouse'
WAREHOUSE_REST_IP = '0.0.0.0'
WAREHOUSE_REST_PORT = 1300


class WarehouseAPI(APIServer):
    """Warehouse API Server for REST calls."""
    
    # Warehouse reference to be able to access warehouse info
    # etc
    warehouse = None

    def __init__(self, warehouse: Warehouse = None) -> None:
        """
        Init the api server, and init the super class RPC
        """
        super().__init__(
            name="WarehouseAPI",
            rest_ip=WAREHOUSE_REST_IP,
            rest_port=WAREHOUSE_REST_PORT,
        )
        if warehouse is None:
            raise Exception("WarehouseAPI needs warehouse object to access data")

        self.warehouse = warehouse

        self.logger.info("Setting up endpoints..")

        # Register application handling
        self.register_warehouse_endpoints()
    
    def Endpoints(self) -> List[Endpoint]:
        """
        Function that returns the List of Endpoint type objects that this API exposes.
        """
        return list(
            [
                Endpoint(
                    name='warehouse_information',
                    rule=f'{WAREHOUSE_BASE_URI}/warehouse_information',
                    handler=self._wh_info,
                    methods=['GET'],
                ),
                Endpoint(
                    name='get_dataset',
                    rule=f'{WAREHOUSE_BASE_URI}/get_dataset/<pair>/<timeframe>/',
                    handler=self._get_dataset,
                    methods=['GET'],
                ),
                Endpoint(
                    name='get_dataset_limit',
                    rule=f'{WAREHOUSE_BASE_URI}/get_dataset/<pair>/<timeframe>/<limit>/',
                    handler=self._get_dataset_limit,
                    methods=['GET'],
                ),
            ]
        )

    def register_warehouse_endpoints(self):
        """
        Registers flask app URLs that are calls to functonality in rpc.rpc.
        First two arguments passed are /URL and 'Label'
        Label can be used as a shortcut when refactoring
        :return:
        """
        self.register_rest_rpc_urls(self.Endpoints())

    def page_not_found(self, error):
        """
        Return "404 not found", 404.
        """
        return self.rest_dump({
            'status': 'error',
            'reason': f"There's no API call for {request.base_url}.",
            'code': 404
        }), 404

    def _wh_info(self):
        """
        Get pairs with available datasets.
        """
        _pairs: list = [str(x) for x in self.warehouse.market_pairs]
        _timeframes: list = [x for x in settings.WAREHOUSE_TIMEFRAMES]
        return self.rest_dump({'pairs':_pairs, 'timeframes': _timeframes})
    
    def _get_dataset(self, pair=None, timeframe=None):
        """
        Get pairs with available datasets.
        """
        tf: str = timeframe.replace('_', ' ')

        if self.warehouse.is_updated():

            dataset = self.warehouse.get_dataset(pair=pair, timeframe=tf, analysed=True)

            return self.rest_dump({'data': dataset.to_csv() })

        return self.rest_dump({'data': {
            'message': 'Warehouse is not updated.'
        }})

    def _get_dataset_limit(self, pair=None, timeframe=None, limit=None):
        """
        Get pairs with available datasets. Optional limit parameter for smaller dataset.
        """
        tf: str = timeframe.replace('_', ' ')

        dataset: pd.DataFrame = None

        if self.warehouse.is_updated():

            if int(limit) == 1:
                dataset = self.warehouse.get_latest_candle(pair=pair, timeframe=tf, analysed=True, closed=True)
            else:
                dataset = self.warehouse.get_dataset(pair=pair, timeframe=tf, analysed=True, limit=int(limit))

            return self.rest_dump({'data': dataset.to_csv() })
        
        return self.rest_dump({'data': {
            'message': 'Warehouse is not updated.'
        }})