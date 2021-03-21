__title__ = "playground"
__author__ = "murlux"
__copyright__ = "Copyright 2019, " + __author__
__credits__ = (__author__, )
__license__ = "MIT"
__email__ = "murlux@protonmail.com"

# Global imports
from typing import Dict, Any, List, Optional

# Local imports
from playground.enums import *
from playground.util import setup_logger
from playground.messaging.stream import Stream, stream_from_json

logger = setup_logger(name=__name__)


class Flow:
    """
    This class represents a Flow of data within the system
    """

    # This is the name of the flow
    name: str = None

    # This value represents the source stream of the flow
    source: Stream = None

    # This value represents the target stream of the flow
    target: Stream = None

    def __init__(self, name: str = None, source: Stream = None, target: Stream = None) -> None:
        """
        Init from json

        :param name: str name of the flow
        :param source: Stream that represents the source of the flow
        :param target: Stream that represents the target of the flow
        """
        if name is None:
            raise Exception("Flow class needs `name` param")

        if source is None:
            raise Exception("Flow class needs `source` param")

        if target is None:
            raise Exception("Flow class needs `target` param")

        self.name = name
        self.source = source
        self.target = target

        logger.info('Created Flow: {} - Source: {} - Target: {}'.format(self.name, self.source.name, self.target.name))

    def __str__(self) -> str:
        """String representation."""
        return '[{}-{}-{}]'.format(self.name, self.source.name, self.target.name)

def flows_from_json(flow_json: Dict[str, Any] = None) -> List[Flow]:
    """
    Parse a list of Flows from json to python obj.
    """
    flow_list: List = []
    
    if flow_json is None:
        raise Exception("BridgeConfig flows_from_json method needs `flow_json` param")

    for item in flow_json:
        flow: Flow = Flow(
            name=item.get('name', None),
            source=stream_from_json(json=item.get('source', None)),
            target=stream_from_json(json=item.get('target', None)),
        )

        flow_list.append(flow)

    return flow_list


def flow_from_json(json: Dict[str, Any] = None) -> Optional[Flow]:
    """
    Return the object from json
    """
    if json is None:
        raise Exception("Flow flow_from_json needs `json` param")
    return Stream(
        name=json.get('name', None),
        source=Stream.from_json(json=json.get('source', None)),
        target=Stream.from_json(json=json.get('target', None)),
    )