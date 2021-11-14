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
            route("<re:(?P<title>^[a-z0-9]+(?:-[a-z0-9]+)*)$>", handler, name="article"),
        )),
    )
>>> router = Router(routes)
>>> router.display()
/
    users/
        <int:id>/
    articles/
        <str:category>/
        <re:(?P<title>^[a-z0-9]+(?:-[a-z0-9]+)*)$>/
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

There is an exception for routes with regex converters that will return the initial path if no keyword arguments is provided:

```python
>>> router.find("article")
'/articles/<re:(?P<title>^[a-z0-9]+(?:-[a-z0-9]+)*)$>/'
```

It behaves similarly to other routes however when keyword arguments are provided:

```python
>>> router.find("article", title="hello-world")
'/articles/hello-world/'
>>> router.find("article", title="hello-world", foo="bar")
```

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

### `ExactConverter`

A converter that matches an exact description.

```python
>>> converter = ExactConverter(description="match-me")
>>> converter.accepts("match-me")
(True, {})
>>> converter.accepts("anything-else")
(False, {})
```

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

The empty route equivalently matches the empty string "" and "/":

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
    route("", handler, name="home:index"),
    route("users/", handler, name="users:index"),
    route("users/<int:id>", handler, name="users:details"),
)
>>> router = Router(routes)
Traceback (most recent call last):
...
yrouter.exceptions.RouterConfigurationError: A node matching 'users' already exists at this level of the tree.
```

Do this instead:

```python
 >>> routes = (
    route("", handler, name="home:index"),
    route("users/", handler, name="users:index", subroutes = (
        route("<int:id>", handler, name="users:details"),
    )),
)
```

The `users:index` route will still be matched, as long as it has a handler attached to it.

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

### Set the first `route` of a router to anything other than the empty path

The first `route` must be the empty `route` described by the empty string "" or "/":

```python
>>> Router((route("home/"),))
Traceback (most recent call last):
...
yrouter.exceptions.RouterConfigurationError: First route must be '' or '/'.
```

## Integration with other libraries

The idea of building `yrouter` came from [this feature request in the websockets library](https://github.com/aaugustin/websockets/issues/311). As such, [`yrouter-websockets`](https://github.com/Tijani-Dia/yrouter-websockets) is a routing package for the `websockets` library based on `yrouter`.

## Benchmark

You can find a comparison of `yrouter` and some other routing modules in [`yrouter-bench`](https://github.com/Tijani-Dia/yrouter-bench).
