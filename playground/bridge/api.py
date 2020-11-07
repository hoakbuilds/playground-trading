__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

# Global imports
from typing import Any, Dict, List
from flask import request

# Local imports
from playground.abstract import APIServer, Endpoint
from playground.bridge.bridge import Bridge


BRIDGE_BASE_URI = '/api/v1/bridge'
BRIDGE_REST_IP = '0.0.0.0'
BRIDGE_REST_PORT = 4567


class BridgeAPI(APIServer):
    """
    Main bridge class, spawns an instance for every flow in the config.
    """

    bridge: Bridge = None
    api_name: str = None
    rest_ip: str = None
    rest_port: int = None

    def __init__(self, bridge: Bridge = None, config: Dict[str, Any] = None) -> None:
        """Initialize the bridge."""
        if config is None:
            super().__init__(
                name="BridgeAPI",
                rest_ip=BRIDGE_REST_IP,
                rest_port=BRIDGE_REST_PORT,
            )
        else:
            self.api_name = config.get('name', None)
            if self.rest_ip is None:
                raise Exception("BridgeAPI got invalid config `name`")

            self.rest_ip = config.get('rest_ip', None)
            if self.rest_ip is None:
                raise Exception("BridgeAPI got invalid config `rest_ip`")

            self.rest_port = config.get('rest_port', None)
            if self.rest_port is None:
                raise Exception("BridgeAPI got invalid config `rest_port`")
            super().__init__(
                name=self.api_name,
                rest_ip=self.rest_ip,
                rest_port=self.rest_port,
            )

        if bridge is None:
            raise Exception("BridgeAPI needs bridge object to access metrics")

        self.bridge = bridge

        self.logger.info("Setting up endpoints..")

        # Register application handling
        self.register_bridge_endpoints()

    def Endpoints(self) -> List[Endpoint]:
        """
        Function that returns the List of Endpoint type objects that this API exposes.
        """
        return list(
            [
                Endpoint(
                    name='get_bridge_information',
                    rule=f'{BRIDGE_BASE_URI}/get_bridge_information',
                    handler=self._bridge_info,
                    methods=['GET'],
                ),
                Endpoint(
                    name='get_metrics',
                    rule=f'{BRIDGE_BASE_URI}/get_metrics',
                    handler=self._get_metrics,
                    methods=['GET'],
                ),
            ]
        )

    def register_bridge_endpoints(self):
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

    def _bridge_info(self):
        """
        Get bridge operating information.
        """
        _flows: list = [str(x) for x in self.bridge.flows]
        return self.rest_dump({
            'data': {
                'flows':_flows,
            }
        })
    
    def _get_metrics(self):
        """
        Get metrics related to bridge operation.
        """

        metrics = self.bridge.metrics.get_metrics()

        return self.rest_dump({'data': metrics })

