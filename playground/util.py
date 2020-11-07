__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

import json
import logging
from typing import Any, Dict, Optional
from dateutil.relativedelta import relativedelta
from datetime import datetime
from jsonschema import validate, exceptions
from playground import enums


def timestamp_to_date(timestamp=None):
    """
    Convert timestamp to datetime object
    """
    return datetime.fromtimestamp(int(timestamp))


def setup_logger(name: str = None) -> logging.Logger:
    logger = logging.getLogger(name)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )
    return logger


class ArgumentDebugger:
    """
    Class used to debug passed args and kwargs into a determined function
    """

    @staticmethod
    def print_kwargs(**kwargs):
            print(kwargs)

    @staticmethod
    def print_values(**kwargs):
        for key, value in kwargs.items():
            print("The value of {} is {}".format(key, value))


def validateJSONString(json_string: str = None) -> Optional[Dict[str, Any]]:
    """
    Validates if a string is json or not. If it is, returns the json object.
    """
    logger: logging.Logger = setup_logger(name='JSONStringValidator')

    if json_string is None:
        raise Exception('JSONStringValidator expects `json_string` param to not be None')

    json_obj = None

    try:
        json_obj = json.loads(json_string)
    except ValueError as err:
        logger.error('Invalid json provided. exc:', exc_info=err)
        return None

    return json_obj

def validateJSONFile(filename: str = None) -> Optional[Dict[str, Any]]:
    """
    Reads a file and validates if it's content is json or not.
    """
    logger: logging.Logger = setup_logger(name='JSONFileValidator')

    if filename is None:
        raise Exception('JSONFileValidator expects `filename` param to not be None')
    try:
        with open(file=filename, mode='r') as file:
            file_content: str = file.read()

            return validateJSONString(json_string=file_content)
    except IOError as io_exc:
        logger.error('I/O Error occurred. exc:', exc_info=io_exc)
    except FileNotFoundError as fnf_exc:
        logger.error('File not found. exc:', exc_info=fnf_exc)
    except OSError as os_exc:
        logger.error('System error occurred. exc:', exc_info=os_exc)
        

def validateJSONSchema(filename: str = None, schema_file: str = None) -> Optional[Dict[str, Any]]:
    """
    Reads a file and validates if it's content is json or not as well as
    checks if it's schema is according to defaults or not.
    """
    logger: logging.Logger = setup_logger(name='JSONSchemaValidator')

    def _load_json_schema(schema_filename: str = None) -> Optional[Dict[str, Any]]:
        """
        Loads the given schema file.
        """
        try:
            with open(schema_filename) as schema_file:
                return json.loads(schema_file.read())
        except IOError as io_exc:
            logger.error('I/O Error occurred. exc:', exc_info=io_exc)
        except FileNotFoundError as fnf_exc:
            logger.error('File not found. exc:', exc_info=fnf_exc)
        except OSError as os_exc:
            logger.error('System error occurred. exc:', exc_info=os_exc)

    if filename is None:
        raise Exception('JSONSchemaValidator expects `filename` param to not be None')

    data = validateJSONFile(filename=filename)

    schema = _load_json_schema(schema_filename=schema_file)
    if schema is not None:
        try:
            validate(data, schema)
        except exceptions.ValidationError as ex:
            return None

        return data
    else:
        raise Exception('JSONSchemaValidator expects schema file to be valid')

