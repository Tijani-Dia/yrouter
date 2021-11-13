from .constants import PATH_DELIMITER
from .exceptions import RouterConfigurationError
from .match import FullMatch, NoMatch
from .route import route
from .route_node import RouteNode
from .utils import add_child_routes, get_components


class Router:
    def __init__(self, routes, append_slash=True):
        if not routes:
            raise RouterConfigurationError(
                "Trying to initialize router with empty routes."
            )
        if routes[0].tree.converter.description != "":
            raise RouterConfigurationError("First route must be '' or '/'.")

        self.tree = self._build_tree(routes)
        self.append_slash = append_slash

    def _build_tree(self, routes):
        return add_child_routes(
            RouteNode(routes[0].tree.converter, routes[0]), routes[1:]
        )

    def match(self, path):
        node = self.tree
        kwargs = {}

        for component in get_components(path):
            partial_match = node.match(component)
            if partial_match is NoMatch:
                return NoMatch

            node = partial_match.node
            if partial_kwargs := partial_match.kwargs:
                kwargs |= partial_kwargs

        if not node.can_match:
            return NoMatch

        should_redirect = False
        redirect_to = None
        if path and path != PATH_DELIMITER:
            if self.append_slash and path[-1] != PATH_DELIMITER:
                redirect_to = path + PATH_DELIMITER
                should_redirect = True
            elif not self.append_slash and path[-1] == PATH_DELIMITER:
                redirect_to = path[:-1]
                should_redirect = True

        return FullMatch(node, kwargs, should_redirect, redirect_to)

    def find(self, handler_name, **kwargs):
        if handler_name not in route._handler_names:
            return

        found = self.tree.find(handler_name, **kwargs)
        if found and not self.append_slash:
            found = found[:-1]

        return found

    def display(self):
        self.tree.display(0)
