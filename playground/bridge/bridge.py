__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

# Global imports
from datetime import time
from logging import Logger, exception
from sys import exc_info
from typing import List

# Local imports
from playground.util import setup_logger
from playground.abstract.websocket import WebSocketServer
from playground.messaging.flow import Flow
from playground.bridge import __version__
from playground.bridge.metrics import BridgeMetrics
from playground.bridge.config import BridgeConfig


class Bridge(WebSocketServer):
    """
    Main bridge class, spawns an instance for every flow in the config.
    """

    logger: Logger = None
    name: str = None
    flows: List[Flow] = None
    metrics: BridgeMetrics = None

    def __init__(self, config: BridgeConfig = None) -> None:
        """Initialize the bridge."""
        
        self.name = '{}.{}-{}.{}'.format(__name__, config.name, config.mode, __version__)
        self.logger = setup_logger(name=self.name)
        self.logger.info('Initializing %s component.', self.name)

        if config is None:
            raise Exception('Bridge needs param `config` to setup')
        
        super().__init__(
            name=self.name,
            socket_ip=config.socket_ip,
            socket_port=config.socket_port,
            open_func= lambda: self.client_connected,
            on_close_func= lambda: self.on_client_disconnected,
            on_message_func= lambda: self.on_message_received,
            check_origin_func= lambda: self.check_origin_headers,
            url_func=lambda: Bridge.bridge_urls(),
        )

        self.flows = config.flows
        self.metrics = BridgeMetrics()

    def StartBridge(self) -> None:
        """
        Start the bridge.
        """
        self.Start()
        try:
            while True:
                self.run()
        except KeyboardInterrupt as exc:
            self.terminate()
        except Exception as exc:
            self.terminate(exc=exc)

    def terminate(self, exc: Exception = None) -> None:
        if exc is not None:
            self.logger.info('Caught exception.', exc_info=exc)
        self.logger.info('Terminating gracefully...')
        self.logger.info('See you next time.')

    @classmethod
    def bridge_urls(cls):
        return [
            (r'/ws', cls, {}),  # Route/Handler/kwargs
        ]

    def run(self) -> None:
        """
        Runs the bridge.
        """

        self.logger.info('Running...')

        time.sleep(5)
        
    def client_connected(self, channel):
        """
        Client opens a websocket.
        """
        self.logger.info('Client connected on channel: %s ', channel)

    def on_message_received(self, message):
        """
        Message received.
        """
        self.logger.info('Message received: %s ', message)
    
    def on_client_disconnected(self):
        """
        Client closes the connection.
        """
        self.logger.info('Client disconnected')
    
    
    def check_origin_headers(self, origin):
        """
        Override the origin check if needed
        """
        return True