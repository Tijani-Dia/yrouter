from functools import cached_property, lru_cache

from .constants import END_DESCRIPTION, PATH_DELIMITER, START_DESCRIPTION
from .match import Match, NoMatch


class RouteNode:
    def __init__(self, converter, route=None, children=None):
        self.converter = converter
        self.route = route
        self.children = children if children else []

    @property
    def component(self):
        return self.converter.description

    @cached_property
    def can_match(self):
        return bool(self.route and self.route.handler)

    @lru_cache
    def match(self, path):
        for child in self.children:
            accepts, kwargs = child.converter.accepts(path)
            if accepts:
                return Match(child, kwargs)

        return NoMatch

    def find(self, handler_name, **kwargs):
        component, converter = self.component, self.converter
        if component.startswith(START_DESCRIPTION) and component.endswith(
            END_DESCRIPTION
        ):

            if converter.name in ["int", "str"]:
                if (identifier := converter.identifier) not in kwargs:
                    return

                accepts, accepted = converter.accepts(str(kwargs[identifier]))
                if not accepts:
                    return

                kwargs.pop(identifier)
                component = str(accepted[identifier])

            else:
                for k, v in kwargs.items():
                    accepts, accepted = converter.accepts(str(v))
                    if accepts and k in accepted:
                        kwargs.pop(k)
                        component = str(accepted[k])
                        break

        matched = component + PATH_DELIMITER
        if self.route and self.route.name == handler_name and not kwargs:
            return matched

        for child in self.children:
            found = child.find(handler_name, **kwargs)
            if found:
                return matched + found

    def __str__(self):
        return f"{self.component}/"

    def __repr__(self):
        return f"<RouteNode: converter={self.converter}; route={self.route}; children={len(self.children)}>"

    def display(self, i):
        print(" " * 4 * i + str(self))
        for child in self.children:
            child.display(i + 1)
