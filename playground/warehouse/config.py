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
from playground.messaging.producer import ProducerConfig, producer_config_from_json

logger = setup_logger(name=__name__)


class WarehouseConfig:
    """An object representing the WarehouseConfig."""

    name: str = None
    module_name: str = None

    api: Dict[str, Any] = None

    socket_ip: str = None
    socket_port: int = None

    producer_config: ProducerConfig = None

    def __init__(
        self, name: str = None, module_name: str = None, api: Dict[str, Any] = None,
        socket_ip: str = None, socket_port: int = None, producer_config: Dict[str, Any] = None,
        ):
        """
        Simply initiate the WarehouseConfig.
        """

        if name is None:
            raise Exception("WarehouseConfig class needs `name` param to designate itself")
        self.name = name

        if module_name is None:
            raise Exception("WarehouseConfig class needs `module_name` param to designate itself")
        self.module_name = module_name

        if producer_config is not None:
            self.producer_config = producer_config_from_json(json=producer_config)


def warehouse_config_from_json(json: Dict[str, Any] = None) -> Optional[WarehouseConfig]:
    """
    Simply initiate the BridgeConfig.
    """

    if json is None:
        raise Exception("BridgeConfig warehouse_config_from_json method needs `json` param")

    warehouse_json = json.get('warehouse', None)
    if warehouse_json is None:
        raise Exception("BridgeConfig warehouse_config_from_json method got invalid json")

    api_json = json.get('api', None)
    if api_json is None:
        raise Exception("BridgeConfig warehouse_config_from_json method got invalid json")

    logger.info('Attempting to create warehouse data flows from config..')

    return WarehouseConfig(
        name=warehouse_json.get('name', None),
        module_name=warehouse_json.get('module_name', None),
        api=api_json,
        socket_ip=warehouse_json.get('websocket_ip', None),
        socket_port=warehouse_json.get('websocket_port', None),
        producer_config=json.get('producer_config', None),
    )
