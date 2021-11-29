from functools import lru_cache
from typing import Any, Callable, Dict, List, Optional, Tuple

from .constants import END_DESCRIPTION, PATH_DELIMITER, START_DESCRIPTION
from .converters import AbstractConverter

NONE_TUPLE = (None, None)


class RouteNode:
    __slots__ = ("converter", "converter_name", "handler", "name", "children")

    def __init__(
        self,
        converter: AbstractConverter,
        handler: Optional[Callable[..., Any]] = None,
        name: str = None,
        children: Optional[List["RouteNode"]] = None,
    ) -> None:
        self.converter = converter
        self.converter_name = converter.name
        self.handler = handler
        self.name = name
        self.children = children if children else []

    @property
    def component(self):
        return self.converter.description

    @lru_cache
    def match(
        self, path: str
    ) -> Tuple[Optional["RouteNode"], Optional[Dict[str, Any]]]:
        for child in self.children:
            accepts, kwargs = child.converter.accepts(path)
            if accepts:
                return (child, kwargs)

        return NONE_TUPLE

    def find(self, handler_name: str, **kwargs) -> Optional[str]:
        component, converter = self.component, self.converter
        if component.startswith(START_DESCRIPTION) and component.endswith(
            END_DESCRIPTION
        ):

            if self.converter_name != "re":
                if (identifier := converter.identifier) not in kwargs:
                    return None

                accepts, accepted = converter.accepts(str(kwargs[identifier]))
                if not accepts:
                    return None

                kwargs.pop(identifier)
                component = str(accepted[identifier])

            else:
                for identifier, value in kwargs.items():
                    accepts, accepted = converter.accepts(str(value))
                    if accepts and identifier in accepted:
                        kwargs.pop(identifier)
                        component = str(accepted[identifier])
                        break

        matched = component + PATH_DELIMITER
        if self.handler and self.name == handler_name and not kwargs:
            return matched

        for child in self.children:
            found = child.find(handler_name, **kwargs)
            if found:
                return matched + found

        return None

    def finalize(self):
        assert (
            self.converter_name == "path"
        ), "Only routes with `path` converters are allowed to be recursive."

        self.children.append(self)

    def __str__(self):
        return f"{self.component}/"

    def __repr__(self):
        return (
            f"<RouteNode: converter={self.converter}; "
            f"handler={self.handler}; children={len(self.children)}>"
        )

    def display(self, i: int) -> None:
        print(" " * 4 * i + str(self))
        for child in self.children:
            child.display(i + 1)
