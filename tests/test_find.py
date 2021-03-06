from yrouter import REFUSED, AbstractConverter, Router, route


def test_find_int(router):
    path = router.find("int", id=5)
    assert path == "/int/5/"


def test_find_multiple_parameter(router):
    kwargs = {
        "year": 2020,
        "month": 1,
        "day": 30,
    }
    path = router.find("articles-year-month-day", **kwargs)
    assert path == "/articles/2020/1/30/"


def test_find_missing_arguments(router):
    kwargs = {
        "year": 2020,
        "month": 1,
    }
    path = router.find("articles-year-month-day", **kwargs)
    assert path is None


def test_find_extra_arguments(router):
    kwargs = {
        "year": 2020,
        "month": 1,
        "day": 30,
        "extra": 2,
    }
    path = router.find("articles-year-month-day", **kwargs)
    assert path is None


def test_find_unregistered_name(router):
    path = router.find("articles-month")
    assert path is None


def test_find_invalid_argument_type(router):
    path = router.find("articles-year-month-day", year="year")
    assert path is None


def test_find_regex(router):
    path = router.find("catchall", catched="whatever")
    assert path == "/whatever/catch/"


def test_find_regex_no_kwargs(router):
    path = router.find("catchall")
    assert path == "/<re:(?P<catched>^[a-z]*$)>/catch/"


def test_find_slug(router):
    path = router.find("users-slug", slug="user-123")
    assert path == "/users/user-123/"

    assert router.find("users-slug") is None
    assert router.find("users-slug", slug="user-123", foo="bar") is None


def test_find_uuid(router):
    uuid = "8fcc1854-50a8-11ec-83dc-479fd603abba"
    path = router.find("items", id=uuid)
    assert path == f"/items/{uuid}/"

    assert router.find("items") is None
    assert router.find("items", id=uuid[1:]) is None
    assert router.find("items", id=uuid, foo="bar") is None


def test_find_static(router):
    img_path = "images/original/hero.jpg"
    path = router.find("static", path=img_path)
    assert path == f"/static/{img_path}/"

    assert router.find("static") is None
    assert router.find("static", path=img_path, foo=1) is None


def test_find_after_path(router):
    path = router.find("path-id", path="folders/new", id=1)
    assert path == "/path/folders/new/1/"


def test_find_with_custom_converter():
    class Converter(AbstractConverter, converter_name="upper"):
        def accepts(self, value):
            return (True, {"letter": value}) if value.isupper() else REFUSED

    routes = [
        route(""),
        route("letters/<upper:letter>", lambda: None, name="letters"),
    ]

    router = Router(routes)

    assert router.find("letters", letter="ALPHA") == "/letters/ALPHA/"
    assert router.find("letters", letter="BETA") == "/letters/BETA/"

    assert router.find("letters") is None
    assert router.find("letters", letter="ALPHa") is None
    assert router.find("letters", letter="ALPHA", word="word") is None
