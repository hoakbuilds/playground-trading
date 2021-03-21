__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

import pickle
import time
from queue import Queue
from playground.abstract.websocket_client import WebSocketClient
from playground.messaging import Message, Stream, Payload
from playground.messaging.consumer.config import ConsumerConfig
from playground.messaging.consumer.consumer import Consumer


class WebSocketConsumer(WebSocketClient):
    """
    Socket consumer class.
    """

    stream: Stream = None
    socket_ip: str = None
    socket_port: int = None
    
    uri: str = None

    # Queues to process data to
    read_queue: Queue = None
    write_queue: Queue = None

    def __init__(self, config: ConsumerConfig = None):
        """Initialize the queue consumer."""

        if config is None:
            raise Exception("SocketConsumer needs `config` param")

        self.socket_ip = config.socket_ip
        self.socket_port = config.socket_port
        self.uri = 'ws://{}:{}/ws/'

        super().__init__(
            name=config.name,
            url=self.uri,
            on_connected_func=self.send_initial_message,
            on_message_func=self.consume,
        )

    def set_stream(self, stream: Stream = None) -> None:
        """
        Used to set the consumer's stream which is None by default.
        """
        if stream is None:
            raise Exception("Consumer set_stream method needs `stream` param")
        
        self.stream = stream
    
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

    def consume(self, message):
        """
        Consumes.
        """

        data = self.pickle_loads(message)
        self.logger.info('Received: {}'.format(data))

        self.write_queue.put(data)


    def send_initial_message(self) -> None:
        """
        Gets the initial message to send to the server.
        """
        if self.ws is None:
            raise Exception('Cannot craft send initial message because connection is/was closed')
        yield self.ws.write_message(message=self.pickle_dumps(self._initial_message()))

    def _initial_message(self) -> Message:
        """
        Gets the initial message to send to the server.
        """
        if self.stream is None:
            raise Exception('Cannot craft initial message due to Producer having `stream` as None')
        return Message(
            stream=self.stream,
            payload=Payload(raw={
                'internal': {
                    'consumer': 'true',
                }
            })
        )

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