__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

import time
import threading
from logging import Logger
from typing import Callable
from playground import __version__
from playground.enums import State
from playground.util import setup_logger


class Worker:
    """
    Base class for a main worker.

    param: name -- the worker's name.

    param: work_func -- the Callable that performs the worker's job.
    param: throttle_func -- the Callable that is used to calculate throttle time.
    """

    state: State = State.STOPPED
    name: str = None
    logger: Logger = None
    
    _daemon: bool = False
    _throttlefunc: Callable = None
    _workfunc: Callable = None

    def __init__(self, name: str = None, work_func: Callable = None, throttle_func: Callable = None, daemon: bool = None) -> None:
        """
        Initialize the worker.
        """
        self.state = State.STARTING

        if name is None:
            raise Exception("Worker class needs `name` param")

        self.name = '{}.{}'.format(__name__, name)
        self.logger = setup_logger(name=self.name)
        self.logger.info('Initializing %s component.', self.name)

        if throttle_func is None:
            self.logger.info('Worker class got no `throttle_func` param, worker will not sleep between work cycles.')
        else:
            self._throttlefunc = throttle_func

        if work_func is None:
            raise Exception("Worker class needs `work_func` param to work")
        
        self._workfunc = work_func

        self.logger.info('Worker is ready.')
        self.state = State.READY

        if daemon != None:
            self._daemon = daemon
        
        if self._daemon == True:
            self.logger.info('Worker is starting as daemon.')
            self.Start()

    def Start(self) -> None:
        """
        Spawns the thread that will run the `StartWorking` method of the Worker.
        The `StartWorking` method changes the worker's state to RUNNING and attempts
        to keep performing it's job while the state does not change to `State.EXIT`.
        """
        thread = threading.Thread(target=self.startWorking, daemon=True)
        thread.start()

    def startWorking(self) -> None:
        """
        Starts worker's work lifecycle.
        """

        if self.state == State.READY:
            self.logger.info('Worker is ready, starting.')
            self.state = State.RUNNING

            # While it's not time to exit, we attempt to run the worker
            while not self.state == State.EXIT:
                self.run()

            self.logger.info('Worker is exiting, bye!')
        else:
            self.logger.info('Worker is not ready.')
    
    def run(self) -> None:
        """
        Perform the worker's job until it's time to stop.
        """

        if self.state == State.RUNNING:
            self.logger.info('Worker is running.')

            while not self.state == State.STOPPED:
                self._work()

                throttle: int = self._get_throttle()

                if throttle != 0:
                    self.logger.info('Worker is sleeping for %ss.', throttle)

                    time.sleep(throttle)

            self.logger.info('Worker is stopping.')
            self.state = State.STOPPED
        else:
            self.logger.info('Worker is stopped.')

    def kill(self) -> None:
        """
        Kills the worker.
        """
        self.logger.info('Killing worker.')
        self.state = State.STOPPED

        self._await_stopped()

        self.state = State.EXIT

    def set_running(self) -> None:
        """
        Stops the worker.
        """
        self.logger.info('Worker set to RUNNING.')
        self.state = State.RUNNING

    def set_stopped(self) -> None:
        """
        Stops the worker.
        """
        self.logger.info('Worker set to STOPPED.')
        self.state = State.STOPPED

    def _await_stopped(self) -> None:
        """
        Waits until having stopped.
        """
        while self.state != State.STOPPED:
            time.sleep(1)
    
    def _await_ready(self) -> None:
        """
        Waits until having stopped.
        """
        while self.state != State.READY:
            time.sleep(1)

    def _work(self) -> None:
        """
        Self-explanatory.
        Uses a Callable set during init that when called performs the worker's job.
        """
        self.logger.info('Worker is working.')
        
        # Call `work_func` Callable
        self._workfunc()

    def _get_throttle(self) -> int:
        """
        Fetch throttle time.
        """
        if self._throttlefunc is None:
            return 0

        return self._throttlefunc()
