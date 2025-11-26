"""
Unit tests for retry utilities.
"""

import pytest

from app.services.retry import create_retry_decorator


def test_retry_decorator_success() -> None:
    """Test retry decorator with successful call."""
    call_count = 0

    @create_retry_decorator(max_attempts=3, min_wait=0.01, max_wait=0.1)
    def successful_function() -> str:
        nonlocal call_count
        call_count += 1
        return "success"

    result = successful_function()
    assert result == "success"
    assert call_count == 1


def test_retry_decorator_retry_then_success() -> None:
    """Test retry decorator with retries before success."""
    call_count = 0

    @create_retry_decorator(max_attempts=3, min_wait=0.01, max_wait=0.1)
    def flaky_function() -> str:
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError("Temporary error")
        return "success"

    result = flaky_function()
    assert result == "success"
    assert call_count == 3


def test_retry_decorator_max_attempts_exceeded() -> None:
    """Test retry decorator when max attempts exceeded."""
    call_count = 0

    @create_retry_decorator(max_attempts=3, min_wait=0.01, max_wait=0.1)
    def failing_function() -> str:
        nonlocal call_count
        call_count += 1
        raise ValueError("Persistent error")

    with pytest.raises(ValueError, match="Persistent error"):
        failing_function()

    assert call_count == 3


def test_retry_decorator_specific_exception() -> None:
    """Test retry decorator with specific exception type."""

    @create_retry_decorator(max_attempts=3, min_wait=0.01, max_wait=0.1, exceptions=(ValueError,))
    def specific_error_function() -> str:
        raise TypeError("Wrong error type")

    # Should not retry TypeError since we only specified ValueError
    with pytest.raises(TypeError, match="Wrong error type"):
        specific_error_function()
