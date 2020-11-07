#!/usr/bin/env python3
"""
Main playground script.
Read the documentation to know what cli arguments you need.
"""
from logging import Logger
from playground.util import validateJSONFile, validateJSONSchema
from playground.bridge.config import bridge_config_from_json
from typing import Any, Dict, List, Optional, Tuple

from playground import __title__, __version__
from playground.config import playground_config_from_json


def split_arguments(logger: Logger = None, argument: str = None) -> Optional[Tuple[str, str]]:
    """
    Split the argument from cli and return a tuple of the argument and value
    param: logger:
    param: argument:
    """
    if argument is None:
        raise Exception("split_arguments needs param `argument`")

    split = argument.split("=", maxsplit= 1)

    if split is not None and len(split) == 2:
        if logger is not None:
            logger.info('Found argument {} with value {}', split[0], split[1])
        return split[0], split[1]
    
    raise Exception("split_arguments unexpected error occurred")


def process_playground_arguments(logger: Logger = None, argument: str = None, value: str = None) -> Optional[Any]:
    """
    This function is only used to parse cli arguments.
    :return: None
    """
    if argument is None:
        raise Exception("process_arguments needs param `argument`")

    if value is None:
        raise Exception("process_arguments needs param `value`")

    switcher = {
        '--config': {
            'function': playground_config_from_json,
            'config_schema': '/envs/playground/ops/default/playground_config_schema.json'
        },
        '--bridge-config':{
            'function': bridge_config_from_json,
            'config_schema': '/envs/playground/ops/default/bridge_module_config_schema.json'
        }
    }

    module = switcher.get(argument, None)
    return_func = module.get('function', None)
    schema_file = module.get('config_schema', None)

    validated: Dict[str, Any] = validateJSONSchema(filename=value, schema_file=schema_file)
    
    if validated is not None:
        logger.info('Config validated successfully.')
        return return_func(json=validated)
    
    logger.info('Provided config is not valid.')
    return None

def parse_arguments(logger: Logger = None, sysargv: List[str] = None) -> Optional[Any]:
    """
    This function is only used to parse cli arguments.
    param: logger: logger
    param: sysargv: list of cli args
    :return: None
    """

    if sysargv is None:
        logger.info('sysargv is None')
        return None
        
    if len(sysargv) <= 1:
        if logger is not None:
            logger.info('No command line arguments found, using deprecated configs.')
        return None
    else:
        arguments : int = len(sysargv) - 1
        if arguments > 1:
            raise Exception("Too many arguments, only need --config=path/to/config/file or --bridge-config=path/to/bridge/config/file.")
        if arguments == 1:
            if logger is not None:
                logger.info('Found {} argument'.format(str(arguments)))
        
        return_arg = None

        arg, value = split_arguments(argument=sysargv[arguments])

        return_arg = process_playground_arguments(
            logger=logger, argument=arg, value=value,
        )
        return return_arg

    