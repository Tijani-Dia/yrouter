import pytest

from yrouter import Router, RouterConfigurationError, route


def test_initialize_router_with_empty_routes():
    expected = "Trying to initialize router with empty routes."
    with pytest.raises(RouterConfigurationError, match=expected):
        Router([])


def test_routes_without_empty_path():
    routes = (route("home/"),)
    expected = "First route must be '' or '/'."
    with pytest.raises(RouterConfigurationError, match=expected):
        Router(routes)


def test_already_registered_path():
    expected = "A node matching 'home' already exists at this level of the tree."
    with pytest.raises(RouterConfigurationError, match=expected):
        Router([route(""), route("home/"), route("home/about")])
