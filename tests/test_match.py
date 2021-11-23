from yrouter import NoMatch

from . import handlers


def test_match_2020(router):
    match = router.match("/articles/2020/")
    assert match.handler_name == "articles-2020"
    assert match.handler == handlers.handler_2020
    assert match.kwargs == {}


def test_match_named_parameter(router):
    match = router.match("/articles/2015/")
    assert match.handler_name == "articles-year"
    assert match.handler == handlers.year_handler
    assert match.kwargs == {"year": 2015}


def test_match_multiple_parameters(router):
    match = router.match("/articles/2015/04/12/")
    assert match.handler_name == "articles-year-month-day"
    assert match.handler == handlers.day_handler
    assert match.kwargs == {
        "year": 2015,
        "month": 4,
        "day": 12,
    }


def test_match_with_inclusion(router):
    match = router.match("/articles/categories/sport/newest/")
    assert match.handler_name == "newest-in-category"
    assert match.handler == handlers.newest
    assert match.kwargs == {"category": "sport"}


def test_match_with_double_inclusion(router):
    match = router.match("/articles/2010/popular/")
    assert match.handler_name == "popular-articles"
    assert match.handler == handlers.popular_articles
    assert match.kwargs == {"year": 2010}


def test_match_included(router):
    match = router.match("/users/guido")
    assert match.handler_name == "user-details"
    assert match.handler == handlers.users_handler
    assert match.kwargs == {"username": "guido"}


def test_match_with_slug(router):
    match = router.match("/users/slug-123/")
    assert match.handler_name == "users-slug"
    assert match.handler == handlers.home_handler
    assert match.kwargs == {}


def test_match_after_regex(router):
    match = router.match("/whatever/catch/")
    assert match.handler_name == "catchall"
    assert match.handler == handlers.catchall
    assert match.kwargs == {"catched": "whatever"}


def test_match_with_empty_handler(router):
    match = router.match("/users")
    assert match is NoMatch


def test_match_bool(router):
    assert router.match("/articles/2015/")
    assert not router.match("/articles/year-2015/")
