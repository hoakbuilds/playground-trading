__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"


from playground.abstract.integrator import Integrator
from playground.enums import State
from playground.bridge.config import BridgeConfig
from playground.bridge.bridge import Bridge
from playground.bridge.api import BridgeAPI


class BridgeIntegrator(Integrator):
    """
    Bridge integrator class, spawns the bridge and it's API to expose metrics.
    """

    bridge: Bridge = None
    api: BridgeAPI = None

    def __init__(self, config: BridgeConfig = None) -> None:
        """Initialize the bridge's integrator."""
        super().__init__(
            name=config.name,
            module_name=config.module_name,
        )
        
        self.bridge = Bridge(config=config)

        self.api = BridgeAPI(bridge=self.bridge)
        

    def run(self) -> None:

        self.bridge.Start()

        self.api.Start()
