"""LMS adapter abstractions and basic provider stubs."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import httpx


@dataclass
class SyncResult:
    adapter: str
    courses: int
    students: int
    assignments: int
    scores_pushed: int


class BaseLMSAdapter(ABC):
    provider: str

    @abstractmethod
    async def get_courses(self) -> list[dict[str, str]]:
        raise NotImplementedError

    @abstractmethod
    async def get_students(self) -> list[dict[str, str]]:
        raise NotImplementedError

    @abstractmethod
    async def get_assignments(self) -> list[dict[str, str]]:
        raise NotImplementedError

    @abstractmethod
    async def push_scores(self, scores: list[dict[str, str]]) -> int:
        raise NotImplementedError


class MoodleAdapter(BaseLMSAdapter):
    provider = "moodle"

    def __init__(self, *, base_url: str = "", token: str = "") -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token

    async def _get_json(self, path: str) -> list[dict[str, str]]:
        if not self.base_url or not self.token:
            return []
        url = f"{self.base_url}{path}"
        headers = {"Authorization": f"Bearer {self.token}"}
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            payload = response.json()
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
        return []

    async def get_courses(self) -> list[dict[str, str]]:
        rows = await self._get_json("/api/v1/courses")
        if rows:
            return rows
        return [{"id": "course-m1", "name": "Writing Fundamentals"}]

    async def get_students(self) -> list[dict[str, str]]:
        rows = await self._get_json("/api/v1/students")
        if rows:
            return rows
        return [{"id": "student-m1", "name": "Student Moodle"}]

    async def get_assignments(self) -> list[dict[str, str]]:
        rows = await self._get_json("/api/v1/assignments")
        if rows:
            return rows
        return [{"id": "assignment-m1", "title": "Essay Draft 1"}]

    async def push_scores(self, scores: list[dict[str, str]]) -> int:
        return len(scores)


class CanvasAdapter(BaseLMSAdapter):
    provider = "canvas"

    def __init__(self, *, base_url: str = "", token: str = "") -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token

    async def _get_json(self, path: str) -> list[dict[str, str]]:
        if not self.base_url or not self.token:
            return []
        url = f"{self.base_url}{path}"
        headers = {"Authorization": f"Bearer {self.token}"}
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            payload = response.json()
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
        return []

    async def get_courses(self) -> list[dict[str, str]]:
        rows = await self._get_json("/api/v1/courses")
        if rows:
            return rows
        return [{"id": "course-c1", "name": "Advanced Composition"}]

    async def get_students(self) -> list[dict[str, str]]:
        rows = await self._get_json("/api/v1/students")
        if rows:
            return rows
        return [{"id": "student-c1", "name": "Student Canvas"}]

    async def get_assignments(self) -> list[dict[str, str]]:
        rows = await self._get_json("/api/v1/assignments")
        if rows:
            return rows
        return [{"id": "assignment-c1", "title": "Argumentative Essay"}]

    async def push_scores(self, scores: list[dict[str, str]]) -> int:
        return len(scores)
