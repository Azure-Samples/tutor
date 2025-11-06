from __future__ import annotations

import asyncio
import json
import logging
from functools import partial
from pathlib import Path
import time
from typing import Any, Dict, List

from azure.ai.inference.prompts._patch import PromptTemplate
from azure.ai.projects import AIProjectClient
from azure.cosmos import exceptions
from azure.identity import DefaultAzureCredential

from common.config import TutorSettings
from common.cosmos import CosmosCRUD

from app.schemas import ChatResponse

logger = logging.getLogger(__name__)


class AvatarChat:
    """Orchestrates avatar conversations backed by Azure AI chat completions."""

    def __init__(
        self,
        *,
        settings: TutorSettings,
        case_repository: CosmosCRUD,
        project_client: AIProjectClient | None = None,
    ) -> None:
        self._settings = settings
        self._case_repository = case_repository
        self._project_client = project_client or AIProjectClient(
            endpoint=settings.azure_ai.project_endpoint,
            credential=DefaultAzureCredential(),
        )
        self._chat_client = self._project_client.inference.get_chat_completions_client()
        self._template = PromptTemplate.from_prompty(str(Path(__file__).parent / "prompts" / "simulation.prompty"))
        self._case_cache: Dict[str, Dict[str, Any]] = {}

    async def respond(self, prompt_data: ChatResponse) -> str:
        """Return the avatar response for the supplied prompt payload."""

        start_time = time.time()
        case = await self._resolve_case(prompt_data.case_id)
        response = await self._evaluate(case, prompt_data)
        logger.info("Avatar response produced in %.2fs", time.time() - start_time)
        return response

    async def _resolve_case(self, case_id: str) -> Dict[str, Any]:
        if cached := self._case_cache.get(case_id):
            return cached
        try:
            case = await self._case_repository.read_item(case_id)
        except exceptions.CosmosResourceNotFoundError as exc:  # pragma: no cover - network guard
            raise ValueError(f"Case with id {case_id} not found") from exc
        self._case_cache[case_id] = case
        return case

    async def _evaluate(self, avatar_data: Dict[str, Any], prompt_data: ChatResponse) -> str:
        messages = self._template.create_messages(
            role=avatar_data.get("profile", {}).get("role"),
            name=avatar_data.get("name"),
            profile=json.dumps(avatar_data.get("profile", {})),
            case=avatar_data.get("role"),
            steps=json.dumps(avatar_data.get("steps", [])),
            user_prompt=prompt_data.prompt,
        )

        for entry in self._coerce_history(prompt_data.chat_history):
            messages.append(entry)

        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None,
            partial(
                self._chat_client.complete,
                model=self._settings.azure_ai.default_deployment,
                messages=messages,
                **self._template.parameters,
            ),
        )

        logger.debug("Avatar service received response: %s", response)
        return self._extract_text(response)

    def _coerce_history(self, history: Any) -> List[Dict[str, str]]:
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

        formatted: List[Dict[str, str]] = []
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

    def _extract_text(self, response: Any) -> str:
        if not getattr(response, "choices", None):
            return ""
        message = response.choices[0].message
        content = getattr(message, "content", "")
        if isinstance(content, str):
            return content
        parts: List[str] = []
        for part in content or []:
            if isinstance(part, dict) and "text" in part:
                parts.append(str(part["text"]))
                continue
            text_attr = getattr(part, "text", None)
            if text_attr is not None:
                parts.append(str(text_attr))
                continue
            parts.append(str(part))
        return "".join(parts)


def build_avatar_chat(settings: TutorSettings, case_repository: CosmosCRUD) -> AvatarChat:
    """Factory to create an `AvatarChat` instance for FastAPI wiring."""

    return AvatarChat(settings=settings, case_repository=case_repository)
