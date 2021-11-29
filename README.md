<p align="center">
<a href="https://github.com/tijani-dia/yrouter/actions/workflows/test.yml">
    <img src="https://github.com/tijani-dia/yrouter/actions/workflows/test.yml/badge.svg"/>
</a>
<a href="https://codecov.io/gh/Tijani-Dia/yrouter">
    <img src="https://codecov.io/gh/Tijani-Dia/yrouter/branch/main/graph/badge.svg?token=MKJ71ZJE67"/>
</a>
<a href="https://pypi.org/project/yrouter/">
    <img src="https://badge.fury.io/py/yrouter.svg" alt="Package version">
</a>
<a href="https://opensource.org/licenses/BSD-3-Clause">
    <img src="https://img.shields.io/badge/license-BSD-blue.svg"/>
</a>
</p>

# Yrouter

Yrouter is a framework-agnostic URL routing package focused on simplicity and performance.

## `Router` class

Given a sequence of `route` objects, the `Router` class builds a tree out of it.

The mapping `routes -> tree` is important to bear in mind when building routes with `yrouter` (More on this later).

The empty route is the root of the tree and the remaining routes are its children.
Let's see an example:

```python
>>> handler = lambda : None
>>> routes = (
        route("", handler, name="index"),
        route("users", handler, name="users", subroutes = (
            route("<int:id>", handler, name="user-details"),
        )),
        route("articles", subroutes = (
            route("<str:category>", handler, name="category"),
            route("<slug:title>", handler, name="article"),
        )),
    )
>>> router = Router(routes)
>>> router.display()
/
    users/
        <int:id>/
    articles/
        <str:category>/
        <slug:title>/
```

### Matching a handler given a path

We can now match URL paths against our router.

```python
>>> router.match("/")
<FullMatch: handler=index, kwargs={}, should_redirect=False>
>>> router.match("users/66/")
<FullMatch: handler=user-details, kwargs={'id': 66}, should_redirect=False>
>>> router.match("articles/tech/")
<FullMatch: handler=category, kwargs={'category': 'tech'}, should_redirect=False>
>>> router.match("articles/hello-world/")
<FullMatch: handler=article, kwargs={'title': 'hello-world'}, should_redirect=False>
```

We can match the `/users/` path but not the `/articles/` path since the latter doesn't have a handler attached to it:

```python
>>> router.match("users/")
<FullMatch: handler=users, kwargs={}, should_redirect=False>
>>> router.match("articles/")
<NoMatch>
```

### Finding a path given a handler name

We can also go in the opposite way: find a path given a handler name and eventual keyword arguments.

```python
>>> router.find("index")
'/'
>>> router.find("user-details", id=66)
'/users/66/'
>>> router.find("category", category="tech")
'/articles/tech/'
```

If given an invalid handler name or missing/extra keywords arguments for the route being searched, the find method returns None.

```python
>>> router.find("something")
>>> router.find("user-details")
>>> router.find("category", category="tech", foo="bar")
```

There is an exception for routes with regex converters that will return the initial path if no keyword arguments is provided. They behave similarly to other routes however when keyword arguments are provided.

## `RouteNode` and `route`

When the `router` builds up a tree out of `route` objects, it creates a `RouteNode` for each component in the `route` being described.

```python
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
```

A `RouteNode` is primarily described by its `converter`.
The job of a `converter` is to find if a given value can be accepted by the `RouteNode` it is attached to:

Here is what happens when we try to match `authors/23/some-title` against the above route:

- First, the path is split like this:

```python
["authors", "23", "some-title"]
```

- Then, we try to match `authors` with the first `RouteNode` converter --> `ExactConverter` --> accepts.

- Match `23` with the next node's converter in the tree --> `IntConverter` --> accepts.

- Match `some-title` with the next node's converter --> `StringConverter` --> refuses.

- The last converter refuses `some-title` since it only matches alphabetic characters ==> return `NoMatch`

