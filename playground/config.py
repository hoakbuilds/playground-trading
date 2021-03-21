__title__ = "simulation"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

from typing import Any, Dict, List, Optional

# Local imorts
from playground.bridge.config import BridgeConfig, bridge_config_from_json
from playground.warehouse.config import WarehouseConfig, warehouse_config_from_json
from playground.analysis.config import AnalysisConfig, analysis_config_from_json
from playground.simulation.config import SimulationConfig, simulation_config_from_json


class PlaygroundConfig:
    """An object representing the PlaygroundConfig."""

    # Name of the config
    name: str = None

    # For development and testing purposes
    mode: str = None

    # Modules to be launched
    modules: List[str] = None

    # List of configs of the modules
    warehouse: WarehouseConfig = None
    analysis: AnalysisConfig = None
    bridge: BridgeConfig = None
    simulation: SimulationConfig = None    

    def __init__(self,
        name: str = None, mode: str = None, modules: List[str] = None, warehouse: Dict[str, Any] = None, 
        analysis: Dict[str, Any] = None, bridge: Dict[str, Any] = None, simulation: Dict[str, Any] = None,
        ):
        """
        Simply initiate the PlaygroundConfig.
        """
        if name is None:
            raise Exception("PlaygroundConfig class needs `name` param to designate itself")

        if mode is None:
            raise Exception("PlaygroundConfig class needs `mode` param to work")

        if modules is None:
            raise Exception("PlaygroundConfig class needs `modules` param to work")

        if bridge is not None:
            self.bridge = bridge_config_from_json(json=bridge)

        if warehouse is not None:
            self.warehouse = warehouse_config_from_json(json=warehouse)

        if analysis is not None:
            self.analysis = analysis_config_from_json(json=analysis)

        if simulation is not None:
            self.simulation = simulation_config_from_json(json=simulation)


def playground_config_from_json(self, json: Dict[str, Any] = None) -> Optional[PlaygroundConfig]:
    """
    Simply initiate the PlaygroundConfig.
    """

    if json is None:
        raise Exception("PlaygroundConfig playground_config_from_json method needs `json` param")

    return PlaygroundConfig(
        name=json.get('name', None),
        mode=json.get('mode', None),
        warehouse=json.get('warehouse', None),
        analysis=json.get('analysis', None),
        bridge=json.get('bridge', None),
        simulation=json.get('simulation', None),
    )
