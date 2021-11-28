from tests.handlers import (
    articles_handler,
    catchall,
    home_handler,
    int_handler,
    uuid_handler,
)
from yrouter import route

from .article_routes import routes as article_routes
from .user_routes import routes as user_routes

routes = (
    route("/", home_handler, name="home"),
    route(
        "articles/",
        articles_handler,
        name="articles_routes",
        subroutes=article_routes,
    ),
    route("users/", name="users_routes", subroutes=user_routes),
    route("int/<int:id>", int_handler, name="int"),
    route("items/<uuid:id>", uuid_handler, name="items"),
    route("<re:(?P<catched>^[a-z]*$)>/catch/", catchall, name="catchall"),
)

__all__ = ["routes"]
