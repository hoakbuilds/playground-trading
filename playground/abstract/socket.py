__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

import threading
from typing import Callable, List
from flask import Flask, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
from playground.util import setup_logger

BASE_URI = '/api/v1'


class SocketEvent:
    """Basic class to specify socket events so the base SocketServer can plug them."""
    name: str = None
    handler: Callable = None
    namespace: str = None

    def __init__(self, name: str = None, namespace: str = None, handler: Callable = None) -> None:
        """Initialize the Endpoint."""
        if name is None:
            raise Exception("Endpoint class needs `name` param to be the endpoint's name")
        self.name = name

        if namespace is None:
            raise Exception("Endpoint class needs `namespace` param to be the WS URL namespace")
        self.namespace = namespace

        if handler is None:
            raise Exception("Endpoint class needs `handler` param to be the endpoint's function handler")
        self.handler = handler


class SocketServer:
    """Basic server for websockets."""
    
    name: str = None
    app: Flask = None
    socket: SocketIO = None

    _socket_base_url: str = None
    _socket_ip: str = '0.0.0.0'
    _socket_port: int = 7666

    def __init__(self, name: str = None, socket_ip: str = None, socket_port: int = None) -> None:
        """
        Init the api server, and init the super class RPC
        """
        if name is None:
            raise Exception("SocketServer needs distinguishable name for logging purposes")
        
        self.name = '{}.{}'.format(__name__, name)
        self.logger = setup_logger(name=self.name)
        self.logger.info('Initializing %s component.', self.name)

        self.app = Flask(__name__)
        CORS(self.app)

        self.app.config['SECRET_KEY'] = "s!"#$123%!%&!&e!"123424#34534$%!5345%&!&c345!"#234$%!1342334224%&!&et!242!"#$%342!%&!&"
        self.socket = SocketIO(self.app)

        if socket_ip is None:
            self.logger.info("SocketServer got no `socket_ip` defaulting to {}".format(self._socket_ip))
        else:
            self._socket_ip = socket_ip

        if socket_port is None:
            self.logger.info("SocketServer got no `socket_port` defaulting to {}".format(self._socket_port))
        else:
            self._socket_port = socket_port

        self._socket_base_url = '{}:{}'.format(self._socket_ip, self._socket_port)

        self.logger.info("Will serve Socket at %s", self._socket_base_url)

    def Start(self) -> None:
        """
        Spawns the thread that will run the `run` method of SocketServer.
        The `run` method creates the HTTP Server and maps it to the Flask app..
        """
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()

    def cleanup(self) -> None:
        self.logger.info("Stopping API Server")
        self.srv.shutdown()

    def run(self):
        """
        Method that runs flask-socketio app in its own thread forever.
        """

        self.logger.info(f"Starting Socket Server at {self._socket_base_url}")

        try:
            self.socket.run(self.app, host=self._socket_ip, port=self._socket_port, log_output=True)
        except Exception:
            self.logger.exception("Socket Server failed to start.")

    def json_dump(self, return_value):
        """ Helper function to jsonify object for a webserver """
        return jsonify(return_value)

    def json_error(self, error_msg):
        return jsonify({"error": error_msg}), 502

    def register_base_socket_events(self):
        """
        Registers flask app URLs that are calls to functonality in rpc.rpc.
        First two arguments passed are /URL and 'Label'
        Label can be used as a shortcut when refactoring
        :return:
        """
        # Error handling
        self.socket.on_error_default(self._base_error_handler)
        # Testing
        self.socket.on_event("message", self._base_message_handler, namespace="/")
        self.socket.on_event("json", self._base_json_handler, namespace="/")
        self.socket.on_event("connect", self._base_connection_handler, namespace="/")
        self.socket.on_event("disconnect", self._base_disconnection_handler, namespace="/")

    def register_socket_events(self, events: List[SocketEvent]):
        """
        Registers flask-socketio events that are handled by the socket server.
        :param events: is a list of events of type `SocketEvent` from the same module.
        :return:
        """
        # Register the passed events
        for event in events:
            self.socket.on_event(
                message=event.name,
                handler=event.handler,
                namespace=event.namespace,
            )

    def _base_error_handler(self, e):
        """
        Base error handler.
        """
        print("An error has occurred: " + str(e))

    def _base_message_handler(self, message):
        """
        Base message handler.
        """
        print("received message: " + message)
    
    def _base_json_handler(self, message):
        """
        Base json handler.
        """
        print("received json: " + message)
    
    def _base_connection_handler(self, message):
        """
        Base connection handler.
        """
        print("received message: " + message)
    
    def _base_disconnection_handler(self, message):
        """
        Base disconnection handler.
        """
        print("received message: " + message)
