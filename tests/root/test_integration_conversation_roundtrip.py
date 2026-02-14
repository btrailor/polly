"""
Integration test: conversation sync populates Python buffer; buffer used for context.

Verifies that when messages are synced via POST /polly/conversation/sync, Polly's
conversation_history is set and can be used for compression/context (integration-contracts).
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from interfaces.server import create_app, get_polly


@pytest.fixture
async def client():
    app = create_app()
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_sync_then_conversation_history_used_for_context(client):
    """After sync, polly.conversation_history matches synced messages."""
    polly = get_polly()
    messages = [
        {"role": "user", "content": "What is Python?"},
        {"role": "assistant", "content": "Python is a programming language."},
        {"role": "user", "content": "Give me an example."},
        {"role": "assistant", "content": "print('Hello, world!')"},
    ]
    r = await client.post(
        "/polly/conversation/sync",
        json={"messages": messages, "conversation_id": "roundtrip_1"},
    )
    assert r.status_code == 200
    assert polly.conversation_history is not None
    assert len(polly.conversation_history) == 4
    assert polly.conversation_history[0]["content"] == "What is Python?"
    assert polly.conversation_history[3]["content"] == "print('Hello, world!')"
