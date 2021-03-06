import pytest

from yrouter import Router, RouterConfigurationError, route


def test_match_home_undifferently(router):
    match = router.match("/")
    assert match.handler_name == "home"
    assert not match.should_redirect
    assert match.redirect_to is None

    match = router.match("")
    assert match.handler_name == "home"
    assert not match.should_redirect
    assert match.redirect_to is None


def test_initialize_router_with_empty_routes():
    expected = "Trying to initialize router with empty routes."
    with pytest.raises(RouterConfigurationError, match=expected):
        Router([])


def test_empty_route_inserted_for_routes_without_empty_path():
    router = Router([route("home/", lambda: None, name="home")])

    match = router.match("/home/")
    assert match
    assert match.handler_name == "home"
    assert router.find("home") == "/home/"

    # Empty route is inserted but won't match
    assert not router.match("")
    assert not router.match("/")


def test_already_registered_path():
    expected = "A node matching 'home' already exists at this level of the tree."
    with pytest.raises(RouterConfigurationError, match=expected):
        Router([route(""), route("home/"), route("home/about")])
