import pytest
from typing import Any

from tests.utils import make_dummy_task

@pytest.fixture
def session() -> Any:
    """A dummy “db” session for pure unit tests (no real DB)."""
    return object()

@pytest.fixture
def dummy_task():
    """A fresh DummyTaskModel for each test."""
    return make_dummy_task()
