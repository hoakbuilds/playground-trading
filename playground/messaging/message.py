__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

from typing import Dict, Any, Optional
from playground.enums import *
from playground.util import setup_logger
from playground.messaging.stream import Stream, stream_from_json
from playground.messaging.payload import Payload, payload_from_json


logger = setup_logger(name=__name__)


class Message:
    """
    This class represents a Message
    """

    stream: Stream = None

    payload: Payload = None

    def __init__(self, stream: Stream = None, payload: Payload = None ) -> None:
        """
        Init from json

        :param config: json dict of the class
        """

        if stream is None:
            raise Exception("Message class needs `stream` param")
        if payload is None:
            raise Exception("Message class needs `payload` param")

        self.stream = stream
        self.payload = payload

    def __str__(self) -> str:
        """String representation."""
        return '[{}-{}-{}]'.format(self.stream.module_name, self.stream.name, self.payload.raw)

    def serialize(self) -> str:
        """Serialize the object"""

    def deserialize(self) -> str:
        """Deserialize the object"""


def message_from_json(json: Dict[str, Any] = None) -> Optional[Message]:
    """
    Return the object from json
    """
    if json is None:
        raise Exception("Message message_from_json needs `json` param")
    return Message(
        stream=stream_from_json(json=json.get('stream', None)),
        payload=payload_from_json(json=json.get('payload', None)),
    )