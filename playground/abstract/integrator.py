__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

from logging import Logger
from playground.util import setup_logger


class Integrator:
    """
    Basic integrator class..
    """

    logger: Logger = None
    name: str = None
    module_name: str = None

    # Critical objects


    def __init__(self, name: str = None, module_name: str = None) -> None:
        """Initialize the playground's simulation integrator."""

        if name is None:
            raise Exception("Integrator class needs `name` param")

        if module_name is None:
            raise Exception("Integrator class needs `module_name` param")

        self.name = '{}.{}'.format(__name__, name)
        self.logger = setup_logger(name=self.name)
        self.logger.info('Initializing %s component.', self.name)

        self.module_name = module_name


    def run(self) -> None:
        """
        Starts the integrator.
        """
        pass

    def get_module_name(self) -> str:
        """
        Get the module name.
        """
        return self.module_name