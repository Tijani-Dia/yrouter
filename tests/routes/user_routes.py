from tests.handlers import home_handler
from yrouter import route

routes = (
    route("extra/", home_handler, name="users-extra"),
    route("<re:^[a-z0-9]+(?:-[a-z0-9]+)*$>", home_handler, name="users-slug"),
)
