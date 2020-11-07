__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

import threading
import time 
import asyncio
import websockets
import pickle
from queue import Empty, Queue
from typing import Callable, Set
from concurrent.futures import ThreadPoolExecutor
from playground.util import setup_logger
from playground.messaging import Stream
BASE_URI = '/api/v1'


class WebSocketServer:
    """Basic server for socket."""
    
    name: str = None
    stream: Stream = None
    socket: websockets.server = None

    _socket_base_url: str = None
    _socket_ip: str = '0.0.0.0'
    _socket_port: int = 7666

    connections: set = None
    read_queue: Queue = None
    write_queue: Queue = None

    event_loop: asyncio.AbstractEventLoop = None
    connection_handler: ThreadPoolExecutor = None

    def __init__(self, name: str = None, stream: Stream = None, socket_ip: str = None, socket_port: int = None) -> None:
        """
        Init the api server, and init the super class RPC
        """
        if name is None:
            raise Exception("WebSocketServer needs distinguishable name for logging purposes")
        
        self.name = '{}.{}'.format(__name__, name)
        self.logger = setup_logger(name=self.name)
        self.logger.info('Initializing %s component.', self.name)

        if stream is None:
            raise Exception("WebSocketServer needs distinguishable stream for operating purposes")
        self.stream = stream
        
        if socket_ip is None:
            self.logger.info("WebSocketServer got no `socket_ip` defaulting to {}".format(self._socket_ip))
        else:
            self._socket_ip = socket_ip

        if socket_port is None:
            self.logger.info("WebSocketServer got no `socket_port` defaulting to {}".format(self._socket_port))
        else:
            self._socket_port = socket_port

        self._socket_base_url = '{}:{}'.format(self._socket_ip, self._socket_port)

        self.logger.info("Will serve WebSocket at %s", self._socket_base_url)

        self.connections = []
        self.read_queue = Queue()
        self.write_queue = Queue()
        self.connections = set()
        self.connection_handler = ThreadPoolExecutor(4)

    def Start(self) -> None:
        """
        Spawns the thread that will run the `run` method of WebSocketServer.
        The `run` method creates the HTTP Server and maps it to the Flask app..
        """
        
        self.logger.info(f"Starting WebSocket Server at {self._socket_base_url}")
        thread = threading.Thread(target=self.serve, daemon=True)
        thread.start()


    def cleanup(self) -> None:
        self.logger.info("Stopping WebSocketServer")
        self.socket.close()

    def serve(self) -> None:
        """
        Serve the websocket.
        """
        self.event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.event_loop)
        start_server = websockets.serve(self.handle_connection, self._socket_ip, self._socket_port)
        self.event_loop.run_until_complete(start_server)
        self.event_loop.run_forever()

    async def handle_connection(self, websocket, path):
        """
        Method that runs socket.
        """
        self.logger.info("Client connected.")
        message = await self.handle_message(websocket=websocket)
        if message is None:
            websocket.close()

        self.logger.info("Received: {}".format(message))
        ok_internal = self.handle_connection_message(message=message, client=websocket)
        if ok_internal is None:
            websocket.close()

        await self.register_client(websocket)

        try:
            producer = ok_internal.get('producer', None)
            consumer = ok_internal.get('consumer', None)

            if producer is None and consumer is not None:
                self.logger.info('Consumer connected. Handling..')
                await self.event_loop.run_in_executor(self.connection_handler, self.handle_consumer_connection(client=websocket))
            if consumer is None and producer is not None:
                self.logger.info('Producer connected. Handling..')
                await self.event_loop.run_in_executor(self.connection_handler, self.handle_producer_connection(client=websocket))

        except Exception as exc:
            self.logger.exception("Socket Server failed to start.", exc_info=exc)
        finally:
            self.logger.info("Client disconnected.")
            await self.unregister_client(websocket)
    
    async def handle_message(self, websocket):
        """
        Handles a received message.
        """
        data = await websocket.recv()

        if len(data) > 0:
            message = self.pickle_loads(data=data)
            self.logger.info('Received: {}'.format(data))

            return message
        
        return None

    async def register_client(self, client):
        """
        Adds the client to the set of connections.
        """
        self.connections.add(client)

    async def unregister_client(self, client):
        """
        Removes the client fron the set of connections.
        """
        self.connections.remove(client)

    def handle_connection_message(self, message = None, client = None,) -> None:
        """
        Handles the initial message received.
        """
        # This is an error
        if message is None or client is None:
            return None

        # This is an actual haywire message
        if message.payload is None and message.stream is None:
            return None

        if self.stream.name != message.stream.name:
            return None

        self.logger.info('Streams - Server {} - Client {} - OK'.format(self.stream.name, message.stream.name))
        
        raw = message.payload.raw
        if raw is None:
            return None

        internal = raw.get('internal', None)

        if internal is None:
            return None

        return internal

    def handle_consumer_connection(self, client) -> None:
        """
        """
        self.logger.info('Consuming...')
        while True:
            try:
                data = self.read_queue.get(block=False)
                if data is not None:
                    self.logger.info('Sending: {}'.format(data))
                    client.send(self.pickle_dumps(data))

            except Empty:
                pass
            except Exception as exc:
                self.logger.info('EXCEPT CONSUMER: {}', exc_info=exc)
                pass

    def handle_producer_connection(self, client) -> None:
        """
        """
        self.logger.info('Producing...')
        while True:
            try:
                message = self.handle_message(websocket=client)
                if message is None:
                    continue

                self.write_queue.put(message)
            except Exception as exc:
                self.logger.info('EXCEPT PRODUCER: {}', exc_info=exc)
                pass
        
    def pickle_loads(self, data = None):
        """ Helper function to jsonify object for a webserver """
        if data is None:
            self.logger.info('pickle_load got `data` None')
            return None
        return pickle.loads(data)

    def pickle_dumps(self, data = None):
        """ Helper function to jsonify object for a webserver """
        if data is None:
            self.logger.info('pickle_load got `data` None')
            return None
        return pickle.dumps(data)

    def pickle_error(self, error_msg):
        return pickle.dumps({"error": error_msg})
