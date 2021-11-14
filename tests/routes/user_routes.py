from tests.handlers import home_handler, users_handler
from yrouter import route

routes = (
    route("<str:username>/", users_handler, name="user-details"),
    route("<re:^[a-z0-9]+(?:-[a-z0-9]+)*$>", home_handler, name="users-slug"),
)
