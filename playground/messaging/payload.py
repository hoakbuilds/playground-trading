__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

from typing import Dict, Any, Optional
from playground.enums import *
from playground.util import setup_logger

logger = setup_logger(name=__name__)


class Payload:
    """
    This class represents the Payload of a Message
    """

    raw: Dict[str, Any]

    def __init__(self, raw: Dict[str, Any] = None) -> None:
        """
        Init from json

        :param config: json dict of the class
        """
        if raw is None:
            raise Exception("Payload class needs `raw` param")

        self.raw = raw

    def __str__(self):
        """
        String rep.
        """
        return f'<Raw: {self.raw}>'

    def serialize(self) -> str:
        """Serialize the object"""

    def deserialize(self) -> str:
        """Deserialize the object"""


def payload_from_json(json: Dict[str, Any] = None) -> Optional[Payload]:
    """
    Return the object from json
    """
    if json is None:
        raise Exception("Payload class needs `json` param")

    return Payload(
        raw=json.get('raw', None),
    )