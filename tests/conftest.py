import pytest

from yrouter import Router

from .routes import routes


@pytest.fixture
def router():
    return Router(routes)
