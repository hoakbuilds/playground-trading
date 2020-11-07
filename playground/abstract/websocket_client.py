__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"


from logging import Logger
from typing import Callable
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado import gen
from tornado.websocket import WebSocketClientConnection, websocket_connect

from playground.util import setup_logger


class WebSocketClient(object):
    """
    Base websocket client.
    """

    logger: Logger = None
    name: str = None

    url: str = None
    timeout: int = None
    ioloop: IOLoop = None
    ws: WebSocketClientConnection = None

    on_message_func: Callable = None
    on_connected_func: Callable = None
    get_data_func: Callable = None

    def __init__(self, 
        on_message_func: Callable = None, on_connected_func: Callable = None, get_data_func: Callable = None,
        name: str = None, url: str = None, timeout: int = None
        ) -> None:

        self.name = '{}.{}'.format(__name__, name)
        self.logger = setup_logger(name=self.name)
        self.logger.info('Initializing %s component.', self.name)
        self.url = url
        self.on_connected_func = on_connected_func
        self.on_message_func = on_message_func
        self.get_data_func = get_data_func
        PeriodicCallback(self.keep_alive, 20000).start()
        self.timeout = timeout
        self.ioloop = IOLoop.instance()
        self.ws = None

    def connect_and_run(self):
        """
        Connects and waits for messages from the client.
        """
        self.connect()
        self.ioloop.start()

    @gen.coroutine
    def connect(self):
        self.logger.info('Attempting to connect to {}...'.format(self.url))
        try:
            self.ws = yield websocket_connect(self.url)
        except Exception as ex:
            self.logger.exception('Could not connect...', exc_info=ex)
        else:
            self.logger.info('Connected.')
            self.on_connected_func()
            self.run()

    @gen.coroutine
    def run(self):
        while True:
            if self.get_data_func is not None:
                self.logger.info('Producing..')
                self.produce()
            
            if self.on_message_func is not None:
                self.logger.info('Consuming..')
                self.consume()

    @gen.coroutine
    def consume(self):
        while True:
            if self.ws is None:
                self.logger.info('Connection closed.')
                self.ws = None
                break
            msg = yield self.ws.read_message()
            if msg is None:
                self.logger.info('Connection closed.')
                self.ws = None
                break
            else:
                self.on_message_func(message=msg)
    
    @gen.coroutine
    def produce(self):
        while True:
            if self.ws is None:
                self.ws = None
                break
            msg = self.get_data_func()
            if msg is None:
                continue

            self.logger.info('Sending message with length: {}'.format(len(msg)))
            yield self.ws.write_message(message=msg)

    def keep_alive(self):
        if self.ws is None:
            self.connect()
        else:
            self.ws.write_message("keep alive")

    def stop(self):
        """
        Closes the connection.
        """
        self.logger.info('Closing connection.')
        if self.ws is not None:
            self.ws.close()

