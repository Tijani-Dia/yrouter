import re
from abc import ABC, abstractmethod

REFUSED = (False, None)
ACCEPTED_NO_KWARGS = (True, {})
CONVERTERS = {}


def get_converters():
    return CONVERTERS


def discard_converter(converter_name):
    return CONVERTERS.pop(converter_name, None)


class AbstractConverter(ABC):
    """
    Abstract converter from which all converters must inherit.
    """

    def __init_subclass__(cls, converter_name=None):
        """Registers a new converter if `converter_name` is provided."""

        super().__init_subclass__()
        if converter_name is not None:
            CONVERTERS[converter_name] = cls
            cls.name = converter_name

    def __init__(self, description, identifier=None):
        self.description = description
        self.identifier = identifier

    def __hash__(self):
        return id(self)

    def __repr__(self):
        return f"<{self.__class__.__name__}: description={self.description}; identifier={self.identifier}>"

    @abstractmethod
    def accepts(self, value):
        """
        Checks if the value provided matches this converter's description.

        Args:
            value (str): Value to check.

        Returns:
            (bool, dict/None): bool is True if the value is accepted, in which case,
                captured parameters, if any, will be available in dict.
                False if the value is refused.
        """

        raise NotImplementedError


class ExactConverter(AbstractConverter):
    """
    A converter that matches an exact description.

    >>> converter = ExactConverter(description="match-me")
    >>> converter.accepts("match-me")
    (True, {})
    >>> converter.accepts("anything-else")
    (False, None)
    """

    def accepts(self, value):
        return ACCEPTED_NO_KWARGS if value == self.description else REFUSED


class IntConverter(AbstractConverter, converter_name="int"):
    """
    A converter that matches positive integers.

    >>> converter = IntConverter(description="<int:id>", identifier="id")
    >>> converter.accepts("100")
    (True, {'id': 100})
    >>> converter.accepts("0")
    (True, {'id': 0})
    >>> converter.accepts("1.0")
    (False, None)
    >>> converter.accepts("-1")
    (False, None)
    >>> converter.accepts("hello-world")
    (False, None)
    """

    def accepts(self, value):
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
    (False, None)
    >>> converter.accepts("hello-world")
    (False, None)
    """

    def accepts(self, value):
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
    (False, None)
    """

    def __init__(self, description, identifier):
        super().__init__(description, identifier)
        self.regex = re.compile(self.identifier)

    def accepts(self, value):
        match = self.regex.match(value)
        return (True, match.groupdict()) if match else REFUSED
