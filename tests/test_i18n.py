"""
Tests for Internationalization (i18n) API (Ticket 3.4).
Verifies Vietnamese and English locale dictionary loading and endpoint responses.
"""

import pytest
from fastapi.testclient import TestClient

from src.web.app import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_i18n_vi_strings(client):
    """Verify Vietnamese translations are returned with core UI keys."""
    res = client.get("/api/v2/i18n/vi")
    assert res.status_code == 200
    data = res.json()
    assert data["lang"] == "vi"
    assert data["count"] > 30

    strings = data["strings"]
    assert "app.title" in strings
    assert "nav.chat" in strings
    assert "mode.hybrid" in strings
    assert "chat.refusal" in strings
    assert "status.offline" in strings


def test_i18n_en_strings(client):
    """Verify English translations are returned with core UI keys."""
    res = client.get("/api/v2/i18n/en")
    assert res.status_code == 200
    data = res.json()
    assert data["lang"] == "en"
    assert data["count"] > 30

    strings = data["strings"]
    assert "app.title" in strings
    assert "nav.chat" in strings
    assert "mode.hybrid" in strings
    assert "chat.refusal" in strings
    assert "status.offline" in strings


def test_i18n_invalid_lang_returns_400(client):
    """Verify invalid language code returns 400 Bad Request."""
    res = client.get("/api/v2/i18n/fr")
    assert res.status_code == 400
