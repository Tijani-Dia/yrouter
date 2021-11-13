from yrouter import Router, route


def test_find_already_registered_name():
    def handler():
        pass

    name = "duplicate"
    router = Router(
        (
            route("", name=name),
            route("duplicate/<int:id>/", handler, name=name),
        )
    )
    assert router.find(name) == "/"
    assert router.find(name, id=5) == "/duplicate/5/"
