__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

from logging import Logger
from playground.enums import State
from playground.util import setup_logger
from playground.warehouse import WarehouseIntegrator
from playground.simulation import SimulationIntegrator


class PlaygroundIntegrator:
    """
    Main playground class, spawns the Warehouse and the Analyser.
    These two classes are responsable for maintaining and providing up to date
    analytics on datasets.
    """

    logger: Logger = None
    warehouse: WarehouseIntegrator = None
    simulation: SimulationIntegrator = None

    state: State = State.STOPPED

    def __init__(self) -> None:
        """Initialize the playground's integrator."""

        self.logger = setup_logger(name='{}.{}'.format(__title__, __name__))
        self.logger.info("Creating the PlaygroundIntegrator...")

        self.warehouse = WarehouseIntegrator()

        self.simulation = SimulationIntegrator()

    def run(self) -> None:

        self.warehouse.run()

        while not self.state == State.EXIT:
            pass