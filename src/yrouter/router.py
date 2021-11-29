from typing import Any, Dict, Optional, Sequence

from .constants import PATH_DELIMITER
from .exceptions import RouterConfigurationError
from .match import FullMatch, Match, NoMatch
from .route import HANDLER_NAMES, route
from .route_node import RouteNode
from .utils import add_child_routes, get_components


class Router:
    def __init__(self, routes: Sequence[RouteNode], append_slash: bool = True) -> None:
        if not routes:
            raise RouterConfigurationError(
                "Trying to initialize router with empty routes."
            )

        self.tree = self._build_tree(routes)
        self.append_slash = append_slash

    def _build_tree(self, routes: Sequence[RouteNode]) -> RouteNode:
        if routes[0].converter.description != "":
            return add_child_routes(route(""), routes)
        return add_child_routes(routes[0], routes[1:])

    def match(self, path: str) -> Match:
        node = self.tree
        kwargs: Dict[str, Any] = {}
        is_home_path = bool(path == "" or path == PATH_DELIMITER)
        components = [] if is_home_path else get_components(path)

        for component in components:
            matched_node, partial_kwargs = node.match(component)
            if matched_node is None:
                return NoMatch

            node = matched_node
            if partial_kwargs:
                if node.converter_name != "path":
                    kwargs |= partial_kwargs
                else:
                    for key, value in partial_kwargs.items():
                        if key in kwargs:
                            kwargs[key] += f"/{value}"
                        else:
                            kwargs[key] = value

        if node.handler is None:
            return NoMatch

        should_redirect = False
        redirect_to = None
        if not is_home_path:
            if self.append_slash and path[-1] != PATH_DELIMITER:
                redirect_to = path + PATH_DELIMITER
                should_redirect = True
            elif not self.append_slash and path[-1] == PATH_DELIMITER:
                redirect_to = path.rstrip(PATH_DELIMITER)
                should_redirect = True

        return FullMatch(node, kwargs, should_redirect, redirect_to)

    def find(self, handler_name: str, **kwargs) -> Optional[str]:
        if handler_name not in HANDLER_NAMES:
            return None

        found = self.tree.find(handler_name, **kwargs)
        if found and not self.append_slash:
            found = found[:-1]

        return found

    def display(self):
        self.tree.display(0)
