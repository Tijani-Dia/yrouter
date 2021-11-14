"""
# Router

Given a sequence of route objects, the Router class builds a tree out of it.
The empty route is the root of the tree and the remaining routes are its children.

Let's see an example:
>>> handler = lambda : None
>>> routes = (\
        route("", handler, name="index"),\
        route("users", handler, name="users", subroutes = (\
            route("<int:id>", handler, name="user-details"),\
        )),\
        route("articles", subroutes = (\
            route("<str:category>", handler, name="category"),\
            route("<re:(?P<title>^[a-z0-9]+(?:-[a-z0-9]+)*)$>", handler, name="article"),\
        )),\
    )
>>> router = Router(routes)
>>> router.display()
/
    users/
        <int:id>/
    articles/
        <str:category>/
        <re:(?P<title>^[a-z0-9]+(?:-[a-z0-9]+)*)$>/

We can now match URL paths against our router.
>>> router.match("/")
<FullMatch: handler=index, kwargs={}, should_redirect=False>
>>> router.match("users/66/")
<FullMatch: handler=user-details, kwargs={'id': 66}, should_redirect=False>
>>> router.match("articles/tech/")
<FullMatch: handler=category, kwargs={'category': 'tech'}, should_redirect=False>
>>> router.match("articles/hello-world/")
<FullMatch: handler=article, kwargs={'title': 'hello-world'}, should_redirect=False>

We can match the "/users/" path but not the "/articles/" path since
the latter doesn't have a handler attached to it:
>>> router.match("users/")
<FullMatch: handler=users, kwargs={}, should_redirect=False>
>>> router.match("articles/")
<NoMatch>

We can also go in the opposite way: find a path given a handler name
and eventual keyword arguments.
>>> router.find("index")
'/'
>>> router.find("user-details", id=66)
'/users/66/'
>>> router.find("category", category="tech")
'/articles/tech/'

If given an invalid handler name or missing/extra keywords arguments for
the route being searched, the find method returns None.
>>> router.find("something")
>>> router.find("user-details")
>>> router.find("category", category="tech", foo="bar")

There is an exception for routes with regex converters that will return the initial route 
if no keyword arguments is provided:
>>> router.find("article")
'/articles/<re:(?P<title>^[a-z0-9]+(?:-[a-z0-9]+)*)$>/'

But it behaves similarly to other routes when keyword arguments are provided:
>>> router.find("article", title="hello-world")
'/articles/hello-world/'
>>> router.find("article", title="hello-world", foo="bar")

It is not allowed to initialize a Router with no routes:
>>> Router([])
Traceback (most recent call last):
...
yrouter.exceptions.RouterConfigurationError: Trying to initialize router with empty routes.

Also, the first route must be the empty route described by the empty string "" or "/":
>>> Router((route("home/"),))
Traceback (most recent call last):
...
yrouter.exceptions.RouterConfigurationError: First route must be '' or '/'.

With yrouter, you either choose if all your URLs have a trailing slash or
if they all don't. This is important; you can't have, let's say `/users/66` and `users/66/`.
For more details about this, see:
https://developers.google.com/search/blog/2010/04/to-slash-or-not-to-slash.

By default, a slash is appended to all URLs which means that if a user
requests a resource like `/users/66`, our above router will match but
will indicate that the user should be redirected; in this case to `users/66/:
>>> router.match("users/66")
<FullMatch: handler=user-details, kwargs={'id': 66}, should_redirect=True>

As such, if you don't want to append a slash to your URLs, you'd define your router
with `append_slash=False`:
>>> no_slash_router = Router(routes, append_slash=False)
>>> no_slash_router.match("users/66")
<FullMatch: handler=user-details, kwargs={'id': 66}, should_redirect=False>
>>> no_slash_router.match("users/66/")
<FullMatch: handler=user-details, kwargs={'id': 66}, should_redirect=True>

It also works when we try to find the path for a given handler name:
>>> no_slash_router.find("category", category="business")
'/articles/business'

The empty route equivalently matches the empty string "" and "/":
>>> router.match("")
<FullMatch: handler=index, kwargs={}, should_redirect=False>
>>> router.match("/")
<FullMatch: handler=index, kwargs={}, should_redirect=False>
>>> no_slash_router.match("")
<FullMatch: handler=index, kwargs={}, should_redirect=False>
>>> no_slash_router.match("/")
<FullMatch: handler=index, kwargs={}, should_redirect=False>

It's not recommended to have routes with similar names.

You can distinguish routes from different modules by using the following technique:
>>> routes = (\
        route("", handler, name="home:index"),\
        route("users", handler, name="users:index", subroutes = (\
            route("<int:id>", handler, name="users:details"),\
        )),\
    )
>>> router = Router(routes)
>>> router.find("home:index")
'/'
>>> router.find("users:index")
'/users/'
>>> router.find("users:details", id=66)
'/users/66/'

>>> routes = (\
    route("", handler, name="home:index"),\
    route("users/", handler, name="users:index"),\
    route("users/<int:id>", handler, name="users:details"),\
)
>>> router = Router(routes)
Traceback (most recent call last):
...
yrouter.exceptions.RouterConfigurationError: A node matching 'users' already exists at this level of the tree.

# route & RouteNode

>>> node = route("authors/<int:id>/<str:title>/")
>>> node.display(0)
authors/
    <int:id>/
        <str:title>/
>>> node
<RouteNode: converter=<ExactConverter: description=authors; identifier=None>; handler=None; children=1>
>>> node = node.children[0]
>>> node
<RouteNode: converter=<IntConverter: description=<int:id>; identifier=id>; handler=None; children=1>
>>> node = node.children[0]
>>> node
<RouteNode: converter=<StringConverter: description=<str:title>; identifier=title>; handler=None; children=0>
>>> node.children
[]
"""

from .converters import REFUSED, AbstractConverter
from .exceptions import RouterConfigurationError, UnknownConverter
from .match import NoMatch
from .route import route
from .router import Router

__version__ = "1.0.0"

__all__ = [
    "REFUSED",
    "AbstractConverter",
    "RouterConfigurationError",
    "UnknownConverter",
    "NoMatch",
    "route",
    "Router",
    "__version__",
]
