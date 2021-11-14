from typing import Any, Dict, Optional

from .route_node import RouteNode


class Match:
    __slots__ = ("node", "kwargs")

    def __init__(self, node: Optional[RouteNode], kwargs: Optional[dict]) -> None:
        self.node = node
        self.kwargs = kwargs


class FullMatch(Match):
    __slots__ = ("should_redirect", "redirect_to")

    def __init__(
        self,
        node: RouteNode,
        kwargs: Dict[str, Any],
        should_redirect: bool,
        redirect_to: Optional[str] = None,
    ) -> None:
        super().__init__(node, kwargs)
        self.should_redirect = should_redirect
        self.redirect_to = redirect_to

    @property
    def handler(self):
        return self.node.handler

    @property
    def handler_name(self):
        return self.node.name

    def __repr__(self):
        handler_name = self.handler_name if self.handler_name else self.handler.__name__
        return (
            f"<FullMatch: handler={handler_name}, "
            f"kwargs={self.kwargs}, should_redirect={self.should_redirect}>"
        )


class _NoMatch(Match):
    def __repr__(self):
        return "<NoMatch>"


NoMatch = _NoMatch(None, None)
