__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

from logging import Logger
from playground.enums import State
from playground.util import setup_logger
from playground.config import PlaygroundConfig
from playground.analysis import AnalysisIntegrator
from playground.warehouse import WarehouseIntegrator
from playground.simulation import SimulationIntegrator
from playground.abstract.integrator import Integrator


class PlaygroundIntegrator(Integrator):
    """
    Main playground class, spawns the Warehouse and the Analyser.
    These two classes are responsable for maintaining and providing up to date
    analytics on datasets.
    """

    warehouse: WarehouseIntegrator = None
    analysis: AnalysisIntegrator = None
    simulation: SimulationIntegrator = None

    state: State = State.STOPPED

    def __init__(self, config: PlaygroundConfig = None) -> None:
        """Initialize the playground's integrator."""

        if config is None:
            super().__init__(
                name="PlaygroundIntegrator",
                module_name="playground",
            )
        else:
            super().__init__(
                name="PlaygroundIntegrator",
                module_name="playground",
            )

        self.warehouse = WarehouseIntegrator(config=config.warehouse)

        self.analysis = AnalysisIntegrator()

        self.simulation = SimulationIntegrator()

    def run(self) -> None:

        self.warehouse.run()

        self.analysis.run()

        while not self.warehouse.worker.state == State.EXIT:
            pass