## Converters

The converters provided by default are:

### `IntConverter`

A converter that matches positive integers.

```python
>>> converter = IntConverter(description="<int:id>", identifier="id")
>>> converter.accepts("100")
(True, {'id': 100})
>>> converter.accepts("0")
(True, {'id': 0})
>>> converter.accepts("1.0")
(False, {})
>>> converter.accepts("-1")
(False, {})
>>> converter.accepts("hello-world")
(False, {})
```

### `StringConverter`

A converter that only matches alphabetic characters.

```python
>>> converter = StringConverter(description="<str:string>", identifier="string")
>>> converter.accepts("hello")
(True, {'string': 'hello'})
>>> converter.accepts("ABC")
(True, {'string': 'ABC'})
>>> converter.accepts("1")
(False, {})
>>> converter.accepts("hello-world")
(False, {})
```

### `SlugConverter`

A converter that matches slugs.

```python
>>> converter = SlugConverter("<slug:slug>", "slug")
>>> converter.accepts("a-slug")
(True, {'slug': 'a-slug'})
>>> converter.accepts("1-random_slug")
(True, {'slug': '1-random_slug'})
>>> converter.accepts("hello")
(True, {'slug': 'hello'})
>>> converter.accepts("hi@hi")
(True, {'slug': 'hi@hi'})
```

### `UUIDConverter`

A converter that matches UUIDs.

```python
>>> converter = UUIDConverter(description="<uuid:uuid>", identifier="uuid_identifier")
>>> converter.accepts("20bfa7b2-50a5-11ec-83dc-479fd603abba")
(True, {'uuid_identifier': '20bfa7b2-50a5-11ec-83dc-479fd603abba'})
>>> converter.accepts("1-2-3-4")
(False, {})
```

### `PathConverter`

A converter that matches arbitrary paths.

```python
>>> converter = PathConverter(description="<path:path>", identifier="path")
>>> converter.accepts("images/original/hero.jpg")
(True, {'path': 'images/original/hero.jpg'})
>>> converter.accepts("1-2/three/_4")
(True, {'path': '1-2/three/_4'})
```

### `RegexConverter`

A converter that matches regular expressions.

```python
>>> converter = RegexConverter("<re:(?P<match>^[a-z]*$)>", "(?P<match>^[a-z]*$)")
>>> converter.accepts("whatever")
(True, {'match': 'whatever'})
>>> converter.accepts("a-b")
(False, {})
```

Since `yrouter` represent routes by delimiting them with the slash (`/`) character, a slash isn't allowed in regex identifiers!

### Adding a converter

You can easily add a new converter to `yrouter`.

A converter has a description and optionally an identifier. The latter represent the keyword argument when matching against a route. If `<int:id>` is the description of a converter, then `id` is the identifier.

To register a new converter, we need to subclass `AbstractConverter` and implement the `accepts` method.
This method should return `(True, matched_kwargs)` if it accepts a given value or `REFUSED` else.

```python
from yrouter import AbstractConverter, REFUSED

class MyCustomConverter(AbstractConverter, converter_name="custom"):
    def accepts(self, value):
        return (True, {self.identifier: value}) if value.isidentifier() else REFUSED
```

This converter will only accept strings that are considered as valid identifiers in Python.

```python
>>> converter = MyCustomConverter(description="<custom:identifier>", identifier="identifier")
>>> converter.accepts("valid_identifier")
(True, {"identifier": "valid_identifier})
>>> converter.accepts("invalid-identifier")
(False, {})
```

To use your converter in a route:

```python
>>> route("<custom:my_identifier>/, handler, name='custom-route'")
```

You need to make sure that the code of the converter is read before attempting to use it in a route.

Ideally, you'd write the code of your converter right above the routes that use it.

## Trailing slash behavior

With `yrouter`, you either choose if all your URLs have a trailing slash or if they all don't.

