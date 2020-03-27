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
from flask_cors import CORS
from werkzeug.serving import make_server
from playground import settings
from playground.util import setup_logger

BASE_URI = '/api/v1'


class ApiServer:
    """Basic api server for REST calls."""

    _worker = None
    def __init__(self, worker) -> None:
        """
        Init the api server, and init the super class RPC
        """
        self.logger = setup_logger(name=__name__)
        self.app = Flask(__name__)
        CORS(self.app)

        if worker:
            self._worker = worker

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
        rest_ip = '0.0.0.0'
        rest_port = 5000

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
        self.app.add_url_rule(f'{BASE_URI}/warehouse_information', 'warehouse_information',
                              view_func=self._wh_info, methods=['GET'])
        self.app.add_url_rule(f'{BASE_URI}/get_dataset/<pair>/<timeframe>/', 'get_dataset',
                              view_func=self._get_dataset, methods=['GET'])
        self.app.add_url_rule(f'{BASE_URI}/wallet_balances', 'wallet_balances',
                              view_func=self._balances, methods=['GET'])
        self.app.add_url_rule(f'{BASE_URI}/forwardtesting_shorts', 'forwardtesting_shorts',
                              view_func=self._ft_shorts, methods=['GET'])
        self.app.add_url_rule(f'{BASE_URI}/forwardtesting_longs', 'forwardtesting_longs',
                              view_func=self._ft_longs, methods=['GET'])
        self.app.add_url_rule(f'{BASE_URI}/forwardtesting_results', 'forwardtesting_results',
                              view_func=self._ft, methods=['GET'])
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

    def _balances(self):
        """
        simple wallet ping
        """
        _balances: list = self._worker.wallet.get_balances()
        return self.rest_dump({"balances": _balances})

    def _ping(self):
        """
        simple poing version
        """
        return self.rest_dump({"status": "pong"})

    def _ft(self):
        """
        get forwardtesting live results
        """
        _fts: list = [x._get_results() for x in self._worker.forwardtests]
        return self.rest_dump(_fts)

    def _ft_longs(self):
        """
        get forwardtesting live results
        """
        _fts: list = [x._get_longs() for x in self._worker.forwardtests]
        return self.rest_dump(_fts)
    
    def _ft_shorts(self):
        """
        get forwardtesting live results
        """
        _fts: list = [x._get_shorts() for x in self._worker.forwardtests]
        return self.rest_dump(_fts)

    def _wh_info(self):
        """
        Get pairs with available datasets.
        """
        _pairs: list = [str(x) for x in self._worker.market_pairs]
        _timeframes: list = [x for x in settings.WAREHOUSE_TIMEFRAMES]
        return self.rest_dump({'pairs':_pairs, 'timeframes': _timeframes})
    
    def _get_dataset(self, pair=None, timeframe=None):
        """
        Get pairs with available datasets.
        """
        tf: str = timeframe.replace('_', ' ')
        dataset = self._worker.wh.get_dataset(pair=pair, timeframe=tf, analysed=True).to_json()
        return self.rest_dump({'data': dataset})
