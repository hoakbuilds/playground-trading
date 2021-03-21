__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

import threading
from typing import Callable, List
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.serving import make_server
from playground.util import setup_logger

BASE_URI = '/api/v1'

VALID_HTTP_METHODS = ['GET', 'POST', 'PUT']


class Endpoint:
    """Basic class to specify REST API endpoints so the base APIServer can plug them."""
    rule: str = None
    name: str = None
    handler: Callable = None
    methods: List[str] = None

    def __init__(self, name: str = None, rule: str = None, handler: Callable = None, methods: List[str] = None) -> None:
        """Initialize the Endpoint."""
        if name is None:
            raise Exception("Endpoint class needs `name` param to be the endpoint's name")
        self.name = name

        if rule is None:
            raise Exception("Endpoint class needs `rule` param to be the endpoint's URL rule")
        self.rule = rule

        if handler is None:
            raise Exception("Endpoint class needs `handler` param to be the endpoint's function handler")
        self.handler = handler

        if methods is None:
            raise Exception("Endpoint class needs `methods` param to be the list of possible HTTP methods for the endpoint")

        method_validation: List = None
        method_validation = [
            Exception("Endpoint {} for rule {} HTTP methods are invalid. Methods received: {} -- Valid: {}".format(name, rule, methods, VALID_HTTP_METHODS))
            if method not in VALID_HTTP_METHODS else None for method in methods
        ]

        if method_validation is not None:
            for exception in method_validation:
                if exception is not None:
                    raise exception

        self.methods = methods


class APIServer:
    """Basic api server for REST calls."""
    
    name: str = None

    _rest_base_url: str = None
    _rest_ip: str = '0.0.0.0'
    _rest_port: int = 6666

    def __init__(self, name: str = None, rest_ip: str = None, rest_port: int = None) -> None:
        """
        Init the api server, and init the super class RPC
        """
        if name is None:
            raise Exception("APIServer needs distinguishable name for logging purposes")
        
        self.name = '{}.{}'.format(__name__, name)
        self.logger = setup_logger(name=self.name)
        self.logger.info('Initializing %s component.', self.name)

        self.app = Flask(__name__)
        CORS(self.app)

        self.app.config['SECRET_KEY'] = "s!"#$123%!%&!&e!"123424#34534$%!5345%&!&c345!"#234$%!1342334224%&!&et!242!"#$%342!%&!&"

        if rest_ip is None:
            self.logger.info('APIServer got no `rest_ip` defaulting to {}'.format(self._rest_ip))
        else:
            self._rest_ip = rest_ip

        if rest_port is None:
            self.logger.info('APIServer got no `rest_port` defaulting to {}'.format(self._rest_port))
        else:
            self._rest_port = rest_port

        self._rest_base_url = '{}:{}'.format(self._rest_ip, self._rest_port)

        self.logger.info("Will serve API at %s", self._rest_base_url)

        # Register base application handling
        self.register_base_rest_rpc_urls()

    def Start(self) -> None:
        """
        Spawns the thread that will run the `run` method of APIServer.
        The `run` method creates the HTTP Server and maps it to the Flask app..
        """
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()

    def cleanup(self) -> None:
        self.logger.info("Stopping API Server")
        self.srv.shutdown()

    def run(self):
        """
        Method that runs flask app in its own thread forever.
        """

        self.logger.info(f'Starting HTTP Server at {self._rest_ip}:{self._rest_port}')

        try:
            self.srv = make_server(self._rest_ip, self._rest_port, self.app)
            self.srv.serve_forever()
        except KeyboardInterrupt:
            self.logger.exception("HTTP Server terminating.")
            self.cleanup()
        except Exception:
            self.logger.exception("HTTP Server failed to start.")
            self.cleanup()

    def rest_dump(self, return_value):
        """ Helper function to jsonify object for a webserver """
        return jsonify(return_value)

    def rest_error(self, error_msg):
        return jsonify({"error": error_msg}), 502

    def register_base_rest_rpc_urls(self):
        """
        Registers flask app URLs that are calls to functonality in rpc.rpc.
        First two arguments passed are /URL and 'Label'
        Label can be used as a shortcut when refactoring
        :return:
        """
        self.app.register_error_handler(404, self.page_not_found)
        # Testing
        self.app.add_url_rule(f'{BASE_URI}/ping', 'ping',
                              view_func=self._ping, methods=['GET'])
        # Actions to control the bot
        self.app.add_url_rule(f'{BASE_URI}/start', 'start',
                              view_func=self._start, methods=['POST'])
        self.app.add_url_rule(f'{BASE_URI}/stop', 'stop', view_func=self._stop, methods=['POST'])

    def register_rest_rpc_urls(self, endpoints: List[Endpoint]):
        """
        Registers flask app URLs that are calls to functionality in rpc.rpc.
        :param endpoints: is a list of endpoints of type Endpoint from the same module.
        :return:
        """
        # Register the passed endpoints
        for endpoint in endpoints:
            self.app.add_url_rule(
                rule=endpoint.rule,
                endpoint=endpoint.name,
                view_func=endpoint.handler,
                methods=endpoint.methods,
            )

    def page_not_found(self, error):
        """
        Return "404 not found", 404.
        """
        return self.rest_dump({
            'status': 'error',
            'reason': f"There's no API call for {request.base_url}.",
            'code': 404
        }), 404

    def _start(self):
        """
        Handler for /start.
        """
        return self.rest_dump()

    def _stop(self):
        """
        Handler for /stop.
        """
        return self.rest_dump()

    def _ping(self):
        """
        Simple poing version.
        """
        return self.rest_dump({"status": "pong"})
