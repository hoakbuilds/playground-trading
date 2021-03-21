__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

import asyncio
import pickle
from queue import Queue
from typing import Callable

from playground import __version__
from playground.enums import State
from playground.abstract.worker import Worker


class Consumer(Worker):
    """
    Base class for a base consumer.

    param: name -- the consumer's name.
    param: consume_func -- the Callable that can be used to obtain specific behavior from the consumer.
    param: work_func -- the Callable that performs the consumer's job.
    param: throttle_func -- the Callable that is used to calculate throttle time.
    param: daemon -- when set to true the class will make itself launch the thread it runs on
    """

    # Consume func can be specififed to obtain component specific behavior
    consume_func: Callable = None

    # Queues to process data to
    read_queue: Queue = None
    write_queue: Queue = None

    throttle_value: int = 5

    event_loop: asyncio.AbstractEventLoop = None

    def __init__(
        self, name: str = None, consume_func: Callable = None, throttle_func: Callable = None, daemon: bool = False
        ) -> None:
        """
        Initialize the consumer.
        """
        if name is None:
            raise Exception("Consumer class needs `name` param to designate itself")

        if throttle_func is None:
            raise Exception("Consumer class needs `throttle_func` param to know it's throttle")

        if consume_func is None:
            raise Exception("Consumer class needs `consume_func` param to work")
        self.consume_func = consume_func

        super().__init__(
            name=name,
            work_func=consume_func,
            throttle_func=throttle_func,
            daemon=daemon,
        )

        self.event_loop = asyncio.get_event_loop()

    def set_consumer_throttle(self, throttle_value: int = None) -> None:
        """
        Used to set the value of the consumer throttle in seconds. By default will be 5.
        """
        pass

    def consumer_throttle(self) -> int:
        """
        Returns the value set as the consumer's throttle value.
        This is used as the `throttle_func` when calling super() for Worker class.
        """
        pass

    def connect_and_consume(self) -> None:
        """
        Connects to the socket and consumes from it.
        """
        pass

    def Consume(self) -> Callable:
        """
        Consumes.
        """
        pass
    
    def set_read_queue(self, queue: Queue = None) -> None:
        """
        Set the read queue
        """
        if queue is None:
            raise Exception("Consumer set_read_queue method needs `queue` param to work")
            
        self.read_queue = queue

    def set_write_queue(self, queue: Queue = None):
        """
        Set the write queue
        """
        if queue is None:
            raise Exception("Producer set_write_queue method needs `queue` param to work")
            
        self.write_queue = queue

    def kill_consumer(self) -> None:
        """
        Kills the worker.
        """
        self.logger.info('Killing ConsumerWorker.')
        self.state = State.STOPPED

        self._await_stopped()

        self.state = State.EXIT

    def set_consuming(self) -> None:
        """
        Stops the worker.
        """
        self.logger.info('ConsumerWorker set to RUNNING.')
        self.state = State.RUNNING

    def set_waiting(self) -> None:
        """
        Stops the worker.
        """
        self.logger.info('ConsumerWorker set to STOPPED.')
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