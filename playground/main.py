#!/usr/bin/env python3
"""
Main Freqtrade bot script.
Read the documentation to know what cli arguments you need.
"""
import logging
from typing import Any, List

from playground import __title__, __version__
from playground.worker import Worker
from playground.util import setup_logger


def main(sysargv: List[str] = None) -> None:
    """
    This function will initiate the bot and start the trading loop.
    :return: None
    """

    logger = setup_logger(name='{}.v{}'.format(__title__, __version__))
    logger.info('Launching environment..')

    return_code: Any = 1

    worker = Worker()

    try:
        worker.run()
    except KeyboardInterrupt:
        logger.info('SIGINT received, aborting ...')
        """
        for ft in worker.forwardtests:
            if len(ft.data) != 0:
                ft.print_results()
                #ft.chart()
        """
        # TODO: stuff related with livetrading

        return_code = 0


if __name__ == '__main__':
    main()