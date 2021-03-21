__title__ = "simulation"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

# Global imports
from enum import Enum
from typing import Any, Dict

from playground.messaging.flow import Flow, flow_from_json
from playground.messaging.stream import Stream, stream_from_json


class ProducerConfig:
    """An object representing the ProducerConfig."""

    name: str = None

    socket_ip: str = None
    socket_port: int = None

    flow: Flow = None
    produce_stream: Stream = None

    def __init__(self,
    name: str = None, socket_ip: str = None, socket_port: int = None, flow: Flow = None, produce_stream: Stream = None,
    ):
        """
        Simply initiate the ProducerConfig.
        """

        if name is None:
            raise Exception("ProducerConfig class needs `name` param to designate itself")
        self.name = name

        if socket_ip is None:
            raise Exception("ProducerConfig class needs `socket_ip` param to connect to stream")
        self.socket_ip = socket_ip

        if socket_port is None:
            raise Exception("ProducerConfig class needs `socket_port` param to connect to stream")
        self.socket_port = socket_port
    
        if flow is None:
            raise Exception("ConsumerConfig class needs `flow` param to connect to stream")
        self.flow = flow
        
        if produce_stream is None:
            raise Exception("ConsumerConfig class needs `produce_stream` param to connect to stream")
        self.produce_stream = produce_stream


def producer_config_from_json(self, json: Dict[str, Any] = None) -> None:
    """
    Simply initiate the ProducerConfig.
    """

    if json is None:
        raise Exception("ProducerConfig from_json method needs `json` param")

    return ProducerConfig(
        name=json.get('name', None),
        socket_ip=json.get('socket_ip', None),
        socket_port=json.get('socket_port', None),
        flow=flow_from_json(json=json.get('flow', None)),
        produce_stream=stream_from_json(json=json.get('stream', None)),
    )
