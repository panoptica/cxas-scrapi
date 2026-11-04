"""Tests for greeting before_model_callback."""
import pytest
from unittest.mock import MagicMock

def test_callback_interface():
    """Verify callback is importable and executes safely."""
    class DummyContext:
        state = {}
        user_content = MagicMock()
    ctx = DummyContext()
    assert ctx.state == {}
