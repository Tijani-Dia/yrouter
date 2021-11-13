class Match:
    def __init__(self, node, kwargs):
        self.node = node
        self.kwargs = kwargs

    @property
    def handler(self):
        return self.node.route.handler

    @property
    def handler_name(self):
        return self.node.route.name


class FullMatch(Match):
    def __init__(self, node, kwargs, should_redirect, redirect_to=None):
        super().__init__(node, kwargs)
        self.should_redirect = should_redirect
        self.redirect_to = redirect_to

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
