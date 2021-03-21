__title__ = "simulation"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

# Global imports
from enum import Enum
from typing import Any, Dict

# Local imports
from playground.messaging.flow import Flow, flow_from_json
from playground.messaging.stream import Stream, stream_from_json

class ConsumerConfig:
    """An object representing the ConsumerConfig."""

    name: str = None
    socket_ip: str = None
    socket_port: int = None

    flow: Flow = None
    consume_stream: Stream = None

    def __init__(self, 
    name: str = None, socket_ip: str = None, socket_port: int = None, flow: Flow = None, consume_stream: Stream = None,
    ):
        """
        Simply initiate the ConsumerConfig.
        """

        if name is None:
            raise Exception("ConsumerConfig class needs `name` param to designate itself")
        self.name = name

        if socket_ip is None:
            raise Exception("ConsumerConfig class needs `socket_ip` param to connect to stream")
        self.socket_ip = socket_ip

        if socket_port is None:
            raise Exception("ConsumerConfig class needs `socket_port` param to connect to stream")
        self.socket_port = socket_port

        if flow is None:
            raise Exception("ConsumerConfig class needs `flow` param to connect to stream")
        self.flow = flow
        
        if consume_stream is None:
            raise Exception("ConsumerConfig class needs `consume_stream` param to connect to stream")
        self.consume_stream = consume_stream


def consumer_config_from_json(self, json: Dict[str, Any] = None) -> None:
    """
    Simply initiate the ConsumerConfig.
    """

    if json is None:
        raise Exception("ConsumerConfig from_json method needs `json` param")

    return ConsumerConfig(
        name=json.get('name', None),
        socket_ip=json.get('socket_ip', None),
        socket_port=json.get('socket_port', None),
        flow=flow_from_json(json=json.get('flow', None)),
        consume_stream=stream_from_json(json=json.get('stream', None)),
    )
