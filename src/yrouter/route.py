from .converters import ExactConverter
from .route_node import RouteNode
from .utils import add_child_routes, get_components, get_converter


class Route:
    _handler_names = set()

    def __init__(self, path, handler=None, name=None, subroutes=None):
        self.handler = handler
        self.name = name
        self.tree = self._build_tree(path, subroutes)
        if name:
            self._handler_names.add(name)

    def _build_tree(self, path, subroutes):
        components = get_components(path)
        converter = get_converter(components[0]) if components else ExactConverter("")
        root = RouteNode(converter)

        node = root
        for component in components[1:]:
            child = RouteNode(get_converter(component))
            node.children.append(child)
            node = child

        node.route = self

        if subroutes:
            add_child_routes(node, subroutes)

        return root

    def __repr__(self):
        name = self.name or (self.handler.__name__ if self.handler else None)
        return f"<Route: name={name}>"


route = Route
