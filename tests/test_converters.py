import pytest

from yrouter import REFUSED, AbstractConverter, NoMatch, Router, UnknownConverter, route
from yrouter.converters import (
    ExactConverter,
    IntConverter,
    PathConverter,
    RegexConverter,
    StringConverter,
    UUIDConverter,
    discard_converter,
    get_converters,
)


def test_get_register_discard_converters():
    default_converters = {
        "__exact__": ExactConverter,
        "int": IntConverter,
        "str": StringConverter,
        "re": RegexConverter,
        "uuid": UUIDConverter,
        "path": PathConverter,
    }

    assert get_converters() == default_converters

    class TestConverter(AbstractConverter, converter_name="test"):
        pass

    assert get_converters() == {**default_converters, "test": TestConverter}

    assert discard_converter("test") == TestConverter
    assert get_converters() == default_converters

    assert discard_converter("not-a-converter") is None
    assert get_converters() == default_converters


def test_exact_converter():
    converter = ExactConverter(description="exact")

    accepts, accepted = converter.accepts("exact")
    assert accepts
    assert accepted == {}

    assert converter.accepts("not-exact") == REFUSED


def test_int_converter():
    converter = IntConverter(description="<int:id>", identifier="id")

    accepts, accepted = converter.accepts("1")
    assert accepts
    assert accepted == {"id": 1}

    assert converter.accepts("1.0") == REFUSED
    assert converter.accepts("hello") == REFUSED


def test_str_converter():
    converter = StringConverter(description="<str:string>", identifier="string")

    accepts, accepted = converter.accepts("helloworld")
    assert accepts
    assert accepted == {"string": "helloworld"}

    assert converter.accepts("") == REFUSED
    assert converter.accepts("1.0") == REFUSED
    assert converter.accepts("hello-world") == REFUSED
    assert converter.accepts("hello_world") == REFUSED


def test_regex_converter():
    rgx = r"page-(?P<page>\d+)?$"
    converter = RegexConverter(description=f"<re:{rgx}>", identifier=rgx)

    accepts, accepted = converter.accepts("page-5")
    assert accepts
    assert accepted == {"page": "5"}

    assert converter.accepts("") == REFUSED
    assert converter.accepts("1.0") == REFUSED
    assert converter.accepts("page-one") == REFUSED


def test_uuid_converter():
    uuid = "b473e2ca-50a5-11ec-83dc-479fd603abba"
    converter = UUIDConverter("<uuid:uuid>", "uuid")
    accepts, accepted = converter.accepts(uuid)

    assert accepts
    assert accepted == {"uuid": uuid}

    assert converter.accepts("") == REFUSED
    assert converter.accepts(uuid[:-1]) == REFUSED


def test_register_new_converter_without_accepts_method():
    class CustomConverter(AbstractConverter, converter_name="custom"):
        pass

    expected = (
        "Can't instantiate abstract class CustomConverter with abstract method accepts"
    )
    with pytest.raises(TypeError, match=expected):
        route("<custom:custom>/")


def test_register_new_converter():
    class CustomConverter(AbstractConverter, converter_name="custom"):
        def accepts(self, value):
            return (True, {"custom": value}) if value == "magic" else REFUSED

    routes = (
        route("/"),
        route("<custom:custom>/", lambda: None, name="custom"),
    )
    router = Router(routes)

    match = router.match("magic/")
    assert match.handler_name == "custom"
    assert match.kwargs == {"custom": "magic"}

    assert router.match("not-magic/") is NoMatch
    discard_converter("custom")


def test_unknown_converter():
    with pytest.raises(UnknownConverter):
        route("<lang>/<route:url>/")


def test_hash_converter():
    class Converter(AbstractConverter, converter_name="__hash__"):
        def accepts(self, value):
            pass

    converter = Converter(description="converter")
    assert hash(converter) == id(converter)
