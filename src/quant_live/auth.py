"""Minimal token refresh helper."""

from __future__ import annotations

from base64 import b64encode
from typing import Dict, Optional

import requests

from quant_live.config import Settings


def refresh_access_token(
    settings: Settings,
    session: Optional[requests.Session] = None,
) -> Dict[str, object]:
    """Exchange a refresh token for a fresh access token using standard OAuth fields."""
    if not settings.refresh_token:
        raise ValueError("SCHWAB_REFRESH_TOKEN is required to refresh the access token")
    if not settings.app_key or not settings.app_secret:
        raise ValueError("SCHWAB_APP_KEY and SCHWAB_APP_SECRET are required to refresh the access token")

    client = session or requests.Session()
    basic = b64encode(f"{settings.app_key}:{settings.app_secret}".encode("utf-8")).decode("ascii")
    response = client.post(
        settings.token_url,
        headers={
            "Authorization": f"Basic {basic}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        },
        data={
            "grant_type": "refresh_token",
            "refresh_token": settings.refresh_token,
        },
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValueError("expected token refresh response to be a JSON object")
    return payload
