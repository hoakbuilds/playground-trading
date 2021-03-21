__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

from typing import Dict, Any, Optional
from playground.util import setup_logger

logger = setup_logger(name=__name__)


class Stream:
    """
    This class represents a Stream of data within the system
    """

    # This is the name of the stream
    module_name: str = None
    name: str = None
    extra: Dict[str, Any] = None

    def __init__(self, name: str = None, module_name: str = None, extra: Dict[str, Any] = None) -> None:
        """
        Init from json

        :param config: json dict of the class
        """
        if name is None:
            raise Exception("Stream class needs `name` param")

        self.name = name

        if module_name is None:
            raise Exception("Stream class needs `module_name` param")

        self.module_name = module_name

        if extra is not None:
            self.extra = extra

    def __str__(self):
        """
        String rep.
        """
        return f'<Module: {self.module_name} - Name: {self.name}>'

def stream_from_json(json: Dict[str, Any] = None) -> Optional[Stream]:
    """
    Return the object from json
    """
    if json is None:
        raise Exception("Stream stream_from_json needs `json` param")

    return Stream(
        name=json.get('name', None),
        module_name=json.get('module_name', None),
        extra=json.get('extra', None),
    )