import pytest

from yrouter import NoMatch, Router, RouterConfigurationError, UnknownConverter, route

from . import handlers


def test_path_lookup_without_parameters(router):
    match = router.match("/articles/2020/")
    assert match.handler_name == "articles-2020"
    assert match.handler == handlers.handler_2020


def test_path_lookup_with_typed_parameters(router):
    match = router.match("/articles/2015/")
    assert match.handler_name == "articles-year"
    assert match.kwargs["year"] == 2015


def test_path_lookup_with_multiple_parameters(router):
    match = router.match("/articles/2015/04/12/")
    assert match.handler_name == "articles-year-month-day"
    assert match.kwargs["year"] == 2015
    assert match.kwargs["month"] == 4
    assert match.kwargs["day"] == 12


def test_path_lookup_with_should_redirect(router):
    match = router.match("/articles/2015/04/12")
    assert match.handler_name == "articles-year-month-day"
    assert match.should_redirect
    assert match.redirect_to == "/articles/2015/04/12/"


def test_match_home_undifferently(router):
    match = router.match("/")
    assert match.handler_name == "home"
    assert not match.should_redirect
    assert match.redirect_to is None

    match = router.match("")
    assert match.handler_name == "home"
    assert not match.should_redirect


def test_path_lookup_with_redirect():
    routes = (route(""), route("home/", lambda: None, name="_home"))
    router = Router(routes, append_slash=False)
    match = router.match("home")
    assert not match.should_redirect
    match = router.match("home/")
    assert match.should_redirect
    assert str(match.node) == "home/"
    assert match.redirect_to == "home"

    assert router.find("_home") == "/home"


def test_path_resolution_with_multiple_parameter(router):
    kwargs = {
        "year": 2020,
        "month": 1,
        "day": 30,
    }
    path = router.find("articles-year-month-day", **kwargs)
    assert path == "/articles/2020/1/30/"


def test_path_resolution_without_enough_kw(router):
    kwargs = {
        "year": 2020,
        "month": 1,
    }
    path = router.find("articles-year-month-day", **kwargs)
    assert path is None


def test_path_resolution_with_extra_kw(router):
    kwargs = {
        "year": 2020,
        "month": 1,
        "day": 30,
        "extra": 2,
    }
    path = router.find("articles-year-month-day", **kwargs)
    assert path is None


def test_path_resolution_with_multiple_parameter_refuse(router):
    path = router.find("articles-year-month-day", year="year")
    assert path is None


def test_path_lookup_with_inclusion(router):
    match = router.match("/articles/categories/sport/newest/")
    assert match.handler_name == "newest-in-category"


def test_path_lookup_with_double_inclusion(router):
    match = router.match("/articles/2010/popular/")
    assert match.handler_name == "popular-articles"
    assert not match.should_redirect


def test_path_lookup_with_empty_handler(router):
    match = router.match("/users/extra")
    assert match.handler_name == "users-extra"
    assert match.should_redirect


def test_path_lookup_with_slug(router):
    match = router.match("/users/slug-123/")
    assert match.handler_name == "users-slug"
    assert match.kwargs == {}


def test_path_lookup_after_regex(router):
    match = router.match("/whatever/catch/")
    assert match.handler_name == "catchall"
    assert match.kwargs == {"catched": "whatever"}


def test_find_with_regex(router):
    path = router.find("catchall", catched="whatever")
    assert path == "/whatever/catch/"


def test_find_with_regex_no_kwargs(router):
    path = router.find("catchall")
    assert path == "/<re:(?P<catched>^[a-z]*$)>/catch/"


def test_find_with_regex_extra_kwargs(router):
    path = router.find("catchall", catched="whatever", foo="bar")
    assert path is None


def test_find_int(router):
    path = router.find("int", id=5)
    assert path == "/int/5/"


def test_unknown_converter():
    with pytest.raises(UnknownConverter):
        route("<lang>/<route:url>/")


def test_routes_without_empty_path():
    routes = (route("home/"),)
    expected = "First route must be '' or '/'."
    with pytest.raises(RouterConfigurationError, match=expected):
        Router(routes)


def test_path_resolution_with_multiple_parameters(router):
    path = router.find("articles-month")
    assert path is None


def test_match_empty_view(router):
    match = router.match("users/")
    assert match is NoMatch


def test_already_registered_path():
    expected = "A node matching 'home' already exists at this level of the tree."
    with pytest.raises(RouterConfigurationError, match=expected):
        Router([route(""), route("home/"), route("home/about")])


def test_initialize_router_with_empty_routes():
    expected = "Trying to initialize router with empty routes."
    with pytest.raises(RouterConfigurationError, match=expected):
        Router([])
