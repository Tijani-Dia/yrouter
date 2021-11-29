from typing import List, Sequence

from .constants import (
    DESCRIPTION_DELIMITER,
    END_DESCRIPTION,
    PATH_DELIMITER,
    START_DESCRIPTION,
)
from .converters import AbstractConverter, ExactConverter, get_converters
from .exceptions import RouterConfigurationError, UnknownConverter
from .route_node import RouteNode


def add_child_routes(root: RouteNode, children: Sequence[RouteNode]) -> RouteNode:
    described = set()

    for route in children:
        if (description := route.converter.description) in described:
            raise RouterConfigurationError(
                f"A node matching '{description}' already exists at this level of the tree."
            )

        described.add(description)
        root.children.append(route)

    return root


def get_components(path: str) -> List[str]:
    return path.strip(PATH_DELIMITER).split(PATH_DELIMITER)


def get_converter(description: str) -> AbstractConverter:
    if description.startswith(START_DESCRIPTION) and description.endswith(
        END_DESCRIPTION
    ):
        delimiter_index = description.find(DESCRIPTION_DELIMITER)
        if delimiter_index == -1:
            return ExactConverter(description)

        if (_type := description[1:delimiter_index]) in (
            CONVERTERS := get_converters()
        ):
            converter_class = CONVERTERS[_type]
            return converter_class(description, description[delimiter_index + 1 : -1])
        else:
            raise UnknownConverter(f"{_type}")

    return ExactConverter(description)
