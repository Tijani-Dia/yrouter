from .constants import (
    DESCRIPTION_DELIMITER,
    END_DESCRIPTION,
    PATH_DELIMITER,
    START_DESCRIPTION,
)
from .converters import ExactConverter, get_converters
from .exceptions import RouterConfigurationError, UnknownConverter


def get_converter(description):
    if (
        description[0] == START_DESCRIPTION
        and len(description) > 1
        and description[-1] == END_DESCRIPTION
    ):
        delimiter_index = description.find(DESCRIPTION_DELIMITER)
        if delimiter_index == -1:
            return ExactConverter(description)

        if (_type := description[1:delimiter_index]) in (CONVERTERS := get_converters()):
            converter_class = CONVERTERS[_type]
            return converter_class(description, description[delimiter_index + 1 : -1])
        else:
            raise UnknownConverter(f"{_type}")

    return ExactConverter(description)


def add_child_routes(root, children):
    described = set()

    for route in children:
        converter = route.tree.converter
        if converter.identifier is None:
            if (description := converter.description) in described:
                err_msg = (
                    f"A node matching '{description}' already exists "
                    "at this level of the tree."
                )
                raise RouterConfigurationError(err_msg)

            described.add(description)

        root.children.append(route.tree)

    return root


def get_components(path):
    if not path:
        return []
    if path[0] == PATH_DELIMITER:
        path = path[1:]
    if path and path[-1] == PATH_DELIMITER:
        path = path[:-1]

    return path.split(PATH_DELIMITER) if path else []
