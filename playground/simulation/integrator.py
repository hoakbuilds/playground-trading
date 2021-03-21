__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

from logging import Logger
from typing import Dict
from playground.util import setup_logger


class SimulationIntegrator:
    """
    Main simulation class, spawns the various engines.
    These two classes are responsable for maintaining and providing up to date datasets.
    """

    logger: Logger = None

    # Critical objects


    def __init__(self, config: Dict = None) -> None:
        """Initialize the playground's simulation integrator."""

        self.logger = setup_logger(name='{}.{}'.format(__title__, __name__))
        self.logger.info("Creating the SimulationIntegrator...")


    def run(self) -> None:
        """
        Starts the engines.
        """
        self.logger.info("Running the SimulationIntegrator...")