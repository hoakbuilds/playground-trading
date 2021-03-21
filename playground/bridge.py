#!/usr/bin/env python3
"""
Main bridge script.
Read the documentation to know what cli arguments you need.
"""
import sys
from typing import Any, List

from playground import __title__, __version__
from playground.util import setup_logger
from playground.bridge.integrator import BridgeIntegrator
from playground.bridge.config import BridgeConfig
from playground.commands import parse_arguments


def main(sysargv: List[str] = None) -> None:
    """
    This function will initiate the bridge.
    :return: None
    """
    return_code: Any = 1

    logger = setup_logger(name='{}.v{}'.format(__title__, __version__))
    logger.info('Launching the bridge environment..\n'  +
                '    __         _     __         ' + '\n' +
                '   / /_  _____(_)___/ /___ ____ ' + '\n' +
                '  / __ \/ ___/ / __  / __ `/ _ \\' + '\n' +
                ' / /_/ / /  / / /_/ / /_/ /  __/' + '\n' +
                '/_.___/_/  /_/\__,_/\__, /\___/ ' + '\n' +
                '                /____/   ₀.₀.₁' + '\n'
    )

    bridge_config: BridgeConfig = None
    bridge: BridgeIntegrator = None

    bridge_config: BridgeConfig = parse_arguments(logger=logger, sysargv=sysargv)

    if bridge_config is not None:
        bridge = BridgeIntegrator(config=bridge_config)
    else:
        logger.warning('WARNING: No bridge config set, exiting.')
        return 0
    try:
        bridge.run()
    except KeyboardInterrupt:
        logger.info('SIGINT received, aborting ...')
        return_code = 0
    
    return return_code


if __name__ == '__main__':
    main(sysargv=sys.argv)
