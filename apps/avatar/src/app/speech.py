"""Speech token broker for browser-based avatar sessions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx
from azure.identity.aio import DefaultAzureCredential


@dataclass(frozen=True)
class SpeechSession:
    """Container for Speech SDK and avatar relay auth payloads."""

    authorization_token: str
    region: str
    expires_on: int
    relay: dict[str, Any]


class SpeechTokenBroker:
    """Builds AAD-backed Speech authorization payloads for browser clients."""

    def __init__(self, resource_id: str, region: str) -> None:
        self._resource_id = resource_id
        self._region = region

    async def create_session(self) -> SpeechSession:
        async with DefaultAzureCredential() as credential:
            token = await credential.get_token("https://cognitiveservices.azure.com/.default")

        authorization_token = f"aad#{self._resource_id}#{token.token}"
        relay_url = f"https://{self._region}.tts.speech.microsoft.com/cognitiveservices/avatar/relay/token/v1"

        async with httpx.AsyncClient(timeout=20) as client:
            relay_response = await client.get(
                relay_url,
                headers={"Authorization": f"Bearer {authorization_token}"},
            )
            relay_response.raise_for_status()
            relay_body = relay_response.json()

        return SpeechSession(
            authorization_token=authorization_token,
            region=self._region,
            expires_on=token.expires_on,
            relay=relay_body,
        )
