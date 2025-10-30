"""
LLM instrumentation utilities.

Provides a thin wrapper around the Google ADK LiteLlm model that records token
usage for each request via the telemetry spine. This allows downstream
components to audit prompt/response spend without modifying third-party
packages.
"""

from __future__ import annotations

import uuid
from typing import AsyncGenerator

from google.adk.models.lite_llm import LiteLlm
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from pydantic import PrivateAttr

from agent.core.telemetry import get_telemetry


class TelemetryLiteLlm(LiteLlm):
    """LiteLlm wrapper that records token usage metrics."""

    # Use PrivateAttr because LiteLlm derives from pydantic.BaseModel, which only
    # preserves declared fields.
    _telemetry = PrivateAttr(default_factory=get_telemetry)

    async def generate_content_async(
        self, llm_request: LlmRequest, stream: bool = False
    ) -> AsyncGenerator[LlmResponse, None]:
        request_id = uuid.uuid4().hex
        self._telemetry.log_event(
            "llm.request",
            request_id=request_id,
            model=self.model,
            stream=stream,
            message_count=len(llm_request.contents),
        )

        usage_logged = False

        async for response in super().generate_content_async(
            llm_request, stream=stream
        ):
            usage = getattr(response, "usage_metadata", None)
            if usage and not usage_logged:
                self._telemetry.log_event(
                    "llm.token_usage",
                    request_id=request_id,
                    model=self.model,
                    stream=stream,
                    prompt_tokens=getattr(usage, "prompt_token_count", None),
                    completion_tokens=getattr(
                        usage, "candidates_token_count", None
                    ),
                    total_tokens=getattr(usage, "total_token_count", None),
                )
                usage_logged = True
            yield response

        if not usage_logged:
            self._telemetry.log_event(
                "llm.token_usage_missing",
                request_id=request_id,
                model=self.model,
                stream=stream,
                reason="usage_metadata_unavailable",
                message_count=len(llm_request.contents),
            )
