__title__ = "simulation"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

# Global imports
from typing import Any, Dict, List, Optional

# Local imports
from playground.util import setup_logger
from playground.messaging.consumer import ConsumerConfig
from playground.messaging.producer import ProducerConfig
from playground.messaging.flow import Flow, flows_from_json
from playground.messaging.stream import Stream, stream_from_json

logger = setup_logger(name=__name__)


class AnalysisConfig:
    """An object representing the BridgeConfig."""

    name: str = None
    module_name: str = None

    flows: List[Flow] = None
    
    api: Dict[str, Any] = None

    consumer_config: ConsumerConfig = None
    producer_config: ProducerConfig = None

    def __init__(
        self, name: str = None, mode: str = None, module_name: str = None, flows: List[Flow] = None, api: Dict[str, Any] = None,
        socket_ip: str = None, socket_port: int = None,
        ):
        """
        Simply initiate the BridgeConfig.
        """

        if name is None:
            raise Exception("BridgeConfig class needs `name` param to designate itself")
        self.name = name
        
        if mode is None:
            raise Exception("BridgeConfig class needs `mode` param to designate itself")
        self.mode = mode

        if module_name is None:
            raise Exception("BridgeConfig class needs `module_name` param to designate itself")
        self.module_name = module_name

        if flows is None:
            raise Exception("BridgeConfig class needs `flows` param to distribute messages based on flows")
        self.flows = flows

        if api is None:
            raise Exception("BridgeConfig class needs `api` param to launch the API server")
        self.api = api

        if socket_ip is None:
            raise Exception("BridgeConfig class needs `socket_ip` param to launch the socket")
        self.socket_ip = socket_ip
        
        if socket_port is None:
            raise Exception("BridgeConfig class needs `socket_port` param to launch the socket")
        self.socket_port = socket_port

def analysis_config_from_json(json: Dict[str, Any] = None) -> Optional[AnalysisConfig]:
    """
    Simply initiate the BridgeConfig.
    """

    if json is None:
        raise Exception("BridgeConfig analysis_config_from_json method needs `json` param")

    analysis_json = json.get('analysis', None)
    if analysis_json is None:
        raise Exception("BridgeConfig analysis_config_from_json method got invalid json")

    api_json = json.get('api', None)
    if api_json is None:
        raise Exception("BridgeConfig analysis_config_from_json method got invalid json")

    logger.info('Attempting to create data flows from config..')

    return AnalysisConfig(
        name=analysis_json.get('name', None),
        module_name=analysis_json.get('module_name', None),
        mode=json.get('mode', None),
        api=api_json,
        socket_ip=analysis_json.get('websocket_ip', None),
        socket_port=analysis_json.get('websocket_port', None),
    )
