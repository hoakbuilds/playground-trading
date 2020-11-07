__title__ = "simulation"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"



# Local imorts
from playground.enums import RunMode
from playground.simulation.backtesting import BackTestingOperation
from playground.simulation.forwardtesting import ForwardTestingOperation


OP_TYPES = {
    RunMode.BACKTEST: BackTestingOperation,
    RunMode.FORDWARDTEST: ForwardTestingOperation,
}

class SimulatedOperationType:
    """An object representing the Simulated Operation."""   

    def __init__(self, ):
        """
        Simply initiate the SimulatedOpType.
        """

        return

    @staticmethod
    def from_config(config, ):
        """
        Simply return the corresponding type's SimulatedOp class based on config
        param: config: A SimulatedOperationConfig
        type: config: SimulatedOperationConfig
        """

        return OP_TYPES[config.RunMode].from_config(config)