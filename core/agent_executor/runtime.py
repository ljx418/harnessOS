"""Governed local Agent executor candidate.

PV20 intentionally supports only explicitly allowlisted execution surfaces.
It does not execute shell, arbitrary filesystem/network calls, durable workflow
mutations, or approval responses directly.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from core.skills.bundled import get_bundled_skills


FORBIDDEN_RAW_TERMS = (
    "raw_prompt",
    "raw prompt",
    "raw_secret",
    "api_key",
    "bearer ",
    "authorization",
    "raw_provider_payload",
    "raw_connector_payload",
)


class GovernedAgentExecutorError(ValueError):
    """Stable PV20 Agent executor validation error."""

    def __init__(self, code: str, message: str, *, reason: str, field: str | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.reason = reason
        self.field = field

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"code": self.code, "message": str(self), "reason": self.reason}
        if self.field:
            payload["field"] = self.field
        return payload


class GovernedAgentExecutor:
    """Execute allowlisted local skill/read-model operations."""

    def __init__(self, *, allowed_skills: set[str] | None = None, allowed_mcp_tools: set[str] | None = None) -> None:
        self.allowed_skills = allowed_skills or {"plan", "review", "diagnose", "test", "simplify"}
        self.allowed_mcp_tools = allowed_mcp_tools or {"data_service_mcp.knowledge_query_v2"}

    def execute_skill(self, *, envelope: dict[str, Any], skill_name: str, input_refs: list[str] | None = None) -> dict[str, Any]:
        """Run a bundled skill contract and return redacted execution evidence."""
        self._validate_envelope(envelope)
        if skill_name not in self.allowed_skills:
            raise GovernedAgentExecutorError("PV20_SKILL_DENIED", "Skill is not allowlisted for PV20-S2.", reason="skill_not_allowlisted", field="skill_name")
        skill = next((item for item in get_bundled_skills() if item.name == skill_name), None)
        if skill is None:
            raise GovernedAgentExecutorError("PV20_SKILL_NOT_FOUND", "Skill was not found in the registry.", reason="skill_not_found", field="skill_name")
        content_hash = hashlib.sha256(skill.content.encode("utf-8")).hexdigest()[:16]
        station_run_id = str(envelope["station_run_id"])
        execution_id = f"pv20-skill-exec-{uuid4().hex[:12]}"
        result = {
            "schema_version": "pv20.agent_skill_execution_result.v1",
            "execution_id": execution_id,
            "execution_envelope_id": envelope["execution_envelope_id"],
            "workflow_instance_id": envelope["workflow_instance_id"],
            "station_run_id": station_run_id,
            "station_id": envelope["station_id"],
            "agent_id": envelope["agent_id"],
            "operation": "agent.skill.execute",
            "status": "completed",
            "skill_call_refs": [f"skill-call://pv20/{station_run_id}/{skill.name}/{execution_id}"],
            "tool_call_refs": [],
            "mcp_call_refs": [],
            "artifact_payload_ref": f"artifact-payload-ref://pv20/{station_run_id}/{execution_id}",
            "input_refs": input_refs or [],
            "skill_ref": f"skill://bundled/{skill.name}",
            "skill_source": skill.source,
            "skill_content_hash": content_hash,
            "summary": f"Executed bundled skill read-model: {skill.name}",
            "created_at": _now_iso(),
            "redaction_status": "redacted",
        }
        self._assert_no_raw(result)
        return result

    def execute_tool(self, *, envelope: dict[str, Any], tool_name: str, tool_input_refs: list[str]) -> dict[str, Any]:
        """Run an allowlisted read-only tool contract."""
        self._validate_envelope(envelope)
        if tool_name != "artifact.metadata.read":
            raise GovernedAgentExecutorError("PV20_TOOL_DENIED", "Tool is not allowlisted for PV20-S3A.", reason="tool_not_allowlisted", field="tool_name")
        if not tool_input_refs:
            raise GovernedAgentExecutorError("PV20_TOOL_INPUT_MISSING", "Tool execution requires at least one artifact metadata ref.", reason="missing_tool_input", field="tool_input_refs")
        station_run_id = str(envelope["station_run_id"])
        execution_id = f"pv20-tool-exec-{uuid4().hex[:12]}"
        result = {
            "schema_version": "pv20.agent_tool_execution_result.v1",
            "execution_id": execution_id,
            "execution_envelope_id": envelope["execution_envelope_id"],
            "workflow_instance_id": envelope["workflow_instance_id"],
            "station_run_id": station_run_id,
            "station_id": envelope["station_id"],
            "agent_id": envelope["agent_id"],
            "operation": "agent.tool.execute",
            "status": "completed",
            "tool_call_refs": [f"tool-call://pv20/{station_run_id}/{tool_name}/{execution_id}"],
            "skill_call_refs": [],
            "mcp_call_refs": [],
            "tool_name": tool_name,
            "tool_input_refs": tool_input_refs,
            "summary": "Executed read-only artifact metadata tool.",
            "created_at": _now_iso(),
            "redaction_status": "redacted",
        }
        self._assert_no_raw(result)
        return result

    def execute_mcp(
        self,
        *,
        envelope: dict[str, Any],
        connector_id: str,
        tool_name: str,
        connector_result: dict[str, Any],
        approval_refs: list[str],
    ) -> dict[str, Any]:
        """Build redacted evidence for an allowlisted MCP connector execution."""
        self._validate_envelope(envelope)
        connector_tool = f"{connector_id}.{tool_name}"
        if connector_tool not in self.allowed_mcp_tools:
            raise GovernedAgentExecutorError("PV20_MCP_DENIED", "MCP tool is not allowlisted for PV20-S3B.", reason="mcp_not_allowlisted", field="connector_id")
        job = connector_result.get("job") if isinstance(connector_result.get("job"), dict) else {}
        artifact = connector_result.get("artifact") if isinstance(connector_result.get("artifact"), dict) else {}
        job_id = str(job.get("job_id") or "").strip()
        artifact_id = str(artifact.get("artifact_id") or "").strip()
        if str(job.get("status") or "") != "completed" or not job_id or not artifact_id:
            raise GovernedAgentExecutorError("PV20_MCP_INCOMPLETE", "MCP connector execution did not complete with an artifact.", reason="mcp_execution_incomplete")
        station_run_id = str(envelope["station_run_id"])
        execution_id = f"pv20-mcp-exec-{uuid4().hex[:12]}"
        result = {
            "schema_version": "pv20.agent_mcp_execution_result.v1",
            "execution_id": execution_id,
            "execution_envelope_id": envelope["execution_envelope_id"],
            "workflow_instance_id": envelope["workflow_instance_id"],
            "station_run_id": station_run_id,
            "station_id": envelope["station_id"],
            "agent_id": envelope["agent_id"],
            "operation": "agent.mcp.execute",
            "status": "completed",
            "connector_id": connector_id,
            "tool_name": tool_name,
            "job_ref": f"connector-job://pv20/{job_id}",
            "approval_refs": approval_refs,
            "artifact_refs": [{"artifact_id": artifact_id, "kind": artifact.get("kind"), "name": artifact.get("name")}],
            "mcp_call_refs": [f"mcp-call://pv20/{station_run_id}/{connector_id}/{tool_name}/{job_id}"],
            "skill_call_refs": [],
            "tool_call_refs": [],
            "summary": f"Executed allowlisted MCP connector: {connector_tool}",
            "created_at": _now_iso(),
            "redaction_status": "redacted",
        }
        self._assert_no_raw(result)
        return result

    def _validate_envelope(self, envelope: dict[str, Any]) -> None:
        self._assert_no_raw(envelope)
        required = {"execution_envelope_id", "workflow_instance_id", "station_run_id", "station_id", "agent_id", "source", "actor_type"}
        missing = sorted(required - set(envelope))
        if missing:
            raise GovernedAgentExecutorError("PV20_ENVELOPE_INVALID", "Agent execution envelope is missing required fields.", reason="missing_required_field", field=missing[0])
        if envelope.get("source") == "agent" or envelope.get("actor_type") == "agent":
            raise GovernedAgentExecutorError("PV20_SOURCE_AGENT_DENIED", "source=agent cannot trigger PV20-S2 execution.", reason="source_agent_denied", field="source")
        authority = envelope.get("execution_authority") if isinstance(envelope.get("execution_authority"), dict) else {}
        if authority.get("browser_direct_execution_allowed") is True:
            raise GovernedAgentExecutorError("PV20_BROWSER_DIRECT_EXECUTION_DENIED", "Browser direct execution is not allowed.", reason="browser_direct_execution_denied")

    def _assert_no_raw(self, value: Any) -> None:
        text = json.dumps(value, ensure_ascii=False).lower()
        for term in FORBIDDEN_RAW_TERMS:
            if term in text:
                raise GovernedAgentExecutorError("PV20_REDACTION_DENIED", "Raw or sensitive content is not allowed in PV20 executor DTO.", reason="forbidden_raw_content")


def _now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")
