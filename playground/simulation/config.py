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

logger = setup_logger(name=__name__)


class SimulationConfig:
    """An object representing the SimulationConfig."""

    name: str = None
    module_name: str = None

    api: Dict[str, Any] = None

    socket_ip: str = None
    socket_port: int = None

    def __init__(
        self, name: str = None, module_name: str = None, api: Dict[str, Any] = None,
        socket_ip: str = None, socket_port: int = None,
        ):
        """
        Simply initiate the SimulationConfig.
        """

        if name is None:
            raise Exception("SimulationConfig class needs `name` param to designate itself")
        self.name = name

        if module_name is None:
            raise Exception("SimulationConfig class needs `module_name` param to designate itself")
        self.module_name = module_name


def simulation_config_from_json(json: Dict[str, Any] = None) -> Optional[SimulationConfig]:
    """
    Simply initiate the BridgeConfig.
    """

    if json is None:
        raise Exception("BridgeConfig simulation_config_from_json method needs `json` param")

    simulation_json = json.get('simulation', None)
    if simulation_json is None:
        raise Exception("BridgeConfig simulation_config_from_json method got invalid json")

    api_json = json.get('api', None)
    if api_json is None:
        raise Exception("BridgeConfig simulation_config_from_json method got invalid json")

    logger.info('Attempting to create Simulation data flows from config..')

    return SimulationConfig(
        name=simulation_json.get('name', None),
        module_name=simulation_json.get('module_name', None),
        api=api_json,
        socket_ip=simulation_json.get('websocket_ip', None),
        socket_port=simulation_json.get('websocket_port', None),
    )
