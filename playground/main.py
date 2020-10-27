#!/usr/bin/env python3
"""
Main playground script.
Read the documentation to know what cli arguments you need.
"""
from typing import Any, List

from playground import __title__, __version__
from playground.integrator import PlaygroundIntegrator
from playground.util import setup_logger


def main(sysargv: List[str] = None) -> None:
    """
    This function will initiate the bot and start the trading loop.
    :return: None
    """

    logger = setup_logger(name='{}.v{}'.format(__title__, __version__))
    logger.info('Launching environment..\n'  +
        '______  __       ______   __  __   ______   ______   ______   __  __   __   __   ______      \n' +
        '/\  == \/\ \     /\  __ \ /\ \_\ \ /\  ___\ /\  == \ /\  __ \ /\ \/\ \ /\ "-.\ \ /\  __-.    \n' +
        '\ \  _-/\ \ \____\ \  __ \\ \____ \\ \ \__ \\\\ \  __< \ \ \/\ \\\\ \ \_\ \\\\ \ \-.  \\\\ \ \/\ \   \n' +
        ' \ \_\   \ \_____\\\\ \_\ \_\\/\_____\\ \_____\\\\ \_\ \_\\\\ \_____\\\\ \_____\\\\ \_\\\\"\_\\\\ \____-\'   \n' +
        '  \/_/    \/_____/ \/_/\/_/ \/_____/ \/_____/ \/_/ /_/ \/_____/ \/_____/ \/_/ \/_/ \/₀.₁.₀/ /\n',
    )

    return_code: Any = 1

    pg = PlaygroundIntegrator()

    try:
        pg.run()
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