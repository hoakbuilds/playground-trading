__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

import logging
import threading
from datetime import date, datetime
from typing import Dict, Callable, Any

from flask import Flask, jsonify, request
from flask.json import JSONEncoder
from werkzeug.serving import make_server
from playground.util import setup_logger
BASE_URI = '/api/v1'


class ApiServer:
    """Basic api server for REST calls."""

    def __init__(self, worker) -> None:
        """
        Init the api server, and init the super class RPC
        """
        self.logger = setup_logger(name=__name__)
        self.app = Flask(__name__)

        # Register application handling
        self.register_rest_rpc_urls()

        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()

    def cleanup(self) -> None:
        self.logger.info("Stopping API Server")
        self.srv.shutdown()

    def run(self):
        """
        Method that runs flask app in its own thread forever.
        """
        rest_ip = '127.0.0.1'
        rest_port = 3000

        self.logger.info(f'Starting HTTP Server at {rest_ip}:{rest_port}')

        # Run the Server
        self.logger.info('Starting Local Rest Server.')
        try:
            self.srv = make_server(rest_ip, rest_port, self.app)
            self.srv.serve_forever()
        except Exception:
            logger.exception("Api server failed to start.")
        self.logger.info('Local Rest Server started.')

    def send_msg(self, msg: Dict[str, str]) -> None:
        """
        We don't push to endpoints at the moment.
        Take a look at webhooks for that functionality.
        """
        pass

    def rest_dump(self, return_value):
        """ Helper function to jsonify object for a webserver """
        return jsonify(return_value)

    def rest_error(self, error_msg):
        return jsonify({"error": error_msg}), 502

    def register_rest_rpc_urls(self):
        """
        Registers flask app URLs that are calls to functonality in rpc.rpc.
        First two arguments passed are /URL and 'Label'
        Label can be used as a shortcut when refactoring
        :return:
        """
        self.app.register_error_handler(404, self.page_not_found)
        # testing
        self.app.add_url_rule(f'{BASE_URI}/ping', 'ping',
                              view_func=self._ping, methods=['GET'])
        # Actions to control the bot
        self.app.add_url_rule(f'{BASE_URI}/start', 'start',
                              view_func=self._start, methods=['POST'])
        self.app.add_url_rule(f'{BASE_URI}/stop', 'stop', view_func=self._stop, methods=['POST'])

        # Combined actions and infos

        # TODO: Implement the following
        # help (?)

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
        Starts TradeThread in bot if stopped.
        """
        msg = self._rpc_start()
        return self.rest_dump(msg)

    def _stop(self):
        """
        Handler for /stop.
        Stops TradeThread in bot if running
        """
        msg = self._rpc_stop()
        return self.rest_dump(msg)

    def _stopbuy(self):
        """
        Handler for /stopbuy.
        Sets max_open_trades to 0 and gracefully sells all open trades
        """
        msg = self._rpc_stopbuy()
        return self.rest_dump(msg)

    def _ping(self):
        """
        simple poing version
        """
        return self.rest_dump({"status": "pong"})
