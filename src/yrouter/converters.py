import re
from abc import ABC, abstractmethod
from typing import Dict, Optional, Pattern, Tuple, Type

REFUSED: Tuple[bool, dict] = (False, {})
CONVERTERS: Dict[str, Type["AbstractConverter"]] = {}


class AbstractConverter(ABC):
    """Abstract converter from which all converters must inherit."""

    name: Optional[str]

    def __init__(self, description: str, identifier: str = None) -> None:
        self.description = description
        self.identifier = identifier

    def __hash__(self):
        return id(self)

    def __repr__(self):
        return f"<{self.__class__.__name__}: description={self.description}; identifier={self.identifier}>"

    @abstractmethod
    def accepts(self, value: str) -> Tuple[bool, dict]:
        """
        Checks if the value provided matches this converter's description.
        Returns `True` if the value is accepted, in which case, captured parameters,
        if any, will be available in `dict`. Returns `REFUSED` else.
        """

        raise NotImplementedError

    def __init_subclass__(cls, converter_name=None):
        """Registers a new converter if `converter_name` is provided."""

        super().__init_subclass__()
        if converter_name is not None:
            CONVERTERS[converter_name] = cls
            cls.name = converter_name


class ExactConverter(AbstractConverter):
    """
    A converter that matches an exact description.

    >>> converter = ExactConverter(description="match-me")
    >>> converter.accepts("match-me")
    (True, {})
    >>> converter.accepts("anything-else")
    (False, {})
    """

    def accepts(self, value: str) -> Tuple[bool, dict]:
        return (True, {}) if value == self.description else REFUSED


class IntConverter(AbstractConverter, converter_name="int"):
    """
    A converter that matches positive integers.

    >>> converter = IntConverter(description="<int:id>", identifier="id")
    >>> converter.accepts("100")
    (True, {'id': 100})
    >>> converter.accepts("0")
    (True, {'id': 0})
    >>> converter.accepts("1.0")
    (False, {})
    >>> converter.accepts("-1")
    (False, {})
    >>> converter.accepts("hello-world")
    (False, {})
    """

    def accepts(self, value: str) -> Tuple[bool, dict]:
        return (True, {self.identifier: int(value)}) if value.isdigit() else REFUSED


class StringConverter(AbstractConverter, converter_name="str"):
    """
    A converter that only matches alphabetic characters.

    >>> converter = StringConverter(description="<str:string>", identifier="string")
    >>> converter.accepts("hello")
    (True, {'string': 'hello'})
    >>> converter.accepts("ABC")
    (True, {'string': 'ABC'})
    >>> converter.accepts("1")
    (False, {})
    >>> converter.accepts("hello-world")
    (False, {})
    """

    def accepts(self, value: str) -> Tuple[bool, dict]:
        return (True, {self.identifier: value}) if value.isalpha() else REFUSED


class RegexConverter(AbstractConverter, converter_name="re"):
    """
    A converter that matches regular expressions.
    Since yrouter represent routes by delimiting them with the '/' character,
    a '/' isn't allowed in regex identifiers...

    >>> converter = RegexConverter("<re:(?P<match>^[a-z]*$)>", "(?P<match>^[a-z]*$)")
    >>> converter.accepts("whatever")
    (True, {'match': 'whatever'})
    >>> converter.accepts("a-b")
    (False, {})
    """

    def __init__(self, description: str, identifier: str) -> None:
        super().__init__(description, identifier)
        self.regex: Pattern = re.compile(self.identifier)

    def accepts(self, value: str) -> Tuple[bool, dict]:
        match = self.regex.match(value)
        return (True, match.groupdict()) if match else REFUSED


def get_converters() -> Dict[str, Type[AbstractConverter]]:
    return CONVERTERS


def discard_converter(converter_name: str) -> Optional[Type[AbstractConverter]]:
    return CONVERTERS.pop(converter_name, None)