**This is important**; you can't have, let's say `/users/66` and `users/66/`.

For more details about this, see: [To slash or no to slash](https://developers.google.com/search/blog/2010/04/to-slash-or-not-to-slash).

By default, a slash is appended to all URLs which means that if a user requests a resource like `/users/66`, our above router will match but will indicate that the user should be redirected; in this case to `users/66/`:

```python
>>> router.match("users/66")
<FullMatch: handler=user-details, kwargs={'id': 66}, should_redirect=True>
```

As such, if you don't want to append a slash to your URLs, you'd define your router with `append_slash=False`:

```python
>>> no_slash_router = Router(routes, append_slash=False)
>>> no_slash_router.match("users/66")
<FullMatch: handler=user-details, kwargs={'id': 66}, should_redirect=False>
>>> no_slash_router.match("users/66/")
<FullMatch: handler=user-details, kwargs={'id': 66}, should_redirect=True>
```

It also works when we try to find the path for a given handler name:

```python
>>> no_slash_router.find("category", category="business")
'/articles/business'
```

The empty route equivalently matches the empty string `''` and `/`:

```python
>>> router.match("")
<FullMatch: handler=index, kwargs={}, should_redirect=False>
>>> router.match("/")
<FullMatch: handler=index, kwargs={}, should_redirect=False>
>>> no_slash_router.match("")
<FullMatch: handler=index, kwargs={}, should_redirect=False>
>>> no_slash_router.match("/")
<FullMatch: handler=index, kwargs={}, should_redirect=False>
```

## Extra considerations

### Routes starting with the same prefix at the same level

The tree structure of the routes assumes that each node's children is described uniquely. Therefore, you can't write something like this:

```python
 >>> routes = (
    route("", handler, name="home"),
    route("users/", handler, name="users"),
    route("users/<int:id>", handler, name="users-details"),
)
>>> router = Router(routes)
Traceback (most recent call last):
...
yrouter.exceptions.RouterConfigurationError: A node matching 'users' already exists at this level of the tree.
```

Do this instead:

```python
 >>> routes = (
    route("", handler, name="home"),
    route("users/", handler, name="users", subroutes = (
        route("<int:id>", handler, name="users-details"),
    )),
)
```

The `users` route will still be matched, as long as it has a handler attached to it.

### Routes with similar names

It's not recommended to have routes with similar names.

You can distinguish routes from different modules by using the following technique:

```python
>>> routes = (
        route("", handler, name="home:index"),
        route("users", handler, name="users:index", subroutes = (
            route("<int:id>", handler, name="users:details"),
        )),
    )
>>> router = Router(routes)
>>> router.find("home:index")
'/'
>>> router.find("users:index")
'/users/'
>>> router.find("users:details", id=66)
'/users/66/'
```

### First `route` of a router different than the empty path

If the first route isn't the empty route described by the empty string `''` or `'/'`, `yrouter` will automatically create a route for it. It's needed as the root of the router's tree. The empty path won't be matched however:

```python
>>> router = Router([route("home/", handler, name="home")])
>>> router.match("/home/")
<FullMatch: handler=home, kwargs={}, should_redirect=False>
>>> assert not (router.match("") or router.match("/"))
```

## Integration with other libraries

The idea of building `yrouter` came from [this feature request in the websockets library](https://github.com/aaugustin/websockets/issues/311). As such, [`yrouter-websockets`](https://github.com/Tijani-Dia/yrouter-websockets) is a routing package for the `websockets` library based on `yrouter`.

## Installation

Yrouter requires `Python>=3.9`. You can install it from Pypi:

```python
pip install yrouter
```

## Running the tests

`yrouter` has a mix of unit tests and doctests. You can run the test suite with `pytest`.

```shell
cd path/to/yrouter
pytest
```

## Benchmark

You can find a comparison of `yrouter` and some other routing modules in [`yrouter-bench`](https://github.com/Tijani-Dia/yrouter-bench).
