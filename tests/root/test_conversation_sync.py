"""Tests for conversation sync endpoint (integration-contracts Task 9)."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from interfaces.server import create_app, get_polly


@pytest.fixture
async def test_client():
    app = create_app()
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_sync_conversation_sets_history(test_client):
    """POST /polly/conversation/sync sets polly.conversation_history from request."""
    polly = get_polly()
    assert isinstance(polly.conversation_history, list)

    messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"},
    ]
    response = await test_client.post(
        "/polly/conversation/sync",
        json={"messages": messages, "conversation_id": "test_conv_1"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "synced"
    assert data.get("message_count") == 2

    assert len(polly.conversation_history) == 2
    assert polly.conversation_history[0]["role"] == "user"
    assert polly.conversation_history[0]["content"] == "Hello"
    assert polly.conversation_history[1]["role"] == "assistant"
    assert polly.conversation_history[1]["content"] == "Hi there!"


@pytest.mark.asyncio
async def test_sync_conversation_empty_clears_buffer(test_client):
    """POST with empty messages clears Python buffer."""
    polly = get_polly()
    polly.conversation_history = [{"role": "user", "content": "x"}, {"role": "assistant", "content": "y"}]

    response = await test_client.post(
        "/polly/conversation/sync",
        json={"messages": []},
    )
    assert response.status_code == 200
    assert response.json().get("message_count") == 0
    assert polly.conversation_history == []
