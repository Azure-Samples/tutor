from __future__ import annotations

import json
import logging
import time
from typing import Any

from azure.cosmos import exceptions
from tutor_lib.agents import AgentInvocationRequest, AgentReference, FoundryAgentFacade

from app.config import AvatarSettings
from app.cosmos import CosmosCRUD
from app.prompts import SIMULATION_PROMPT
from app.schemas import ChatResponse

logger = logging.getLogger(__name__)


class AvatarChat:
    """Orchestrates avatar conversations backed by Azure AI chat completions."""

    def __init__(
        self,
        *,
        settings: AvatarSettings,
        case_repository: CosmosCRUD,
        agent_facade: FoundryAgentFacade | None = None,
    ) -> None:
        self._settings = settings
        self._case_repository = case_repository
        self._agent_facade = agent_facade or FoundryAgentFacade(settings.azure_ai.project_endpoint)
        self._case_cache: dict[str, dict[str, Any]] = {}

    async def respond(self, prompt_data: ChatResponse) -> str:
        """Return the avatar response for the supplied prompt payload."""

        start_time = time.time()
        case = await self._resolve_case(prompt_data.case_id)
        response = await self._evaluate(case, prompt_data)
        logger.info("Avatar response produced in %.2fs", time.time() - start_time)
        return response

    async def _resolve_case(self, case_id: str) -> dict[str, Any]:
        if cached := self._case_cache.get(case_id):
            return cached
        try:
            case = await self._case_repository.read_item(case_id)
        except exceptions.CosmosResourceNotFoundError as exc:  # pragma: no cover - network guard
            raise ValueError(f"Case with id {case_id} not found") from exc
        self._case_cache[case_id] = case
        return case

    async def _evaluate(self, avatar_data: dict[str, Any], prompt_data: ChatResponse) -> str:
        history_messages = self._coerce_history(prompt_data.chat_history)
        history_text = self._history_as_text(history_messages)

        system_message = SIMULATION_PROMPT.safe_substitute(
            name=avatar_data.get("name", ""),
            profile=json.dumps(avatar_data.get("profile", {}), ensure_ascii=False),
            role=avatar_data.get("profile", {}).get("role", avatar_data.get("role", "")),
            steps=json.dumps(avatar_data.get("steps", []), ensure_ascii=False),
            case=json.dumps(avatar_data.get("role", ""), ensure_ascii=False),
            previous_chat=history_text or "No prior conversation.",
        )

        request = AgentInvocationRequest(
            agent=AgentReference(
                agent_name=f"avatar-{avatar_data.get('id', prompt_data.case_id)}",
                agent_version="current",
                model_name=self._settings.azure_ai.default_deployment,
            ),
            input=prompt_data.prompt,
            context={"case_id": prompt_data.case_id},
            instructions=system_message,
            temperature=self._settings.azure_ai.temperature,
            store=False,
        )

        response = await self._agent_facade.invoke(request)

        logger.debug("Avatar service received response: %s", response)
        return response.output_text

    def _coerce_history(self, history: Any) -> list[dict[str, str]]:
        if history is None:
            return []
        parsed = history
        if isinstance(history, str):
            try:
                parsed = json.loads(history)
            except json.JSONDecodeError:
                logger.debug("Failed to parse chat history string; ignoring")
                return []
        if not isinstance(parsed, list):
            return []

        formatted: list[dict[str, str]] = []
        for message in parsed:
            if not isinstance(message, dict):
                continue
            if "assistant" in message:
                formatted.append({"role": "assistant", "content": str(message["assistant"])})
            elif "system" in message:
                formatted.append({"role": "system", "content": str(message["system"])})
            elif "user" in message:
                formatted.append({"role": "user", "content": str(message["user"])})
        return formatted

    def _history_as_text(self, history: list[dict[str, str]]) -> str:
        if not history:
            return ""
        return "\n".join(f"{entry['role'].title()}: {entry['content']}" for entry in history)

def build_avatar_chat(settings: AvatarSettings, case_repository: CosmosCRUD) -> AvatarChat:
    """Factory to create an `AvatarChat` instance for FastAPI wiring."""

    return AvatarChat(settings=settings, case_repository=case_repository)
