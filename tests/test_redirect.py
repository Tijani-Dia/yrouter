from yrouter import NoMatch, Router, route


def test_match_find_append_slash_true(router):
    match = router.match("/articles/2015/04/12")

    assert match.handler_name == "articles-year-month-day"
    assert match.should_redirect
    assert match.redirect_to == "/articles/2015/04/12/"

    match = router.match("/articles/2015/04/12/")

    assert match.handler_name == "articles-year-month-day"
    assert not match.should_redirect
    assert match.redirect_to is None

    found = router.find("articles-year-month-day", year=2015, month=4, day=12)
    assert found == "/articles/2015/4/12/"


def test_match_find_append_slash_false():
    routes = (route(""), route("home/", lambda: None, name="_home"))
    router = Router(routes, append_slash=False)

    match = router.match("home")
    assert match is not NoMatch
    assert not match.should_redirect

    match = router.match("home/")
    assert match is not NoMatch
    assert match.should_redirect
    assert match.redirect_to == "home"

    assert router.find("_home") == "/home"
