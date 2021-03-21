#!/usr/bin/env python3
"""
Main playground script.
Read the documentation to know what cli arguments you need.
"""

import sys
from typing import Any, List

from playground import __title__, __version__
from playground.integrator import PlaygroundIntegrator
from playground.util import setup_logger
from playground.config import PlaygroundConfig
from playground.commands import parse_arguments


def main(sysargv: List[str] = None) -> None:
    """
    This function will initiate the playground.
    :return: None
    """
    return_code: Any = 1

    logger = setup_logger(name='{}.v{}'.format(__title__, __version__))
    logger.info('Launching playground environment..\n'  +
        '           __                                             __\n' +
        '    ____  / /___ ___  ______ __________  __  ______  ____/ /\n' +
        '   / __ \/ / __ `/ / / / __ `/ ___/ __ \/ / / / __ \/ __  / \n' +
        '  / /_/ / / /_/ / /_/ / /_/ / /  / /_/ / /_/ / / / / /_/ /  \n' +
        ' / .___/_/\__,_/\__, /\__, /_/   \____/\__,_/_/ /_/\__,_/   \n' +
        '/_/            /____//____/                         ₀.₁.₁   \n'
    )

    pg_config: PlaygroundConfig = None
    pg: PlaygroundIntegrator = None
    pg_config: PlaygroundConfig = parse_arguments(logger=logger, sysargv=sysargv)

    if pg_config is not None:
        pg = PlaygroundIntegrator(config=pg_config)
    else:
        logger.warning('WARNING: No playground config set, running with deprecated default settings.')
        pg = PlaygroundIntegrator()
    try:
        pg.run()
    except KeyboardInterrupt:
        logger.info('SIGINT received, aborting ...')
        return_code = 0
        """
        for ft in worker.forwardtests:
            if len(ft.data) != 0:
                ft.print_results()
                #ft.chart()
        """
        # TODO: stuff related with livetrading
    
    return return_code


if __name__ == '__main__':
    main(sysargv=sys.argv)