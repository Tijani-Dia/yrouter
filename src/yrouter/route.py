from typing import Any, Callable, Optional, Sequence

from .converters import ExactConverter
from .route_node import RouteNode
from .utils import add_child_routes, get_components, get_converter

HANDLER_NAMES = set()


def route(
    path: str,
    handler: Optional[Callable[..., Any]] = None,
    name: Optional[str] = None,
    subroutes: Optional[Sequence[RouteNode]] = None,
) -> RouteNode:

    components = get_components(path)
    converter = get_converter(components[0]) if components else ExactConverter("")
    root = RouteNode(converter)

    node = root
    for component in components[1:]:
        child = RouteNode(get_converter(component))
        node.children.append(child)
        node = child

    node.handler = handler
    if name:
        node.name = name
        HANDLER_NAMES.add(name)

    if subroutes:
        add_child_routes(node, subroutes)

    return root
