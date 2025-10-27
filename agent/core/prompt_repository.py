"""
Prompt repository service for the Canister agent.

This module centralizes the storage and lifecycle of prompt templates so that
the planner/executor can reason about prompt upgrades just like code changes.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from agent.core.telemetry import get_telemetry

__all__ = [
    "PromptVersion",
    "PromptRecord",
    "PromptRepository",
    "get_prompt_repository",
]


@dataclass
class PromptVersion:
    version_id: str
    content: str
    created_at: str
    author: Optional[str] = None
    status: str = "active"  # active | staged | archived
    metadata: Dict[str, str] = None
    evaluation_report: Dict[str, str] = None

    def to_dict(self) -> Dict[str, any]:
        payload = asdict(self)
        payload["metadata"] = self.metadata or {}
        payload["evaluation_report"] = self.evaluation_report or {}
        return payload

    @classmethod
    def from_dict(cls, data: Dict[str, any]) -> "PromptVersion":
        return cls(
            version_id=data["version_id"],
            content=data["content"],
            created_at=data["created_at"],
            author=data.get("author"),
            status=data.get("status", "active"),
            metadata=data.get("metadata") or {},
            evaluation_report=data.get("evaluation_report") or {},
        )


@dataclass
class PromptRecord:
    prompt_id: str
    description: str
    tags: List[str]
    versions: List[PromptVersion]

    def to_dict(self) -> Dict[str, any]:
        return {
            "prompt_id": self.prompt_id,
            "description": self.description,
            "tags": self.tags,
            "versions": [version.to_dict() for version in self.versions],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, any]) -> "PromptRecord":
        versions = [PromptVersion.from_dict(v) for v in data.get("versions", [])]
        return cls(
            prompt_id=data["prompt_id"],
            description=data.get("description", ""),
            tags=data.get("tags", []),
            versions=versions,
        )


class PromptRepository:
    """Persistent prompt storage with basic versioning."""

    def __init__(self, storage_path: Optional[Path] = None) -> None:
        self.storage_path = storage_path or Path(".agent_state/prompts.json")
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.telemetry = get_telemetry()
        self._prompts: Dict[str, PromptRecord] = {}
        self._load()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def list_prompts(self) -> List[PromptRecord]:
        return list(self._prompts.values())

    def get_prompt(self, prompt_id: str) -> Optional[PromptRecord]:
        return self._prompts.get(prompt_id)

    def get_active_version(self, prompt_id: str) -> Optional[PromptVersion]:
        prompt = self._prompts.get(prompt_id)
        if not prompt:
            return None
        for version in prompt.versions:
            if version.status == "active":
                return version
        return None

    def register_prompt(
        self,
        prompt_id: str,
        description: str,
        content: str,
        *,
        tags: Optional[List[str]] = None,
        author: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> PromptVersion:
        created_at = datetime.utcnow().isoformat()
        version = PromptVersion(
            version_id=str(uuid.uuid4()),
            content=content,
            created_at=created_at,
            author=author,
            status="active",
            metadata=metadata or {},
        )
        record = PromptRecord(
            prompt_id=prompt_id,
            description=description,
            tags=tags or [],
            versions=[version],
        )
        self._prompts[prompt_id] = record
        self._persist()
        self.telemetry.log_event(
            "prompt_repository.register",
            prompt_id=prompt_id,
            version_id=version.version_id,
        )
        return version

    def stage_prompt(
        self,
        prompt_id: str,
        content: str,
        *,
        author: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> PromptVersion:
        record = self._prompts.get(prompt_id)
        if not record:
            raise ValueError(f"Prompt not registered: {prompt_id}")

        created_at = datetime.utcnow().isoformat()
        version = PromptVersion(
            version_id=str(uuid.uuid4()),
            content=content,
            created_at=created_at,
            author=author,
            status="staged",
            metadata=metadata or {},
        )
        record.versions.append(version)
        self._persist()
        self.telemetry.log_event(
            "prompt_repository.stage",
            prompt_id=prompt_id,
            version_id=version.version_id,
        )
        return version

    def promote_prompt(
        self,
        prompt_id: str,
        version_id: str,
        *,
        evaluation_report: Optional[Dict[str, str]] = None,
    ) -> PromptVersion:
        record = self._prompts.get(prompt_id)
        if not record:
            raise ValueError(f"Prompt not registered: {prompt_id}")

        target = None
        for version in record.versions:
            if version.version_id == version_id:
                target = version
                break

        if not target:
            raise ValueError(f"Version {version_id} not found for prompt {prompt_id}")

        for version in record.versions:
            if version.status == "active":
                version.status = "archived"

        target.status = "active"
        if evaluation_report:
            target.evaluation_report = evaluation_report

        self._persist()
        self.telemetry.log_event(
            "prompt_repository.promote",
            prompt_id=prompt_id,
            version_id=target.version_id,
        )
        return target

    def rollback_prompt(self, prompt_id: str) -> Optional[PromptVersion]:
        record = self._prompts.get(prompt_id)
        if not record:
            return None

        active_index = None
        for idx, version in enumerate(record.versions):
            if version.status == "active":
                active_index = idx
                break

        if active_index is None or active_index == 0:
            return record.versions[active_index] if active_index is not None else None

        record.versions[active_index].status = "archived"
        previous = record.versions[active_index - 1]
        previous.status = "active"
        self._persist()

        self.telemetry.log_event(
            "prompt_repository.rollback",
            prompt_id=prompt_id,
            version_id=previous.version_id,
        )
        return previous

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    def _load(self) -> None:
        if not self.storage_path.exists():
            return
        try:
            data = json.loads(self.storage_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return

        for record_data in data.get("prompts", []):
            record = PromptRecord.from_dict(record_data)
            self._prompts[record.prompt_id] = record

    def _persist(self) -> None:
        payload = {
            "prompts": [record.to_dict() for record in self._prompts.values()],
        }
        self.storage_path.write_text(
            json.dumps(payload, indent=2), encoding="utf-8"
        )


_global_prompt_repository: Optional[PromptRepository] = None


def get_prompt_repository() -> PromptRepository:
    global _global_prompt_repository
    if _global_prompt_repository is None:
        _global_prompt_repository = PromptRepository()
    return _global_prompt_repository

