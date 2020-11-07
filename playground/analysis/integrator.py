__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

from logging import Logger
from playground.abstract import Integrator
from playground.util import setup_logger
from playground.analysis.analysis import Analysis
from playground.analysis.config import AnalysisConfig
from playground.analysis.consumer import AnalysisSocketConsumer
from playground.analysis.worker import AnalysisWorker


class AnalysisIntegrator(Integrator):
    """
    Main analysis class, spawns the the AnalysisWorker and the AnalysisAPI.
    These two classes are responsable for maintaining and providing up to date analysis of input datasets.
    """

    logger: Logger = None

    # Critical objects
    analysis: Analysis = None
    consumer: AnalysisSocketConsumer = None
    worker: AnalysisWorker = None

    def __init__(self, config: AnalysisConfig = None) -> None:
        """Initialize the analysis integrator."""
        super().__init__(
            name="AnalysisIntegrator",
            module_name="analysis",
        )

        self.analysis = Analysis()
        self.consumer = AnalysisSocketConsumer(config=config.consumer_config)
        self.worker = AnalysisWorker(analysis=self.analysis)

    def run(self) -> None:
        """
        Starts the analysis worker and serves analysis API.
        
        """
        
        self.consumer.set_write_queue(self.analysis.get_read_queue())

        self.consumer.connect_and_run()