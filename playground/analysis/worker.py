
__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

import datetime
import time
from queue import Empty
from dateutil.relativedelta import relativedelta as rd
from datetime import datetime as dt
from playground import __version__, settings
from playground.abstract import Worker
from playground.util_ops import get_delta_callable_for_tf
from playground.analysis.analysis import Analysis
from playground.messaging.message import Message


class AnalysisWorker(Worker):
    """Basic class for a main worker."""

    analysis: Analysis = None

    __startup_throttle: int = 5

    def __init__(self, analysis: Analysis = None):
        """
        Init all variables and objects the worker needs.
        """
        super().__init__(
            name="AnalysisWorker",
            work_func=self.work,
            throttle_func=self._throttle_func,
        )

        if analysis is None:
            raise Exception("AnalysisWorker class needs a analysis to control")

        self.analysis = analysis

    def work(self):
        """
        Perform the Analyser's job.
        """
        message: Message = None
        try:
            message = self.analysis.read_queue.get(block=False)
        except Empty:
            self.logger.info('Nothing to analyse, sleeping.')
            return 

        dict = message.payload.raw

        self.logger.info('Got {} datasets to analyse..'.format(len(dict)))

        for item in dict:
            self.analysis.prepare_dataset(item=item)
            self.analysis.analyse(df=self.analysis.dataset)
            self.analysis.save_dataset(item=item)
            
    def _throttle_func(self) -> int:
        """
        Returns an integer representing in seconds how long the warehouse will sleep.
        """
        
        return 1

    def _await_warehouse(self):
        """
        Awaits until the analysis has gone from READY to ANALYSED.
        """

        while not self.analysis.is_ready():
            time.sleep(self.__startup_throttle)
            self.logger.info('Waiting for the analysis to be ready..')


