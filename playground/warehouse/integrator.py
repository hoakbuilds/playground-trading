__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

from logging import Logger
from typing import Any, Dict
from playground.abstract import Integrator
from playground.util import setup_logger
from playground.warehouse.config import WarehouseConfig
from playground.warehouse.persistence import Warehouse
from playground.warehouse.worker import WarehouseWorker
from playground.warehouse.api import WarehouseAPI
from playground.warehouse.socket import WarehouseSocket
from playground.messaging.stream import Stream
from playground.warehouse.producer import WarehouseSocketProducer


class WarehouseIntegrator(Integrator):
    """
    Main warehouse class, spawns the Warehouse, the WarehouseWorker and the WarehouseAPI.
    These two classes are responsable for maintaining and providing up to date datasets.
    """

    logger: Logger = None

    # Critical objects
    warehouse: Warehouse = None
    worker: WarehouseWorker = None
    api: WarehouseAPI = None
    socket: WarehouseSocket = None
    producer: WarehouseSocketProducer = None


    def __init__(self, config: WarehouseConfig) -> None:
        """Initialize the warehouse's integrator."""
        if config is None:
            super().__init__(
                name="WarehouseIntegrator",
                module_name="warehouse",
            )
        else:
            super().__init__(
                name=config.get("name", None),
                module_name=config.get("module_name", None),
            )

        self.warehouse = Warehouse()
        self.worker = WarehouseWorker(warehouse=self.warehouse)
        self.api = WarehouseAPI(warehouse=self.warehouse)
        self.socket = WarehouseSocket(warehouse=self.warehouse)
        self.producer = WarehouseSocketProducer(
            config=config.producer_config
        )

    def run(self) -> None:
        """
        Starts the warehouse worker and serves warehouse API.
        """
        # Start the thread that will serve the HTTP Server
        self.api.Start()

        # Start the thread that will perform the Warehouse upkeep
        self.worker.Start()

        # Start the thread that will launch the socket
        self.socket.Start()

        # Start the thread that will launch the socket
        self.producer.connect_and_run()
        
        #self.logger.info('Setting the warehouse\'s producer queue')
        self.producer.set_read_queue(queue=self.warehouse.get_producer_queue())