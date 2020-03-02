__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

from playground.worker import Worker
from playground.api_server import ApiServer

class ServiceManager:

    _worker: Worker =  None
    _api: ApiServer = None
    def __init__(self, worker):

        self._worker = worker        
        self._api = ApiServer()

