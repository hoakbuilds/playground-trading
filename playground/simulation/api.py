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
from playground.simulation.engine import SimulationEngine
from playground.simulation.settings import (
    SIM_ENGINE_REST_IP, SIM_ENGINE_REST_PORT, SIM_ENGINE_BASE_URI,
)


class SimulationEngineAPI(APIServer):
    """Simulation Engine API Server for REST calls."""
    
    # Warehouse reference to be able to access warehouse info
    # etc
    se = None

    def __init__(self, simulation_engine: SimulationEngine = None) -> None:
        """
        Init the api server, and init the super class RPC
        """
        super().__init__(
            name="SimulationEngineAPI",
            rest_ip=SIM_ENGINE_REST_IP,
            rest_port=SIM_ENGINE_REST_PORT,
        )
        if simulation_engine is None:
            raise Exception("SimulationEngineAPI needs warehouse object to access data")

        self.se = simulation_engine

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
                    name='get_operations',
                    rule=f'{SIM_ENGINE_BASE_URI}/get_operations',
                    handler=self._get_operations,
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

    def _get_operations(self):
        """
        Get pairs with available datasets.
        """
        _operations: list = [str(x) for x in self.se.operations]
        return self.rest_dump({'operations':_operations})
