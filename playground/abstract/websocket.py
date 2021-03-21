__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

import threading
import time
import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.websocket
import pickle
from queue import Empty, Queue
from typing import Callable, Set
from playground.util import setup_logger
from playground.messaging import Stream

BASE_URI = '/api/v1'


class WSConnection:
    """
    Basic class that represents a ws client connected.
    """
    ws: tornado.websocket.WebSocketHandler = None
    stream: Stream = None
    last: time.time = None

    def __init__(self, ws, stream, last) -> None:
        """Init the connection."""
        self.ws = ws
        self.last = last
        self.stream = stream

class WebSocketServer(tornado.websocket.WebSocketHandler):
    """Basic server for socket."""
    
    name: str = None

    wst: threading.Thread = None
    app: tornado.web.Application = None
    http_server: tornado.httpserver.HTTPServer = None
    ioloop: tornado.ioloop.IOLoop = None

    _socket_base_url: str = None
    _socket_ip: str = '0.0.0.0'
    _socket_port: int = 7666

    connections: Set[WSConnection] = None
    read_queue: Queue = None
    write_queue: Queue = None

    open_func: Callable = None
    on_close_func: Callable = None
    on_message_func: Callable = None
    check_origin_func: Callable = None
    url_func: Callable = None

    def __init__(self, 
        open_func: Callable = None, on_close_func: Callable = None, on_message_func: Callable = None, 
        check_origin_func: Callable = None, url_func: Callable = None, name: str = None, stream: Stream = None, 
        socket_ip: str = None, socket_port: int = None,
        ) -> None:
        """
        Init the socket server and it's internals. Server provided by Tornado.
        """
        if name is None:
            raise Exception("WebSocketServer needs distinguishable name for logging purposes")
        
        self.name = '{}.{}'.format(__name__, name)
        self.logger = setup_logger(name=self.name)
        self.logger.info('Initializing %s component.', self.name)

        if stream is not None:
            self.stream = stream

        if open_func is None:
            self.logger.error("WebSocketServer got no `open_func` defaulting to internal {}".format(self.__open_func))
        else:
            self.open_func = open_func

        if on_close_func is None:
            self.logger.error("WebSocketServer got no `on_close_func` defaulting to internal {}".format(self.__on_close_func))
        else:
            self.on_close_func = on_close_func

        if on_message_func is None:
            self.logger.error("WebSocketServer got no `on_message_func` defaulting to internal {}".format(self.__on_message_func))
        else:
            self.on_message_func = on_message_func

        if check_origin_func is None:
            self.logger.error("WebSocketServer got no `check_origin_func` defaulting to internal {}".format(self.__check_origin_func))
        else:
            self.check_origin_func = check_origin_func

        if url_func is None:
            self.logger.error("WebSocketServer got no `url_func` defaulting to internal {}".format(self.__url_func))
        else:
            self.url_func = url_func
        
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

        self.read_queue = Queue()
        self.write_queue = Queue()
        self.connections = set()

    def Start(self) -> None:
        """
        Spawns the thread that will run the `run` method of WebSocketServer.
        The `run` method creates the HTTP Server and maps it to the Flask app..
        """
        self.logger.info(f"Attempting to start.")
        self.serve()

    def cleanup(self) -> None:
        self.logger.info("Stopping WebSocketServer")
        self.http_server.stop()
        self.wst.join()
        self.logger.info("WebSocketServer stopped")

    def serve(self) -> None:
        """
        Serve the websocket.
        """
        self.logger.info(f"Setting up tornado application...")
        # Create tornado application and supply URL routes
        self.app = tornado.web.Application(self.urls())
        
        # Setup HTTP Server
        self.logger.info(f"Starting WebSocket Server at {self._socket_base_url}")
        self.http_server = tornado.httpserver.HTTPServer(self.app)
        self.http_server.listen(port=self._socket_port, address=self._socket_ip)
        
        # Start IO/Event loop
        self.logger.info(f"Tornado loop started.")
        self.ioloop = tornado.ioloop.IOLoop.instance().start()

    def register_client(self, client):
        """
        Adds the client to the set of connections.
        """
        self.connections.add(client)

    def unregister_client(self, client):
        """
        Removes the client fron the set of connections.
        """
        self.connections.remove(client)

    @classmethod
    def urls(cls):
        return [
            (r'/ws/', cls, {}),  # Route/Handler/kwargs
        ]

    def open(self, channel):
        """
        Client opens a websocket.
        """
        return self.open_func(self, channel=channel)
    
    def on_message(self, message):
        """
        Message received.
        """
        return self.on_message_func(self, message=message)
    
    def on_close(self):
        """
        Client closes the connection.
        """
        return self.on_close_func(self)
    
    def check_origin(self, origin):
        """
        Override the origin check if needed
        """
        return self.check_origin_func(self, origin=origin)

    def __open_func(self, channel):
        """
        Client opens a websocket.
        """
        self.logger.info("Client connected. Channel: %s", channel)
    
    def __on_message_func(self, message):
        """
        Message received.
        """
        self.logger.info("Message received. Channel: %s", message)
    
    def __on_close_func(self):
        """
        Client closes the connection.
        """
        self.logger.info("Client exited..")
    
    def __check_origin_func(self, origin):
        """
        Override the origin check if needed
        """
        return True

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
