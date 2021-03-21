__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

import pickle
from queue import Queue
from typing import Callable, List

from playground import __version__
from playground.enums import State
from playground.abstract.worker import Worker


class Producer(Worker):
    """
    Base class for a base producer.

    param: name -- the producer's name.
    param: produce_func -- the Callable that can be used to obtain specific behavior from the producer.
    param: work_func -- the Callable that performs the producer's job.
    param: throttle_func -- the Callable that is used to calculate throttle time.
    param: daemon -- when set to true the class will make itself launch the thread it runs on
    """

    # Produce func can be specififed to obtain component specific behavior
    produce_func: Callable = None

    # Queues to process data to/from
    read_queue: Queue = None
    write_queue: Queue = None

    throttle_value: int = 5

    def __init__(
        self, name: str = None, produce_func: Callable = None, throttle_func: Callable = None, daemon: bool = None
        ) -> None:
        """
        Initialize the producer.
        """
        if name is None:
            raise Exception("Producer class needs `name` param to designate itself")

        if throttle_func is None:
            raise Exception("Producer class needs `throttle_func` param to know it's throttle")

        if produce_func is None:
            raise Exception("Producer class needs `produce_func` param to work")
        self.produce_func = produce_func

        super().__init__(
            name=name,
            work_func=produce_func,
            throttle_func=throttle_func,
            daemon=daemon,
        )

    def set_producer_throttle(self, throttle_value: int = None) -> None:
        """
        Used to set the value of the producer throttle in seconds. By default will be 5.
        """
        pass

    def producer_throttle(self) -> int:
        """
        Returns the value set as the producer's throttle value.
        This is used as the `throttle_func` when calling super() for Worker class.
        """
        pass

    def connect_and_produce(self):
        """
        Connects to the socket and produces from it.
        """
        pass

    def Produce(self):
        """
        Produces.
        """
        pass

    def set_read_queue(self, queue: Queue = None):
        """
        Set the read queue
        """
        if queue is None:
            raise Exception("Producer set_read_queue method needs `queue` param to work")
            
        self.read_queue = queue

    def set_write_queue(self, queue: Queue = None):
        """
        Set the write queue
        """
        if queue is None:
            raise Exception("Producer set_write_queue method needs `queue` param to work")
            
        self.write_queue = queue

    def kill_producer(self) -> None:
        """
        Kills the producer.
        """
        self.logger.info('Killing ProducerWorker.')
        self.state = State.STOPPED

        self._await_stopped()

        self.state = State.EXIT

    def set_producing(self) -> None:
        """
        Stops the worker.
        """
        self.logger.info('Worker set to RUNNING.')
        self.state = State.RUNNING

    def set_waiting(self) -> None:
        """
        Stops the worker.
        """
        self.logger.info('Worker set to STOPPED.')
        self.state = State.STOPPED

    def pickle_loads(self, data = None):
        """ Helper function to jsonify object for a webserver """
        if data is None:
            self.logger.info('pickle_loads got `data` None')
            return None
        return pickle.loads(data)

    def pickle_dumps(self, data = None):
        """ Helper function to jsonify object for a webserver """
        if data is None:
            self.logger.info('pickle_dumps got `data` None')
            return None
        return pickle.dumps(data)