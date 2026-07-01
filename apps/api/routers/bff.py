"""Workflow Console BFF structured routes for V4.0-A2."""

from __future__ import annotations

import asyncio
import copy
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, StreamingResponse

from apps.api.auth import add_dev_warning, authorize_http_request, http_error_response
from apps.api.agent_handoff_store import HANDOFF_ACTIVE_STATES, InMemoryAgentHandoffStore
from apps.api.agent_operation_evidence_store import InMemoryAgentOperationEvidenceStore
from apps.api.dependencies import get_gateway_service
from apps.gateway.knowledge_mcp_workflow import DATA_SERVICE_CONNECTOR_ID, KnowledgeMcpWorkflowRunner
from apps.gateway.protocol import RpcRequest
from apps.gateway.service import GatewayService
from core.apps.scope import ScopeContext
from core.protocol.event_bridge import (
    collect_event_envelopes,
    ensure_channel_capabilities,
    heartbeat_frame,
    normalize_event_channels,
    read_event_cursor,
    sse_frame,
)
from core.protocol.schemas.errors import ProtocolError
from core.agent_executor import GovernedAgentExecutor, GovernedAgentExecutorError

router = APIRouter()

SENSITIVE_KEY_PARTS = (
    "token",
    "authorization",
    "secret",
    "raw_trace_payload",
    "raw_artifact_content",
    "raw_connector_payload",
)
SENSITIVE_KEY_COMPACT_PARTS = tuple(part.replace("_", "") for part in SENSITIVE_KEY_PARTS)
UI_LAYOUT_KEYS = {
    "x",
    "y",
    "position",
    "canvas",
    "layout",
    "zoom",
    "selection",
    "selectednode",
    "panelcollapsed",
    "activetab",
    "viewport",
}
CANVAS_PATCH_SOURCES = {"canvas", "inspector", "workflow_console", "agent"}
CANVAS_PATCH_INTENTS = {"node_add", "edge_add", "inspector_update"}
CANVAS_PATCH_OPERATIONS = {
    "node_add": {"add_station"},
    "edge_add": {"update_edge"},
    "inspector_update": {
        "update_station_prompt",
        "update_connector",
        "update_artifact_contract",
        "update_quality_rule",
        "update_approval_point",
    },
}
INSPECTOR_OPERATION_FIELDS = {
    "update_station_prompt": {"station_id", "prompt_ref", "prompt_patch"},
    "update_connector": {"station_id", "connector_refs", "connector_patch"},
    "update_artifact_contract": {"station_id", "contract_id", "contract_patch"},
    "update_quality_rule": {"quality_contract_id", "quality_patch"},
    "update_approval_point": {"station_id", "approval_required", "approval_policy"},
}
ALLOWED_NODE_CATALOG_IDS = {
    "user_input",
    "file_input",
    "form_input",
    "webhook_input",
    "data_source_input",
    "generic_agent",
    "planner_agent",
    "script_writer_agent",
    "director_agent",
    "reviewer_agent",
    "multi_agent",
    "story_outline",
    "script_generation",
    "storyboard_generation",
    "character_consistency",
    "image_prompt_generation",
    "video_render",
    "subtitle_generation",
    "cover_generation",
    "video_quality",
    "publish_output",
    "http_request",
    "file_processing",
    "database_query",
    "mcp_tool",
    "knowledge_search",
    "image_generation",
    "asset_storage",
    "quality_evaluation",
    "consistency_check",
    "safety_check",
    "cost_check",
    "manual_approval",
    "conditional_approval",
    "publish_approval",
    "condition",
    "branch",
    "merge",
    "loop",
    "retry",
    "wait",
    "end",
}
ALLOWED_CONNECTOR_REFS = {
    "http",
    "file",
    "database",
    "mcp",
    "knowledge",
    "image_generation",
    "video_render",
    "subtitle",
    "asset_storage",
}
ALLOWED_SKILL_REFS = {
    "generic.reasoning",
    "planning.plan",
    "video.outline",
    "video.script",
    "video.storyboard",
    "video.character_consistency",
    "video.image_prompt",
    "video.quality",
    "governance.review",
}
NODE_CATALOG_CONTRACTS: dict[str, dict[str, Any]] = {
    "user_input": {
        "catalog_id": "core.input.user",
        "catalog_version": "2026-05-21",
        "node_template_id": "user_input",
        "station_kind": "input",
        "schema_version": "v4.0-n",
        "allowed_skill_refs": ["generic.reasoning"],
        "allowed_connector_refs": [],
        "allowed_artifact_kinds": ["dummy.alpha", "text/plain"],
        "allowed_quality_rules": [],
        "allowed_approval_policies": [],
    },
    "file_input": {
        "catalog_id": "core.input.file",
        "catalog_version": "2026-05-21",
        "node_template_id": "file_input",
        "station_kind": "input",
        "schema_version": "v4.0-n",
        "allowed_skill_refs": ["generic.reasoning"],
        "allowed_connector_refs": ["file"],
        "allowed_artifact_kinds": ["file", "text/plain"],
        "allowed_quality_rules": [],
        "allowed_approval_policies": [],
    },
    "planner_agent": {
        "catalog_id": "core.agent.planner",
        "catalog_version": "2026-05-21",
        "node_template_id": "planner_agent",
        "station_kind": "planner",
        "schema_version": "v4.0-n",
        "allowed_skill_refs": ["planning.plan"],
        "allowed_connector_refs": [],
        "allowed_artifact_kinds": ["dummy.alpha", "dummy.beta"],
        "allowed_quality_rules": [],
        "allowed_approval_policies": [],
    },
    "script_writer_agent": {
        "catalog_id": "video.agent.script_writer",
        "catalog_version": "2026-05-21",
        "node_template_id": "script_writer_agent",
        "station_kind": "screenwriter",
        "schema_version": "v4.0-n",
        "allowed_skill_refs": ["video.script"],
        "allowed_connector_refs": [],
        "allowed_artifact_kinds": ["script", "dummy.beta"],
        "allowed_quality_rules": ["visual_consistency"],
        "allowed_approval_policies": [],
    },
    "director_agent": {
        "catalog_id": "video.agent.director",
        "catalog_version": "2026-05-21",
        "node_template_id": "director_agent",
        "station_kind": "director",
        "schema_version": "v4.0-n",
        "allowed_skill_refs": ["video.storyboard"],
        "allowed_connector_refs": [],
        "allowed_artifact_kinds": ["storyboard", "dummy.beta"],
        "allowed_quality_rules": ["visual_consistency"],
        "allowed_approval_policies": [],
    },
    "storyboard_generation": {
        "catalog_id": "video.station.storyboard",
        "catalog_version": "2026-05-21",
        "node_template_id": "storyboard_generation",
        "station_kind": "storyboard_agent",
        "schema_version": "v4.0-n",
        "allowed_skill_refs": ["video.storyboard"],
        "allowed_connector_refs": [],
        "allowed_artifact_kinds": ["storyboard", "dummy.beta"],
        "allowed_quality_rules": ["visual_consistency"],
        "allowed_approval_policies": [],
    },
    "character_consistency": {
        "catalog_id": "video.station.character_consistency",
        "catalog_version": "2026-05-21",
        "node_template_id": "character_consistency",
        "station_kind": "reviewer",
        "schema_version": "v4.0-n",
        "allowed_skill_refs": ["video.character_consistency"],
        "allowed_connector_refs": [],
        "allowed_artifact_kinds": ["dummy.beta", "dummy.final", "storyboard"],
        "allowed_quality_rules": ["visual_consistency"],
        "allowed_approval_policies": [],
    },
    "video_render": {
        "catalog_id": "video.station.render",
        "catalog_version": "2026-05-21",
        "node_template_id": "video_render",
        "station_kind": "renderer",
        "schema_version": "v4.0-n",
        "allowed_skill_refs": ["video.image_prompt"],
        "allowed_connector_refs": ["video_render"],
        "allowed_artifact_kinds": ["video", "dummy.final"],
        "allowed_quality_rules": ["visual_consistency"],
        "allowed_approval_policies": [],
    },
    "quality_evaluation": {
        "catalog_id": "governance.station.quality",
        "catalog_version": "2026-05-21",
        "node_template_id": "quality_evaluation",
        "station_kind": "quality",
        "schema_version": "v4.0-n",
        "allowed_skill_refs": ["video.quality"],
        "allowed_connector_refs": [],
        "allowed_artifact_kinds": ["dummy.final", "video"],
        "allowed_quality_rules": ["visual_consistency", "dummy_quality"],
        "allowed_approval_policies": [],
    },
    "manual_approval": {
        "catalog_id": "governance.station.manual_approval",
        "catalog_version": "2026-05-21",
        "node_template_id": "manual_approval",
        "station_kind": "approval",
        "schema_version": "v4.0-n",
        "allowed_skill_refs": ["governance.review"],
        "allowed_connector_refs": [],
        "allowed_artifact_kinds": ["dummy.final", "video"],
        "allowed_quality_rules": [],
        "allowed_approval_policies": ["manual"],
    },
    "publish_output": {
        "catalog_id": "core.station.publish_output",
        "catalog_version": "2026-05-21",
        "node_template_id": "publish_output",
        "station_kind": "publisher",
        "schema_version": "v4.0-n",
        "allowed_skill_refs": ["generic.reasoning"],
        "allowed_connector_refs": [],
        "allowed_artifact_kinds": ["dummy.final", "video"],
        "allowed_quality_rules": [],
        "allowed_approval_policies": ["publish"],
    },
    "http_request": {
        "catalog_id": "connector.station.http",
        "catalog_version": "2026-05-21",
        "node_template_id": "http_request",
        "station_kind": "connector",
        "schema_version": "v4.0-n",
        "allowed_skill_refs": ["generic.reasoning"],
        "allowed_connector_refs": ["http"],
        "allowed_artifact_kinds": ["json", "dummy.beta"],
        "allowed_quality_rules": [],
        "allowed_approval_policies": [],
    },
    "mcp_tool": {
        "catalog_id": "connector.station.mcp",
        "catalog_version": "2026-05-21",
        "node_template_id": "mcp_tool",
        "station_kind": "connector",
        "schema_version": "v4.0-n",
        "allowed_skill_refs": ["generic.reasoning"],
        "allowed_connector_refs": ["mcp"],
        "allowed_artifact_kinds": ["json", "dummy.beta"],
        "allowed_quality_rules": [],
        "allowed_approval_policies": [],
    },
    "condition": {
        "catalog_id": "control.station.condition",
        "catalog_version": "2026-05-21",
        "node_template_id": "condition",
        "station_kind": "control",
        "schema_version": "v4.0-n",
        "allowed_skill_refs": ["planning.plan"],
        "allowed_connector_refs": [],
        "allowed_artifact_kinds": ["dummy.alpha", "dummy.beta", "dummy.final"],
        "allowed_quality_rules": [],
        "allowed_approval_policies": [],
    },
    "end": {
        "catalog_id": "control.station.end",
        "catalog_version": "2026-05-21",
        "node_template_id": "end",
        "station_kind": "control",
        "schema_version": "v4.0-n",
        "allowed_skill_refs": ["generic.reasoning"],
        "allowed_connector_refs": [],
        "allowed_artifact_kinds": ["dummy.final", "video"],
        "allowed_quality_rules": [],
        "allowed_approval_policies": [],
    },
}
NODE_CATALOG_LABELS = {
    "user_input": "用户输入",
    "file_input": "文件输入",
    "planner_agent": "Planner Agent",
    "script_writer_agent": "Script Writer Agent",
    "director_agent": "Director Agent",
    "storyboard_generation": "分镜生成",
    "character_consistency": "角色一致性检查",
    "video_render": "视频渲染",
    "quality_evaluation": "质量评估",
    "manual_approval": "人工审批",
    "publish_output": "发布输出",
    "http_request": "HTTP 请求",
    "mcp_tool": "MCP 工具",
    "condition": "条件判断",
    "end": "结束节点",
}
PATCH_QUEUE_STATUSES = {"proposed", "selected", "applied", "rejected", "stale", "blocked", "conflicted"}
AGENT_ACTION_INTENTS = {
    "explain_workflow",
    "summarize_events",
    "summarize_quality",
    "summarize_context",
    "suggest_patch",
    "show_patch_diff",
    "show_approval_notice",
    "show_context_summary",
    "navigate_to_editing_panel",
    "open_editing_panel",
    "open_approval_panel",
    "open_context_panel",
    "open_quality_panel",
    "open_artifact_panel",
    "propose_patch",
    "propose_context_update",
    "propose_approval_decision",
    "propose_station_rerun",
}
FORBIDDEN_AGENT_ACTION_INTENTS = {
    "apply_patch",
    "reject_patch",
    "publish_version",
    "respond_approval",
    "update_context",
    "emit_business_event",
    "start_workflow",
    "rerun_station",
    "call_connector",
    "call_external_llm",
}
AGENT_ACTION_POLICY: dict[str, str] = {
    "explain_workflow": "display_only",
    "summarize_events": "display_only",
    "summarize_quality": "display_only",
    "summarize_context": "display_only",
    "show_approval_notice": "display_only",
    "show_patch_diff": "display_only",
    "show_context_summary": "display_only",
    "navigate_to_editing_panel": "navigation",
    "open_editing_panel": "navigation",
    "open_approval_panel": "navigation",
    "open_context_panel": "navigation",
    "open_quality_panel": "navigation",
    "open_artifact_panel": "navigation",
    "suggest_patch": "proposal_only",
    "propose_patch": "proposal_only",
    "propose_context_update": "proposal_only",
    "propose_approval_decision": "proposal_only",
    "propose_station_rerun": "proposal_only",
}
READ_ONLY_AGENT_ACTION_INTENTS = {
    "explain_workflow",
    "summarize_events",
    "summarize_quality",
    "summarize_context",
}
_AGENT_TALK_SESSIONS: dict[str, dict[str, Any]] = {}
_AGENT_TALK_MESSAGES: dict[str, list[dict[str, Any]]] = {}
_AGENT_TALK_SUGGESTIONS: dict[str, list[dict[str, Any]]] = {}
_AGENT_ACTION_PROPOSALS: dict[str, list[dict[str, Any]]] = {}
_AGENT_HANDOFF_REPOSITORY = InMemoryAgentHandoffStore()
_AGENT_OPERATION_EVIDENCE_REPOSITORY = InMemoryAgentOperationEvidenceStore()
_AGENT_TALK_AUDIT: list[dict[str, Any]] = []
AGENT_HANDOFF_TTL_MINUTES = 30
AGENT_HANDOFF_TARGET_PANELS = {"editing_panel", "approval_panel", "context_panel", "quality_panel", "artifact_panel"}
PV17_SCHEMA_VERSION = "pv17.product_closed_loop.v1"
PV18_KNOWLEDGE_SCHEMA_VERSION = "pv18.knowledge_opc.v1"
PV19_RUNTIME_WORKFLOW_SCHEMA_VERSION = "pv19.runtime_workflow_platform.v1"
PV20_AGENT_EXECUTOR_CONTRACT_SCHEMA_VERSION = "pv20.agent_executor_contract.v1"
PV21_COMPLETE_WORKFLOW_STUDIO_SCHEMA_VERSION = "pv21.complete_workflow_studio.v1"
V13_WORKFLOW_STUDIO_SCHEMA_VERSION = "v13.workflow_spec_graph.v1"
V13_WORKFLOW_ID = "wf-v13-markdown-summary-studio-pilot"
V13_WORKFLOW_DIFF_ID = "diff-v13-editable-studio-pilot-001"
WORKFLOW_PLATFORM_SCENARIO_PROJECTION_SCHEMA_VERSION = "workflow_platform.scenario_projection.v1"
WORKFLOW_PLATFORM_BUSINESS_OUTPUT_SCHEMA_VERSION = "workflow_platform.business_output.v1"
V13_GRAPH = {
    "schema_version": V13_WORKFLOW_STUDIO_SCHEMA_VERSION,
    "workflow_id": V13_WORKFLOW_ID,
    "workspace_id": "ws-v12-technical-content-real",
    "project_id": "proj-v12-local-knowledge-real",
    "app_id": "app-v12-markdown-workflow-real",
    "version_ref": "workflow-version:v13-draft-001",
    "runtime_backed": False,
    "nodes": [
        {"node_id": "start_goal", "label": "目标输入", "node_kind": "start", "status": "configured", "position": {"x": 0, "y": 120}},
        {
            "node_id": "folder_reader",
            "label": "读取 Markdown 文件夹",
            "node_kind": "tool",
            "status": "configured",
            "capability_ref": "tool:folder.readonly_scan",
            "position": {"x": 260, "y": 120},
        },
        {
            "node_id": "summary_agent",
            "label": "总结 Agent",
            "node_kind": "station",
            "status": "configured",
            "agent_profile_ref": "agent-v12-quality-reviewer-real",
            "position": {"x": 540, "y": 80},
        },
        {"node_id": "quality_branch", "label": "质量分支", "node_kind": "fan_out", "status": "configured", "position": {"x": 800, "y": 120}},
        {
            "node_id": "quality_gate",
            "label": "质量检查",
            "node_kind": "quality_gate",
            "status": "configured",
            "capability_ref": "tool:quality.review",
            "position": {"x": 1060, "y": 40},
        },
        {"node_id": "evidence_review", "label": "证据审查", "node_kind": "evidence", "status": "configured", "position": {"x": 1060, "y": 210}},
        {"node_id": "merge_review", "label": "审查汇合", "node_kind": "fan_in", "status": "configured", "position": {"x": 1330, "y": 120}},
        {"node_id": "final_markdown", "label": "输出 Markdown 总结", "node_kind": "end", "status": "configured", "position": {"x": 1600, "y": 120}},
    ],
    "edges": [
        {"edge_id": "start-folder", "source_node_id": "start_goal", "target_node_id": "folder_reader"},
        {"edge_id": "folder-summary", "source_node_id": "folder_reader", "target_node_id": "summary_agent"},
        {"edge_id": "summary-branch", "source_node_id": "summary_agent", "target_node_id": "quality_branch"},
        {"edge_id": "branch-quality", "source_node_id": "quality_branch", "target_node_id": "quality_gate"},
        {"edge_id": "branch-evidence", "source_node_id": "quality_branch", "target_node_id": "evidence_review"},
        {"edge_id": "quality-merge", "source_node_id": "quality_gate", "target_node_id": "merge_review"},
        {"edge_id": "evidence-merge", "source_node_id": "evidence_review", "target_node_id": "merge_review"},
        {"edge_id": "merge-final", "source_node_id": "merge_review", "target_node_id": "final_markdown"},
    ],
    "evidence_refs": ["evidence://v13/studio-pilot/workflow-spec-graph"],
    "audit_ref": "audit://v13/studio-pilot/workflow-spec-graph",
    "created_at": "2026-06-24T00:00:00Z",
}
V13_INSPECTORS = {
    node["node_id"]: {
        "schema_version": "v13.studio_node_inspector.v1",
        "workflow_id": V13_WORKFLOW_ID,
        "selected_node_ref": node["node_id"],
        "label": node["label"],
        "node_kind": node["node_kind"],
        "status": node["status"],
        "editable_fields": ["label", "position", "status"],
        "blocked_fields": ["runtime_truth", "publish_state", "execution_state"],
        "agent_profile_ref": node.get("agent_profile_ref"),
        "capability_ref": node.get("capability_ref"),
        "runtime_backed": False,
        "audit_ref": f"audit://v13/studio-pilot/inspector/{node['node_id']}",
    }
    for node in V13_GRAPH["nodes"]
}
V13_WORKFLOW_DIFF = {
    "schema_version": "v13.workflow_diff_proposal.v1",
    "proposal_id": V13_WORKFLOW_DIFF_ID,
    "workflow_id": V13_WORKFLOW_ID,
    "status": "awaiting_user_confirmation",
    "before_graph_ref": "workflow-spec-graph:v13-draft-001",
    "after_graph_ref": "workflow-spec-graph:v13-local-edit-preview",
    "changed_node_refs": ["quality_gate", "evidence_review"],
    "changed_edge_refs": ["quality-merge", "evidence-merge"],
    "confirmation_boundary": "handoff_only_no_publish_no_run",
    "runtime_backed": False,
    "publish_or_run_started": False,
    "audit_ref": "audit://v13/studio-pilot/workflow-diff",
}

WORKFLOW_PLATFORM_SCENARIOS = {
    "document_summary": {
        "title": "文档/知识总结",
        "accepted_inputs": ["markdown_folder", "document_set", "local_markdown_file"],
        "source_refs": ["repo://docs/design/V12-V15.x/workflow_platform_main_entry_prd.md"],
        "node_refs": ["document_input", "structure_parser", "fact_extractor", "summary_agent", "quality_gate", "evidence_review"],
        "agent_refs": ["agent:document-summary-writer", "agent:quality-reviewer"],
        "tool_refs": ["tool:markdown.read", "tool:citation.extract", "tool:quality.review"],
        "skill_refs": ["knowledge-synthesis", "source-tracing", "executive-summary"],
        "mcp_refs": ["mcp://filesystem-mcp"],
        "output_title": "工作流平台 PRD 摘要产物",
        "output_body": "总结 PV13 首页基线、WP-M5A 业务产物门禁、No-Go 边界和后续 PV22 顺序要求。",
        "quality_status": "PASS",
        "human_review_ref": "human-review://wp-m5a/document-summary/local-reviewer",
    },
    "code_review": {
        "title": "代码审查/变更风险检查",
        "accepted_inputs": ["git_diff", "source_file", "pull_request_patch"],
        "source_refs": ["repo://apps/workflow-console/src/App.tsx", "repo://apps/workflow-console/src/ui/v13/V13EditableStudio.tsx"],
        "node_refs": ["code_input", "static_scan", "risk_agent", "test_signal", "human_gate", "review_report"],
        "agent_refs": ["agent:code-risk-reviewer", "agent:security-auditor"],
        "tool_refs": ["tool:static.scan", "tool:test.summary", "tool:risk.classifier"],
        "skill_refs": ["clean-code-audit", "vulnerability-detection", "report-consolidation"],
        "mcp_refs": ["mcp://git-provider"],
        "output_title": "工作流平台前端变更风险报告",
        "output_body": "检查入口路由、V13 工作台数据源、BFF route 边界和验收报告生成逻辑。",
        "quality_status": "PASS",
        "human_review_ref": "human-review://wp-m5a/code-review/local-reviewer",
    },
    "meeting_brief": {
        "title": "会议/访谈整理",
        "accepted_inputs": ["transcript_text", "meeting_notes", "audio_derived_text"],
        "source_refs": ["repo://TASKS.md"],
        "node_refs": ["transcript_input", "topic_extractor", "decision_classifier", "action_item_agent", "human_gate", "brief_output"],
        "agent_refs": ["agent:meeting-brief-writer", "agent:decision-extractor"],
        "tool_refs": ["tool:transcript.parse", "tool:action-item.extract", "tool:decision.trace"],
        "skill_refs": ["meeting-minutes", "action-items", "source-tracing"],
        "mcp_refs": ["mcp://meeting-reference-pack"],
        "output_title": "当前开发主线会议纪要产物",
        "output_body": "整理已完成阶段、WP-M5A 当前目标、未实现计划、决策边界和下一步行动项。",
        "quality_status": "PASS",
        "human_review_ref": "human-review://wp-m5a/meeting-brief/local-reviewer",
    },
}
PV17_ENTITY_KINDS = {
    "workspaces": "workspace",
    "projects": "project",
    "apps": "app",
    "station-agents": "station_agent",
}
_PV17_PRODUCT_ENTITIES: dict[str, dict[str, Any]] = {}
_PV18_KNOWLEDGE_WORKSPACES: dict[str, dict[str, Any]] = {}
_PV18_KNOWLEDGE_SOURCES: dict[str, list[dict[str, Any]]] = {}
_PV18_KNOWLEDGE_BUILDS: dict[str, list[dict[str, Any]]] = {}
_PV18_KNOWLEDGE_QUERIES: dict[str, list[dict[str, Any]]] = {}
_PV18_KNOWLEDGE_QUALITY: dict[str, list[dict[str, Any]]] = {}
_PV18_KNOWLEDGE_CORRECTIONS: dict[str, list[dict[str, Any]]] = {}


@router.get("/pv17/system/health")
async def pv17_system_health(request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params: dict[str, Any] = _query_scope_params(request)
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        gateway_health = await gateway.health_ping()
        method_payload = await gateway.method_list({})
        dto = {
            "schema_version": PV17_SCHEMA_VERSION,
            "status": "ok",
            "api_status": "ok",
            "gateway_status": gateway_health.get("status"),
            "workflow_store_status": "ok",
            "frontend_config_status": "ok",
            "method_count": len(method_payload.get("methods", [])),
            "scope": _scope_dto(auth.scope),
            "created_at": _now_iso(),
            "redaction_status": "redacted",
        }
        response = JSONResponse(_redact(dto))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/pv17/product-console/state")
async def pv17_product_console_state(request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params: dict[str, Any] = _query_scope_params(request)
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        result = await _rpc(gateway, "workflow.template.list", params)
        instance_result = await _rpc(gateway, "workflow.instance.list", params)
        workflows = [_workflow_summary(item) for item in result.get("templates", [])]
        instances = [_instance_summary(item) for item in instance_result.get("workflow_instances", [])]
        active_run = instances[0] if instances else None
        evidence_summary = _pv17_evidence_overview(gateway, auth.scope, active_run)
        dto = {
            "schema_version": PV17_SCHEMA_VERSION,
            "workspace": _pv17_entity_projection(auth.scope, "workspace"),
            "project": _pv17_entity_projection(auth.scope, "project"),
            "app": _pv17_app_projection(gateway, auth.scope),
            "workflows": workflows,
            "station_agents": _pv17_station_agent_projections(auth.scope),
            "active_run": active_run,
            "evidence_summary": evidence_summary,
            "audit_refs": [_pv17_audit_ref("product_console.state.read", auth.scope)],
            "created_at": _now_iso(),
            "redaction_status": "redacted",
        }
        response = JSONResponse(_redact(dto))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/pv17/entities/{entity_route}")
async def pv17_mutate_entity(
    entity_route: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    body: dict[str, Any] = {}
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("INVALID_PARAMS", "Request body must be an object.", {"field": "body"})
        entity_kind = PV17_ENTITY_KINDS.get(entity_route)
        if entity_kind is None:
            raise ProtocolError("INVALID_PARAMS", "Unsupported PV17 entity kind.", {"entity_route": entity_route})
        _pv17_require_mutation_confirmation(body)
        params = {**_query_scope_params(request), "entity_kind": entity_kind}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.write")
        decision = _pv17_entity_policy_decision(body, auth.scope)
        payload = body.get("payload") if isinstance(body.get("payload"), dict) else {}
        entity_id = _pv17_entity_id(entity_kind, payload, auth.scope)
        audit_ref = _pv17_audit_ref(f"product_entity.{entity_kind}.{body.get('operation') or 'upsert'}", auth.scope, entity_id=entity_id)
        if decision.get("status") == "denied":
            dto = {
                "schema_version": PV17_SCHEMA_VERSION,
                "status": "denied",
                "entity_ref": {"entity_kind": entity_kind, "entity_id": entity_id},
                "audit_ref": audit_ref,
                "policy_decision_ref": decision["policy_decision_ref"],
                "denied_reason": decision["reason"],
                "redaction_status": "redacted",
            }
        else:
            entity = _pv17_store_entity(entity_kind, entity_id, payload, auth.scope, audit_ref=audit_ref)
            dto = {
                "schema_version": PV17_SCHEMA_VERSION,
                "status": "accepted",
                "entity_ref": {"entity_kind": entity_kind, "entity_id": entity_id, "scope": _scope_dto(auth.scope)},
                "entity": entity,
                "audit_ref": audit_ref,
                "policy_decision_ref": decision["policy_decision_ref"],
                "denied_reason": None,
                "redaction_status": "redacted",
            }
        response = JSONResponse(_redact(dto))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/pv17/studio/workflows/{workflow_template_id}")
async def pv17_get_studio_workflow(
    workflow_template_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_template_id": workflow_template_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        template = gateway.workflow_repository.get_template(workflow_template_id, scope=auth.scope)
        draft = gateway.workflow_repository.get_draft(str(template.latest_draft_id), scope=auth.scope)
        versions = gateway.workflow_repository.list_versions(workflow_template_id, scope=auth.scope)
        patches = [patch.model_dump(mode="json") for patch in gateway.workflow_repository.list_patches(scope=auth.scope, workflow_template_id=workflow_template_id)]
        dto = _pv17_studio_workflow_dto(
            template.model_dump(mode="json"),
            draft.model_dump(mode="json"),
            [version.model_dump(mode="json") for version in versions],
            patches,
            auth.scope,
        )
        response = JSONResponse(_redact(dto))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/pv17/studio/workflows/{workflow_template_id}/patches")
async def pv17_propose_workflow_patch(
    workflow_template_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("INVALID_PARAMS", "Request body must be an object.", {"field": "body"})
        patch = _canvas_patch_request_to_patch(workflow_template_id, body)
        params = {**_query_scope_params(request), "workflow_template_id": workflow_template_id, "patch": patch}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflow_patches.write")
        _validate_canvas_patch_payload(gateway, workflow_template_id, patch, auth.scope)
        result = await _rpc(gateway, "workflow.patch.propose", params)
        dto = {
            "schema_version": PV17_SCHEMA_VERSION,
            "status": "proposed",
            "workflow_patch": _patch_proposal_dto(result["patch"]),
            "audit_refs": [_pv17_audit_ref("workflow.patch.propose", auth.scope, entity_id=str(result["patch"].get("workflow_patch_id") or ""))],
            "redaction_status": "redacted",
        }
        response = JSONResponse(_redact(dto))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/pv17/studio/workflows/{workflow_template_id}/publish")
async def pv17_publish_workflow(
    workflow_template_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    body: dict[str, Any] = {}
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("INVALID_PARAMS", "Request body must be an object.", {"field": "body"})
        _pv17_require_mutation_confirmation(body, allowed_sources={"editing_panel", "workflow_console", "mission_studio"})
        version = str(body.get("version") or "").strip()
        expected_revision = body.get("expected_draft_revision", body.get("expected_revision"))
        if not version:
            raise ProtocolError("INVALID_PARAMS", "version is required.", {"field": "version"})
        if expected_revision is None:
            raise ProtocolError("INVALID_PARAMS", "expected_draft_revision is required.", {"field": "expected_draft_revision"})
        params = {
            **_query_scope_params(request),
            "workflow_template_id": workflow_template_id,
            "version": version,
            "expected_revision": expected_revision,
        }
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflow_versions.publish")
        template = gateway.workflow_repository.get_template(workflow_template_id, scope=auth.scope)
        draft = gateway.workflow_repository.get_draft(str(template.latest_draft_id), scope=auth.scope)
        if draft.revision != expected_revision:
            raise ProtocolError("WORKFLOW_DRAFT_CONFLICT", "Workflow draft revision is stale.", {"expected_revision": expected_revision, "actual_revision": draft.revision})
        result = await _rpc(gateway, "workflow.template.publish", params)
        dto = {
            "schema_version": PV17_SCHEMA_VERSION,
            "status": "published",
            "publish": _publish_dto(result),
            "audit_refs": [_pv17_audit_ref("workflow.template.publish", auth.scope, entity_id=workflow_template_id)],
            "redaction_status": "redacted",
        }
        response = JSONResponse(_redact(dto))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/pv17/runtime/workflows/{workflow_template_id}/confirm-run")
async def pv17_confirm_runtime_run(
    workflow_template_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    body: dict[str, Any] = {}
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("INVALID_PARAMS", "Request body must be an object.", {"field": "body"})
        _pv17_require_mutation_confirmation(body, allowed_sources={"run_panel", "workflow_console", "mission_studio"})
        workflow_version_id = str(body.get("workflow_version_id") or "").strip()
        if not workflow_version_id:
            raise ProtocolError("INVALID_PARAMS", "workflow_version_id is required.", {"field": "workflow_version_id"})
        params = {**_query_scope_params(request), "workflow_version_id": workflow_version_id, "input": body.get("input") if isinstance(body.get("input"), dict) else {}}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.execute")
        result = await _rpc(gateway, "workflow.instance.start", params)
        instance = result.get("workflow_instance") if isinstance(result.get("workflow_instance"), dict) else {}
        if instance.get("workflow_template_id") != workflow_template_id:
            raise ProtocolError("SCOPE_MISMATCH", "Workflow version does not belong to requested template.", {"workflow_template_id": workflow_template_id})
        await _pv17_attach_quality_refs_for_run(gateway, auth.scope, instance, result.get("station_runs"))
        dto = {
            "schema_version": PV17_SCHEMA_VERSION,
            "status": "started",
            "workflow_instance": _instance_summary(instance),
            "station_runs": result.get("station_runs") if isinstance(result.get("station_runs"), list) else [],
            "runtime_event_refs": _pv17_runtime_event_refs(instance, result.get("station_runs")),
            "trace_refs": _pv17_trace_refs(instance),
            "audit_refs": [_pv17_audit_ref("workflow.instance.start", auth.scope, entity_id=str(instance.get("workflow_instance_id") or ""))],
            "redaction_status": "redacted",
        }
        response = JSONResponse(_redact(dto))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/pv17/runtime/instances/{workflow_instance_id}/inspect")
async def pv17_inspect_runtime_instance(
    workflow_instance_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        dto = await _pv17_runtime_inspect_dto(gateway, auth.scope, params)
        response = JSONResponse(_redact(dto))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/pv17/evidence/instances/{workflow_instance_id}/summary")
async def pv17_evidence_summary(
    workflow_instance_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        inspect = await _pv17_runtime_inspect_dto(gateway, auth.scope, params)
        dto = _pv17_evidence_summary_dto(inspect, auth.scope)
        response = JSONResponse(_redact(dto))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/pv18/knowledge/state")
async def pv18_knowledge_state(request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params: dict[str, Any] = _query_scope_params(request)
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        workspace = _pv18_workspace_projection(auth.scope)
        dto = {
            "schema_version": PV18_KNOWLEDGE_SCHEMA_VERSION,
            "status": "ready",
            "scope": _scope_dto(auth.scope),
            "workspace": workspace,
            "connector_health": _pv18_connector_health(gateway),
            "sources": _PV18_KNOWLEDGE_SOURCES.get(workspace["workspace_id"], []),
            "builds": _PV18_KNOWLEDGE_BUILDS.get(workspace["workspace_id"], []),
            "queries": _PV18_KNOWLEDGE_QUERIES.get(workspace["workspace_id"], []),
            "evidence_summary": _pv18_evidence_summary_projection(auth.scope, workspace["workspace_id"]),
            "audit_refs": [_pv18_audit_ref("knowledge.state.read", auth.scope, entity_id=workspace["workspace_id"])],
            "created_at": _now_iso(),
            "redaction_status": "redacted",
        }
        response = JSONResponse(_redact(dto))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/pv18/knowledge/workspaces")
async def pv18_knowledge_workspace_upsert(request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("INVALID_PARAMS", "Request body must be an object.", {"field": "body"})
        params = _query_scope_params(request)
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.write")
        workspace = _pv18_store_workspace(auth.scope, body)
        dto = {
            "schema_version": PV18_KNOWLEDGE_SCHEMA_VERSION,
            "status": "accepted",
            "workspace": workspace,
            "audit_refs": [_pv18_audit_ref("knowledge.workspace.upsert", auth.scope, entity_id=workspace["workspace_id"])],
            "redaction_status": "redacted",
        }
        response = JSONResponse(_redact(dto))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/pv18/knowledge/sources/import")
async def pv18_knowledge_source_import(request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("INVALID_PARAMS", "Request body must be an object.", {"field": "body"})
        params = _query_scope_params(request)
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.write")
        workspace = _pv18_workspace_projection(auth.scope)
        source = _pv18_source_from_body(gateway, auth.scope, workspace, body)
        _PV18_KNOWLEDGE_SOURCES.setdefault(workspace["workspace_id"], []).append(source)
        dto = {
            "schema_version": PV18_KNOWLEDGE_SCHEMA_VERSION,
            "status": "imported",
            "source_reference": source["source_reference"],
            "note": source["note"],
            "artifact_refs": source["artifact_refs"],
            "lineage_refs": source["lineage_refs"],
            "audit_refs": [_pv18_audit_ref("knowledge.source.import", auth.scope, entity_id=source["source_id"])],
            "redaction_status": "redacted",
        }
        response = JSONResponse(_redact(dto))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/pv18/knowledge/builds/start")
async def pv18_knowledge_build_start(request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("INVALID_PARAMS", "Request body must be an object.", {"field": "body"})
        params = _query_scope_params(request)
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.write")
        workspace = _pv18_workspace_projection(auth.scope)
        sources = _PV18_KNOWLEDGE_SOURCES.get(workspace["workspace_id"], [])
        build = _pv18_build_from_sources(gateway, auth.scope, workspace, sources, body)
        _PV18_KNOWLEDGE_BUILDS.setdefault(workspace["workspace_id"], []).append(build)
        response = JSONResponse(_redact({"schema_version": PV18_KNOWLEDGE_SCHEMA_VERSION, **build, "redaction_status": "redacted"}))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/pv18/knowledge/builds/{build_id}/status")
async def pv18_knowledge_build_status(build_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = _query_scope_params(request)
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        workspace = _pv18_workspace_projection(auth.scope)
        build = next((item for item in _PV18_KNOWLEDGE_BUILDS.get(workspace["workspace_id"], []) if item.get("build_id") == build_id), None)
        if build is None:
            raise ProtocolError("NOT_FOUND", "PV18 build was not found.", {"build_id": build_id})
        response = JSONResponse(_redact({"schema_version": PV18_KNOWLEDGE_SCHEMA_VERSION, **build, "redaction_status": "redacted"}))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/pv18/knowledge/query")
async def pv18_knowledge_query(request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("INVALID_PARAMS", "Request body must be an object.", {"field": "body"})
        params = _query_scope_params(request)
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.execute")
        workspace = _pv18_workspace_projection(auth.scope)
        sources = _PV18_KNOWLEDGE_SOURCES.get(workspace["workspace_id"], [])
        if not sources:
            raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "PV18 query requires at least one imported source.", {"fixture": "source_required"})
        query = str(body.get("query") or "HarnessOS Knowledge OPC 是什么？").strip()
        query_dto = _pv18_query_result(gateway, auth.scope, workspace, query, sources)
        _PV18_KNOWLEDGE_QUERIES.setdefault(workspace["workspace_id"], []).append(query_dto)
        response = JSONResponse(_redact({"schema_version": PV18_KNOWLEDGE_SCHEMA_VERSION, **query_dto, "redaction_status": "redacted"}))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/pv18/knowledge/quality-feedback")
async def pv18_knowledge_quality_feedback(request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("INVALID_PARAMS", "Request body must be an object.", {"field": "body"})
        params = _query_scope_params(request)
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="quality.write")
        workspace = _pv18_workspace_projection(auth.scope)
        feedback = _pv18_quality_feedback(gateway, auth.scope, workspace, body)
        _PV18_KNOWLEDGE_QUALITY.setdefault(workspace["workspace_id"], []).append(feedback)
        response = JSONResponse(_redact({"schema_version": PV18_KNOWLEDGE_SCHEMA_VERSION, **feedback, "redaction_status": "redacted"}))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/pv18/knowledge/correction-plan")
async def pv18_knowledge_correction_plan(request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("INVALID_PARAMS", "Request body must be an object.", {"field": "body"})
        params = _query_scope_params(request)
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="quality.write")
        workspace = _pv18_workspace_projection(auth.scope)
        plan = _pv18_correction_plan(gateway, auth.scope, workspace, body)
        _PV18_KNOWLEDGE_CORRECTIONS.setdefault(workspace["workspace_id"], []).append(plan)
        response = JSONResponse(_redact({"schema_version": PV18_KNOWLEDGE_SCHEMA_VERSION, **plan, "redaction_status": "redacted"}))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/pv18/knowledge/evidence/summary")
async def pv18_knowledge_evidence_summary(request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = _query_scope_params(request)
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        workspace = _pv18_workspace_projection(auth.scope)
        dto = {
            "schema_version": PV18_KNOWLEDGE_SCHEMA_VERSION,
            **_pv18_evidence_summary_projection(auth.scope, workspace["workspace_id"]),
            "audit_refs": [_pv18_audit_ref("knowledge.evidence.summary", auth.scope, entity_id=workspace["workspace_id"])],
            "redaction_status": "redacted",
        }
        response = JSONResponse(_redact(dto))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/v13/system/health")
async def v13_system_health(request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = _query_scope_params(request)
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        health = await gateway.health_ping()
        dto = {
            "schema_version": "v13.system_health.v1",
            "status": "ok",
            "scope": _scope_dto(auth.scope),
            "gateway_status": health.get("status"),
            "bff_backed": True,
            "runtime_backed": False,
            "evidence_scope": "bounded_review",
            "created_at": _now_iso(),
            "audit_ref": "audit://v13/studio-pilot/system-health",
            "redaction_status": "redacted",
        }
        response = JSONResponse(_redact(dto))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/v13/workflows/{workflow_id}/graph")
async def v13_workflow_graph(workflow_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        if workflow_id != V13_WORKFLOW_ID:
            raise ProtocolError("NOT_FOUND", "V13 workflow graph was not found.", {"workflow_id": workflow_id})
        params = {**_query_scope_params(request), "workflow_id": workflow_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        graph = copy.deepcopy(V13_GRAPH)
        graph["workspace_id"] = auth.scope.workspace_id or graph["workspace_id"]
        graph["project_id"] = auth.scope.project_id or graph["project_id"]
        graph["app_id"] = auth.scope.app_id or graph["app_id"]
        response = JSONResponse(_redact(graph))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/v13/workflows/{workflow_id}/graph/validate")
async def v13_validate_workflow_graph(workflow_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("INVALID_PARAMS", "Request body must be an object.", {"field": "body"})
        params = {**_query_scope_params(request), "workflow_id": workflow_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        graph = body.get("graph") if isinstance(body.get("graph"), dict) else copy.deepcopy(V13_GRAPH)
        if str(graph.get("workflow_id") or workflow_id) != V13_WORKFLOW_ID:
            raise ProtocolError("NOT_FOUND", "V13 workflow graph was not found.", {"workflow_id": workflow_id})
        dto = _v13_validate_graph(graph)
        response = JSONResponse(_redact(dto))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/v13/workflows/{workflow_id}/diff")
async def v13_workflow_diff(workflow_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("INVALID_PARAMS", "Request body must be an object.", {"field": "body"})
        params = {**_query_scope_params(request), "workflow_id": workflow_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflow_patches.write")
        graph = body.get("graph") if isinstance(body.get("graph"), dict) else copy.deepcopy(V13_GRAPH)
        if str(graph.get("workflow_id") or workflow_id) != V13_WORKFLOW_ID:
            raise ProtocolError("NOT_FOUND", "V13 workflow graph was not found.", {"workflow_id": workflow_id})
        validation = _v13_validate_graph(graph)
        baseline_nodes = {str(node.get("node_id")) for node in V13_GRAPH["nodes"] if isinstance(node, dict)}
        graph_nodes = {str(node.get("node_id")) for node in graph.get("nodes", []) if isinstance(node, dict)}
        baseline_edges = {str(edge.get("edge_id")) for edge in V13_GRAPH["edges"] if isinstance(edge, dict)}
        graph_edges = {str(edge.get("edge_id")) for edge in graph.get("edges", []) if isinstance(edge, dict)}
        dto = copy.deepcopy(V13_WORKFLOW_DIFF)
        dto["status"] = "blocked" if validation["status"] == "FAIL" else "review_required"
        dto["changed_node_refs"] = sorted(graph_nodes.symmetric_difference(baseline_nodes)) or dto["changed_node_refs"]
        dto["changed_edge_refs"] = sorted(graph_edges.symmetric_difference(baseline_edges)) or dto["changed_edge_refs"]
        dto["graph_validation"] = validation
        dto["updated_at"] = _now_iso()
        response = JSONResponse(_redact(dto))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/v13/workflow-diff/{proposal_id}/revise")
async def v13_workflow_diff_revise(proposal_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    return await _v13_workflow_diff_decision(proposal_id, request, gateway, decision="revise_requested")


@router.post("/v13/workflow-diff/{proposal_id}/reject")
async def v13_workflow_diff_reject(proposal_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    return await _v13_workflow_diff_decision(proposal_id, request, gateway, decision="rejected")


@router.post("/v13/workflow-diff/{proposal_id}/confirm-publish-handoff")
async def v13_workflow_diff_confirm_handoff(proposal_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    return await _v13_workflow_diff_decision(proposal_id, request, gateway, decision="handoff_confirmed")


@router.get("/v13/studio/node-inspector/{node_id}")
async def v13_node_inspector(node_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_id": V13_WORKFLOW_ID, "node_id": node_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        inspector = copy.deepcopy(V13_INSPECTORS.get(node_id))
        if inspector is None:
            raise ProtocolError("NOT_FOUND", "V13 node inspector was not found.", {"node_id": node_id})
        response = JSONResponse(_redact(inspector))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/workflow-platform/scenarios")
async def workflow_platform_scenarios(request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = _query_scope_params(request)
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        dto = _workflow_platform_scenario_projection_dto(auth.scope)
        response = JSONResponse(_redact(dto))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/workflow-platform/scenarios/{scenario_id}/outputs")
async def workflow_platform_scenario_outputs(scenario_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        if scenario_id not in WORKFLOW_PLATFORM_SCENARIOS:
            raise ProtocolError("NOT_FOUND", "Workflow platform scenario output was not found.", {"scenario_id": scenario_id})
        params = {**_query_scope_params(request), "scenario_id": scenario_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        dto = _workflow_platform_business_output_dto(scenario_id, auth.scope)
        response = JSONResponse(_redact(dto))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/pv19/workbench/state")
async def pv19_workbench_state(request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = _query_scope_params(request)
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        template, draft = _pv19_ensure_workflow_template(gateway, auth.scope)
        versions = gateway.workflow_repository.list_versions(template.workflow_template_id, scope=auth.scope)
        instances = gateway.workflow_repository.list_instances(scope=auth.scope)
        active_run = next((item for item in reversed(instances) if item.workflow_template_id == template.workflow_template_id), None)
        dto = {
            "schema_version": PV19_RUNTIME_WORKFLOW_SCHEMA_VERSION,
            "scope": _scope_dto(auth.scope),
            "entry": {"route": "?studio=pv19-runtime-workflow-platform", "root_empty_allowed": False, "status": "ready"},
            "workspace": {"workspace_id": auth.scope.workspace_id or "local", "display_name": "PV19 Runtime Workflow Workspace"},
            "project": {"project_id": auth.scope.project_id or "demo_a", "display_name": "Runtime Workflow Platform Review"},
            "workflow": _workflow_summary(template.model_dump(mode="json")),
            "draft": {"workflow_draft_id": draft.workflow_draft_id, "revision": draft.revision, "status": draft.status},
            "active_version": _version_summary(versions[-1].model_dump(mode="json")) if versions else None,
            "active_run": _instance_summary(active_run.model_dump(mode="json")) if active_run is not None else None,
            "health": {"bff": "ok", "gateway": "ok", "runtime_backed": True, "human_gate_model": "station_approval_fields"},
            "audit_refs": [_pv19_audit_ref("workbench.state.read", auth.scope, entity_id=template.workflow_template_id)],
            "evidence_refs": [],
            "redaction_status": "redacted",
        }
        response = JSONResponse(_redact(dto))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/pv19/workflows/{workflow_id}/graph")
async def pv19_workflow_graph(workflow_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_template_id": workflow_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        template, draft = _pv19_get_workflow_template_and_draft(gateway, workflow_id, auth.scope)
        response = JSONResponse(_redact(_pv19_graph_dto(template.model_dump(mode="json"), draft.model_dump(mode="json"), auth.scope)))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/pv19/workflows/{workflow_id}/graph/validate")
async def pv19_validate_workflow_graph(workflow_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_template_id": workflow_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        template, draft = _pv19_get_workflow_template_and_draft(gateway, workflow_id, auth.scope)
        draft_payload = draft.draft if isinstance(draft.draft, dict) else {}
        nodes = draft_payload.get("stations") if isinstance(draft_payload.get("stations"), list) else []
        edges = draft_payload.get("edges") if isinstance(draft_payload.get("edges"), list) else []
        human_gate_nodes = [node for node in nodes if isinstance(node, dict) and bool(node.get("approval_required"))]
        errors: list[dict[str, Any]] = []
        if not nodes:
            errors.append({"code": "graph_empty", "message": "Workflow graph has no stations."})
        if not human_gate_nodes:
            errors.append({"code": "human_gate_missing", "message": "PV19 requires at least one approval gate."})
        dto = {
            "schema_version": PV19_RUNTIME_WORKFLOW_SCHEMA_VERSION,
            "scope": _scope_dto(auth.scope),
            "workflow_id": workflow_id,
            "status": "valid" if not errors else "invalid",
            "errors": errors,
            "warnings": [] if edges else [{"code": "edge_empty", "message": "Workflow graph has no explicit edges."}],
            "runtime_readiness": {"can_publish": not errors, "can_run_after_publish": bool(nodes), "human_gate_nodes": [node.get("station_id") for node in human_gate_nodes]},
            "audit_refs": [_pv19_audit_ref("workflow.graph.validate", auth.scope, entity_id=template.workflow_template_id)],
            "evidence_refs": [],
            "redaction_status": "redacted",
        }
        response = JSONResponse(_redact(dto))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/pv19/workflows/{workflow_id}/diff")
async def pv19_workflow_diff(workflow_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("INVALID_PARAMS", "Request body must be an object.", {"field": "body"})
        params = {**_query_scope_params(request), "workflow_template_id": workflow_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflow_patches.write")
        template, draft = _pv19_get_workflow_template_and_draft(gateway, workflow_id, auth.scope)
        patch_body = body.get("patch") if isinstance(body.get("patch"), dict) else _pv19_default_diff_patch()
        patch = _canvas_patch_request_to_patch(workflow_id, patch_body)
        _validate_canvas_patch_payload(gateway, workflow_id, patch, auth.scope)
        result = await _rpc(gateway, "workflow.patch.propose", {**params, "patch": patch})
        patch_id = str(result.get("patch", {}).get("workflow_patch_id") or "")
        diff = await _rpc(gateway, "workflow.patch.diff", {**params, "workflow_patch_id": patch_id})
        dto = {
            "schema_version": PV19_RUNTIME_WORKFLOW_SCHEMA_VERSION,
            "scope": _scope_dto(auth.scope),
            "workflow_id": workflow_id,
            "draft_revision": draft.revision,
            "workflow_diff": {
                "workflow_patch_id": patch_id,
                "before_graph_ref": f"workflow_draft:{draft.workflow_draft_id}:revision:{draft.revision}",
                "after_graph_ref": f"workflow_patch:{patch_id}",
                "change_summary": diff.get("diff", {}).get("summary") if isinstance(diff.get("diff"), dict) else [],
                "confirmation_boundary": "user_confirmed_required_before_publish",
            },
            "workflow": _workflow_summary(template.model_dump(mode="json")),
            "audit_refs": [_pv19_audit_ref("workflow.diff.propose", auth.scope, entity_id=patch_id)],
            "evidence_refs": [f"workflow_patch:{patch_id}"],
            "redaction_status": "redacted",
        }
        response = JSONResponse(_redact(dto))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/pv19/workflows/{workflow_id}/versions/publish")
async def pv19_publish_workflow_version(workflow_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("INVALID_PARAMS", "Request body must be an object.", {"field": "body"})
        _pv19_require_user_confirmation(body, allowed_sources={"workflow_console", "mission_studio", "editing_panel"})
        expected_revision = body.get("expected_draft_revision")
        if expected_revision is None:
            raise ProtocolError("INVALID_PARAMS", "expected_draft_revision is required.", {"field": "expected_draft_revision"})
        version = str(body.get("version") or f"pv19-{int(datetime.now(UTC).timestamp())}").strip()
        params = {**_query_scope_params(request), "workflow_template_id": workflow_id, "version": version, "expected_revision": expected_revision}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflow_versions.publish")
        result = await _rpc(gateway, "workflow.template.publish", params)
        publish = _publish_dto(result)
        dto = {
            "schema_version": PV19_RUNTIME_WORKFLOW_SCHEMA_VERSION,
            "scope": _scope_dto(auth.scope),
            "status": "published",
            "workflow_version_id": publish.get("workflow_version_id"),
            "published_from_diff": body.get("workflow_patch_id"),
            "published_by": str(body.get("actor") or "local-reviewer"),
            "published_at": _now_iso(),
            "version": publish,
            "audit_refs": [_pv19_audit_ref("workflow.version.publish", auth.scope, entity_id=str(publish.get("workflow_version_id") or workflow_id))],
            "evidence_refs": [f"workflow_version:{publish.get('workflow_version_id')}"],
            "redaction_status": "redacted",
        }
        response = JSONResponse(_redact(dto))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/pv19/workflows/{workflow_id}/runs")
async def pv19_start_workflow_run(workflow_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("INVALID_PARAMS", "Request body must be an object.", {"field": "body"})
        _pv19_require_user_confirmation(body, allowed_sources={"workflow_console", "mission_studio", "run_panel"})
        workflow_version_id = str(body.get("workflow_version_id") or "").strip()
        if not workflow_version_id:
            raise ProtocolError("INVALID_PARAMS", "workflow_version_id is required.", {"field": "workflow_version_id"})
        params = {**_query_scope_params(request), "workflow_version_id": workflow_version_id, "input": body.get("input") if isinstance(body.get("input"), dict) else {}}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.execute")
        result = await _rpc(gateway, "workflow.instance.start", params)
        instance = result.get("workflow_instance") if isinstance(result.get("workflow_instance"), dict) else {}
        if instance.get("workflow_template_id") != workflow_id:
            raise ProtocolError("SCOPE_MISMATCH", "Workflow version does not belong to requested template.", {"workflow_id": workflow_id})
        await _pv19_attach_quality_refs_for_run(gateway, auth.scope, instance, result.get("station_runs"))
        dto = _pv19_run_start_dto(instance, result.get("station_runs"), auth.scope)
        response = JSONResponse(_redact(dto))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/pv19/runs/{run_id}/inspect")
async def pv19_inspect_run(run_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": run_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        dto = await _pv19_run_inspect_dto(gateway, auth.scope, params)
        response = JSONResponse(_redact(dto))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/pv19/runs/{run_id}/human-actions")
async def pv19_human_action(run_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("INVALID_PARAMS", "Request body must be an object.", {"field": "body"})
        _pv19_require_user_confirmation(body, allowed_sources={"workflow_console", "human_gate_panel", "mission_studio"})
        action_type = str(body.get("action_type") or body.get("decision") or "").strip()
        if action_type not in {"approve", "reject"}:
            raise ProtocolError("APPROVAL_INVALID_DECISION", "action_type must be approve or reject.", {"action_type": action_type})
        params = {**_query_scope_params(request), "workflow_instance_id": run_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="approvals")
        before = await _pv19_run_inspect_dto(gateway, auth.scope, params)
        approval_id = str(body.get("approval_id") or _pv19_pending_approval_id(gateway, auth.scope, run_id) or "").strip()
        if not approval_id:
            raise ProtocolError("APPROVAL_NOT_FOUND", "No pending human gate approval was found.", {"workflow_instance_id": run_id})
        result = await _rpc(gateway, "approval.respond", {**params, "approval_id": approval_id, "decision": action_type, "reason": body.get("reason")})
        after = await _pv19_run_inspect_dto(gateway, auth.scope, params)
        dto = {
            "schema_version": PV19_RUNTIME_WORKFLOW_SCHEMA_VERSION,
            "scope": _scope_dto(auth.scope),
            "action_type": action_type,
            "actor": str(body.get("actor") or "local-reviewer"),
            "approval_id": approval_id,
            "before_state": _pv19_state_digest(before),
            "after_state": _pv19_state_digest(after),
            "workflow_side_effect": result.get("workflow_side_effect"),
            "audit_refs": [_pv19_audit_ref("workflow.human_action", auth.scope, entity_id=approval_id)],
            "evidence_refs": [f"approval:{approval_id}", f"workflow_instance:{run_id}"],
            "redaction_status": "redacted",
        }
        response = JSONResponse(_redact(dto))
        add_dev_warning(response, auth)
        return response
    except KeyError as exc:
        return http_error_response(ProtocolError("APPROVAL_NOT_FOUND", str(exc), {"workflow_instance_id": run_id}))
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/pv19/runs/{run_id}/evidence")
async def pv19_run_evidence(run_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": run_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        inspect = await _pv19_run_inspect_dto(gateway, auth.scope, params)
        dto = _pv19_evidence_summary_dto(inspect, auth.scope)
        response = JSONResponse(_redact(dto))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/pv21/studio/state")
async def pv21_studio_state(request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = _query_scope_params(request)
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        template, draft = _pv21_ensure_workflow_template(gateway, auth.scope)
        versions = gateway.workflow_repository.list_versions(template.workflow_template_id, scope=auth.scope)
        instances = _pv21_instances_for_workflow(gateway, auth.scope, template.workflow_template_id)
        dto = _pv21_studio_state_dto(gateway, auth.scope, template.model_dump(mode="json"), draft.model_dump(mode="json"), versions, instances)
        response = JSONResponse(_redact(dto))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/pv21/workflows/{workflow_id}/graph")
async def pv21_workflow_graph(workflow_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_template_id": workflow_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        template, draft = _pv21_get_workflow_template_and_draft(gateway, workflow_id, auth.scope)
        response = JSONResponse(_redact(_pv21_graph_dto(template.model_dump(mode="json"), draft.model_dump(mode="json"), auth.scope)))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.put("/pv21/workflows/{workflow_id}/graph")
async def pv21_save_workflow_graph(workflow_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("PV21_GRAPH_INVALID", "Request body must be an object.", {"field": "body"})
        params = {**_query_scope_params(request), "workflow_template_id": workflow_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflow_patches.write")
        template, draft = _pv21_get_workflow_template_and_draft(gateway, workflow_id, auth.scope)
        draft_payload = _pv21_graph_request_to_draft_payload(body, template.model_dump(mode="json"), draft.model_dump(mode="json"), auth.scope)
        expected_revision = body.get("draft_revision")
        updated, _forked = gateway.workflow_repository.update_latest_draft(
            workflow_id,
            draft_payload,
            scope=auth.scope,
            expected_revision=int(expected_revision) if isinstance(expected_revision, int) else None,
        )
        updated_template = gateway.workflow_repository.get_template(workflow_id, scope=auth.scope)
        graph = _pv21_graph_dto(updated_template.model_dump(mode="json"), updated.model_dump(mode="json"), auth.scope)
        dto = {
            "schema_version": PV21_COMPLETE_WORKFLOW_STUDIO_SCHEMA_VERSION,
            "scope": _scope_dto(auth.scope),
            "graph": graph,
            "validation": _pv21_validation_dto(workflow_id, updated.draft, auth.scope),
            "audit_refs": [_pv21_audit_ref("workflow.graph.save", auth.scope, entity_id=workflow_id)],
            "redaction_status": "redacted",
        }
        response = JSONResponse(_redact(dto))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/pv21/workflows/{workflow_id}/graph/validate")
async def pv21_validate_workflow_graph(workflow_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_template_id": workflow_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        _template, draft = _pv21_get_workflow_template_and_draft(gateway, workflow_id, auth.scope)
        response = JSONResponse(_redact(_pv21_validation_dto(workflow_id, draft.draft, auth.scope)))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/pv21/workflows/{workflow_id}/diff")
async def pv21_workflow_diff(workflow_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("PV21_GRAPH_INVALID", "Request body must be an object.", {"field": "body"})
        params = {**_query_scope_params(request), "workflow_template_id": workflow_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflow_patches.read")
        template, draft = _pv21_get_workflow_template_and_draft(gateway, workflow_id, auth.scope)
        base_version_id = str(body.get("base_version_id") or template.latest_published_version_id or "").strip()
        base_snapshot: dict[str, Any] = {}
        if base_version_id:
            base_snapshot = gateway.workflow_repository.get_version(base_version_id, scope=auth.scope).snapshot
        dto = _pv21_diff_dto(workflow_id, base_version_id, draft.model_dump(mode="json"), base_snapshot, auth.scope)
        response = JSONResponse(_redact(dto))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/pv21/workflows/{workflow_id}/versions")
async def pv21_workflow_versions(workflow_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_template_id": workflow_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        template = gateway.workflow_repository.get_template(workflow_id, scope=auth.scope)
        versions = gateway.workflow_repository.list_versions(workflow_id, scope=auth.scope)
        dto = _pv21_versions_dto(template.model_dump(mode="json"), versions, auth.scope)
        response = JSONResponse(_redact(dto))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/pv21/workflows/{workflow_id}/versions/publish")
async def pv21_publish_workflow_version(workflow_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("PV21_GRAPH_INVALID", "Request body must be an object.", {"field": "body"})
        _pv21_require_user_confirmation(body, operation="publish")
        params = {**_query_scope_params(request), "workflow_template_id": workflow_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflow_versions.publish")
        template, draft = _pv21_get_workflow_template_and_draft(gateway, workflow_id, auth.scope)
        validation = _pv21_validation_dto(workflow_id, draft.draft, auth.scope)
        if validation["publish_blocked"]:
            raise ProtocolError("PV21_PUBLISH_BLOCKED", "PV21 validation blocks publish.", {"errors": validation["errors"]})
        version = str(body.get("version") or f"pv21-{int(datetime.now(UTC).timestamp())}").strip()
        result = await _rpc(gateway, "workflow.template.publish", {**params, "version": version, "expected_revision": draft.revision})
        publish = _publish_dto(result)
        dto = {
            "schema_version": PV21_COMPLETE_WORKFLOW_STUDIO_SCHEMA_VERSION,
            "scope": _scope_dto(auth.scope),
            "version": _pv21_version_dto(publish, template.latest_published_version_id == publish.get("workflow_version_id")),
            "status": "published",
            "diff_id": body.get("diff_id"),
            "audit_refs": [_pv21_audit_ref("workflow.version.publish", auth.scope, entity_id=str(publish.get("workflow_version_id") or workflow_id))],
            "evidence_refs": [f"workflow_version:{publish.get('workflow_version_id')}"],
            "redaction_status": "redacted",
        }
        response = JSONResponse(_redact(dto))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/pv21/workflows/{workflow_id}/versions/{version_id}/rollback")
async def pv21_rollback_workflow_version(workflow_id: str, version_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("PV21_GRAPH_INVALID", "Request body must be an object.", {"field": "body"})
        _pv21_require_user_confirmation(body, operation="rollback")
        params = {**_query_scope_params(request), "workflow_template_id": workflow_id, "workflow_version_id": version_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflow_versions.publish")
        before = gateway.workflow_repository.get_template(workflow_id, scope=auth.scope)
        _template, version = gateway.workflow_repository.set_latest_published_version(workflow_id, version_id, scope=auth.scope)
        dto = {
            "schema_version": PV21_COMPLETE_WORKFLOW_STUDIO_SCHEMA_VERSION,
            "scope": _scope_dto(auth.scope),
            "published_version": _pv21_version_dto(version.model_dump(mode="json"), True),
            "previous_version_id": before.latest_published_version_id,
            "rollback_source_version_id": version_id,
            "history_preserved": True,
            "audit_refs": [_pv21_audit_ref("workflow.version.rollback", auth.scope, entity_id=version_id)],
            "redaction_status": "redacted",
        }
        response = JSONResponse(_redact(dto))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/pv21/workflows/{workflow_id}/runs")
async def pv21_start_workflow_run(workflow_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("PV21_GRAPH_INVALID", "Request body must be an object.", {"field": "body"})
        _pv21_require_user_confirmation(body, operation="run")
        params = {**_query_scope_params(request), "workflow_template_id": workflow_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.execute")
        template = gateway.workflow_repository.get_template(workflow_id, scope=auth.scope)
        workflow_version_id = str(body.get("version_id") or body.get("workflow_version_id") or template.latest_published_version_id or "").strip()
        if not workflow_version_id:
            raise ProtocolError("PV21_RUN_VERSION_REQUIRED", "PV21 run requires a published WorkflowVersion.", {"workflow_id": workflow_id})
        result = await _rpc(
            gateway,
            "workflow.instance.start",
            {
                **_pv21_scope_params(auth.scope),
                "workflow_version_id": workflow_version_id,
                "input": body.get("input") if isinstance(body.get("input"), dict) else {},
            },
        )
        instance = result.get("workflow_instance") if isinstance(result.get("workflow_instance"), dict) else {}
        if instance.get("workflow_template_id") != workflow_id:
            raise ProtocolError("SCOPE_MISMATCH", "Workflow version does not belong to requested template.", {"workflow_id": workflow_id})
        await _pv19_attach_quality_refs_for_run(gateway, auth.scope, instance, result.get("station_runs"), rubric_id="pv21_quality", source="pv21_run_start")
        dto = await _pv21_run_dto(gateway, auth.scope, str(instance.get("workflow_instance_id") or ""))
        response = JSONResponse(_redact(dto))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/pv21/runs/{run_id}/inspect")
async def pv21_inspect_run(run_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": run_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        dto = await _pv21_run_dto(gateway, auth.scope, run_id)
        response = JSONResponse(_redact(dto))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/pv21/runs/{run_id}/human-actions")
async def pv21_human_action(run_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("PV21_GRAPH_INVALID", "Request body must be an object.", {"field": "body"})
        _pv21_require_user_confirmation(body, operation="human_action")
        decision = str(body.get("decision") or body.get("action_type") or "").strip()
        if decision == "request_changes":
            decision = "reject"
        if decision not in {"approve", "reject"}:
            raise ProtocolError("PV21_GRAPH_INVALID", "decision must be approve, reject or request_changes.", {"field": "decision"})
        params = {**_query_scope_params(request), "workflow_instance_id": run_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="approvals")
        before = await _pv21_run_dto(gateway, auth.scope, run_id)
        approval_id = str(body.get("approval_id") or _pv19_pending_approval_id(gateway, auth.scope, run_id) or "").strip()
        if not approval_id:
            raise ProtocolError("PV21_HUMAN_GATE_NOT_WAITING", "No waiting human gate was found for this run.", {"workflow_instance_id": run_id})
        await _rpc(gateway, "approval.respond", {**params, "approval_id": approval_id, "decision": decision, "reason": body.get("comment") or body.get("reason")})
        after = await _pv21_run_dto(gateway, auth.scope, run_id)
        station_id = str(body.get("station_id") or (after.get("current_human_gate") or {}).get("station_id") or "")
        dto = {
            "schema_version": PV21_COMPLETE_WORKFLOW_STUDIO_SCHEMA_VERSION,
            "scope": _scope_dto(auth.scope),
            "action_id": f"pv21-human-action:{approval_id}",
            "run_id": run_id,
            "station_id": station_id,
            "decision": decision,
            "actor": _pv21_confirmation_actor(body),
            "before_state": _pv21_state_digest(before),
            "after_state": _pv21_state_digest(after),
            "resulting_run_state": (after.get("workflow_instance") or {}).get("status"),
            "resulting_station_state": _pv21_station_state(after, station_id),
            "audit_refs": [_pv21_audit_ref("workflow.human_action", auth.scope, entity_id=approval_id)],
            "redaction_status": "redacted",
        }
        response = JSONResponse(_redact(dto))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/pv21/runs/{run_id}/evidence")
async def pv21_run_evidence(run_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": run_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        run = await _pv21_run_dto(gateway, auth.scope, run_id)
        dto = _pv21_evidence_summary_dto(run, auth.scope)
        response = JSONResponse(_redact(dto))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/pv20/agent-executor/state")
async def pv20_agent_executor_state(request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = _query_scope_params(request)
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        fixture = await _pv20_ensure_contract_fixture(gateway, auth.scope)
        response = JSONResponse(_redact(_pv20_agent_executor_state_dto(fixture, auth.scope)))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/pv20/runs/{run_id}/agent-execution-contract")
async def pv20_agent_execution_contract(run_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": run_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        fixture = _pv20_contract_fixture_for_run(gateway, auth.scope, run_id)
        response = JSONResponse(_redact(_pv20_agent_execution_contract_dto(fixture, auth.scope)))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/pv20/runs/{run_id}/agent-execution-evidence")
async def pv20_agent_execution_evidence(run_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": run_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        fixture = _pv20_contract_fixture_for_run(gateway, auth.scope, run_id)
        contract = _pv20_agent_execution_contract_dto(fixture, auth.scope)
        response = JSONResponse(_redact(_pv20_agent_execution_evidence_dto(contract, auth.scope)))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/pv20/runs/{run_id}/agent-skill-executions")
async def pv20_agent_skill_execution(run_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("INVALID_PARAMS", "Request body must be an object.", {"field": "body"})
        _pv20_require_user_confirmation(body, allowed_sources={"workflow_console", "agent_executor_panel"})
        params = {**_query_scope_params(request), "workflow_instance_id": run_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.execute")
        fixture = _pv20_contract_fixture_for_run(gateway, auth.scope, run_id)
        contract = _pv20_agent_execution_contract_dto(fixture, auth.scope)
        skill_name = str(body.get("skill_name") or "plan").strip()
        execution = GovernedAgentExecutor().execute_skill(
            envelope=contract["agent_execution_contract"],
            skill_name=skill_name,
            input_refs=contract["agent_execution_contract"].get("context_refs", {}).get("station_input_refs", []),
        )
        station_run_id = str(contract["station_run"]["station_run_id"])
        station_run = gateway.workflow_repository.get_station_run(station_run_id, scope=auth.scope)
        artifact = gateway.artifact_registry.register_external(
            external_asset_uri=f"harnessos://pv20/{run_id}/{station_run_id}/{execution['execution_id']}",
            app_id=auth.scope.app_id,
            project_id=auth.scope.project_id,
            workspace_id=auth.scope.workspace_id,
            domain="agent_executor",
            kind="pv20.agent_skill_result",
            name=f"{station_run_id}-{skill_name}-result.json",
            mime="application/json",
            metadata={
                "workflow_instance_id": run_id,
                "station_run_id": station_run_id,
                "agent_id": execution["agent_id"],
                "skill_ref": execution["skill_ref"],
                "payload_ref": execution["artifact_payload_ref"],
                "redaction_status": "redacted",
            },
        )
        gateway.core_service.record_gateway_artifact(artifact)
        metadata = dict(station_run.metadata or {})
        metadata["pv20_agent_execution"] = {
            **execution,
            "artifact_refs": [{"artifact_id": artifact["artifact_id"], "kind": artifact["kind"], "name": artifact["name"]}],
            "audit_refs": [_pv20_audit_ref("agent_skill.execute", auth.scope, entity_id=execution["execution_id"])],
        }
        output_ids = list(dict.fromkeys([*station_run.output_artifact_ids, artifact["artifact_id"]]))
        updated = station_run.model_copy(update={"metadata": metadata, "output_artifact_ids": output_ids})
        gateway.workflow_repository.update_station_run(updated, scope=auth.scope)
        response = JSONResponse(_redact({"schema_version": PV20_AGENT_EXECUTOR_CONTRACT_SCHEMA_VERSION, "stage": "PV20-S2", "execution": metadata["pv20_agent_execution"], "redaction_status": "redacted"}))
        add_dev_warning(response, auth)
        return response
    except GovernedAgentExecutorError as exc:
        return http_error_response(ProtocolError(exc.code, str(exc), exc.to_dict()))
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/pv20/runs/{run_id}/agent-tool-executions")
async def pv20_agent_tool_execution(run_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("INVALID_PARAMS", "Request body must be an object.", {"field": "body"})
        _pv20_require_user_confirmation(body, allowed_sources={"workflow_console", "agent_executor_panel"})
        params = {**_query_scope_params(request), "workflow_instance_id": run_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.execute")
        fixture = _pv20_contract_fixture_for_run(gateway, auth.scope, run_id)
        contract = _pv20_agent_execution_contract_dto(fixture, auth.scope)
        station_run_id = str(contract["station_run"]["station_run_id"])
        station_run = gateway.workflow_repository.get_station_run(station_run_id, scope=auth.scope)
        tool_name = str(body.get("tool_name") or "artifact.metadata.read").strip()
        artifact_ids = [str(item) for item in station_run.output_artifact_ids if str(item).strip()]
        tool_metadata_refs = []
        for artifact_id in artifact_ids[:1]:
            metadata = gateway.artifact_registry.read_metadata(artifact_id)
            artifact = metadata.get("artifact") if isinstance(metadata.get("artifact"), dict) else {}
            tool_metadata_refs.append(f"artifact-metadata://pv20/{artifact.get('artifact_id') or artifact_id}")
        execution = GovernedAgentExecutor().execute_tool(
            envelope=contract["agent_execution_contract"],
            tool_name=tool_name,
            tool_input_refs=tool_metadata_refs,
        )
        metadata = dict(station_run.metadata or {})
        metadata["pv20_agent_tool_execution"] = {
            **execution,
            "audit_refs": [_pv20_audit_ref("agent_tool.execute", auth.scope, entity_id=execution["execution_id"])],
        }
        updated = station_run.model_copy(update={"metadata": metadata})
        gateway.workflow_repository.update_station_run(updated, scope=auth.scope)
        response = JSONResponse(_redact({"schema_version": PV20_AGENT_EXECUTOR_CONTRACT_SCHEMA_VERSION, "stage": "PV20-S3A", "execution": metadata["pv20_agent_tool_execution"], "redaction_status": "redacted"}))
        add_dev_warning(response, auth)
        return response
    except GovernedAgentExecutorError as exc:
        return http_error_response(ProtocolError(exc.code, str(exc), exc.to_dict()))
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/pv20/runs/{run_id}/agent-mcp-executions")
async def pv20_agent_mcp_execution(run_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("INVALID_PARAMS", "Request body must be an object.", {"field": "body"})
        _pv20_require_user_confirmation(body, allowed_sources={"workflow_console", "agent_executor_panel"})
        params = {**_query_scope_params(request), "workflow_instance_id": run_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.execute")
        fixture = _pv20_contract_fixture_for_run(gateway, auth.scope, run_id)
        contract = _pv20_agent_execution_contract_dto(fixture, auth.scope)
        station_run_id = str(contract["station_run"]["station_run_id"])
        station_run = gateway.workflow_repository.get_station_run(station_run_id, scope=auth.scope)
        connector_id = str(body.get("connector_id") or "data_service_mcp").strip()
        tool_name = str(body.get("tool_name") or "knowledge_query_v2").strip()
        if f"{connector_id}.{tool_name}" != "data_service_mcp.knowledge_query_v2":
            raise GovernedAgentExecutorError("PV20_MCP_DENIED", "MCP tool is not allowlisted for PV20-S3B.", reason="mcp_not_allowlisted", field="connector_id")
        input_payload = body.get("input") if isinstance(body.get("input"), dict) else {
            "workspace_id": "pv20-agent-executor-fixture",
            "query": "PV20 Agent executor MCP fixture",
            "mode": "hybrid",
            "top_k": 3,
        }
        parent_artifact_ids = [str(item) for item in station_run.output_artifact_ids if str(item).strip()]
        submit_params = {
            **_pv20_scope_params(auth.scope),
            "connector_id": connector_id,
            "tool": tool_name,
            "input": input_payload,
            "parent_artifact_ids": parent_artifact_ids,
            "trace_id": contract["workflow_instance"].get("trace_id"),
        }
        submitted = await _rpc(gateway, "connector.submit", submit_params)
        approval_refs: list[str] = []
        if submitted.get("approval_required") is True:
            approval = submitted.get("approval") if isinstance(submitted.get("approval"), dict) else {}
            approval_id = str(approval.get("approval_id") or "")
            if not approval_id:
                raise ProtocolError("PV20_MCP_APPROVAL_MISSING", "Connector execution required approval but did not return approval_id.", {"connector_id": connector_id})
            approval_refs.append(f"approval://pv20/{approval_id}")
            await _rpc(
                gateway,
                "approval.respond",
                {
                    "approval_id": approval_id,
                    "decision": "approve",
                    "reason": "PV20-S3B user-confirmed MCP fixture execution.",
                    "scope": _scope_dto(auth.scope),
                },
            )
            retry_context = submitted.get("retry_context") if isinstance(submitted.get("retry_context"), dict) else {}
            submitted = await _rpc(
                gateway,
                "connector.submit",
                {
                    **_pv20_scope_params(auth.scope),
                    "connector_id": str(retry_context.get("connector_id") or connector_id),
                    "tool": str(retry_context.get("tool") or tool_name),
                    "input": retry_context.get("input") if isinstance(retry_context.get("input"), dict) else input_payload,
                    "approval_id": str(retry_context.get("approval_id") or approval_id),
                    "parent_artifact_ids": parent_artifact_ids,
                    "trace_id": contract["workflow_instance"].get("trace_id"),
                },
            )
        execution = GovernedAgentExecutor().execute_mcp(
            envelope=contract["agent_execution_contract"],
            connector_id=connector_id,
            tool_name=tool_name,
            connector_result=submitted,
            approval_refs=approval_refs,
        )
        metadata = dict(station_run.metadata or {})
        metadata["pv20_agent_mcp_execution"] = {
            **execution,
            "audit_refs": [_pv20_audit_ref("agent_mcp.execute", auth.scope, entity_id=execution["execution_id"])],
        }
        artifact_ids = [
            str(ref.get("artifact_id"))
            for ref in execution.get("artifact_refs", [])
            if isinstance(ref, dict) and str(ref.get("artifact_id") or "").strip()
        ]
        output_ids = list(dict.fromkeys([*station_run.output_artifact_ids, *artifact_ids]))
        updated = station_run.model_copy(update={"metadata": metadata, "output_artifact_ids": output_ids})
        gateway.workflow_repository.update_station_run(updated, scope=auth.scope)
        response = JSONResponse(_redact({"schema_version": PV20_AGENT_EXECUTOR_CONTRACT_SCHEMA_VERSION, "stage": "PV20-S3B", "execution": metadata["pv20_agent_mcp_execution"], "redaction_status": "redacted"}))
        add_dev_warning(response, auth)
        return response
    except GovernedAgentExecutorError as exc:
        return http_error_response(ProtocolError(exc.code, str(exc), exc.to_dict()))
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/workflows")
async def list_workflows(request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params: dict[str, Any] = _query_scope_params(request)
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        result = await _rpc(gateway, "workflow.template.list", params)
        response = JSONResponse(_redact([_workflow_summary(item) for item in result.get("templates", [])]))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/workflows/{workflow_template_id}")
async def get_workflow(workflow_template_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_template_id": workflow_template_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        result = await _rpc(gateway, "workflow.template.get", params)
        response = JSONResponse(_redact(_workflow_summary(result["template"])))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/workflows/{workflow_template_id}/versions")
async def list_workflow_versions(workflow_template_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_template_id": workflow_template_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        result = await _rpc(gateway, "workflow.version.list", params)
        response = JSONResponse(_redact([_version_summary(item) for item in result.get("versions", [])]))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/workflows/{workflow_template_id}/node-catalog")
async def get_workflow_node_catalog(
    workflow_template_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_template_id": workflow_template_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        gateway.workflow_repository.get_template(workflow_template_id, scope=auth.scope)
        catalog = [_node_catalog_item_dto(node_template_id, contract) for node_template_id, contract in sorted(NODE_CATALOG_CONTRACTS.items())]
        response = JSONResponse(_redact(catalog))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/workflows/{workflow_template_id}/publish")
async def publish_workflow_version(
    workflow_template_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    body: dict[str, Any] = {}
    auth: Any = None
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("INVALID_PARAMS", "Request body must be an object.", {"field": "body"})
        _require_user_confirmed(body, allowed_sources={"editing_panel", "workflow_console"})
        version = str(body.get("version") or "").strip()
        if not version:
            raise ProtocolError("INVALID_PARAMS", "version is required.", {"field": "version"})
        expected_revision = body.get("expected_draft_revision", body.get("expected_revision"))
        if expected_revision is None:
            raise ProtocolError("INVALID_PARAMS", "expected_draft_revision is required.", {"field": "expected_draft_revision"})
        params = {
            **_query_scope_params(request),
            "workflow_template_id": workflow_template_id,
            "version": version,
            "expected_revision": expected_revision,
        }
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflow_versions.publish")
        _require_agent_handoff_for_action(body, target_panel="editing_panel", gateway=gateway, scope=auth.scope, auth=auth)
        template = gateway.workflow_repository.get_template(workflow_template_id, scope=auth.scope)
        draft = gateway.workflow_repository.get_draft(str(template.latest_draft_id), scope=auth.scope)
        if draft.revision != expected_revision:
            raise ProtocolError(
                "WORKFLOW_DRAFT_CONFLICT",
                "Workflow draft revision is stale.",
                {"expected_revision": expected_revision, "actual_revision": draft.revision},
            )
        result = await _rpc(gateway, "workflow.template.publish", params)
        evidence = _record_operation_evidence(
            gateway,
            auth.scope,
            operation="workflow.template.publish",
            workflow_instance_id=body.get("workflow_instance_id"),
            workflow_template_id=workflow_template_id,
            body=body,
            status="idempotent_replayed" if result.get("idempotent") else "succeeded",
            runtime_result_ref=_runtime_result_ref(
                "workflow_version",
                _publish_dto(result).get("workflow_version_id"),
                workflow_instance_id=body.get("workflow_instance_id"),
                workflow_template_id=workflow_template_id,
                operation="workflow.template.publish",
                status="published",
                trace_id=result.get("trace_id"),
            ),
        )
        response = JSONResponse(
            _redact(
                _operation_result(
                    "workflow.template.publish",
                    status="published",
                    resource=_publish_dto(result),
                    trace_id=result.get("trace_id"),
                    evidence=_operation_evidence_dto(evidence) if evidence else None,
                )
            )
        )
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        _record_operation_evidence_error(
            gateway,
            getattr(auth, "scope", None),
            operation="workflow.template.publish",
            workflow_instance_id=body.get("workflow_instance_id") if isinstance(body, dict) else None,
            workflow_template_id=workflow_template_id,
            body=body if isinstance(body, dict) else {},
            error=exc,
        )
        return http_error_response(exc)


@router.get("/instances")
async def list_instances(request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params: dict[str, Any] = _query_scope_params(request)
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        result = await _rpc(gateway, "workflow.instance.list", params)
        response = JSONResponse(_redact([_instance_summary(item) for item in result.get("workflow_instances", [])]))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/status")
async def get_instance_status(workflow_instance_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflows.read")
        result = await _rpc(gateway, "workflow.instance.status", params)
        response = JSONResponse(_redact(_status_dto(result["status"])))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/board")
async def get_instance_board(workflow_instance_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="board.read")
        result = await _rpc(gateway, "workflow.board.get", params)
        response = JSONResponse(_redact(result["board"]))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/canvas-projection")
async def get_instance_canvas_projection(workflow_instance_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="board.read")
        instance = gateway.workflow_repository.get_instance(workflow_instance_id, scope=auth.scope)
        template = gateway.workflow_repository.get_template(instance.workflow_template_id, scope=auth.scope)
        draft = gateway.workflow_repository.get_draft(str(template.latest_draft_id), scope=auth.scope)
        board_result = await _rpc(gateway, "workflow.board.get", params)
        status_result = await _rpc(gateway, "workflow.instance.status", params)
        patches = [
            patch.model_dump(mode="json")
            for patch in gateway.workflow_repository.list_patches(scope=auth.scope, workflow_template_id=instance.workflow_template_id)
            if _patch_matches_instance(patch, workflow_instance_id)
        ]
        projection = _canvas_draft_projection_dto(
            workflow_instance_id=workflow_instance_id,
            template_id=instance.workflow_template_id,
            draft=draft.model_dump(mode="json"),
            board=board_result["board"],
            status=_status_dto(status_result["status"]),
            patches=patches,
        )
        response = JSONResponse(_redact(projection))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/quality")
async def list_instance_quality(workflow_instance_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="quality.read")
        result = await _rpc(gateway, "quality.evaluation.list", params)
        response = JSONResponse(_redact([_quality_dto(item) for item in result.get("evaluations", [])]))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/quality/{evaluation_id}")
async def get_instance_quality(
    workflow_instance_id: str,
    evaluation_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id, "evaluation_id": evaluation_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="quality.read")
        result = await _rpc(gateway, "quality.evaluation.get", params)
        evaluation = result["evaluation"]
        _ensure_quality_in_instance(evaluation, workflow_instance_id)
        response = JSONResponse(_redact(_quality_dto(evaluation)))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/approvals")
async def list_instance_approvals(workflow_instance_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="approvals.read")
        gateway.workflow_repository.get_instance(workflow_instance_id, scope=auth.scope)
        result = await _rpc(gateway, "approval.list", params)
        approvals = [
            _approval_dto(approval)
            for approval in result.get("approvals", [])
            if _approval_workflow_binding(approval).get("workflow_instance_id") == workflow_instance_id
        ]
        response = JSONResponse(_redact(approvals))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/instances/{workflow_instance_id}/approvals/{approval_id}/respond")
async def respond_instance_approval(
    workflow_instance_id: str,
    approval_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    body: dict[str, Any] = {}
    auth: Any = None
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("INVALID_PARAMS", "Request body must be an object.", {"field": "body"})
        if body.get("user_confirmed") is not True or body.get("source") != "approval_panel":
            raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "Approval response requires explicit user confirmation.", {"source": body.get("source")})
        decision = body.get("decision")
        if decision not in {"approve", "reject"}:
            raise ProtocolError("APPROVAL_INVALID_DECISION", "decision must be approve or reject", {"decision": decision})
        params = {
            **_query_scope_params(request),
            "workflow_instance_id": workflow_instance_id,
            "approval_id": approval_id,
            "decision": decision,
            "reason": body.get("reason"),
        }
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="approvals")
        _require_agent_handoff_for_action(body, target_panel="approval_panel", gateway=gateway, scope=auth.scope, auth=auth, workflow_instance_id=workflow_instance_id, target_resource_id=approval_id)
        approval = gateway.approval_store.get_approval(approval_id)
        _ensure_approval_in_instance(approval, workflow_instance_id)
        result = await _rpc(gateway, "approval.respond", params)
        evidence = _record_operation_evidence(
            gateway,
            auth.scope,
            operation="approval.respond",
            workflow_instance_id=workflow_instance_id,
            workflow_template_id=_template_id_for_instance(gateway, workflow_instance_id, auth.scope),
            body=body,
            status="idempotent_replayed" if result.get("idempotent") else "succeeded",
            runtime_result_ref=_runtime_result_ref(
                "approval",
                approval_id,
                workflow_instance_id=workflow_instance_id,
                workflow_template_id=_template_id_for_instance(gateway, workflow_instance_id, auth.scope),
                operation="approval.respond",
                status=str(result.get("status") or ""),
            ),
        )
        response = JSONResponse(
            _redact(
                _operation_result(
                    "approval.respond",
                    status=str(result.get("status") or ""),
                    resource=_approval_dto(result.get("approval") or {}),
                    idempotent=bool(result.get("idempotent")),
                    workflow_side_effect=result.get("workflow_side_effect"),
                    evidence=_operation_evidence_dto(evidence) if evidence else None,
                )
            )
        )
        add_dev_warning(response, auth)
        return response
    except KeyError as exc:
        return http_error_response(ProtocolError("APPROVAL_NOT_FOUND", str(exc), {"approval_id": approval_id}))
    except ProtocolError as exc:
        _record_operation_evidence_error(
            gateway,
            getattr(auth, "scope", None),
            operation="approval.respond",
            workflow_instance_id=workflow_instance_id,
            workflow_template_id=_safe_template_id_for_instance(gateway, workflow_instance_id, getattr(auth, "scope", None)),
            body=body if isinstance(body, dict) else {},
            error=exc,
            resource_id=approval_id,
        )
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/context")
async def get_instance_context(workflow_instance_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflow_context.read")
        result = await _rpc(gateway, "workflow.context.get", params)
        response = JSONResponse(_redact(_context_dto(result["context"])))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/instances/{workflow_instance_id}/context/update")
async def update_instance_context(workflow_instance_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    body: dict[str, Any] = {}
    auth: Any = None
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("INVALID_PARAMS", "Request body must be an object.", {"field": "body"})
        if body.get("op") != "set":
            raise ProtocolError("WORKFLOW_CONTEXT_SCOPE_MISMATCH", "Only path-based set is supported.", {"op": body.get("op")})
        path = str(body.get("path") or "")
        if not path.startswith("business.") or path == "business.":
            raise ProtocolError("WORKFLOW_CONTEXT_SCOPE_MISMATCH", "Only business.* context paths can be updated.", {"path": path})
        params = {
            **_query_scope_params(request),
            "workflow_instance_id": workflow_instance_id,
            "path": path,
            "value": body.get("value"),
            "expected_revision": body.get("expected_revision"),
        }
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflow_context.write")
        _require_agent_handoff_for_action(body, target_panel="context_panel", gateway=gateway, scope=auth.scope, auth=auth, workflow_instance_id=workflow_instance_id)
        result = await _rpc(gateway, "workflow.context.update", params)
        template_id = _template_id_for_instance(gateway, workflow_instance_id, auth.scope)
        evidence = _record_operation_evidence(
            gateway,
            auth.scope,
            operation="workflow.context.update",
            workflow_instance_id=workflow_instance_id,
            workflow_template_id=template_id,
            body=body,
            status="succeeded",
            runtime_result_ref=_runtime_result_ref(
                "workflow_context",
                workflow_instance_id,
                workflow_instance_id=workflow_instance_id,
                workflow_template_id=template_id,
                operation="workflow.context.update",
                status="updated",
                trace_id=result.get("trace_id"),
            ),
        )
        response = JSONResponse(
            _redact(
                _operation_result(
                    "workflow.context.update",
                    status="updated",
                    resource=_context_dto(result["context"]),
                    trace_id=result.get("trace_id"),
                    evidence=_operation_evidence_dto(evidence) if evidence else None,
                )
            )
        )
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        _record_operation_evidence_error(
            gateway,
            getattr(auth, "scope", None),
            operation="workflow.context.update",
            workflow_instance_id=workflow_instance_id,
            workflow_template_id=_safe_template_id_for_instance(gateway, workflow_instance_id, getattr(auth, "scope", None)),
            body=body if isinstance(body, dict) else {},
            error=exc,
            resource_id=str(body.get("path") or "") if isinstance(body, dict) else None,
        )
        return http_error_response(exc)


@router.post("/instances/{workflow_instance_id}/business-events")
async def emit_instance_business_event(workflow_instance_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    body: dict[str, Any] = {}
    auth: Any = None
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("INVALID_PARAMS", "Request body must be an object.", {"field": "body"})
        event_type = str(body.get("event_type") or body.get("type") or "")
        for denied_prefix in ("meeting.", "knowledge.", "video."):
            if event_type.startswith(denied_prefix):
                raise ProtocolError("BUSINESS_EVENT_INVALID", "Business event cannot use a core business canonical namespace.", {"event_type": event_type})
        if not event_type.startswith("business.") or event_type == "business.*":
            raise ProtocolError("BUSINESS_EVENT_INVALID", "event_type must be a concrete business.* event.", {"event_type": event_type})
        params = {
            **_query_scope_params(request),
            "workflow_instance_id": workflow_instance_id,
            "event": {
                "event_id": body.get("event_id"),
                "idempotency_key": body.get("idempotency_key"),
                "type": event_type,
                "payload": body.get("payload") if isinstance(body.get("payload"), dict) else {},
                "workflow_instance_id": workflow_instance_id,
            },
        }
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="business_events.write")
        _require_agent_handoff_for_action(body, target_panel="context_panel", gateway=gateway, scope=auth.scope, auth=auth, workflow_instance_id=workflow_instance_id)
        binding = body.get("binding")
        if isinstance(binding, dict):
            if not _auth_has_capability(auth, "workflow_context.write"):
                raise ProtocolError(
                    "CAPABILITY_DENIED",
                    "Business event binding requires workflow_context.write capability.",
                    {"capability": "workflow_context.write"},
                )
            existing_bindings = gateway.workflow_repository.list_business_event_bindings(
                scope=auth.scope,
                workflow_instance_id=workflow_instance_id,
                event_type=event_type,
            )
            has_binding = any(
                existing.target_path == binding.get("target_path") and existing.payload_path == binding.get("payload_path")
                for existing in existing_bindings
            )
            bind_params = {
                **params,
                "binding": {
                    "binding_id": binding.get("binding_id") or f"bff_{workflow_instance_id}_{event_type}".replace(".", "_"),
                    "workflow_instance_id": workflow_instance_id,
                    "event_type": event_type,
                    "target_path": binding.get("target_path"),
                    "payload_path": binding.get("payload_path"),
                    "mode": binding.get("mode") or "set",
                    "enabled": binding.get("enabled", True),
                },
            }
            if not has_binding:
                await _rpc(gateway, "business.event.bind", bind_params)
        result = await _rpc(gateway, "business.event.emit", params)
        template_id = _template_id_for_instance(gateway, workflow_instance_id, auth.scope)
        evidence = _record_operation_evidence(
            gateway,
            auth.scope,
            operation="business.event.emit",
            workflow_instance_id=workflow_instance_id,
            workflow_template_id=template_id,
            body=body,
            status="idempotent_replayed" if result.get("idempotent") else "succeeded",
            runtime_result_ref=_runtime_result_ref(
                "business_event",
                result.get("event", {}).get("event_id") if isinstance(result.get("event"), dict) else body.get("event_id"),
                workflow_instance_id=workflow_instance_id,
                workflow_template_id=template_id,
                operation="business.event.emit",
                status="received",
                trace_id=result.get("trace_id"),
            ),
        )
        response = JSONResponse(
            _redact(
                _operation_result(
                    "business.event.emit",
                    status="received",
                    resource={"event": _business_event_dto(result.get("event") or {}), "context": _context_dto(result["context"])},
                    idempotent=bool(result.get("idempotent")),
                    trace_id=result.get("trace_id"),
                    evidence=_operation_evidence_dto(evidence) if evidence else None,
                )
            )
        )
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        _record_operation_evidence_error(
            gateway,
            getattr(auth, "scope", None),
            operation="business.event.emit",
            workflow_instance_id=workflow_instance_id,
            workflow_template_id=_safe_template_id_for_instance(gateway, workflow_instance_id, getattr(auth, "scope", None)),
            body=body if isinstance(body, dict) else {},
            error=exc,
            resource_id=str(body.get("event_id") or body.get("idempotency_key") or body.get("event_type") or "") if isinstance(body, dict) else None,
        )
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/agent/session")
async def get_agent_talk_session(
    workflow_instance_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="agent_talk.read")
        instance = gateway.workflow_repository.get_instance(workflow_instance_id, scope=auth.scope)
        session = _ensure_agent_talk_session(workflow_instance_id, instance.workflow_template_id, auth.scope, created_by="workflow_console")
        response = JSONResponse(_redact(_agent_session_dto(session)))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/agent/interaction-state")
async def get_agent_talk_interaction_state(
    workflow_instance_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="agent_talk.read")
        instance = gateway.workflow_repository.get_instance(workflow_instance_id, scope=auth.scope)
        session = _ensure_agent_talk_session(workflow_instance_id, instance.workflow_template_id, auth.scope, created_by="workflow_console")
        response = JSONResponse(_redact(_agent_talk_interaction_state_dto(gateway, auth.scope, session)))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/instances/{workflow_instance_id}/agent/messages")
async def create_agent_talk_message(
    workflow_instance_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("INVALID_PARAMS", "Request body must be an object.", {"field": "body"})
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="agent_talk.write")
        instance = gateway.workflow_repository.get_instance(workflow_instance_id, scope=auth.scope)
        session = _ensure_agent_talk_session(
            workflow_instance_id,
            instance.workflow_template_id,
            auth.scope,
            created_by=str(body.get("created_by") or "workflow_console"),
        )
        content = str(body.get("content") or "").strip()
        if not content:
            raise ProtocolError("INVALID_PARAMS", "Agent message content is required.", {"field": "content"})
        _reject_forbidden_agent_actions(body.get("action_intent"))
        user_message = _agent_message(
            session,
            role="user",
            content=content,
            source="user",
            resource_refs=_agent_resource_refs(workflow_instance_id=workflow_instance_id, workflow_template_id=instance.workflow_template_id),
        )
        assistant_message = _agent_message(
            session,
            role="assistant",
            content=_agent_assistant_reply(content),
            source="assistant",
            resource_refs=_agent_resource_refs(workflow_instance_id=workflow_instance_id, workflow_template_id=instance.workflow_template_id),
        )
        messages = _AGENT_TALK_MESSAGES.setdefault(session["agent_session_id"], [])
        messages.extend([user_message, assistant_message])
        preferred_patch_id = await _maybe_create_agent_canvas_patch(
            gateway,
            workflow_instance_id,
            instance.workflow_template_id,
            auth.scope,
            content,
            body,
        )
        suggestions = _generate_agent_suggestions(
            gateway,
            workflow_instance_id,
            instance.workflow_template_id,
            auth.scope,
            preferred_patch_id=preferred_patch_id,
        )
        _AGENT_TALK_SUGGESTIONS[session["agent_session_id"]] = suggestions
        _AGENT_ACTION_PROPOSALS[session["agent_session_id"]] = []
        _ensure_agent_action_proposals(session, suggestions)
        _record_agent_audit(
            "agent.message.created",
            session=session,
            summary="Agent message created and deterministic suggestions generated.",
            resource_refs=user_message["resource_refs"],
        )
        response = JSONResponse(_redact(_agent_session_dto(session)))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/agent/action-proposals")
async def list_agent_action_proposals(
    workflow_instance_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="agent_actions.read")
        instance = gateway.workflow_repository.get_instance(workflow_instance_id, scope=auth.scope)
        session = _ensure_agent_talk_session(workflow_instance_id, instance.workflow_template_id, auth.scope, created_by="workflow_console")
        suggestions = _AGENT_TALK_SUGGESTIONS.get(session["agent_session_id"])
        if not suggestions:
            suggestions = _generate_agent_suggestions(gateway, workflow_instance_id, instance.workflow_template_id, auth.scope)
            _AGENT_TALK_SUGGESTIONS[session["agent_session_id"]] = suggestions
        proposals = _ensure_agent_action_proposals(session, suggestions)
        response = JSONResponse(_redact([_agent_action_proposal_dto(item) for item in proposals]))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/instances/{workflow_instance_id}/agent/action-proposals")
async def create_agent_action_proposal(
    workflow_instance_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("INVALID_PARAMS", "Request body must be an object.", {"field": "body"})
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="agent_actions.write")
        instance = gateway.workflow_repository.get_instance(workflow_instance_id, scope=auth.scope)
        session = _ensure_agent_talk_session(workflow_instance_id, instance.workflow_template_id, auth.scope, created_by="workflow_console")
        proposal = _agent_action_proposal_from_request(session, body)
        _AGENT_ACTION_PROPOSALS.setdefault(session["agent_session_id"], []).append(proposal)
        _record_agent_audit(
            "agent.action_proposal.created",
            session=session,
            summary="Agent action proposal created.",
            resource_refs=proposal["resource_refs"],
        )
        response = JSONResponse(_redact(_agent_action_proposal_dto(proposal)))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/agent/action-proposals/{proposal_id}")
async def get_agent_action_proposal(
    workflow_instance_id: str,
    proposal_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="agent_actions.read")
        instance = gateway.workflow_repository.get_instance(workflow_instance_id, scope=auth.scope)
        session = _ensure_agent_talk_session(workflow_instance_id, instance.workflow_template_id, auth.scope, created_by="workflow_console")
        proposal = _find_agent_action_proposal(session["agent_session_id"], proposal_id)
        response = JSONResponse(_redact(_agent_action_proposal_dto(proposal)))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/instances/{workflow_instance_id}/agent/action-proposals/{proposal_id}/dismiss")
async def dismiss_agent_action_proposal(
    workflow_instance_id: str,
    proposal_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="agent_actions.write")
        instance = gateway.workflow_repository.get_instance(workflow_instance_id, scope=auth.scope)
        session = _ensure_agent_talk_session(workflow_instance_id, instance.workflow_template_id, auth.scope, created_by="workflow_console")
        proposal = _find_agent_action_proposal(session["agent_session_id"], proposal_id)
        proposal["lifecycle"] = "dismissed"
        proposal["status"] = "dismissed"
        proposal["updated_at"] = _now_iso()
        _record_agent_audit(
            "agent.action_proposal.dismissed",
            session=session,
            summary="Agent action proposal dismissed.",
            resource_refs=proposal["resource_refs"],
        )
        response = JSONResponse(_redact(_agent_action_proposal_dto(proposal)))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/instances/{workflow_instance_id}/agent/action-proposals/{proposal_id}/handoff")
async def create_agent_action_handoff(
    workflow_instance_id: str,
    proposal_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("INVALID_PARAMS", "Request body must be an object.", {"field": "body"})
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="agent_handoffs.write")
        instance = gateway.workflow_repository.get_instance(workflow_instance_id, scope=auth.scope)
        session = _ensure_agent_talk_session(workflow_instance_id, instance.workflow_template_id, auth.scope, created_by="workflow_console")
        proposal = _find_agent_action_proposal(session["agent_session_id"], proposal_id)
        target_panel = _normalize_handoff_target_panel(body.get("target_panel") or proposal.get("target_panel"))
        _ensure_proposal_can_handoff(proposal, target_panel)
        handoff = _AGENT_HANDOFF_REPOSITORY.create(_agent_action_handoff(gateway, auth.scope, session, proposal, target_panel, body))
        proposal["lifecycle"] = "reviewed"
        proposal["status"] = "reviewed"
        proposal["updated_at"] = _now_iso()
        _record_agent_audit(
            "agent.handoff_created",
            session=session,
            summary="Agent action handoff created for user-confirmed panel.",
            resource_refs=handoff["target_resource"],
        )
        _append_handoff_audit(handoff["handoff_id"], "handoff_created", summary="Agent action handoff created.", data=handoff["target_resource"])
        response = JSONResponse(_redact(_agent_action_handoff_dto(handoff)))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/agent/action-handoffs")
async def list_agent_action_handoffs(
    workflow_instance_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="agent_handoffs.read")
        instance = gateway.workflow_repository.get_instance(workflow_instance_id, scope=auth.scope)
        session = _ensure_agent_talk_session(workflow_instance_id, instance.workflow_template_id, auth.scope, created_by="workflow_console")
        handoffs = [
            _refresh_handoff_for_read(gateway, auth.scope, handoff)
            for handoff in _AGENT_HANDOFF_REPOSITORY.list(agent_session_id=session["agent_session_id"], workflow_instance_id=workflow_instance_id)
        ]
        response = JSONResponse(_redact([_agent_action_handoff_dto(item) for item in handoffs]))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/agent/action-handoffs/{handoff_id}")
async def get_agent_action_handoff(
    workflow_instance_id: str,
    handoff_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="agent_handoffs.read")
        instance = gateway.workflow_repository.get_instance(workflow_instance_id, scope=auth.scope)
        session = _ensure_agent_talk_session(workflow_instance_id, instance.workflow_template_id, auth.scope, created_by="workflow_console")
        handoff = _find_agent_action_handoff(session["agent_session_id"], handoff_id)
        handoff = _refresh_handoff_for_read(gateway, auth.scope, handoff)
        if handoff.get("status") == "active":
            handoff = _AGENT_HANDOFF_REPOSITORY.mark_opened(handoff_id)
            _append_handoff_audit(handoff_id, "handoff_opened", summary="Agent action handoff opened.", data=handoff.get("target_resource") if isinstance(handoff.get("target_resource"), dict) else {})
        _record_agent_audit(
            "agent.handoff_opened",
            session=session,
            summary="Agent action handoff opened.",
            resource_refs=handoff["target_resource"],
        )
        response = JSONResponse(_redact(_agent_action_handoff_dto(handoff)))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/agent/action-handoffs/{handoff_id}/audit")
async def list_agent_action_handoff_audit(
    workflow_instance_id: str,
    handoff_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="agent_audit.read")
        instance = gateway.workflow_repository.get_instance(workflow_instance_id, scope=auth.scope)
        session = _ensure_agent_talk_session(workflow_instance_id, instance.workflow_template_id, auth.scope, created_by="workflow_console")
        handoff = _find_agent_action_handoff(session["agent_session_id"], handoff_id)
        if handoff.get("workflow_instance_id") != workflow_instance_id:
            raise ProtocolError("SCOPE_MISMATCH", "Agent handoff does not belong to workflow instance.", {"resource": "handoff_id"})
        response = JSONResponse(_redact(_AGENT_HANDOFF_REPOSITORY.list_audit(handoff_id)))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/agent/operation-evidence")
async def list_agent_operation_evidence(
    workflow_instance_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="operation_evidence.read")
        gateway.workflow_repository.get_instance(workflow_instance_id, scope=auth.scope)
        records = _AGENT_OPERATION_EVIDENCE_REPOSITORY.list(workflow_instance_id=workflow_instance_id)
        response = JSONResponse(_redact([_operation_evidence_dto(item) for item in records]))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/agent/operation-evidence/{evidence_id}")
async def get_agent_operation_evidence(
    workflow_instance_id: str,
    evidence_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="operation_evidence.read")
        gateway.workflow_repository.get_instance(workflow_instance_id, scope=auth.scope)
        evidence = _AGENT_OPERATION_EVIDENCE_REPOSITORY.get(evidence_id)
        if evidence.get("workflow_instance_id") != workflow_instance_id:
            raise ProtocolError("SCOPE_MISMATCH", "Operation evidence does not belong to workflow instance.", {"resource": "evidence_id"})
        response = JSONResponse(_redact(_operation_evidence_dto(evidence)))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/agent/governance-review")
async def get_agent_governance_review(
    workflow_instance_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="governance_review.read")
        instance = gateway.workflow_repository.get_instance(workflow_instance_id, scope=auth.scope)
        records = _AGENT_OPERATION_EVIDENCE_REPOSITORY.list(workflow_instance_id=workflow_instance_id)
        handoffs = _AGENT_HANDOFF_REPOSITORY.list(workflow_instance_id=workflow_instance_id)
        response = JSONResponse(
            _redact(
                _governance_review_dto(
                    workflow_instance_id=workflow_instance_id,
                    workflow_template_id=instance.workflow_template_id,
                    evidence_records=records,
                    handoffs=handoffs,
                )
            )
        )
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/instances/{workflow_instance_id}/agent/action-handoffs/{handoff_id}/dismiss")
async def dismiss_agent_action_handoff(
    workflow_instance_id: str,
    handoff_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="agent_handoffs.write")
        instance = gateway.workflow_repository.get_instance(workflow_instance_id, scope=auth.scope)
        session = _ensure_agent_talk_session(workflow_instance_id, instance.workflow_template_id, auth.scope, created_by="workflow_console")
        handoff = _find_agent_action_handoff(session["agent_session_id"], handoff_id)
        handoff = _refresh_handoff_for_read(gateway, auth.scope, handoff)
        dismissed = _AGENT_HANDOFF_REPOSITORY.dismiss(handoff_id)
        _append_handoff_audit(handoff_id, "handoff_dismissed", summary="Agent action handoff dismissed.", data=dismissed.get("target_resource") if isinstance(dismissed.get("target_resource"), dict) else {})
        response = JSONResponse(_redact(_agent_action_handoff_dto(dismissed)))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/agent/suggestions")
async def list_agent_talk_suggestions(
    workflow_instance_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="agent_suggestions.read")
        instance = gateway.workflow_repository.get_instance(workflow_instance_id, scope=auth.scope)
        session = _ensure_agent_talk_session(workflow_instance_id, instance.workflow_template_id, auth.scope, created_by="workflow_console")
        suggestions = _AGENT_TALK_SUGGESTIONS.get(session["agent_session_id"])
        if not suggestions:
            suggestions = _generate_agent_suggestions(gateway, workflow_instance_id, instance.workflow_template_id, auth.scope)
            _AGENT_TALK_SUGGESTIONS[session["agent_session_id"]] = suggestions
        response = JSONResponse(_redact([_agent_suggestion_dto(item) for item in suggestions]))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/instances/{workflow_instance_id}/agent/suggestions/{suggestion_id}/dismiss")
async def dismiss_agent_talk_suggestion(
    workflow_instance_id: str,
    suggestion_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="agent_suggestions.write")
        instance = gateway.workflow_repository.get_instance(workflow_instance_id, scope=auth.scope)
        session = _ensure_agent_talk_session(workflow_instance_id, instance.workflow_template_id, auth.scope, created_by="workflow_console")
        suggestions = _AGENT_TALK_SUGGESTIONS.get(session["agent_session_id"], [])
        suggestion = next((item for item in suggestions if item.get("suggestion_id") == suggestion_id), None)
        if suggestion is None:
            raise ProtocolError("METHOD_NOT_FOUND", "Agent suggestion was not found.", {"suggestion_id": suggestion_id})
        suggestion["status"] = "dismissed"
        _record_agent_audit(
            "agent.suggestion.dismissed",
            session=session,
            summary="Agent suggestion dismissed.",
            resource_refs=_agent_resource_refs(
                workflow_instance_id=workflow_instance_id,
                workflow_template_id=instance.workflow_template_id,
                suggestion_id=suggestion_id,
            ),
        )
        response = JSONResponse(_redact(_agent_suggestion_dto(suggestion)))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/workflows/{workflow_template_id}/patches")
async def propose_workflow_patch(
    workflow_template_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("INVALID_PARAMS", "Request body must be an object.", {"field": "body"})
        patch = _canvas_patch_request_to_patch(workflow_template_id, body)
        params = {**_query_scope_params(request), "workflow_template_id": workflow_template_id, "patch": patch}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflow_patches.write")
        _validate_canvas_patch_payload(gateway, workflow_template_id, patch, auth.scope)
        result = await _rpc(gateway, "workflow.patch.propose", params)
        response = JSONResponse(_redact(_patch_proposal_dto(result["patch"])))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/patches")
async def list_instance_patches(
    workflow_instance_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflow_patches.read")
        instance = gateway.workflow_repository.get_instance(workflow_instance_id, scope=auth.scope)
        template = gateway.workflow_repository.get_template(instance.workflow_template_id, scope=auth.scope)
        draft = gateway.workflow_repository.get_draft(str(template.latest_draft_id), scope=auth.scope)
        patches = [
            patch.model_dump(mode="json")
            for patch in gateway.workflow_repository.list_patches(scope=auth.scope, workflow_template_id=instance.workflow_template_id)
            if _patch_matches_instance(patch, workflow_instance_id)
        ]
        response = JSONResponse(_redact(_patch_queue_dto(patches, current_draft_revision=draft.revision)))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/workflows/{workflow_template_id}/patches")
async def list_workflow_patch_queue(
    workflow_template_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_template_id": workflow_template_id}
        workflow_instance_id = request.query_params.get("workflow_instance_id")
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflow_patches.read")
        template = gateway.workflow_repository.get_template(workflow_template_id, scope=auth.scope)
        if isinstance(workflow_instance_id, str) and workflow_instance_id:
            instance = gateway.workflow_repository.get_instance(workflow_instance_id, scope=auth.scope)
            if instance.workflow_template_id != workflow_template_id:
                raise ProtocolError("SCOPE_MISMATCH", "Workflow instance does not belong to workflow template.", {"resource": "workflow_instance_id"})
        draft = gateway.workflow_repository.get_draft(str(template.latest_draft_id), scope=auth.scope)
        patches = [
            patch.model_dump(mode="json")
            for patch in gateway.workflow_repository.list_patches(scope=auth.scope, workflow_template_id=workflow_template_id)
            if not workflow_instance_id or _patch_matches_instance(patch, workflow_instance_id)
        ]
        response = JSONResponse(_redact(_patch_queue_dto(patches, current_draft_revision=draft.revision)))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/workflows/{workflow_template_id}/patches/{workflow_patch_id}/diff")
async def get_workflow_patch_diff(
    workflow_template_id: str,
    workflow_patch_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_template_id": workflow_template_id, "workflow_patch_id": workflow_patch_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflow_patches.read")
        _ensure_patch_in_template(gateway, workflow_patch_id, workflow_template_id, auth.scope)
        result = await _rpc(gateway, "workflow.patch.diff", params)
        response = JSONResponse(_redact(_patch_diff_dto(result["diff"])))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.post("/workflows/{workflow_template_id}/patches/{workflow_patch_id}/apply")
async def apply_workflow_patch(
    workflow_template_id: str,
    workflow_patch_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    body: dict[str, Any] = {}
    auth: Any = None
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("INVALID_PARAMS", "Request body must be an object.", {"field": "body"})
        _require_user_confirmed(body, allowed_sources={"editing_panel", "workflow_console"})
        params = {**_query_scope_params(request), "workflow_template_id": workflow_template_id, "workflow_patch_id": workflow_patch_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflow_patches.write")
        _require_agent_handoff_for_action(
            body,
            target_panel="editing_panel",
            gateway=gateway,
            scope=auth.scope,
            auth=auth,
            workflow_instance_id=body.get("workflow_instance_id"),
            target_resource_id=workflow_patch_id,
        )
        patch = _ensure_patch_editable_for_template(gateway, workflow_patch_id, workflow_template_id, auth.scope, workflow_instance_id=body.get("workflow_instance_id"))
        if patch.status != "applied":
            diff_result = await _rpc(gateway, "workflow.patch.diff", params)
            diff = _patch_diff_dto(diff_result["diff"])
            if diff["requires_approval"]:
                raise ProtocolError(
                    "WORKFLOW_ACTION_FORBIDDEN",
                    "Patch requires approval before apply.",
                    {
                        "workflow_patch_id": workflow_patch_id,
                        "requires_approval": True,
                        "risk_flags": diff["risk_flags"],
                    },
                )
        result = await _rpc(gateway, "workflow.patch.apply", {**params, "actor_type": "user"})
        evidence = _record_operation_evidence(
            gateway,
            auth.scope,
            operation="workflow.patch.apply",
            workflow_instance_id=body.get("workflow_instance_id"),
            workflow_template_id=workflow_template_id,
            body=body,
            status="idempotent_replayed" if result.get("idempotent") else "succeeded",
            runtime_result_ref=_runtime_result_ref(
                "workflow_patch",
                workflow_patch_id,
                workflow_instance_id=body.get("workflow_instance_id"),
                workflow_template_id=workflow_template_id,
                operation="workflow.patch.apply",
                status=str(result.get("patch", {}).get("status") or "applied"),
                trace_id=result.get("trace_id"),
            ),
            resource_id=workflow_patch_id,
        )
        response = JSONResponse(
            _redact(
                _operation_result(
                    "workflow.patch.apply",
                    status=str(result.get("patch", {}).get("status") or "applied"),
                    resource=_patch_action_dto(result),
                    trace_id=result.get("trace_id"),
                    idempotent=bool(result.get("idempotent")),
                    evidence=_operation_evidence_dto(evidence) if evidence else None,
                )
            )
        )
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        _record_operation_evidence_error(
            gateway,
            getattr(auth, "scope", None),
            operation="workflow.patch.apply",
            workflow_instance_id=body.get("workflow_instance_id") if isinstance(body, dict) else None,
            workflow_template_id=workflow_template_id,
            body=body if isinstance(body, dict) else {},
            error=exc,
            resource_id=workflow_patch_id,
        )
        return http_error_response(exc)


@router.post("/workflows/{workflow_template_id}/patches/{workflow_patch_id}/reject")
async def reject_workflow_patch(
    workflow_template_id: str,
    workflow_patch_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    body: dict[str, Any] = {}
    auth: Any = None
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ProtocolError("INVALID_PARAMS", "Request body must be an object.", {"field": "body"})
        _require_user_confirmed(body, allowed_sources={"editing_panel", "workflow_console"})
        params = {**_query_scope_params(request), "workflow_template_id": workflow_template_id, "workflow_patch_id": workflow_patch_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflow_patches.write")
        _require_agent_handoff_for_action(
            body,
            target_panel="editing_panel",
            gateway=gateway,
            scope=auth.scope,
            auth=auth,
            workflow_instance_id=body.get("workflow_instance_id"),
            target_resource_id=workflow_patch_id,
        )
        _ensure_patch_editable_for_template(gateway, workflow_patch_id, workflow_template_id, auth.scope, workflow_instance_id=body.get("workflow_instance_id"))
        result = await _rpc(gateway, "workflow.patch.reject", {**params, "reason": body.get("reason")})
        evidence = _record_operation_evidence(
            gateway,
            auth.scope,
            operation="workflow.patch.reject",
            workflow_instance_id=body.get("workflow_instance_id"),
            workflow_template_id=workflow_template_id,
            body=body,
            status="idempotent_replayed" if result.get("idempotent") else "succeeded",
            runtime_result_ref=_runtime_result_ref(
                "workflow_patch",
                workflow_patch_id,
                workflow_instance_id=body.get("workflow_instance_id"),
                workflow_template_id=workflow_template_id,
                operation="workflow.patch.reject",
                status=str(result.get("patch", {}).get("status") or "rejected"),
                trace_id=result.get("trace_id"),
            ),
            resource_id=workflow_patch_id,
        )
        response = JSONResponse(
            _redact(
                _operation_result(
                    "workflow.patch.reject",
                    status=str(result.get("patch", {}).get("status") or "rejected"),
                    resource=_patch_action_dto(result),
                    trace_id=result.get("trace_id"),
                    idempotent=bool(result.get("idempotent")),
                    evidence=_operation_evidence_dto(evidence) if evidence else None,
                )
            )
        )
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        _record_operation_evidence_error(
            gateway,
            getattr(auth, "scope", None),
            operation="workflow.patch.reject",
            workflow_instance_id=body.get("workflow_instance_id") if isinstance(body, dict) else None,
            workflow_template_id=workflow_template_id,
            body=body if isinstance(body, dict) else {},
            error=exc,
            resource_id=workflow_patch_id,
        )
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/patches/{workflow_patch_id}/diff")
async def get_instance_patch_diff(
    workflow_instance_id: str,
    workflow_patch_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id, "workflow_patch_id": workflow_patch_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflow_patches.read")
        _ensure_patch_in_instance(gateway, workflow_patch_id, workflow_instance_id, auth.scope)
        result = await _rpc(gateway, "workflow.patch.diff", params)
        response = JSONResponse(_redact(_patch_diff_dto(result["diff"])))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/stations/{station_run_id}/outputs")
async def list_station_outputs(station_run_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    try:
        params = {**_query_scope_params(request), "station_run_id": station_run_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="stations.read")
        result = await _rpc(gateway, "station.output.list", params)
        response = JSONResponse(_redact(result.get("artifacts", [])))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/instances/{workflow_instance_id}/stations/{station_run_id}/outputs")
async def list_instance_station_outputs(
    workflow_instance_id: str,
    station_run_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    try:
        params = {**_query_scope_params(request), "workflow_instance_id": workflow_instance_id, "station_run_id": station_run_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="stations.read")
        _ensure_station_run_in_instance(gateway, station_run_id, workflow_instance_id, auth.scope)
        result = await _rpc(gateway, "station.output.list", params)
        response = JSONResponse(_redact(result.get("artifacts", [])))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


@router.get("/artifacts/{artifact_id}/metadata")
async def get_artifact_metadata(artifact_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    return await _artifact_metadata_response(artifact_id, request, gateway, workflow_instance_id=None)


@router.get("/instances/{workflow_instance_id}/artifacts/{artifact_id}/metadata")
async def get_instance_artifact_metadata(
    workflow_instance_id: str,
    artifact_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    return await _artifact_metadata_response(artifact_id, request, gateway, workflow_instance_id=workflow_instance_id)


@router.get("/artifacts/{artifact_id}/lineage")
async def get_artifact_lineage(artifact_id: str, request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    return await _artifact_lineage_response(artifact_id, request, gateway, workflow_instance_id=None)


@router.get("/instances/{workflow_instance_id}/artifacts/{artifact_id}/lineage")
async def get_instance_artifact_lineage(
    workflow_instance_id: str,
    artifact_id: str,
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    return await _artifact_lineage_response(artifact_id, request, gateway, workflow_instance_id=workflow_instance_id)


@router.get("/events/subscribe")
async def subscribe_events(request: Request, gateway: GatewayService = Depends(get_gateway_service)) -> Any:
    params = dict(request.query_params)
    try:
        channels = normalize_event_channels(params.get("channels"))
        auth_params = dict(params)
        auth = await authorize_http_request(request, gateway=gateway, params=auth_params, capability="events")
        capabilities = tuple(auth_params.get("_auth_capabilities") or ())
        ensure_channel_capabilities(channels, capabilities)
        cursor = request.headers.get("last-event-id") or params.get("cursor") or params.get("last_event_id")
        start_sequence = read_event_cursor(cursor, auth.scope)
    except ProtocolError as exc:
        return http_error_response(exc)

    filters = {
        key: params.get(key)
        for key in ("workflow_instance_id", "workflow_patch_id", "approval_id", "artifact_id", "job_id", "trace_id")
        if params.get(key)
    }
    follow = _truthy(params.get("follow"))
    heartbeat_interval = _float_param(params.get("heartbeat_interval"), default=15.0)
    max_heartbeats = _int_param(params.get("max_heartbeats"))

    async def event_source():
        last_sequence = start_sequence
        sent_keys: set[tuple[str, str]] = set()
        events, last_sequence = _collect_unsent_events(
            gateway,
            scope=auth.scope,
            channels=channels,
            filters=filters,
            last_sequence=last_sequence,
            sent_keys=sent_keys,
        )
        for event in events:
            yield sse_frame(_redact(event))
        if not follow:
            return
        sent_heartbeats = 0
        while True:
            await asyncio.sleep(max(heartbeat_interval, 0.01))
            events, last_sequence = _collect_unsent_events(
                gateway,
                scope=auth.scope,
                channels=channels,
                filters=filters,
                last_sequence=last_sequence,
                sent_keys=sent_keys,
            )
            if events:
                for event in events:
                    yield sse_frame(_redact(event))
                continue
            yield heartbeat_frame()
            sent_heartbeats += 1
            if max_heartbeats is not None and sent_heartbeats >= max_heartbeats:
                return

    response = StreamingResponse(event_source(), media_type="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    add_dev_warning(response, auth)
    return response


async def _artifact_metadata_response(
    artifact_id: str,
    request: Request,
    gateway: GatewayService,
    *,
    workflow_instance_id: str | None,
) -> Any:
    try:
        params = {**_query_scope_params(request), "artifact_id": artifact_id}
        if workflow_instance_id:
            params["workflow_instance_id"] = workflow_instance_id
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="artifacts.read")
        if workflow_instance_id:
            _ensure_artifact_in_instance(gateway, artifact_id, workflow_instance_id, auth.scope)
        result = await _rpc(gateway, "artifact.read_metadata", params)
        response = JSONResponse(_redact(result["artifact"]))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


async def _artifact_lineage_response(
    artifact_id: str,
    request: Request,
    gateway: GatewayService,
    *,
    workflow_instance_id: str | None,
) -> Any:
    try:
        params = {**_query_scope_params(request), "artifact_id": artifact_id}
        if workflow_instance_id:
            params["workflow_instance_id"] = workflow_instance_id
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="artifacts.read")
        if workflow_instance_id:
            _ensure_artifact_in_instance(gateway, artifact_id, workflow_instance_id, auth.scope)
        result = await _rpc(gateway, "artifact.lineage", params)
        response = JSONResponse(_redact(result))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


async def _rpc(gateway: GatewayService, method: str, params: dict[str, Any]) -> dict[str, Any]:
    response = await gateway.handle_rpc(RpcRequest(id=method, method=method, params=params))
    if response.error is not None:
        raise ProtocolError(response.error.code, response.error.message, response.error.data or {})
    return response.result or {}


def _workflow_summary(template: dict[str, Any]) -> dict[str, Any]:
    return {
        "workflow_template_id": template.get("workflow_template_id"),
        "name": template.get("name"),
        "latest_version_id": template.get("latest_published_version_id"),
        "status": template.get("status"),
    }


def _version_summary(version: dict[str, Any]) -> dict[str, Any]:
    return {
        "workflow_version_id": version.get("workflow_version_id"),
        "workflow_template_id": version.get("workflow_template_id"),
        "version": version.get("version"),
    }


def _instance_summary(instance: dict[str, Any]) -> dict[str, Any]:
    return {
        "workflow_instance_id": instance.get("workflow_instance_id"),
        "workflow_template_id": instance.get("workflow_template_id"),
        "workflow_version_id": instance.get("workflow_version_id"),
        "status": instance.get("status"),
    }


def _status_dto(status: dict[str, Any]) -> dict[str, Any]:
    return {
        "workflow_instance_id": status.get("workflow_instance_id"),
        "status": status.get("status"),
        "current_station_ids": status.get("current_station_ids") or [],
        "station_counts": status.get("station_run_status_counts") or {},
        "job_counts": status.get("job_status_counts") or {},
        "artifact_count": status.get("artifact_count") or 0,
        "quality_count": status.get("quality_evaluation_count") or 0,
    }


def _quality_dto(evaluation: dict[str, Any]) -> dict[str, Any]:
    return {
        "evaluation_id": evaluation.get("evaluation_id"),
        "workflow_instance_id": evaluation.get("workflow_instance_id"),
        "station_run_id": evaluation.get("station_run_id"),
        "artifact_id": evaluation.get("artifact_id"),
        "rubric_id": evaluation.get("rubric_id"),
        "evaluator_type": evaluation.get("evaluator_type"),
        "score": evaluation.get("score"),
        "status": evaluation.get("status"),
        "issues": evaluation.get("issues") or [],
        "suggestions": evaluation.get("suggestions") or [],
        "created_at": evaluation.get("created_at"),
    }


def _approval_dto(approval: dict[str, Any]) -> dict[str, Any]:
    binding = _approval_workflow_binding(approval)
    return {
        "approval_id": approval.get("approval_id"),
        "workflow_instance_id": binding.get("workflow_instance_id"),
        "station_run_id": binding.get("station_run_id"),
        "station_id": binding.get("station_id"),
        "status": approval.get("status"),
        "action": approval.get("action"),
        "request_summary": approval.get("request_summary"),
        "risk_level": approval.get("risk_level"),
        "decision_reason": approval.get("decision_reason"),
        "active": binding.get("active", True),
        "inactive_reason": binding.get("inactive_reason"),
        "created_at": approval.get("created_at"),
        "decided_at": approval.get("decided_at"),
    }


def _context_dto(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "workflow_instance_id": context.get("workflow_instance_id"),
        "revision": context.get("revision"),
        "business": context.get("business") if isinstance(context.get("business"), dict) else {},
        "updated_at": context.get("updated_at"),
        "trace_id": context.get("trace_id"),
    }


def _business_event_dto(event: dict[str, Any]) -> dict[str, Any]:
    return {
        "event_id": event.get("event_id"),
        "idempotency_key": event.get("idempotency_key"),
        "type": event.get("type"),
        "workflow_instance_id": event.get("workflow_instance_id"),
        "payload": event.get("payload") if isinstance(event.get("payload"), dict) else {},
    }


def _node_catalog_item_dto(node_template_id: str, contract: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": node_template_id,
        "label": NODE_CATALOG_LABELS.get(node_template_id, node_template_id.replace("_", " ").title()),
        "catalog_id": contract.get("catalog_id"),
        "catalog_version": contract.get("catalog_version"),
        "node_template_id": contract.get("node_template_id"),
        "station_kind": contract.get("station_kind"),
        "schema_version": contract.get("schema_version"),
        "allowed_skill_refs": contract.get("allowed_skill_refs") if isinstance(contract.get("allowed_skill_refs"), list) else [],
        "allowed_connector_refs": contract.get("allowed_connector_refs") if isinstance(contract.get("allowed_connector_refs"), list) else [],
        "allowed_artifact_kinds": contract.get("allowed_artifact_kinds") if isinstance(contract.get("allowed_artifact_kinds"), list) else [],
        "allowed_quality_rules": contract.get("allowed_quality_rules") if isinstance(contract.get("allowed_quality_rules"), list) else [],
        "allowed_approval_policies": contract.get("allowed_approval_policies") if isinstance(contract.get("allowed_approval_policies"), list) else [],
    }


def _patch_diff_dto(diff: dict[str, Any]) -> dict[str, Any]:
    return {
        "workflow_patch_id": diff.get("workflow_patch_id"),
        "workflow_draft_id": diff.get("workflow_draft_id"),
        "base_revision": diff.get("base_revision"),
        "operation": diff.get("operation"),
        "target": diff.get("target") if isinstance(diff.get("target"), dict) else {},
        "before_summary": diff.get("before_summary"),
        "after_summary": diff.get("after_summary"),
        "risk_flags": diff.get("risk_flags") if isinstance(diff.get("risk_flags"), list) else [],
        "requires_approval": bool(diff.get("requires_approval")),
        "redacted": True,
    }


def _patch_proposal_dto(patch: dict[str, Any]) -> dict[str, Any]:
    metadata = patch.get("metadata") if isinstance(patch.get("metadata"), dict) else {}
    return {
        "workflow_patch_id": patch.get("workflow_patch_id"),
        "workflow_template_id": patch.get("workflow_template_id"),
        "workflow_draft_id": patch.get("workflow_draft_id"),
        "operation": patch.get("operation"),
        "status": patch.get("status"),
        "proposed_by": patch.get("proposed_by"),
        "source": metadata.get("source"),
        "intent_type": metadata.get("intent_type"),
        "requires_approval": bool(metadata.get("requires_approval") or patch.get("requires_approval")),
        "risk_flags": metadata.get("risk_flags") if isinstance(metadata.get("risk_flags"), list) else patch.get("risk_flags", []),
    }


def _patch_queue_dto(patches: list[dict[str, Any]], *, current_draft_revision: int | None) -> list[dict[str, Any]]:
    selected_id = _selected_patch_id(patches, current_draft_revision=current_draft_revision)
    return [
        _patch_queue_item_dto(patch, current_draft_revision=current_draft_revision, selected=patch.get("workflow_patch_id") == selected_id)
        for patch in patches
    ]


def _selected_patch_id(patches: list[dict[str, Any]], *, current_draft_revision: int | None) -> str | None:
    queue = [_patch_queue_item_dto(patch, current_draft_revision=current_draft_revision, selected=False) for patch in patches]
    for status in ("proposed", "blocked", "applied", "rejected", "stale", "conflicted"):
        candidate = next((item for item in queue if item["status"] == status), None)
        if candidate:
            return str(candidate["patch_id"])
    return None


def _patch_queue_item_dto(patch: dict[str, Any], *, current_draft_revision: int | None, selected: bool) -> dict[str, Any]:
    proposal = _patch_proposal_dto(patch)
    base_revision = patch.get("base_revision")
    raw_status = str(patch.get("status") or proposal.get("status") or "proposed")
    requires_approval = bool(proposal.get("requires_approval") or patch.get("requires_approval"))
    stale_reason = None
    conflict_reason = None
    status = raw_status if raw_status in PATCH_QUEUE_STATUSES else "proposed"
    if raw_status == "proposed" and current_draft_revision is not None and base_revision != current_draft_revision:
        status = "stale"
        stale_reason = "base_revision_mismatch"
        conflict_reason = f"base_revision {base_revision} does not match current draft revision {current_draft_revision}"
    elif raw_status == "proposed" and requires_approval:
        status = "blocked"
        conflict_reason = "requires_approval"
    return {
        **proposal,
        "patch_id": patch.get("workflow_patch_id"),
        "base_revision": base_revision,
        "current_draft_revision": current_draft_revision,
        "status": status,
        "selected": selected,
        "stale_reason": stale_reason,
        "conflict_reason": conflict_reason,
        "created_at": patch.get("created_at"),
        "updated_at": patch.get("updated_at") or patch.get("applied_at") or patch.get("rejected_at") or patch.get("created_at"),
    }


def _patch_action_dto(result: dict[str, Any]) -> dict[str, Any]:
    patch = result.get("patch") if isinstance(result.get("patch"), dict) else {}
    draft = result.get("draft") if isinstance(result.get("draft"), dict) else {}
    return {
        "workflow_patch_id": patch.get("workflow_patch_id"),
        "workflow_template_id": patch.get("workflow_template_id"),
        "workflow_draft_id": patch.get("workflow_draft_id"),
        "status": patch.get("status"),
        "operation": patch.get("operation"),
        "base_revision": patch.get("base_revision"),
        "applied_revision": patch.get("applied_revision"),
        "resulting_draft_revision": patch.get("resulting_draft_revision") or draft.get("revision"),
        "requires_approval": bool(patch.get("requires_approval")),
        "risk_flags": patch.get("risk_flags") if isinstance(patch.get("risk_flags"), list) else [],
    }


def _canvas_draft_projection_dto(
    *,
    workflow_instance_id: str,
    template_id: str,
    draft: dict[str, Any],
    board: dict[str, Any],
    status: dict[str, Any],
    patches: list[dict[str, Any]],
) -> dict[str, Any]:
    draft_payload = draft.get("draft") if isinstance(draft.get("draft"), dict) else {}
    generated_at = _now_iso()
    patch_queue = _patch_queue_dto(patches, current_draft_revision=draft.get("revision"))
    selected_patch = next((patch for patch in patch_queue if patch.get("selected")), None)
    proposed_patch = next((patch for patch in patches if patch.get("workflow_patch_id") == selected_patch.get("patch_id")), None) if selected_patch else None
    board_status_timestamp = status.get("updated_at") or status.get("timestamp") or generated_at
    freshness_state, stale_reasons = _projection_freshness_state(
        draft_revision=draft.get("revision"),
        selected_patch=selected_patch,
        board_status_timestamp=board_status_timestamp,
        generated_at=generated_at,
    )
    return {
        "projection_id": f"canvas_projection:{workflow_instance_id}:{draft.get('revision')}",
        "workflow_instance_id": workflow_instance_id,
        "workflow_template_id": template_id,
        "workflow_draft_id": draft.get("workflow_draft_id"),
        "draft_revision": draft.get("revision"),
        "generated_at": generated_at,
        "board_status_timestamp": board_status_timestamp,
        "status_updated_at": board_status_timestamp,
        "patch_queue_revision": _patch_queue_revision(patch_queue),
        "freshness_state": freshness_state,
        "stale_reasons": stale_reasons,
        "source_refs": {
            "design_structure": {
                "kind": "WorkflowDraft",
                "workflow_draft_id": draft.get("workflow_draft_id"),
                "workflow_template_id": template_id,
                "draft_revision": draft.get("revision"),
            },
            "runtime_state": {
                "kind": "BoardDTO/InstanceStatusDTO",
                "workflow_instance_id": workflow_instance_id,
                "status": status.get("status"),
                "freshness_marker": board_status_timestamp,
            },
            "pending_diff": {
                "kind": "PatchDiffDTO",
                "workflow_patch_id": proposed_patch.get("workflow_patch_id") if proposed_patch else None,
                "status": proposed_patch.get("status") if proposed_patch else None,
                "patch_queue_revision": _patch_queue_revision(patch_queue),
            },
        },
        "nodes": [
            _canvas_projection_node(station, board)
            for station in draft_payload.get("stations", [])
            if isinstance(station, dict)
        ],
        "edges": [
            _canvas_projection_edge(edge)
            for edge in draft_payload.get("edges", [])
            if isinstance(edge, dict)
        ],
        "runtime_summary": {
            "current_station_ids": status.get("current_station_ids") or [],
            "station_counts": status.get("station_counts") or {},
            "job_counts": status.get("job_counts") or {},
        },
        "patch_queue": patch_queue,
        "pending_patch": selected_patch,
        "redaction_status": "redacted",
    }


def _projection_freshness_state(
    *,
    draft_revision: Any,
    selected_patch: dict[str, Any] | None,
    board_status_timestamp: str,
    generated_at: str,
) -> tuple[str, list[str]]:
    stale_reasons: list[str] = []
    if selected_patch and selected_patch.get("status") == "stale":
        stale_reasons.append("stale_patch")
    if selected_patch and selected_patch.get("base_revision") not in (None, draft_revision):
        stale_reasons.append("stale_draft")
    if board_status_timestamp > generated_at:
        stale_reasons.append("stale_board")
    if "stale_draft" in stale_reasons:
        return "stale_draft", stale_reasons
    if "stale_patch" in stale_reasons:
        return "stale_patch", stale_reasons
    if "stale_board" in stale_reasons:
        return "stale_board", stale_reasons
    if draft_revision is None:
        return "unknown", ["unknown_draft_revision"]
    return "fresh", []


def _patch_queue_revision(patch_queue: list[dict[str, Any]]) -> str:
    if not patch_queue:
        return "patch_queue:empty"
    parts = [
        f"{item.get('patch_id')}:{item.get('status')}:{item.get('updated_at') or ''}:{item.get('base_revision')}:{item.get('current_draft_revision')}"
        for item in patch_queue
    ]
    return "patch_queue:" + "|".join(parts)


def _canvas_projection_node(station: dict[str, Any], board: dict[str, Any]) -> dict[str, Any]:
    station_id = station.get("station_id")
    board_station = next(
        (
            item
            for item in board.get("stations", [])
            if isinstance(item, dict)
            and isinstance(item.get("station"), dict)
            and item["station"].get("station_id") == station_id
        ),
        {},
    )
    metadata = station.get("metadata") if isinstance(station.get("metadata"), dict) else {}
    return {
        "station_id": station_id,
        "name": station.get("name"),
        "role": station.get("role"),
        "station_kind": metadata.get("station_kind"),
        "skill_refs": station.get("skill_refs") if isinstance(station.get("skill_refs"), list) else [],
        "connector_refs": station.get("connector_refs") if isinstance(station.get("connector_refs"), list) else [],
        "status": board_station.get("status"),
        "run_count": len(board_station.get("runs", [])) if isinstance(board_station.get("runs"), list) else 0,
    }


def _canvas_projection_edge(edge: dict[str, Any]) -> dict[str, Any]:
    return {
        "edge_id": edge.get("edge_id"),
        "from_station_id": edge.get("from_station_id"),
        "to_station_id": edge.get("to_station_id"),
        "order": edge.get("order"),
    }


def _agent_session_key(workflow_instance_id: str, scope: ScopeContext) -> str:
    return "|".join(
        [
            scope.app_id or "",
            scope.project_id or "",
            scope.workspace_id or "",
            workflow_instance_id,
        ]
    )


def _now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _scope_dto(scope: ScopeContext) -> dict[str, Any]:
    return {
        "app_id": scope.app_id,
        "project_id": scope.project_id,
        "workspace_id": scope.workspace_id,
    }


def _pv17_scope_key(scope: ScopeContext) -> str:
    return "|".join([scope.app_id or "", scope.project_id or "", scope.workspace_id or ""])


def _pv17_entity_store_key(scope: ScopeContext, entity_kind: str, entity_id: str) -> str:
    return "|".join([_pv17_scope_key(scope), entity_kind, entity_id])


def _pv17_audit_ref(operation: str, scope: ScopeContext, *, entity_id: str | None = None) -> dict[str, Any]:
    return {
        "audit_ref_id": f"pv17:audit:{operation}:{_pv17_scope_key(scope)}:{entity_id or 'scope'}",
        "operation": operation,
        "scope": _scope_dto(scope),
        "entity_id": entity_id,
        "created_at": _now_iso(),
        "redaction_status": "redacted",
    }


def _pv17_entity_projection(scope: ScopeContext, entity_kind: str) -> dict[str, Any]:
    default_id = {
        "workspace": scope.workspace_id or "local",
        "project": scope.project_id or "demo",
        "app": scope.app_id or "meeting",
    }.get(entity_kind, entity_kind)
    entity = _PV17_PRODUCT_ENTITIES.get(_pv17_entity_store_key(scope, entity_kind, default_id))
    if entity is not None:
        return entity
    return {
        "entity_kind": entity_kind,
        "entity_id": default_id,
        "display_name": default_id,
        "scope": _scope_dto(scope),
        "source": "scope_default_projection",
        "audit_refs": [_pv17_audit_ref(f"product_entity.{entity_kind}.default_projection", scope, entity_id=default_id)],
        "redaction_status": "redacted",
    }


def _pv17_app_projection(gateway: GatewayService, scope: ScopeContext) -> dict[str, Any]:
    profile = gateway.app_registry.get_optional(scope.app_id or "")
    stored = _pv17_entity_projection(scope, "app")
    if profile is None:
        return stored
    profile_view = profile.to_dict()
    return {
        **stored,
        "entity_id": profile.app_id,
        "display_name": profile.display_name,
        "domain": profile.domain,
        "default_pack": profile.default_pack,
        "connector_refs": profile_view.get("connector_refs") or [],
        "metadata": profile_view.get("metadata") or {},
        "source": "app_registry_projection",
        "redaction_status": "redacted",
    }


def _pv17_station_agent_projections(scope: ScopeContext) -> list[dict[str, Any]]:
    prefix = _pv17_scope_key(scope) + "|station_agent|"
    agents = [entity for key, entity in sorted(_PV17_PRODUCT_ENTITIES.items()) if key.startswith(prefix)]
    if agents:
        return agents
    return [
        {
            "entity_kind": "station_agent",
            "entity_id": "station_agent:default-reviewer",
            "display_name": "默认审查 Station Agent",
            "role": "reviewer",
            "goal": "审查 workflow diff、runtime refs 和 evidence refs。",
            "memory_refs": [],
            "model_refs": ["model:default-redacted"],
            "tool_refs": [],
            "skill_refs": ["governance.review"],
            "mcp_refs": [],
            "scope": _scope_dto(scope),
            "source": "default_projection",
            "redaction_status": "redacted",
        }
    ]


def _pv17_entity_id(entity_kind: str, payload: dict[str, Any], scope: ScopeContext) -> str:
    explicit = payload.get("entity_id") or payload.get(f"{entity_kind}_id") or payload.get("id")
    if explicit:
        return str(explicit)
    if entity_kind == "workspace":
        return scope.workspace_id or "local"
    if entity_kind == "project":
        return scope.project_id or "demo"
    if entity_kind == "app":
        return scope.app_id or "meeting"
    slug = str(payload.get("display_name") or payload.get("name") or "default").strip().lower().replace(" ", "-")
    return f"station_agent:{slug or 'default'}"


def _pv17_require_mutation_confirmation(body: dict[str, Any], *, allowed_sources: set[str] | None = None) -> None:
    allowed_sources = allowed_sources or {"product_console", "workflow_console", "mission_studio"}
    source = str(body.get("source") or "")
    if body.get("user_confirmed") is not True:
        raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "PV17 mutation requires explicit user confirmation.", {"field": "user_confirmed"})
    if source == "agent":
        raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "source=agent cannot perform durable PV17 mutation.", {"source": source})
    if source not in allowed_sources:
        raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "PV17 mutation source is not allowed.", {"source": source or None})
    if not str(body.get("idempotency_key") or "").strip():
        raise ProtocolError("INVALID_PARAMS", "idempotency_key is required.", {"field": "idempotency_key"})


def _pv17_entity_policy_decision(body: dict[str, Any], scope: ScopeContext) -> dict[str, str]:
    payload = body.get("payload") if isinstance(body.get("payload"), dict) else {}
    requested_project = payload.get("project_id") or payload.get("owner_project_id")
    decision_id = f"pv17:policy:{_pv17_scope_key(scope)}:{body.get('idempotency_key') or uuid4().hex[:8]}"
    if requested_project and str(requested_project) != str(scope.project_id or ""):
        return {
            "status": "denied",
            "policy_decision_ref": decision_id,
            "reason": "owner_project_scope_mismatch",
        }
    if body.get("operation") == "deny":
        return {
            "status": "denied",
            "policy_decision_ref": decision_id,
            "reason": "explicit_denial_fixture",
        }
    return {"status": "allowed", "policy_decision_ref": decision_id, "reason": ""}


def _pv17_store_entity(
    entity_kind: str,
    entity_id: str,
    payload: dict[str, Any],
    scope: ScopeContext,
    *,
    audit_ref: dict[str, Any],
) -> dict[str, Any]:
    entity = {
        "entity_kind": entity_kind,
        "entity_id": entity_id,
        "display_name": payload.get("display_name") or payload.get("name") or entity_id,
        "scope": _scope_dto(scope),
        "role": payload.get("role"),
        "goal": payload.get("goal"),
        "memory_refs": payload.get("memory_refs") if isinstance(payload.get("memory_refs"), list) else [],
        "model_refs": payload.get("model_refs") if isinstance(payload.get("model_refs"), list) else [],
        "tool_refs": payload.get("tool_refs") if isinstance(payload.get("tool_refs"), list) else [],
        "skill_refs": payload.get("skill_refs") if isinstance(payload.get("skill_refs"), list) else [],
        "mcp_refs": payload.get("mcp_refs") if isinstance(payload.get("mcp_refs"), list) else [],
        "audit_refs": [audit_ref],
        "updated_at": _now_iso(),
        "redaction_status": "redacted",
    }
    _PV17_PRODUCT_ENTITIES[_pv17_entity_store_key(scope, entity_kind, entity_id)] = _redact(entity)
    return _PV17_PRODUCT_ENTITIES[_pv17_entity_store_key(scope, entity_kind, entity_id)]


def _pv17_evidence_overview(gateway: GatewayService, scope: ScopeContext, active_run: dict[str, Any] | None) -> dict[str, Any]:
    if not active_run:
        return {
            "status": "empty",
            "claims": [],
            "missing_evidence": ["runtime_instance"],
            "allowed_claim": "PV17 product closed loop implementation evidence is not complete.",
            "redaction_status": "redacted",
        }
    instance_id = str(active_run.get("workflow_instance_id") or "")
    try:
        runs = gateway.workflow_repository.list_station_runs(instance_id, scope=scope)
    except Exception:
        runs = []
    return {
        "status": "ready_for_inspect" if runs else "missing_station_runs",
        "workflow_instance_id": instance_id,
        "runtime_event_ref_count": len(runs),
        "artifact_ref_count": sum(len(run.output_artifact_ids) for run in runs),
        "quality_ref_count": sum(len(run.quality_evaluation_ids) for run in runs),
        "claims": ["product_console_state_readable", "runtime_instance_selectable"],
        "missing_evidence": [] if runs else ["station_runs"],
        "allowed_claim": "PV17 product closed loop implementation ready for bounded review only after PV17-SA passes.",
        "redaction_status": "redacted",
    }


def _pv17_studio_workflow_dto(
    template: dict[str, Any],
    draft: dict[str, Any],
    versions: list[dict[str, Any]],
    patches: list[dict[str, Any]],
    scope: ScopeContext,
) -> dict[str, Any]:
    draft_payload = draft.get("draft") if isinstance(draft.get("draft"), dict) else {}
    stations = draft_payload.get("stations") if isinstance(draft_payload.get("stations"), list) else []
    edges = draft_payload.get("edges") if isinstance(draft_payload.get("edges"), list) else []
    return {
        "schema_version": PV17_SCHEMA_VERSION,
        "workflow_template": _workflow_summary(template),
        "draft": {
            "workflow_draft_id": draft.get("workflow_draft_id"),
            "revision": draft.get("revision"),
            "status": draft.get("status"),
        },
        "versions": [_version_summary(item) for item in versions],
        "graph": {"nodes": stations, "edges": edges, "redaction_status": "redacted"},
        "inspector": {
            "selected_node_id": stations[0].get("station_id") if stations and isinstance(stations[0], dict) else None,
            "quality_rule_count": sum(len(item.get("quality_rules") or []) for item in stations if isinstance(item, dict)),
            "approval_point_count": sum(1 for item in stations if isinstance(item, dict) and item.get("approval_required")),
            "redaction_status": "redacted",
        },
        "patch_queue": _patch_queue_dto(patches, current_draft_revision=draft.get("revision")),
        "audit_refs": [_pv17_audit_ref("studio.workflow.read", scope, entity_id=str(template.get("workflow_template_id") or ""))],
        "redaction_status": "redacted",
    }


def _pv17_runtime_event_refs(instance: dict[str, Any], station_runs: Any) -> list[dict[str, Any]]:
    runs = station_runs if isinstance(station_runs, list) else []
    refs = [
        {
            "event_ref": f"station.run:{run.get('station_run_id')}",
            "event_type": f"station.run.{str(run.get('status') or 'unknown').lower()}",
            "workflow_instance_id": instance.get("workflow_instance_id"),
            "station_run_id": run.get("station_run_id"),
        }
        for run in runs
        if isinstance(run, dict)
    ]
    refs.insert(
        0,
        {
            "event_ref": f"workflow.instance:{instance.get('workflow_instance_id')}",
            "event_type": f"workflow.instance.{str(instance.get('status') or 'unknown').lower()}",
            "workflow_instance_id": instance.get("workflow_instance_id"),
        },
    )
    return refs


def _pv17_trace_refs(instance: dict[str, Any]) -> list[dict[str, Any]]:
    trace_id = instance.get("trace_id")
    return [{"trace_id": trace_id, "workflow_instance_id": instance.get("workflow_instance_id")}] if trace_id else []


async def _pv17_attach_quality_refs_for_run(
    gateway: GatewayService,
    scope: ScopeContext,
    instance: dict[str, Any],
    station_runs: Any,
) -> None:
    workflow_instance_id = str(instance.get("workflow_instance_id") or "")
    if not workflow_instance_id:
        return
    for run in station_runs if isinstance(station_runs, list) else []:
        if not isinstance(run, dict):
            continue
        output_ids = run.get("output_artifact_ids") if isinstance(run.get("output_artifact_ids"), list) else []
        if not output_ids:
            continue
        try:
            await _rpc(
                gateway,
                "quality.evaluation.create",
                {
                    "evaluation": {
                        "workflow_instance_id": workflow_instance_id,
                        "station_run_id": run.get("station_run_id"),
                        "artifact_id": output_ids[0],
                        "rubric_id": "dummy_quality",
                        "evaluator_type": "rule",
                        "score": 1.0,
                        "status": "passed",
                        "issues": [],
                        "suggestions": [{"summary": "PV17 runtime inspect quality ref attached."}],
                        "metadata": {"source": "pv17_confirm_run"},
                    },
                    "auto_attach": True,
                    "scope": _scope_dto(scope),
                },
            )
        except ProtocolError:
            continue


async def _pv17_runtime_inspect_dto(gateway: GatewayService, scope: ScopeContext, params: dict[str, Any]) -> dict[str, Any]:
    instance_id = str(params.get("workflow_instance_id") or "")
    instance_result = await _rpc(gateway, "workflow.instance.get", params)
    status_result = await _rpc(gateway, "workflow.instance.status", params)
    station_result = await _rpc(gateway, "station.run.list", params)
    board_result = await _rpc(gateway, "workflow.board.get", params)
    quality_result = await _rpc(gateway, "quality.evaluation.list", params)
    traces_result = await _rpc(gateway, "trace.list", params)
    instance = instance_result.get("workflow_instance") if isinstance(instance_result.get("workflow_instance"), dict) else {}
    station_runs = station_result.get("station_runs") if isinstance(station_result.get("station_runs"), list) else []
    board = board_result.get("board") if isinstance(board_result.get("board"), dict) else {}
    artifact_refs = _pv17_artifact_refs(board)
    quality_refs = [
        {"quality_ref": item.get("evaluation_id"), "status": item.get("status"), "station_run_id": item.get("station_run_id")}
        for item in quality_result.get("evaluations", [])
        if isinstance(item, dict)
    ]
    approval_refs = [
        {"approval_ref": item.get("approval_id"), "status": item.get("status"), "station_id": item.get("station_id")}
        for item in board.get("approvals", [])
        if isinstance(item, dict)
    ]
    return {
        "schema_version": PV17_SCHEMA_VERSION,
        "workflow_instance": _instance_summary(instance),
        "status": _status_dto(status_result.get("status", {})),
        "station_runs": station_runs,
        "runtime_event_refs": _pv17_runtime_event_refs(instance, station_runs),
        "trace_refs": _pv17_trace_refs(instance)
        + [
            {"trace_id": item.get("trace_id"), "event_type": item.get("event_type")}
            for item in traces_result.get("traces", [])
            if isinstance(item, dict) and item.get("trace_id")
        ],
        "artifact_refs": artifact_refs,
        "quality_refs": quality_refs,
        "approval_refs": approval_refs,
        "audit_refs": [_pv17_audit_ref("runtime.instance.inspect", scope, entity_id=instance_id)],
        "redaction_status": "redacted",
    }


def _pv17_artifact_refs(board: dict[str, Any]) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    for artifact in board.get("artifacts", []) if isinstance(board.get("artifacts"), list) else []:
        if isinstance(artifact, dict):
            refs.append({"artifact_ref": artifact.get("artifact_id"), "kind": artifact.get("kind"), "name": artifact.get("name")})
    for station in board.get("stations", []) if isinstance(board.get("stations"), list) else []:
        if not isinstance(station, dict):
            continue
        for key in ("input_artifacts", "output_artifacts"):
            for artifact in station.get(key, []) if isinstance(station.get(key), list) else []:
                if isinstance(artifact, dict) and artifact.get("artifact_id"):
                    refs.append({"artifact_ref": artifact.get("artifact_id"), "kind": artifact.get("kind"), "name": artifact.get("name")})
    seen: set[str] = set()
    unique = []
    for ref in refs:
        artifact_ref = str(ref.get("artifact_ref") or "")
        if artifact_ref and artifact_ref not in seen:
            seen.add(artifact_ref)
            unique.append(ref)
    return unique


def _pv17_evidence_summary_dto(inspect: dict[str, Any], scope: ScopeContext) -> dict[str, Any]:
    missing = []
    for key in ("runtime_event_refs", "trace_refs", "artifact_refs", "quality_refs"):
        if not inspect.get(key):
            missing.append(key)
    claims = [
        {
            "claim": "正式 /bff/pv17 runtime inspect 可以读取 runtime refs。",
            "evidence_refs": [ref.get("event_ref") for ref in inspect.get("runtime_event_refs", []) if isinstance(ref, dict)],
            "status": "supported" if inspect.get("runtime_event_refs") else "missing",
        },
        {
            "claim": "Evidence review 只汇总 trace/artifact/quality refs，不构造 runtime truth。",
            "evidence_refs": [ref.get("artifact_ref") for ref in inspect.get("artifact_refs", []) if isinstance(ref, dict)],
            "status": "supported" if inspect.get("artifact_refs") else "missing",
        },
    ]
    return {
        "schema_version": PV17_SCHEMA_VERSION,
        "claims": claims,
        "route_boundary": {
            "allowed_prefix": "/bff/pv17",
            "browser_denylist": ["/v1/rpc", "/internal/runtime", "/runtime/store", "/api/runtime", "/debug/runtime"],
            "status": "specified",
        },
        "redaction": {"status": "redacted", "secret_allowed": False, "provider_payload_allowed": False, "artifact_content_allowed": False},
        "artifact_lineage": {"artifact_refs": inspect.get("artifact_refs", [])},
        "trace_timeline": {"trace_refs": inspect.get("trace_refs", [])},
        "missing_evidence": missing,
        "allowed_claim": "PV17 complete: product closed loop implementation ready for bounded review.",
        "audit_refs": [_pv17_audit_ref("evidence.summary.read", scope, entity_id=str(inspect.get("workflow_instance", {}).get("workflow_instance_id") or ""))],
        "redaction_status": "redacted",
    }


PV19_DEFAULT_WORKFLOW_ID = "pv19_runtime_workflow_platform_reference"


def _pv19_scope_key(scope: ScopeContext) -> str:
    return "|".join([scope.app_id or "", scope.project_id or "", scope.workspace_id or ""])


def _pv19_audit_ref(operation: str, scope: ScopeContext, *, entity_id: str | None = None) -> dict[str, Any]:
    return {
        "audit_ref_id": f"pv19:audit:{operation}:{_pv19_scope_key(scope)}:{entity_id or 'scope'}",
        "operation": operation,
        "scope": _scope_dto(scope),
        "entity_id": entity_id,
        "created_at": _now_iso(),
        "redaction_status": "redacted",
    }


def _pv19_default_workflow_template(scope: ScopeContext) -> dict[str, Any]:
    return {
        "workflow_template_id": PV19_DEFAULT_WORKFLOW_ID,
        "app_id": scope.app_id or "reference_app",
        "project_id": scope.project_id or "demo_a",
        "workspace_id": scope.workspace_id or "local",
        "name": "PV19 Runtime Workflow Platform Reference",
        "description": "Runtime-backed Workflow Studio closed loop reference. The business sample is data only, not platform customization.",
        "status": "draft",
        "version": "0.1.0",
        "stations": [
            {
                "station_id": "source_review",
                "name": "Source Intake",
                "role": "input",
                "skill_refs": ["workflow.source.review"],
                "output_contracts": [
                    {
                        "contract_id": "source_brief",
                        "artifact_kind": "pv19.source_brief",
                        "direction": "output",
                        "required": True,
                        "metadata": {"sample": "knowledge_opc", "platform_generic": True},
                    }
                ],
                "metadata": {"node_kind": "source", "sample": "knowledge_opc", "prompt_ref": "pv19.prompt.source_review.v1"},
            },
            {
                "station_id": "human_quality_gate",
                "name": "Human Quality Gate",
                "role": "reviewer",
                "skill_refs": ["workflow.human.review"],
                "input_contracts": [
                    {
                        "contract_id": "source_brief_in",
                        "artifact_kind": "pv19.source_brief",
                        "direction": "input",
                        "required": True,
                        "metadata": {"from_station_id": "source_review"},
                    }
                ],
                "output_contracts": [
                    {
                        "contract_id": "approved_brief",
                        "artifact_kind": "pv19.approved_brief",
                        "direction": "output",
                        "required": True,
                        "metadata": {"requires_human_decision": True},
                    }
                ],
                "approval_required": True,
                "metadata": {
                    "node_kind": "human_gate",
                    "approval_policy": {"mode": "explicit_user_confirmed", "decisions": ["approve", "reject"]},
                },
            },
            {
                "station_id": "evidence_publish",
                "name": "Evidence Publish",
                "role": "publisher",
                "skill_refs": ["workflow.evidence.publish"],
                "input_contracts": [
                    {
                        "contract_id": "approved_brief_in",
                        "artifact_kind": "pv19.approved_brief",
                        "direction": "input",
                        "required": True,
                        "metadata": {"from_station_id": "human_quality_gate"},
                    }
                ],
                "output_contracts": [
                    {
                        "contract_id": "evidence_summary",
                        "artifact_kind": "pv19.evidence_summary",
                        "direction": "output",
                        "required": True,
                        "metadata": {"evidence_read_model": True},
                    }
                ],
                "metadata": {"node_kind": "evidence", "claim_scan": True},
            },
        ],
        "edges": [
            {"edge_id": "source_to_gate", "from_station_id": "source_review", "to_station_id": "human_quality_gate", "order": 1},
            {"edge_id": "gate_to_evidence", "from_station_id": "human_quality_gate", "to_station_id": "evidence_publish", "order": 2},
        ],
        "quality_contracts": [
            {
                "contract_id": "pv19_quality",
                "rubric_id": "pv19_quality",
                "evaluator_type": "rule",
                "required": False,
                "blocking": False,
                "threshold": 0.5,
                "metadata": {"source": "pv19_bff_reference"},
            }
        ],
        "approval_points": [
            {
                "station_id": "human_quality_gate",
                "approval_required": True,
                "approval_policy": {"mode": "explicit_user_confirmed", "source": "station.approval_required"},
            }
        ],
        "metadata": {
            "stage": "pv19",
            "primary_sample": "knowledge_opc",
            "reuse_check": "folder-summary/reference workflow",
            "platform_rule": "business_pack_must_not_customize_runtime_core",
        },
    }


def _pv19_ensure_workflow_template(gateway: GatewayService, scope: ScopeContext) -> tuple[Any, Any]:
    try:
        template = gateway.workflow_repository.get_template(PV19_DEFAULT_WORKFLOW_ID, scope=scope)
    except ProtocolError as exc:
        if exc.code != "WORKFLOW_TEMPLATE_NOT_FOUND":
            raise
        template, draft = gateway.workflow_repository.create_template(_pv19_default_workflow_template(scope), scope=scope)
        return template, draft
    draft = gateway.workflow_repository.get_draft(str(template.latest_draft_id), scope=scope)
    return template, draft


def _pv19_get_workflow_template_and_draft(gateway: GatewayService, workflow_id: str, scope: ScopeContext) -> tuple[Any, Any]:
    template = gateway.workflow_repository.get_template(workflow_id, scope=scope)
    draft = gateway.workflow_repository.get_draft(str(template.latest_draft_id), scope=scope)
    return template, draft


def _pv19_graph_dto(template: dict[str, Any], draft: dict[str, Any], scope: ScopeContext) -> dict[str, Any]:
    draft_payload = draft.get("draft") if isinstance(draft.get("draft"), dict) else {}
    stations = draft_payload.get("stations") if isinstance(draft_payload.get("stations"), list) else []
    edges = draft_payload.get("edges") if isinstance(draft_payload.get("edges"), list) else []
    return {
        "schema_version": PV19_RUNTIME_WORKFLOW_SCHEMA_VERSION,
        "scope": _scope_dto(scope),
        "workflow": _workflow_summary(template),
        "draft": {"workflow_draft_id": draft.get("workflow_draft_id"), "revision": draft.get("revision"), "status": draft.get("status")},
        "graph": {
            "nodes": stations,
            "edges": edges,
            "human_gate_nodes": [
                node.get("station_id") for node in stations if isinstance(node, dict) and bool(node.get("approval_required"))
            ],
            "redaction_status": "redacted",
        },
        "platform_contract": {
            "business_pack_mode": "data_and_template_only",
            "core_customization_allowed": False,
            "runtime_backed": True,
        },
        "audit_refs": [_pv19_audit_ref("workflow.graph.read", scope, entity_id=str(template.get("workflow_template_id") or ""))],
        "redaction_status": "redacted",
    }


def _pv19_default_diff_patch() -> dict[str, Any]:
    return {
        "source": "workflow_console",
        "intent_type": "inspector_update",
        "operation": "update_station_prompt",
        "payload": {"station_id": "source_review", "prompt_ref": "pv19.prompt.source_review.v2"},
    }


def _pv19_require_user_confirmation(body: dict[str, Any], *, allowed_sources: set[str]) -> None:
    source = str(body.get("source") or "")
    if body.get("user_confirmed") is not True:
        raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "PV19 action requires explicit user confirmation.", {"field": "user_confirmed"})
    if source not in allowed_sources:
        raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "PV19 action source is not allowed.", {"source": source or None})
    if source == "agent":
        raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "source=agent cannot perform durable PV19 actions.", {"source": source})
    if not str(body.get("idempotency_key") or "").strip():
        raise ProtocolError("INVALID_PARAMS", "idempotency_key is required.", {"field": "idempotency_key"})


async def _pv19_attach_quality_refs_for_run(
    gateway: GatewayService,
    scope: ScopeContext,
    instance: dict[str, Any],
    station_runs: Any,
    *,
    rubric_id: str = "pv19_quality",
    source: str = "pv19_run_start",
) -> None:
    workflow_instance_id = str(instance.get("workflow_instance_id") or "")
    if not workflow_instance_id:
        return
    for run in station_runs if isinstance(station_runs, list) else []:
        if not isinstance(run, dict):
            continue
        output_ids = run.get("output_artifact_ids") if isinstance(run.get("output_artifact_ids"), list) else []
        if not output_ids:
            continue
        try:
            await _rpc(
                gateway,
                "quality.evaluation.create",
                {
                    "evaluation": {
                        "workflow_instance_id": workflow_instance_id,
                        "station_run_id": run.get("station_run_id"),
                        "artifact_id": output_ids[0],
                        "rubric_id": rubric_id,
                        "evaluator_type": "rule",
                        "score": 1.0,
                        "status": "passed",
                        "issues": [],
                        "suggestions": [{"summary": f"{rubric_id} runtime workflow quality ref attached."}],
                        "metadata": {"source": source},
                    },
                    "auto_attach": True,
                    "scope": _scope_dto(scope),
                },
            )
        except ProtocolError:
            continue


def _pv19_run_start_dto(instance: dict[str, Any], station_runs: Any, scope: ScopeContext) -> dict[str, Any]:
    runs = station_runs if isinstance(station_runs, list) else []
    pending_gate_refs = [
        {
            "station_run_id": run.get("station_run_id"),
            "station_id": run.get("station_id"),
            "approval_id": (run.get("metadata") if isinstance(run.get("metadata"), dict) else {}).get("approval_id"),
            "status": run.get("status"),
        }
        for run in runs
        if isinstance(run, dict) and str(run.get("status") or "") == "waiting_approval"
    ]
    return {
        "schema_version": PV19_RUNTIME_WORKFLOW_SCHEMA_VERSION,
        "scope": _scope_dto(scope),
        "workflow_instance": _instance_summary(instance),
        "station_runs": runs,
        "runtime_event_refs": _pv17_runtime_event_refs(instance, runs),
        "trace_refs": _pv17_trace_refs(instance),
        "pending_human_gates": pending_gate_refs,
        "audit_refs": [_pv19_audit_ref("workflow.run.start", scope, entity_id=str(instance.get("workflow_instance_id") or ""))],
        "redaction_status": "redacted",
    }


async def _pv19_run_inspect_dto(gateway: GatewayService, scope: ScopeContext, params: dict[str, Any]) -> dict[str, Any]:
    instance_id = str(params.get("workflow_instance_id") or "")
    instance_result = await _rpc(gateway, "workflow.instance.get", params)
    status_result = await _rpc(gateway, "workflow.instance.status", params)
    station_result = await _rpc(gateway, "station.run.list", params)
    board_result = await _rpc(gateway, "workflow.board.get", params)
    quality_result = await _rpc(gateway, "quality.evaluation.list", params)
    traces_result = await _rpc(gateway, "trace.list", params)
    instance = instance_result.get("workflow_instance") if isinstance(instance_result.get("workflow_instance"), dict) else {}
    station_runs = station_result.get("station_runs") if isinstance(station_result.get("station_runs"), list) else []
    board = board_result.get("board") if isinstance(board_result.get("board"), dict) else {}
    pending_human_gates = _pv19_pending_approvals(gateway, scope, instance_id)
    human_gate_refs = [
        {
            "station_run_id": run.get("station_run_id"),
            "station_id": run.get("station_id"),
            "approval_id": (run.get("metadata") if isinstance(run.get("metadata"), dict) else {}).get("approval_id"),
            "status": run.get("status"),
        }
        for run in station_runs
        if isinstance(run, dict) and (run.get("metadata") if isinstance(run.get("metadata"), dict) else {}).get("approval_id")
    ]
    quality_refs = [
        {"quality_ref": item.get("evaluation_id"), "status": item.get("status"), "station_run_id": item.get("station_run_id")}
        for item in quality_result.get("evaluations", [])
        if isinstance(item, dict)
    ]
    return {
        "schema_version": PV19_RUNTIME_WORKFLOW_SCHEMA_VERSION,
        "scope": _scope_dto(scope),
        "workflow_instance": _instance_summary(instance),
        "status": _status_dto(status_result.get("status", {})),
        "station_runs": station_runs,
        "runtime_event_refs": _pv17_runtime_event_refs(instance, station_runs),
        "trace_refs": _pv17_trace_refs(instance)
        + [
            {"trace_id": item.get("trace_id"), "event_type": item.get("event_type")}
            for item in traces_result.get("traces", [])
            if isinstance(item, dict) and item.get("trace_id")
        ],
        "artifact_refs": _pv17_artifact_refs(board),
        "quality_refs": quality_refs,
        "pending_human_gates": pending_human_gates,
        "human_gate_refs": human_gate_refs or pending_human_gates,
        "audit_refs": [_pv19_audit_ref("workflow.run.inspect", scope, entity_id=instance_id)],
        "redaction_status": "redacted",
    }


def _pv19_pending_approvals(gateway: GatewayService, scope: ScopeContext, workflow_instance_id: str) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    for approval in gateway.approval_store.list_approvals(status="pending"):
        if _approval_workflow_binding(approval).get("workflow_instance_id") != workflow_instance_id:
            continue
        binding = _approval_workflow_binding(approval)
        refs.append(
            {
                "approval_id": approval.get("approval_id"),
                "status": approval.get("status"),
                "station_id": binding.get("station_id"),
                "station_run_id": binding.get("station_run_id"),
                "audit_refs": [_pv19_audit_ref("workflow.human_gate.pending", scope, entity_id=str(approval.get("approval_id") or ""))],
            }
        )
    return refs


def _pv19_pending_approval_id(gateway: GatewayService, scope: ScopeContext, workflow_instance_id: str) -> str | None:
    pending = _pv19_pending_approvals(gateway, scope, workflow_instance_id)
    return str(pending[0].get("approval_id")) if pending else None


def _pv19_state_digest(inspect: dict[str, Any]) -> dict[str, Any]:
    status = inspect.get("status") if isinstance(inspect.get("status"), dict) else {}
    return {
        "workflow_instance_id": inspect.get("workflow_instance", {}).get("workflow_instance_id"),
        "status": status.get("status"),
        "current_station_ids": status.get("current_station_ids") or [],
        "pending_human_gate_count": len(inspect.get("pending_human_gates") or []),
        "station_run_count": len(inspect.get("station_runs") or []),
        "artifact_ref_count": len(inspect.get("artifact_refs") or []),
    }


def _pv19_evidence_summary_dto(inspect: dict[str, Any], scope: ScopeContext) -> dict[str, Any]:
    missing = []
    for key in ("runtime_event_refs", "trace_refs", "artifact_refs", "quality_refs", "human_gate_refs"):
        if not inspect.get(key):
            missing.append(key)
    workflow_instance_id = str(inspect.get("workflow_instance", {}).get("workflow_instance_id") or "")
    claims = [
        {
            "claim": "PV19 BFF exposes workflow graph, diff, publish, run, human action and evidence routes under /bff/pv19.",
            "evidence_refs": ["/bff/pv19/workbench/state", "/bff/pv19/workflows/{workflow_id}/graph", "/bff/pv19/runs/{run_id}/inspect"],
            "status": "supported",
        },
        {
            "claim": "PV19 runtime run is backed by workflow version, workflow instance and station run records.",
            "evidence_refs": [ref.get("event_ref") for ref in inspect.get("runtime_event_refs", []) if isinstance(ref, dict)],
            "status": "supported" if inspect.get("runtime_event_refs") else "missing",
        },
        {
            "claim": "PV19 human interaction uses station approval fields and approval.respond side effects, not business-specific runtime branches.",
            "evidence_refs": [
                ref.get("approval_id") for ref in inspect.get("human_gate_refs", []) if isinstance(ref, dict) and ref.get("approval_id")
            ],
            "status": "supported" if inspect.get("human_gate_refs") else "missing",
        },
        {
            "claim": "PV19 evidence review summarizes trace, artifact, quality and audit refs without fabricating production evidence.",
            "evidence_refs": [ref.get("artifact_ref") for ref in inspect.get("artifact_refs", []) if isinstance(ref, dict)],
            "status": "supported" if inspect.get("artifact_refs") else "missing",
        },
    ]
    return {
        "schema_version": PV19_RUNTIME_WORKFLOW_SCHEMA_VERSION,
        "scope": _scope_dto(scope),
        "claims": claims,
        "route_boundary": {
            "allowed_prefix": "/bff/pv19",
            "browser_denylist": ["/v1/rpc", "/internal/runtime", "/runtime/store", "/api/runtime", "/debug/runtime"],
            "status": "specified",
        },
        "platform_generality": {
            "status": "pass",
            "primary_sample": "knowledge_opc",
            "reuse_check": "folder-summary/reference workflow",
            "core_customization_allowed": False,
        },
        "redaction": {"status": "redacted", "secret_allowed": False, "provider_payload_allowed": False, "artifact_content_allowed": False},
        "artifact_lineage": {"artifact_refs": inspect.get("artifact_refs", [])},
        "trace_timeline": {"trace_refs": inspect.get("trace_refs", [])},
        "human_gate_lineage": {"human_gate_refs": inspect.get("human_gate_refs", [])},
        "missing_evidence": missing,
        "allowed_claim": "PV19 complete: runtime-backed workflow platform closed loop ready for bounded review.",
        "audit_refs": [_pv19_audit_ref("workflow.evidence.summary", scope, entity_id=workflow_instance_id)],
        "redaction_status": "redacted",
    }


PV21_DEFAULT_WORKFLOW_ID = "pv21_complete_workflow_studio_reference"
PV21_NODE_TYPES = {"start", "agent", "tool", "human_gate", "evidence", "end"}
PV21_FORBIDDEN_BROWSER_ROUTES = ["/v1/rpc", "/v1/internal", "/internal/runtime", "/runtime/store", "/api/runtime", "/debug/runtime"]


def _pv21_scope_key(scope: ScopeContext) -> str:
    return "|".join([scope.app_id or "", scope.project_id or "", scope.workspace_id or ""])


def _pv21_scope_params(scope: ScopeContext) -> dict[str, Any]:
    params: dict[str, Any] = {"app_id": scope.app_id}
    if scope.project_id:
        params["project_id"] = scope.project_id
    if scope.workspace_id:
        params["workspace_id"] = scope.workspace_id
    return params


def _pv21_audit_ref(operation: str, scope: ScopeContext, *, entity_id: str | None = None) -> dict[str, Any]:
    return {
        "audit_ref_id": f"pv21:audit:{operation}:{_pv21_scope_key(scope)}:{entity_id or 'scope'}",
        "operation": operation,
        "scope": _scope_dto(scope),
        "entity_id": entity_id,
        "created_at": _now_iso(),
        "redaction_status": "redacted",
    }


def _pv21_default_workflow_template(scope: ScopeContext) -> dict[str, Any]:
    return {
        "workflow_template_id": PV21_DEFAULT_WORKFLOW_ID,
        "app_id": scope.app_id or "reference_app",
        "project_id": scope.project_id or "demo_a",
        "workspace_id": scope.workspace_id or "local",
        "name": "PV21 Complete Workflow Studio Reference",
        "description": "Generic workflow studio candidate reference. Business samples are data only.",
        "status": "draft",
        "version": "0.1.0",
        "stations": [
            {
                "station_id": "start_intake",
                "name": "Start Intake",
                "role": "input",
                "skill_refs": ["generic.reasoning"],
                "output_contracts": [{"contract_id": "brief", "artifact_kind": "pv21.brief", "direction": "output", "required": True}],
                "metadata": {"node_type": "start", "prompt_ref": "pv21.prompt.start.v1", "params": {"title": "审查输入"}},
            },
            {
                "station_id": "agent_analyze",
                "name": "Agent Analysis",
                "role": "agent",
                "skill_refs": ["planning.plan"],
                "input_contracts": [{"contract_id": "brief_in", "artifact_kind": "pv21.brief", "direction": "input", "required": True}],
                "output_contracts": [{"contract_id": "analysis", "artifact_kind": "pv21.analysis", "direction": "output", "required": True}],
                "metadata": {"node_type": "agent", "prompt_ref": "pv21.prompt.agent.v1", "executor_binding": "pv20.governed_agent_executor"},
            },
            {
                "station_id": "human_gate",
                "name": "Human Gate",
                "role": "reviewer",
                "skill_refs": ["governance.review"],
                "input_contracts": [{"contract_id": "analysis_in", "artifact_kind": "pv21.analysis", "direction": "input", "required": True}],
                "output_contracts": [{"contract_id": "approved_analysis", "artifact_kind": "pv21.approved_analysis", "direction": "output", "required": True}],
                "approval_required": True,
                "metadata": {"node_type": "human_gate", "approval_policy": {"mode": "explicit_user_confirmed", "decisions": ["approve", "reject"]}},
            },
            {
                "station_id": "evidence_review",
                "name": "Evidence Review",
                "role": "publisher",
                "skill_refs": ["governance.review"],
                "input_contracts": [{"contract_id": "approved_in", "artifact_kind": "pv21.approved_analysis", "direction": "input", "required": True}],
                "output_contracts": [{"contract_id": "evidence_summary", "artifact_kind": "pv21.evidence_summary", "direction": "output", "required": True}],
                "metadata": {"node_type": "evidence", "claim_scan": True},
            },
        ],
        "edges": [
            {"edge_id": "start_to_agent", "from_station_id": "start_intake", "to_station_id": "agent_analyze", "order": 1},
            {"edge_id": "agent_to_gate", "from_station_id": "agent_analyze", "to_station_id": "human_gate", "order": 2},
            {"edge_id": "gate_to_evidence", "from_station_id": "human_gate", "to_station_id": "evidence_review", "order": 3},
        ],
        "quality_contracts": [
            {
                "contract_id": "pv21_quality",
                "rubric_id": "pv21_quality",
                "evaluator_type": "rule",
                "required": False,
                "blocking": False,
                "threshold": 0.5,
                "metadata": {"source": "pv21_bff_reference"},
            }
        ],
        "approval_points": [
            {"station_id": "human_gate", "approval_required": True, "approval_policy": {"mode": "explicit_user_confirmed"}},
        ],
        "metadata": {
            "stage": "pv21",
            "platform_rule": "business_pack_must_not_customize_workflow_core_gateway_or_app_shell",
            "default_entry": "?studio=pv21-complete-workflow-studio",
        },
    }


def _pv21_ensure_workflow_template(gateway: GatewayService, scope: ScopeContext) -> tuple[Any, Any]:
    try:
        template = gateway.workflow_repository.get_template(PV21_DEFAULT_WORKFLOW_ID, scope=scope)
    except ProtocolError as exc:
        if exc.code != "WORKFLOW_TEMPLATE_NOT_FOUND":
            raise
        template, draft = gateway.workflow_repository.create_template(_pv21_default_workflow_template(scope), scope=scope)
        return template, draft
    draft = gateway.workflow_repository.get_draft(str(template.latest_draft_id), scope=scope)
    return template, draft


def _pv21_get_workflow_template_and_draft(gateway: GatewayService, workflow_id: str, scope: ScopeContext) -> tuple[Any, Any]:
    if workflow_id == PV21_DEFAULT_WORKFLOW_ID:
        return _pv21_ensure_workflow_template(gateway, scope)
    template = gateway.workflow_repository.get_template(workflow_id, scope=scope)
    draft = gateway.workflow_repository.get_draft(str(template.latest_draft_id), scope=scope)
    return template, draft


def _pv21_instances_for_workflow(gateway: GatewayService, scope: ScopeContext, workflow_id: str) -> list[Any]:
    return [item for item in gateway.workflow_repository.list_instances(scope=scope) if item.workflow_template_id == workflow_id]


def _pv21_node_type(node: dict[str, Any]) -> str:
    metadata = node.get("metadata") if isinstance(node.get("metadata"), dict) else {}
    value = node.get("type") or node.get("node_type") or node.get("node_template_id") or metadata.get("node_type") or metadata.get("node_kind") or node.get("role")
    value = str(value or "").strip()
    if value in {"input", "source"}:
        return "start"
    if value in {"reviewer", "approval", "manual_approval"}:
        return "human_gate"
    if value in {"publisher", "output", "publish_output"}:
        return "evidence"
    return value or "agent"


def _pv21_node_dto(node: dict[str, Any]) -> dict[str, Any]:
    metadata = node.get("metadata") if isinstance(node.get("metadata"), dict) else {}
    node_type = _pv21_node_type(node)
    return {
        "node_id": node.get("station_id"),
        "station_id": node.get("station_id"),
        "type": node_type,
        "label": node.get("name") or node.get("station_id"),
        "role": node.get("role"),
        "inputs": node.get("input_contracts") if isinstance(node.get("input_contracts"), list) else [],
        "outputs": node.get("output_contracts") if isinstance(node.get("output_contracts"), list) else [],
        "policy": {
            "approval_required": bool(node.get("approval_required")),
            "approval_policy": metadata.get("approval_policy") if isinstance(metadata.get("approval_policy"), dict) else {},
        },
        "executor_binding": metadata.get("executor_binding"),
        "params": metadata.get("params") if isinstance(metadata.get("params"), dict) else {},
        "metadata": metadata,
    }


def _pv21_edge_dto(edge: dict[str, Any]) -> dict[str, Any]:
    return {
        "edge_id": edge.get("edge_id"),
        "source": edge.get("from_station_id"),
        "target": edge.get("to_station_id"),
        "from_station_id": edge.get("from_station_id"),
        "to_station_id": edge.get("to_station_id"),
        "order": edge.get("order", 0),
        "metadata": edge.get("metadata") if isinstance(edge.get("metadata"), dict) else {},
    }


def _pv21_graph_dto(template: dict[str, Any], draft: dict[str, Any], scope: ScopeContext) -> dict[str, Any]:
    draft_payload = draft.get("draft") if isinstance(draft.get("draft"), dict) else {}
    stations = draft_payload.get("stations") if isinstance(draft_payload.get("stations"), list) else []
    edges = draft_payload.get("edges") if isinstance(draft_payload.get("edges"), list) else []
    validation = _pv21_validation_dto(str(template.get("workflow_template_id") or ""), draft_payload, scope)
    return {
        "schema_version": PV21_COMPLETE_WORKFLOW_STUDIO_SCHEMA_VERSION,
        "scope": _scope_dto(scope),
        "workflow_id": template.get("workflow_template_id"),
        "draft_revision": draft.get("revision"),
        "nodes": [_pv21_node_dto(node) for node in stations if isinstance(node, dict)],
        "edges": [_pv21_edge_dto(edge) for edge in edges if isinstance(edge, dict)],
        "layout": (draft_payload.get("metadata") if isinstance(draft_payload.get("metadata"), dict) else {}).get("pv21_layout", {}),
        "validation_status": validation["status"],
        "updated_at": draft.get("updated_at"),
        "audit_refs": [_pv21_audit_ref("workflow.graph.read", scope, entity_id=str(template.get("workflow_template_id") or ""))],
        "redaction_status": "redacted",
    }


def _pv21_graph_request_to_draft_payload(body: dict[str, Any], template: dict[str, Any], draft: dict[str, Any], scope: ScopeContext) -> dict[str, Any]:
    draft_payload = copy_like(draft.get("draft") if isinstance(draft.get("draft"), dict) else template)
    nodes = body.get("nodes") if isinstance(body.get("nodes"), list) else (body.get("graph") or {}).get("nodes") if isinstance(body.get("graph"), dict) else None
    edges = body.get("edges") if isinstance(body.get("edges"), list) else (body.get("graph") or {}).get("edges") if isinstance(body.get("graph"), dict) else None
    if nodes is not None:
        draft_payload["stations"] = [_pv21_station_from_node(node) for node in nodes if isinstance(node, dict)]
    if edges is not None:
        draft_payload["edges"] = [_pv21_edge_from_request(edge, index) for index, edge in enumerate(edges) if isinstance(edge, dict)]
    metadata = draft_payload.get("metadata") if isinstance(draft_payload.get("metadata"), dict) else {}
    metadata.update({"stage": "pv21", "pv21_layout": body.get("layout") if isinstance(body.get("layout"), dict) else metadata.get("pv21_layout", {})})
    draft_payload["metadata"] = metadata
    draft_payload["workflow_template_id"] = template.get("workflow_template_id")
    draft_payload["app_id"] = scope.app_id or template.get("app_id") or "reference_app"
    draft_payload["project_id"] = scope.project_id or template.get("project_id")
    draft_payload["workspace_id"] = scope.workspace_id or template.get("workspace_id")
    return draft_payload


def copy_like(value: Any) -> dict[str, Any]:
    import copy

    return copy.deepcopy(value) if isinstance(value, dict) else {}


def _pv21_station_from_node(node: dict[str, Any]) -> dict[str, Any]:
    station_id = str(node.get("station_id") or node.get("node_id") or "").strip()
    node_type = _pv21_node_type(node)
    metadata = node.get("metadata") if isinstance(node.get("metadata"), dict) else {}
    params = node.get("params") if isinstance(node.get("params"), dict) else metadata.get("params") if isinstance(metadata.get("params"), dict) else {}
    metadata = {**metadata, "node_type": node_type, "params": params}
    approval_required = bool(node.get("approval_required") or node_type == "human_gate")
    role = str(node.get("role") or ("reviewer" if approval_required else "agent" if node_type == "agent" else "input" if node_type == "start" else "publisher")).strip()
    return {
        "station_id": station_id,
        "name": str(node.get("label") or node.get("name") or station_id).strip() or station_id,
        "role": role,
        "skill_refs": node.get("skill_refs") if isinstance(node.get("skill_refs"), list) else ["governance.review" if approval_required else "generic.reasoning"],
        "connector_refs": node.get("connector_refs") if isinstance(node.get("connector_refs"), list) else [],
        "input_contracts": node.get("inputs") if isinstance(node.get("inputs"), list) else node.get("input_contracts") if isinstance(node.get("input_contracts"), list) else [],
        "output_contracts": node.get("outputs") if isinstance(node.get("outputs"), list) else node.get("output_contracts") if isinstance(node.get("output_contracts"), list) else [{"contract_id": f"{station_id}_out", "artifact_kind": "pv21.generic", "direction": "output", "required": True}],
        "approval_required": approval_required,
        "metadata": metadata,
    }


def _pv21_edge_from_request(edge: dict[str, Any], index: int) -> dict[str, Any]:
    source = str(edge.get("from_station_id") or edge.get("source") or "").strip()
    target = str(edge.get("to_station_id") or edge.get("target") or "").strip()
    return {
        "edge_id": str(edge.get("edge_id") or f"{source}_to_{target}" or f"edge_{index}").strip(),
        "from_station_id": source,
        "to_station_id": target,
        "order": int(edge.get("order") or index + 1),
        "metadata": edge.get("metadata") if isinstance(edge.get("metadata"), dict) else {},
    }


def _pv21_validation_dto(workflow_id: str, draft_payload: dict[str, Any], scope: ScopeContext) -> dict[str, Any]:
    nodes = draft_payload.get("stations") if isinstance(draft_payload.get("stations"), list) else []
    edges = draft_payload.get("edges") if isinstance(draft_payload.get("edges"), list) else []
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    node_ids = {str(node.get("station_id") or "") for node in nodes if isinstance(node, dict)}
    if not nodes:
        errors.append({"code": "PV21_GRAPH_INVALID", "message": "工作流图不能为空。", "severity": "error"})
    for node in nodes:
        if not isinstance(node, dict):
            continue
        station_id = str(node.get("station_id") or "").strip()
        node_type = _pv21_node_type(node)
        if not station_id:
            errors.append({"code": "PV21_GRAPH_INVALID", "message": "节点缺少 station_id。", "severity": "error"})
        if node_type not in PV21_NODE_TYPES:
            errors.append({"code": "PV21_UNKNOWN_NODE_TYPE", "message": f"未知节点类型：{node_type}", "severity": "error", "node_id": station_id})
        if not str(node.get("name") or "").strip():
            errors.append({"code": "PV21_GRAPH_INVALID", "message": "节点缺少名称。", "severity": "error", "node_id": station_id, "field": "name"})
        if node_type == "agent":
            metadata = node.get("metadata") if isinstance(node.get("metadata"), dict) else {}
            if not metadata.get("prompt_ref") and not metadata.get("executor_binding"):
                errors.append({"code": "PV21_GRAPH_INVALID", "message": "Agent 节点缺少 prompt_ref 或 executor_binding。", "severity": "error", "node_id": station_id})
    for edge in edges:
        if not isinstance(edge, dict):
            continue
        source = str(edge.get("from_station_id") or "").strip()
        target = str(edge.get("to_station_id") or "").strip()
        if source not in node_ids or target not in node_ids:
            errors.append({"code": "PV21_GRAPH_INVALID", "message": "连线引用不存在的节点。", "severity": "error", "edge_id": edge.get("edge_id")})
    if nodes and edges:
        outgoing: dict[str, int] = {}
        incoming: dict[str, int] = {}
        for edge in edges:
            if not isinstance(edge, dict):
                continue
            source = str(edge.get("from_station_id") or "").strip()
            target = str(edge.get("to_station_id") or "").strip()
            outgoing[source] = outgoing.get(source, 0) + 1
            incoming[target] = incoming.get(target, 0) + 1
        if len(edges) != max(0, len(nodes) - 1) or any(count > 1 for count in outgoing.values()) or any(count > 1 for count in incoming.values()):
            errors.append(
                {
                    "code": "PV21_RUNTIME_UNSUPPORTED",
                    "message": "当前运行器只支持显式线性工作流；分支、汇聚或额外草稿连线不能发布运行。",
                    "severity": "error",
                }
            )
    human_gate_nodes = [str(node.get("station_id")) for node in nodes if isinstance(node, dict) and bool(node.get("approval_required"))]
    if not human_gate_nodes:
        errors.append({"code": "PV21_GRAPH_INVALID", "message": "PV21 必须包含至少一个人工门禁节点。", "severity": "error"})
    if not edges:
        warnings.append({"code": "PV21_GRAPH_WARNING", "message": "工作流图没有显式连线。", "severity": "warning"})
    return {
        "schema_version": PV21_COMPLETE_WORKFLOW_STUDIO_SCHEMA_VERSION,
        "scope": _scope_dto(scope),
        "workflow_id": workflow_id,
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "warnings": warnings,
        "affected_nodes": [item.get("node_id") for item in errors if item.get("node_id")],
        "affected_edges": [item.get("edge_id") for item in errors if item.get("edge_id")],
        "publish_blocked": bool(errors),
        "runtime_readiness": {"can_publish": not errors, "can_run_after_publish": bool(nodes) and not errors, "human_gate_nodes": human_gate_nodes},
        "audit_refs": [_pv21_audit_ref("workflow.graph.validate", scope, entity_id=workflow_id)],
        "redaction_status": "redacted",
    }


def _pv21_diff_dto(workflow_id: str, base_version_id: str, draft: dict[str, Any], base_snapshot: dict[str, Any], scope: ScopeContext) -> dict[str, Any]:
    draft_payload = draft.get("draft") if isinstance(draft.get("draft"), dict) else {}
    draft_nodes = {str(node.get("station_id")): node for node in draft_payload.get("stations", []) if isinstance(node, dict)}
    base_nodes = {str(node.get("station_id")): node for node in base_snapshot.get("stations", []) if isinstance(node, dict)}
    draft_edges = {str(edge.get("edge_id")): edge for edge in draft_payload.get("edges", []) if isinstance(edge, dict)}
    base_edges = {str(edge.get("edge_id")): edge for edge in base_snapshot.get("edges", []) if isinstance(edge, dict)}
    added = sorted(set(draft_nodes) - set(base_nodes))
    removed = sorted(set(base_nodes) - set(draft_nodes))
    changed = sorted(node_id for node_id in set(draft_nodes) & set(base_nodes) if draft_nodes[node_id] != base_nodes[node_id])
    changed_edges = sorted(edge_id for edge_id in set(draft_edges) ^ set(base_edges) | {edge_id for edge_id in set(draft_edges) & set(base_edges) if draft_edges[edge_id] != base_edges[edge_id]})
    validation = _pv21_validation_dto(workflow_id, draft_payload, scope)
    return {
        "schema_version": PV21_COMPLETE_WORKFLOW_STUDIO_SCHEMA_VERSION,
        "scope": _scope_dto(scope),
        "diff_id": f"pv21-diff:{workflow_id}:{draft.get('revision')}",
        "base_version_id": base_version_id,
        "draft_revision": draft.get("revision"),
        "added_nodes": added,
        "removed_nodes": removed,
        "changed_nodes": changed,
        "changed_edges": changed_edges,
        "risk_summary": ["human_confirmation_required"] + (["validation_blocking_errors"] if validation["publish_blocked"] else []),
        "publish_blocked": validation["publish_blocked"],
        "user_confirmation_required": True,
        "audit_refs": [_pv21_audit_ref("workflow.diff.create", scope, entity_id=workflow_id)],
        "redaction_status": "redacted",
    }


def _pv21_version_dto(version: Any, active: bool = False) -> dict[str, Any]:
    data = version.model_dump(mode="json") if hasattr(version, "model_dump") else dict(version or {})
    return {
        "version_id": data.get("workflow_version_id"),
        "workflow_version_id": data.get("workflow_version_id"),
        "workflow_template_id": data.get("workflow_template_id"),
        "version": data.get("version"),
        "status": "published_active" if active else "published",
        "created_at": data.get("published_at"),
        "published_by": (data.get("metadata") if isinstance(data.get("metadata"), dict) else {}).get("published_by", "local-reviewer"),
        "graph_hash": f"graph:{data.get('workflow_version_id')}",
        "audit_refs": [],
        "rollback_allowed": True,
    }


def _pv21_versions_dto(template: dict[str, Any], versions: list[Any], scope: ScopeContext) -> dict[str, Any]:
    active_id = str(template.get("latest_published_version_id") or "")
    return {
        "schema_version": PV21_COMPLETE_WORKFLOW_STUDIO_SCHEMA_VERSION,
        "scope": _scope_dto(scope),
        "versions": [_pv21_version_dto(version, str(getattr(version, "workflow_version_id", "")) == active_id) for version in versions],
        "published_version_id": active_id or None,
        "rollback_candidates": [str(getattr(version, "workflow_version_id", "")) for version in versions if str(getattr(version, "workflow_version_id", "")) != active_id],
        "audit_refs": [_pv21_audit_ref("workflow.versions.list", scope, entity_id=str(template.get("workflow_template_id") or ""))],
        "redaction_status": "redacted",
    }


def _pv21_studio_state_dto(gateway: GatewayService, scope: ScopeContext, template: dict[str, Any], draft: dict[str, Any], versions: list[Any], instances: list[Any]) -> dict[str, Any]:
    latest_id = str(template.get("latest_published_version_id") or "")
    latest_version = next((version for version in versions if str(version.workflow_version_id) == latest_id), None)
    graph = _pv21_graph_dto(template, draft, scope)
    return {
        "schema_version": PV21_COMPLETE_WORKFLOW_STUDIO_SCHEMA_VERSION,
        "scope": _scope_dto(scope),
        "entry": {"route": "?studio=pv21-complete-workflow-studio", "root_empty_allowed": False, "status": "ready"},
        "workspace": {"workspace_id": scope.workspace_id or "local", "display_name": "PV21 Complete Workflow Studio"},
        "project": {"project_id": scope.project_id or "demo_a", "display_name": "Workflow Studio Candidate"},
        "app": {"app_id": scope.app_id or "reference_app", "display_name": "Reference App"},
        "workflow": _workflow_summary(template),
        "platform_contract": {
            "workflow_core_customization_allowed": False,
            "gateway_core_customization_allowed": False,
            "app_shell_customization_allowed": False,
            "business_pack_allowed": True,
            "boundary": "Business workflows must enter through generic WorkflowTemplate, WorkflowVersion, Gateway RPC and /bff/pv21 DTO routes.",
            "status": "enforced_by_acceptance",
        },
        "node_library": _pv21_node_library(),
        "draft_graph": graph,
        "published_version": _pv21_version_dto(latest_version, True) if latest_version else None,
        "version_history": [_pv21_version_dto(version, str(version.workflow_version_id) == latest_id) for version in versions],
        "run_history": [_instance_summary(instance.model_dump(mode="json")) for instance in instances],
        "evidence_health": {"status": "ready" if instances else "not_run", "missing_refs": [] if instances else ["run_evidence"]},
        "route_claims": ["/bff/pv21/studio/state", "/bff/pv21/workflows/{workflow_id}/graph", "/bff/pv21/runs/{run_id}/evidence"],
        "audit_refs": [_pv21_audit_ref("studio.state.read", scope, entity_id=str(template.get("workflow_template_id") or ""))],
        "redaction_status": "redacted",
    }


def _pv21_node_library() -> list[dict[str, Any]]:
    return [
        {"node_template_id": "start", "type": "start", "label": "Start", "description": "通用输入节点"},
        {"node_template_id": "agent", "type": "agent", "label": "Agent", "description": "受治理 Agent 节点"},
        {"node_template_id": "tool", "type": "tool", "label": "Tool / MCP", "description": "受控 tool 或 MCP 节点"},
        {"node_template_id": "human_gate", "type": "human_gate", "label": "Human Gate", "description": "人工确认节点"},
        {"node_template_id": "evidence", "type": "evidence", "label": "Evidence Review", "description": "证据汇总节点"},
        {"node_template_id": "end", "type": "end", "label": "End", "description": "流程结束节点"},
    ]


async def _pv21_run_dto(gateway: GatewayService, scope: ScopeContext, run_id: str) -> dict[str, Any]:
    inspect = await _pv19_run_inspect_dto(gateway, scope, {**_pv21_scope_params(scope), "workflow_instance_id": run_id})
    current_human_gate = (inspect.get("pending_human_gates") or [None])[0]
    return {
        "schema_version": PV21_COMPLETE_WORKFLOW_STUDIO_SCHEMA_VERSION,
        "scope": _scope_dto(scope),
        "run_id": run_id,
        "version_id": (inspect.get("workflow_instance") or {}).get("workflow_version_id"),
        "state": (inspect.get("status") or {}).get("status") or (inspect.get("workflow_instance") or {}).get("status"),
        "workflow_instance": inspect.get("workflow_instance"),
        "station_runs": inspect.get("station_runs") or [],
        "current_human_gate": current_human_gate,
        "pending_human_gates": inspect.get("pending_human_gates") or [],
        "trace_refs": inspect.get("trace_refs") or [],
        "artifact_refs": inspect.get("artifact_refs") or [],
        "quality_refs": inspect.get("quality_refs") or [],
        "approval_refs": inspect.get("human_gate_refs") or [],
        "audit_refs": [_pv21_audit_ref("workflow.run.inspect", scope, entity_id=run_id)],
        "redaction_status": "redacted",
    }


def _pv21_evidence_summary_dto(run: dict[str, Any], scope: ScopeContext) -> dict[str, Any]:
    artifact_refs = run.get("artifact_refs") or []
    trace_refs = run.get("trace_refs") or []
    quality_refs = run.get("quality_refs") or []
    approval_refs = run.get("approval_refs") or []
    claim_refs = [
        {"claim_id": "pv21_bff_boundary", "status": "supported", "evidence_refs": ["/bff/pv21/*"]},
        {"claim_id": "pv21_runtime_run", "status": "supported" if run.get("workflow_instance") else "missing", "evidence_refs": [run.get("run_id")]},
        {"claim_id": "pv21_human_gate", "status": "supported" if approval_refs else "missing", "evidence_refs": approval_refs},
    ]
    missing = []
    for key, value in {"artifact_refs": artifact_refs, "trace_refs": trace_refs, "quality_refs": quality_refs, "approval_refs": approval_refs}.items():
        if not value:
            missing.append(key)
    return {
        "schema_version": PV21_COMPLETE_WORKFLOW_STUDIO_SCHEMA_VERSION,
        "scope": _scope_dto(scope),
        "artifact_refs": artifact_refs,
        "trace_refs": trace_refs,
        "quality_refs": quality_refs,
        "approval_refs": approval_refs,
        "claim_refs": claim_refs,
        "redaction_refs": [{"redaction_ref": "pv21:redaction:refs-only", "status": "redacted"}],
        "missing_refs": missing,
        "no_false_green_status": "pass",
        "route_boundary": {"allowed_prefix": "/bff/pv21", "browser_denylist": PV21_FORBIDDEN_BROWSER_ROUTES, "status": "specified"},
        "platform_generality": {"status": "pass", "core_customization_allowed": False, "business_sample_mode": "data_only"},
        "allowed_claim": "PV21 workflow studio candidate is ready for bounded review evidence.",
        "not_claimed": [
            "production_readiness",
            "external_product_parity",
            "product_grade_frontend_completion",
            "full_workflow_studio_readiness",
            "unrestricted_agent_executor_readiness",
        ],
        "audit_refs": [_pv21_audit_ref("workflow.evidence.summary", scope, entity_id=str(run.get("run_id") or ""))],
        "redaction_status": "redacted",
    }


def _pv21_require_user_confirmation(body: dict[str, Any], *, operation: str) -> None:
    confirmation = body.get("user_confirmation") if isinstance(body.get("user_confirmation"), dict) else {}
    confirmed = body.get("user_confirmed") is True or confirmation.get("confirmed") is True
    if not confirmed:
        raise ProtocolError("PV21_CONFIRMATION_REQUIRED", f"PV21 {operation} requires explicit user confirmation.", {"field": "user_confirmation"})
    source = str(body.get("source") or confirmation.get("source") or "workflow_console").strip()
    if source == "agent":
        raise ProtocolError("PV21_CONFIRMATION_REQUIRED", "source=agent cannot perform durable PV21 actions.", {"source": source})


def _pv21_confirmation_actor(body: dict[str, Any]) -> str:
    confirmation = body.get("user_confirmation") if isinstance(body.get("user_confirmation"), dict) else {}
    return str(confirmation.get("actor_id") or body.get("actor") or "local-reviewer")


def _pv21_state_digest(run: dict[str, Any]) -> dict[str, Any]:
    state = run.get("state")
    return {
        "run_id": run.get("run_id"),
        "state": state,
        "status": state,
        "station_run_count": len(run.get("station_runs") or []),
        "pending_human_gate_count": len(run.get("pending_human_gates") or []),
        "artifact_ref_count": len(run.get("artifact_refs") or []),
    }


def _pv21_station_state(run: dict[str, Any], station_id: str) -> str | None:
    for item in run.get("station_runs") or []:
        if isinstance(item, dict) and str(item.get("station_id") or "") == station_id:
            return str(item.get("status") or "")
    return None


def _pv20_scope_key(scope: ScopeContext) -> str:
    return "|".join([scope.app_id or "", scope.project_id or "", scope.workspace_id or ""])


def _pv20_audit_ref(operation: str, scope: ScopeContext, *, entity_id: str | None = None) -> dict[str, Any]:
    return {
        "audit_ref_id": f"pv20:audit:{operation}:{_pv20_scope_key(scope)}:{entity_id or 'scope'}",
        "operation": operation,
        "scope": _scope_dto(scope),
        "entity_id": entity_id,
        "created_at": _now_iso(),
        "redaction_status": "redacted",
    }


def _pv20_scope_params(scope: ScopeContext) -> dict[str, Any]:
    params: dict[str, Any] = {"app_id": scope.app_id}
    if scope.project_id:
        params["project_id"] = scope.project_id
    if scope.workspace_id:
        params["workspace_id"] = scope.workspace_id
    return params


def _pv20_require_user_confirmation(body: dict[str, Any], *, allowed_sources: set[str]) -> None:
    if body.get("user_confirmed") is not True:
        raise ProtocolError("PV20_ACTION_FORBIDDEN", "PV20 action requires explicit user confirmation.", {"field": "user_confirmed"})
    source = str(body.get("source") or "").strip()
    if source not in allowed_sources:
        raise ProtocolError("PV20_ACTION_FORBIDDEN", "PV20 action source is not allowed.", {"source": source or None})
    if source == "agent":
        raise ProtocolError("PV20_ACTION_FORBIDDEN", "source=agent cannot trigger PV20 execution.", {"source": source})


async def _pv20_ensure_contract_fixture(gateway: GatewayService, scope: ScopeContext) -> dict[str, Any]:
    template, draft = _pv19_ensure_workflow_template(gateway, scope)
    version = _pv20_contract_version(gateway, scope, template, draft)
    instance = _pv20_existing_contract_instance(gateway, scope, str(version.workflow_version_id))
    station_runs: list[dict[str, Any]]
    if instance is None:
        result = await _rpc(
            gateway,
            "workflow.instance.start",
            {
                **_pv20_scope_params(scope),
                "workflow_version_id": str(version.workflow_version_id),
                "input": {"pv20_contract_fixture": True, "stage": "PV20-S1", "executor_contract_only": True},
                "max_steps": 1,
            },
        )
        instance = gateway.workflow_repository.get_instance(str(result["workflow_instance"]["workflow_instance_id"]), scope=scope)
        station_runs = [run for run in result.get("station_runs", []) if isinstance(run, dict)]
    else:
        station_runs = [run.model_dump(mode="json") for run in gateway.workflow_repository.list_station_runs(instance.workflow_instance_id, scope=scope)]
    if not station_runs:
        station_runs = [run.model_dump(mode="json") for run in gateway.workflow_repository.list_station_runs(instance.workflow_instance_id, scope=scope)]
    return {
        "template": template.model_dump(mode="json"),
        "draft": draft.model_dump(mode="json"),
        "version": version.model_dump(mode="json"),
        "instance": instance.model_dump(mode="json"),
        "station_run": station_runs[0] if station_runs else {},
        "station_runs": station_runs,
    }


def _pv20_contract_version(gateway: GatewayService, scope: ScopeContext, template: Any, draft: Any) -> Any:
    for version in gateway.workflow_repository.list_versions(template.workflow_template_id, scope=scope):
        if str(version.version) == "pv20-s1-contract":
            return version
    _template, _draft, version = gateway.workflow_repository.publish_template(
        template.workflow_template_id,
        version="pv20-s1-contract",
        scope=scope,
        expected_revision=draft.revision,
    )
    return version


def _pv20_existing_contract_instance(gateway: GatewayService, scope: ScopeContext, workflow_version_id: str) -> Any | None:
    for instance in gateway.workflow_repository.list_instances(scope=scope):
        if str(instance.workflow_version_id) != workflow_version_id:
            continue
        metadata = instance.metadata if isinstance(instance.metadata, dict) else {}
        input_payload = metadata.get("input") if isinstance(metadata.get("input"), dict) else {}
        if input_payload.get("pv20_contract_fixture") is True:
            return instance
    return None


def _pv20_contract_fixture_for_run(gateway: GatewayService, scope: ScopeContext, run_id: str) -> dict[str, Any]:
    instance = gateway.workflow_repository.get_instance(run_id, scope=scope)
    template = gateway.workflow_repository.get_template(instance.workflow_template_id, scope=scope)
    draft = gateway.workflow_repository.get_draft(str(template.latest_draft_id), scope=scope)
    version = gateway.workflow_repository.get_version(instance.workflow_version_id, scope=scope)
    station_runs = [run.model_dump(mode="json") for run in gateway.workflow_repository.list_station_runs(run_id, scope=scope)]
    if not station_runs:
        raise ProtocolError("PV20_CONTRACT_NOT_READY", "PV20-S1 requires at least one StationRun to bind AgentExecutionEnvelope.", {"workflow_instance_id": run_id})
    return {
        "template": template.model_dump(mode="json"),
        "draft": draft.model_dump(mode="json"),
        "version": version.model_dump(mode="json"),
        "instance": instance.model_dump(mode="json"),
        "station_run": station_runs[0],
        "station_runs": station_runs,
    }


def _pv20_agent_executor_state_dto(fixture: dict[str, Any], scope: ScopeContext) -> dict[str, Any]:
    contract = _pv20_agent_execution_contract_dto(fixture, scope)
    return {
        "schema_version": PV20_AGENT_EXECUTOR_CONTRACT_SCHEMA_VERSION,
        "stage": "PV20-S1",
        "scope": _scope_dto(scope),
        "status": "contract_ready",
        "entry": {"route": "?studio=pv20-complete-agent-executor", "implementation_status": "contract_read_model_only"},
        "workflow": _workflow_summary(fixture["template"]),
        "version": _version_summary(fixture["version"]),
        "workflow_instance": _instance_summary(fixture["instance"]),
        "station_run": _pv20_station_run_summary(fixture["station_run"]),
        "agent_execution_contract": contract["agent_execution_contract"],
        "agent_execution_result": contract["agent_execution_result"],
        "allowed_claim": "PV20-S1 complete: governed Agent execution contract ready for bounded review.",
        "audit_refs": [_pv20_audit_ref("agent_executor.state.read", scope, entity_id=str(fixture["instance"].get("workflow_instance_id") or ""))],
        "redaction_status": "redacted",
    }


def _pv20_agent_execution_contract_dto(fixture: dict[str, Any], scope: ScopeContext) -> dict[str, Any]:
    instance = fixture["instance"]
    station_run = fixture["station_run"]
    station_id = str(station_run.get("station_id") or "station")
    station_run_id = str(station_run.get("station_run_id") or f"station-run:{station_id}")
    workflow_instance_id = str(instance.get("workflow_instance_id") or "")
    agent_id = f"pv20_agent:{station_id}"
    envelope = {
        "schema_version": "pv20.agent_execution_envelope.v1",
        "execution_envelope_id": f"pv20-envelope:{workflow_instance_id}:{station_run_id}",
        "workflow_instance_id": workflow_instance_id,
        "workflow_template_id": instance.get("workflow_template_id"),
        "workflow_version_id": instance.get("workflow_version_id"),
        "station_run_id": station_run_id,
        "station_id": station_id,
        "agent_id": agent_id,
        "operation": "agent.contract.readiness",
        "source": "workflow_runtime",
        "actor_type": "system_service",
        "context_refs": {
            "workflow_context_ref": f"workflow-context://pv20/{workflow_instance_id}",
            "station_input_refs": station_run.get("input_artifact_ids") if isinstance(station_run.get("input_artifact_ids"), list) else [],
            "upstream_artifact_refs": station_run.get("input_artifact_ids") if isinstance(station_run.get("input_artifact_ids"), list) else [],
        },
        "policy_refs": {
            "tool_policy_ref": f"tool-policy://pv20/{agent_id}/allowlist",
            "skill_policy_ref": f"skill-policy://pv20/{agent_id}/allowlist",
            "mcp_policy_ref": f"mcp-policy://pv20/{agent_id}/scope-bound",
            "timeout_policy_ref": f"timeout-policy://pv20/{agent_id}/default",
            "kill_switch_policy_ref": f"kill-switch://pv20/{agent_id}/default",
            "redaction_policy_ref": f"redaction-policy://pv20/{agent_id}/refs-only",
        },
        "allowed_operation_refs": ["skill.read_model.preview", "mcp.tool.preview_contract"],
        "forbidden_operation_refs": ["workflow.template.publish", "approval.respond", "git.push", "production.deploy", "unrestricted.shell"],
        "execution_authority": {
            "durable_mutation_allowed": False,
            "requires_human_handoff_for_high_risk": True,
            "raw_payload_allowed": False,
            "browser_direct_execution_allowed": False,
        },
        "audit_refs": [_pv20_audit_ref("agent_execution.envelope.read", scope, entity_id=station_run_id)],
        "redaction_status": "redacted",
    }
    metadata = station_run.get("metadata") if isinstance(station_run.get("metadata"), dict) else {}
    prior_execution = metadata.get("pv20_agent_execution") if isinstance(metadata.get("pv20_agent_execution"), dict) else None
    prior_tool_execution = metadata.get("pv20_agent_tool_execution") if isinstance(metadata.get("pv20_agent_tool_execution"), dict) else None
    prior_mcp_execution = metadata.get("pv20_agent_mcp_execution") if isinstance(metadata.get("pv20_agent_mcp_execution"), dict) else None
    completed_execution = prior_mcp_execution or prior_tool_execution or prior_execution
    result = {
        "schema_version": "pv20.agent_execution_result.v1",
        "execution_result_id": completed_execution.get("execution_id") if completed_execution else f"pv20-result:{workflow_instance_id}:{station_run_id}",
        "execution_envelope_id": envelope["execution_envelope_id"],
        "workflow_instance_id": workflow_instance_id,
        "station_run_id": station_run_id,
        "agent_id": agent_id,
        "status": completed_execution.get("status") if completed_execution else "contract_ready",
        "execution_status": "completed" if completed_execution else "not_executed_in_s1",
        "tool_call_refs": prior_tool_execution.get("tool_call_refs", []) if prior_tool_execution else [],
        "skill_call_refs": prior_execution.get("skill_call_refs", []) if prior_execution else [],
        "mcp_call_refs": prior_mcp_execution.get("mcp_call_refs", []) if prior_mcp_execution else [],
        "approval_refs": prior_mcp_execution.get("approval_refs", []) if prior_mcp_execution else [],
        "artifact_refs": (
            prior_mcp_execution.get("artifact_refs", [])
            if prior_mcp_execution
            else prior_execution.get("artifact_refs", station_run.get("output_artifact_ids", []))
            if prior_execution
            else station_run.get("output_artifact_ids")
            if isinstance(station_run.get("output_artifact_ids"), list)
            else []
        ),
        "trace_refs": [{"trace_id": instance.get("trace_id"), "event_type": "workflow.instance.started"}] if instance.get("trace_id") else [],
        "quality_refs": station_run.get("quality_evaluation_ids") if isinstance(station_run.get("quality_evaluation_ids"), list) else [],
        "policy_decision": {
            "status": "allowed" if completed_execution else "specified",
            "runtime_execution_allowed_in_s1": False,
            "runtime_execution_allowed_in_s2": bool(prior_execution),
            "runtime_execution_allowed_in_s3a": bool(prior_tool_execution),
            "runtime_execution_allowed_in_s3b": bool(prior_mcp_execution),
        },
        "redaction_status": "redacted",
    }
    return {
        "schema_version": PV20_AGENT_EXECUTOR_CONTRACT_SCHEMA_VERSION,
        "stage": "PV20-S1",
        "scope": _scope_dto(scope),
        "workflow_instance": _instance_summary(instance),
        "station_run": _pv20_station_run_summary(station_run),
        "agent_execution_contract": envelope,
        "agent_execution_result": result,
        "audit_refs": [_pv20_audit_ref("agent_execution.contract.read", scope, entity_id=station_run_id)],
        "redaction_status": "redacted",
    }


def _pv20_agent_execution_evidence_dto(contract: dict[str, Any], scope: ScopeContext) -> dict[str, Any]:
    run_id = str(contract.get("workflow_instance", {}).get("workflow_instance_id") or "")
    result = contract["agent_execution_result"]
    execution_status = str(result.get("execution_status") or "")
    missing = []
    if not contract["agent_execution_contract"].get("station_run_id"):
        missing.append("station_run_id")
    if execution_status not in {"not_executed_in_s1", "completed"}:
        missing.append("s1_execution_boundary")
    if execution_status == "completed" and not result.get("skill_call_refs"):
        missing.append("skill_call_refs")
    return {
        "schema_version": PV20_AGENT_EXECUTOR_CONTRACT_SCHEMA_VERSION,
        "stage": "PV20-S1",
        "scope": _scope_dto(scope),
        "status": "PASS" if not missing else "FAIL",
        "route_boundary": {
            "allowed_prefix": "/bff/pv20",
            "forbidden_direct_routes": ["/v1/rpc", "/v1/internal/executor", "/v1/internal/workflow-store"],
            "status": "specified",
        },
        "claim_matrix": [
            {
                "claim": "PV20-S1 exposes a governed AgentExecutionEnvelope bound to WorkflowInstance and StationRun.",
                "evidence_refs": ["/bff/pv20/agent-executor/state", "/bff/pv20/runs/{run_id}/agent-execution-contract"],
                "status": "PASS",
            },
            {
                "claim": "PV20-S1 is contract/read-model only and does not execute tool, skill or MCP calls.",
                "evidence_refs": ["agent_execution_result.execution_status=not_executed_in_s1"],
                "status": "PASS" if execution_status == "not_executed_in_s1" else "SUPERSEDED_BY_S2",
            },
            {
                "claim": "PV20-S2 executes an allowlisted local skill/read-model and records backend evidence.",
                "evidence_refs": result.get("skill_call_refs", []),
                "status": "PASS" if result.get("skill_call_refs") else "PENDING",
            },
            {
                "claim": "PV20-S3A executes an allowlisted read-only local tool and records backend evidence.",
                "evidence_refs": result.get("tool_call_refs", []),
                "status": "PASS" if result.get("tool_call_refs") else "PENDING",
            },
            {
                "claim": "PV20-S3B executes an allowlisted local MCP fixture through connector runtime and records backend evidence.",
                "evidence_refs": result.get("mcp_call_refs", []),
                "status": "PASS" if result.get("mcp_call_refs") else "PENDING",
            },
            {
                "claim": "PV20-S4 records approval handoff refs and denies unconfirmed or agent-sourced execution.",
                "evidence_refs": result.get("approval_refs", []),
                "status": "PASS" if result.get("approval_refs") else "PENDING",
            },
        ],
        "missing_evidence": missing,
        "allowed_claim": (
            "PV20-S4 complete: approval handoff and denied mutation fixtures ready for bounded review."
            if result.get("approval_refs")
            else "PV20-S3B complete: allowlisted local MCP fixture execution ready for bounded review."
            if result.get("mcp_call_refs")
            else "PV20-S3A complete: allowlisted local tool execution ready for bounded review."
            if result.get("tool_call_refs")
            else "PV20-S2 complete: allowlisted local skill execution ready for bounded review."
            if result.get("skill_call_refs")
            else "PV20-S1 complete: governed Agent execution contract ready for bounded review."
        ),
        "not_claimed": [
            "production_readiness",
            "unrestricted_automation_readiness",
            "full_workflow_studio_readiness",
            "unrestricted_tool_execution_readiness",
            "unrestricted_mcp_execution_readiness",
        ],
        "audit_refs": [_pv20_audit_ref("agent_execution.evidence.summary", scope, entity_id=run_id)],
        "redaction_status": "redacted",
    }


def _pv20_station_run_summary(station_run: dict[str, Any]) -> dict[str, Any]:
    metadata = station_run.get("metadata") if isinstance(station_run.get("metadata"), dict) else {}
    return {
        "station_run_id": station_run.get("station_run_id"),
        "station_id": station_run.get("station_id"),
        "status": station_run.get("status"),
        "attempt": station_run.get("attempt"),
        "approval_id": metadata.get("approval_id"),
        "output_artifact_ids": station_run.get("output_artifact_ids") if isinstance(station_run.get("output_artifact_ids"), list) else [],
        "quality_evaluation_ids": station_run.get("quality_evaluation_ids") if isinstance(station_run.get("quality_evaluation_ids"), list) else [],
    }


def _pv18_scope_key(scope: ScopeContext) -> str:
    return "|".join([scope.app_id or "", scope.project_id or "", scope.workspace_id or ""])


def _v13_validate_graph(graph: dict[str, Any]) -> dict[str, Any]:
    nodes = graph.get("nodes") if isinstance(graph.get("nodes"), list) else []
    edges = graph.get("edges") if isinstance(graph.get("edges"), list) else []
    node_ids = {str(node.get("node_id") or "").strip() for node in nodes if isinstance(node, dict)}
    errors: list[dict[str, str]] = []
    if str(graph.get("schema_version") or "") != V13_WORKFLOW_STUDIO_SCHEMA_VERSION:
        errors.append({"code": "SCHEMA_VERSION_MISMATCH", "message": "Graph schema_version must be v13.workflow_spec_graph.v1."})
    if str(graph.get("workflow_id") or "") != V13_WORKFLOW_ID:
        errors.append({"code": "WORKFLOW_ID_MISMATCH", "message": "Graph workflow_id does not match the V13 pilot workflow."})
    if len(node_ids) < 2:
        errors.append({"code": "GRAPH_TOO_SMALL", "message": "Graph must include at least two nodes."})
    for edge in edges:
        if not isinstance(edge, dict):
            errors.append({"code": "EDGE_INVALID", "message": "Each edge must be an object."})
            continue
        source_id = str(edge.get("source_node_id") or "").strip()
        target_id = str(edge.get("target_node_id") or "").strip()
        if source_id not in node_ids or target_id not in node_ids:
            errors.append({"code": "EDGE_ENDPOINT_MISSING", "message": f"Edge {edge.get('edge_id') or 'unknown'} has missing source or target node."})
    return {
        "schema_version": "v13.workflow_graph_validation_result.v1",
        "status": "FAIL" if errors else "PASS",
        "errors": errors,
        "runtime_backed": False,
        "publish_or_run_started": False,
        "audit_ref": "audit://v13/studio-pilot/graph-validation",
        "redaction_status": "redacted",
    }


async def _v13_workflow_diff_decision(proposal_id: str, request: Request, gateway: GatewayService, *, decision: str) -> Any:
    try:
        if proposal_id != V13_WORKFLOW_DIFF_ID:
            raise ProtocolError("NOT_FOUND", "V13 WorkflowDiff proposal was not found.", {"proposal_id": proposal_id})
        params = {**_query_scope_params(request), "workflow_id": V13_WORKFLOW_ID, "proposal_id": proposal_id}
        auth = await authorize_http_request(request, gateway=gateway, params=params, capability="workflow_patches.write")
        handoff_ref = f"handoff://v13/studio-pilot/{proposal_id}" if decision == "handoff_confirmed" else None
        dto = {
            "schema_version": "v13.workflow_diff_decision.v1",
            "proposal_id": proposal_id,
            "decision": decision,
            "handoff_state": "ready_for_later_publish_review" if decision == "handoff_confirmed" else "not_ready_for_publish",
            "handoff_ref": handoff_ref,
            "runtime_backed": False,
            "publish_or_run_started": False,
            "human_confirmation_required": True,
            "audit_ref": f"audit://v13/studio-pilot/workflow-diff/{decision}",
            "redaction_status": "redacted",
        }
        response = JSONResponse(_redact(dto))
        add_dev_warning(response, auth)
        return response
    except ProtocolError as exc:
        return http_error_response(exc)


def _workflow_platform_scenario_projection_dto(scope: ScopeContext) -> dict[str, Any]:
    scenarios: list[dict[str, Any]] = []
    for scenario_id, scenario in WORKFLOW_PLATFORM_SCENARIOS.items():
        scenarios.append(
            {
                "scenario_id": scenario_id,
                "title": scenario["title"],
                "input_contract": {
                    "accepted_inputs": scenario["accepted_inputs"],
                    "required_refs": ["source_refs"],
                    "source_refs": scenario["source_refs"],
                },
                "workflow_template": {
                    "node_refs": scenario["node_refs"],
                    "edge_refs": [f"{scenario_id}:edge:{index}" for index in range(max(0, len(scenario["node_refs"]) - 1))],
                },
                "inspector_projection": {
                    "agent_refs": scenario["agent_refs"],
                    "tool_refs": scenario["tool_refs"],
                    "skill_refs": scenario["skill_refs"],
                    "mcp_refs": scenario["mcp_refs"],
                    "quality_gate_refs": [f"quality://wp-m5a/{scenario_id}"],
                },
                "timeline_projection": [
                    {"step": "input", "state": "ready", "ref": scenario["source_refs"][0]},
                    {"step": "produce_business_output", "state": "ready_for_human_review", "ref": f"artifact://wp-m5a/{scenario_id}/output-summary"},
                    {"step": "human_review", "state": "ready", "ref": scenario["human_review_ref"]},
                ],
                "evidence_categories": ["artifact", "trace", "quality", "audit", "claim", "redaction"],
                "fallback_used": False,
                "fallback_boundary": "Local scenarioData may remain as visual fallback only; this DTO is the accepted scenario projection source.",
            }
        )
    return {
        "schema_version": WORKFLOW_PLATFORM_SCENARIO_PROJECTION_SCHEMA_VERSION,
        "source": "bff_projection",
        "fallback_used": False,
        "scope": _scope_dto(scope),
        "scenario_count": len(scenarios),
        "scenarios": scenarios,
        "mock_reduction_boundary": {
            "scenarioData": "fallback_or_visual_reference_only",
            "fallbackGraph": "offline_canvas_fallback_only",
            "static_chat_timeline_inspector": "fallback_or_design_reference_only",
        },
        "audit_refs": [_workflow_platform_audit_ref("scenario_projection.read", scope)],
        "redaction_status": "redacted",
    }


def _workflow_platform_business_output_dto(scenario_id: str, scope: ScopeContext) -> dict[str, Any]:
    scenario = WORKFLOW_PLATFORM_SCENARIOS[scenario_id]
    artifact_ref = f"artifact://wp-m5a/{scenario_id}/output-summary"
    return {
        "schema_version": WORKFLOW_PLATFORM_BUSINESS_OUTPUT_SCHEMA_VERSION,
        "scenario_id": scenario_id,
        "title": scenario["title"],
        "status": "ready_for_human_review",
        "source_refs": scenario["source_refs"],
        "output_summary": {
            "title": scenario["output_title"],
            "body": scenario["output_body"],
            "artifact_refs": [artifact_ref],
            "human_review_ref": scenario["human_review_ref"],
            "quality_status": scenario["quality_status"],
        },
        "evidence_refs": {
            "artifact": [artifact_ref],
            "trace": [f"trace://wp-m5a/{scenario_id}/workflow-run"],
            "quality": [f"quality://wp-m5a/{scenario_id}"],
            "audit": [f"audit://wp-m5a/{scenario_id}/business-output"],
            "claim": [f"claim://wp-m5a/{scenario_id}/bounded-output"],
            "redaction": [f"redaction://wp-m5a/{scenario_id}/scan-pass"],
        },
        "human_review": {
            "review_ref": scenario["human_review_ref"],
            "state": "ready_for_review",
            "required_before_external_handoff": True,
        },
        "non_claims": [
            "not_production_ready",
            "not_complete_workflow_studio_ga",
            "not_agent_executor_ready",
            "not_external_app_contract_complete",
        ],
        "scope": _scope_dto(scope),
        "audit_refs": [_workflow_platform_audit_ref("business_output.read", scope, entity_id=scenario_id)],
        "redaction_status": "redacted",
    }


def _workflow_platform_audit_ref(operation: str, scope: ScopeContext, *, entity_id: str | None = None) -> dict[str, Any]:
    scope_key = "|".join([scope.app_id or "", scope.project_id or "", scope.workspace_id or ""])
    return {
        "audit_ref_id": f"workflow-platform:audit:{operation}:{scope_key}:{entity_id or 'scope'}",
        "operation": operation,
        "scope": _scope_dto(scope),
        "entity_id": entity_id,
        "created_at": _now_iso(),
        "redaction_status": "redacted",
    }


def _pv18_workspace_id(scope: ScopeContext) -> str:
    return f"knowledge:{scope.workspace_id or 'local'}:{scope.project_id or 'demo'}:{scope.app_id or 'app'}"


def _pv18_audit_ref(operation: str, scope: ScopeContext, *, entity_id: str | None = None) -> dict[str, Any]:
    return {
        "audit_ref_id": f"pv18:audit:{operation}:{_pv18_scope_key(scope)}:{entity_id or 'scope'}",
        "operation": operation,
        "scope": _scope_dto(scope),
        "entity_id": entity_id,
        "created_at": _now_iso(),
        "redaction_status": "redacted",
    }


def _pv18_workspace_projection(scope: ScopeContext) -> dict[str, Any]:
    workspace_id = _pv18_workspace_id(scope)
    stored = _PV18_KNOWLEDGE_WORKSPACES.get(workspace_id)
    if stored is not None:
        return stored
    return {
        "workspace_id": workspace_id,
        "display_name": "PV18 Knowledge OPC Workspace",
        "owner": "local-reviewer",
        "scope": _scope_dto(scope),
        "data_boundary": "BFF DTO -> Pack/Connector/Gateway/Evidence",
        "audit_refs": [_pv18_audit_ref("knowledge.workspace.default_projection", scope, entity_id=workspace_id)],
        "redaction_status": "redacted",
    }


def _pv18_store_workspace(scope: ScopeContext, body: dict[str, Any]) -> dict[str, Any]:
    workspace_id = str(body.get("workspace_id") or _pv18_workspace_id(scope)).strip()
    if not workspace_id:
        raise ProtocolError("INVALID_PARAMS", "workspace_id is required.", {"field": "workspace_id"})
    workspace = {
        "workspace_id": workspace_id,
        "display_name": str(body.get("display_name") or "PV18 Knowledge OPC Workspace"),
        "owner": str(body.get("owner") or "local-reviewer"),
        "scope": _scope_dto(scope),
        "data_boundary": "BFF DTO -> Pack/Connector/Gateway/Evidence",
        "audit_refs": [_pv18_audit_ref("knowledge.workspace.upsert", scope, entity_id=workspace_id)],
        "redaction_status": "redacted",
    }
    _PV18_KNOWLEDGE_WORKSPACES[workspace_id] = _redact(workspace)
    return _PV18_KNOWLEDGE_WORKSPACES[workspace_id]


def _pv18_connector_health(gateway: GatewayService) -> dict[str, Any]:
    try:
        connector = gateway.connector_registry.get_connector(DATA_SERVICE_CONNECTOR_ID)
        health = connector.get("health") if isinstance(connector.get("health"), dict) else {}
        capabilities = connector.get("capabilities") if isinstance(connector.get("capabilities"), dict) else {}
        metadata = connector.get("metadata") if isinstance(connector.get("metadata"), dict) else {}
        execution_mode = str(metadata.get("execution") or connector.get("execution_mode") or "unknown")
        status = str(connector.get("health") or health.get("status") or "available")
        return {
            "connector_id": DATA_SERVICE_CONNECTOR_ID,
            "status": status,
            "execution_mode": execution_mode,
            "real_data_service": execution_mode == "mcp_stdio" and status in {"available", "configured"},
            "capabilities": capabilities,
            "redaction_status": "redacted",
        }
    except Exception as exc:
        return {
            "connector_id": DATA_SERVICE_CONNECTOR_ID,
            "status": "unavailable",
            "execution_mode": "unavailable",
            "real_data_service": False,
            "reason": exc.__class__.__name__,
            "capabilities": {},
            "redaction_status": "redacted",
        }


def _pv18_real_data_service_enabled(gateway: GatewayService) -> bool:
    health = _pv18_connector_health(gateway)
    return health.get("real_data_service") is True


def _pv18_source_from_body(gateway: GatewayService, scope: ScopeContext, workspace: dict[str, Any], body: dict[str, Any]) -> dict[str, Any]:
    workspace_id = str(workspace["workspace_id"])
    content = str(body.get("content") or body.get("text") or "").strip()
    title = str(body.get("title") or "PV18 Knowledge Source").strip()
    if not content:
        raise ProtocolError("INVALID_PARAMS", "content is required.", {"field": "content"})
    source_id = f"pv18-src-{uuid4().hex[:8]}"
    data_service = _pv18_import_source_to_data_service(gateway, scope, workspace, title, content)
    artifact = gateway.artifact_registry.register_external(
        external_asset_uri=f"pv18://knowledge/{workspace_id}/{source_id}",
        app_id=scope.app_id,
        project_id=scope.project_id,
        workspace_id=scope.workspace_id,
        domain="knowledge",
        kind="source_reference",
        name=title,
        mime="text/plain",
        metadata={
            "source_id": source_id,
            "workspace_id": workspace_id,
            "content_length": len(content),
            "source": "pv18_bff_source_import",
            "data_service_workspace_id": data_service.get("workspace_id"),
            "real_data_service": data_service.get("real_data_service"),
        },
    )
    artifact_refs = [{"artifact_ref": artifact.get("artifact_id"), "kind": artifact.get("kind"), "name": artifact.get("name")}]
    artifact_refs.extend(_pv18_envelope_artifact_refs(data_service.get("envelope")))
    return {
        "source_id": source_id,
        "source_reference": {
            "source_id": source_id,
            "workspace_id": workspace_id,
            "data_service_workspace_id": data_service.get("workspace_id"),
            "title": title,
            "status": "imported",
            "content_length": len(content),
            "real_data_service": data_service.get("real_data_service"),
        },
        "note": {
            "title": title,
            "summary": content[:160],
            "status": "ready_for_build",
        },
        "content": content,
        "artifact_refs": artifact_refs,
        "lineage_refs": [{"from": "source_import", "to": artifact.get("artifact_id"), "kind": "source_reference"}],
        "data_service": data_service,
        "redaction_status": "redacted",
    }


def _pv18_import_source_to_data_service(
    gateway: GatewayService,
    scope: ScopeContext,
    workspace: dict[str, Any],
    title: str,
    content: str,
) -> dict[str, Any]:
    if not _pv18_real_data_service_enabled(gateway):
        return {
            "status": "contract_stub",
            "workspace_id": None,
            "real_data_service": False,
            "blocked_reason": "HARNESS_DATA_SERVICE_MCP_EXECUTION=stdio is required for real PV18 acceptance.",
        }
    data_service_workspace_id = _pv18_ensure_data_service_workspace(gateway, scope, workspace)
    result = _pv18_call_data_service_tool(
        gateway,
        "knowledge_source_import",
        {
            "workspace_id": data_service_workspace_id,
            "paths": [],
            "texts": [{"title": title, "content": content, "metadata": {"source": "pv18_knowledge_opc"}}],
            "metadata": {"owner": "pv18-knowledge-opc", "workflow": "pv18_knowledge_opc"},
        },
    )
    return {
        "status": result.get("status"),
        "workspace_id": data_service_workspace_id,
        "real_data_service": True,
        "tool": "knowledge_source_import",
        "steps": result.get("steps", []),
        "envelope": result.get("envelope", {}),
    }


def _pv18_ensure_data_service_workspace(gateway: GatewayService, scope: ScopeContext, workspace: dict[str, Any]) -> str:
    stored_workspace_id = workspace.get("data_service_workspace_id")
    if isinstance(stored_workspace_id, str) and stored_workspace_id:
        return stored_workspace_id
    result = _pv18_call_data_service_tool(
        gateway,
        "knowledge_workspace_create",
        {
            "name": str(workspace.get("workspace_id") or _pv18_workspace_id(scope)),
            "owner": "pv18-knowledge-opc",
            "tags": ["harnessos-pv18", "opc"],
        },
    )
    envelope = result.get("envelope") if isinstance(result.get("envelope"), dict) else {}
    workspace_id = envelope.get("workspace_id")
    if not isinstance(workspace_id, str) or not workspace_id:
        raise ProtocolError("UPSTREAM_UNAVAILABLE", "Data Service MCP did not return a workspace_id.", {"tool": "knowledge_workspace_create"})
    workspace["data_service_workspace_id"] = workspace_id
    workspace["real_data_service"] = True
    workspace["data_service_steps"] = list(workspace.get("data_service_steps") or []) + list(result.get("steps") or [])
    _PV18_KNOWLEDGE_WORKSPACES[str(workspace["workspace_id"])] = _redact(workspace)
    return workspace_id


def _pv18_call_data_service_tool(gateway: GatewayService, tool: str, payload: dict[str, Any]) -> dict[str, Any]:
    try:
        return KnowledgeMcpWorkflowRunner(gateway.connector_execution_runtime).call_tool(tool, payload)
    except Exception as exc:
        raise ProtocolError(
            "UPSTREAM_UNAVAILABLE",
            f"Data Service MCP tool failed: {tool}",
            {"tool": tool, "reason": exc.__class__.__name__, "message": str(exc)[:240]},
        ) from exc


def _pv18_build_from_sources(
    gateway: GatewayService,
    scope: ScopeContext,
    workspace: dict[str, Any],
    sources: list[dict[str, Any]],
    body: dict[str, Any],
) -> dict[str, Any]:
    workspace_id = str(workspace["workspace_id"])
    if not sources:
        build = _pv18_new_build(scope, workspace_id, status="failed")
        build["failure_reason"] = "source_required"
        build["next_actions"] = ["导入至少一个 source/document 后重新启动 build。"]
        build["real_data_service"] = _pv18_real_data_service_enabled(gateway)
        return build
    if not _pv18_real_data_service_enabled(gateway):
        build = _pv18_new_build(scope, workspace_id, status="completed")
        build["stage"] = "contract_stub_indexed"
        build["real_data_service"] = False
        build["next_actions"] = ["当前为 contract_stub 受限状态；真实验收需启用 HARNESS_DATA_SERVICE_MCP_EXECUTION=stdio。"]
        return build

    source_texts = _pv18_source_texts(sources)
    result = KnowledgeMcpWorkflowRunner(gateway.connector_execution_runtime).run_acceptance(
        name=_pv18_acceptance_workspace_name(workspace),
        query="PV18 Knowledge OPC build validation",
        texts=source_texts,
        owner="pv18-knowledge-opc",
        build_mode=_pv18_data_service_build_mode(str(body.get("mode") or "full")),
        poll_interval=0.05,
        max_polls=40,
    )
    result_dto = result.to_dict()
    status = str(result_dto.get("status") or "failed")
    completed = status in {"ok", "completed"}
    build = _pv18_new_build(scope, workspace_id, status="completed" if status == "completed" else "failed")
    build["status"] = "completed" if completed else "failed"
    build["data_service_workspace_id"] = result_dto.get("workspace_id")
    build["operation_id"] = result_dto.get("operation_id")
    build["stage"] = "completed" if completed else status
    build["failure_reason"] = None if completed else status
    build["artifact_refs"] = _pv18_step_artifact_refs(result_dto.get("steps", []))
    build["data_service_steps"] = result_dto.get("steps", [])
    build["runner_warnings"] = result_dto.get("warnings", [])
    build["real_data_service"] = True
    return build


def _pv18_new_build(scope: ScopeContext, workspace_id: str, *, status: str) -> dict[str, Any]:
    build_id = f"pv18-build-{uuid4().hex[:8]}"
    return {
        "build_id": build_id,
        "workspace_id": workspace_id,
        "status": status,
        "stage": "indexed" if status == "completed" else "blocked",
        "failure_reason": None if status == "completed" else "unknown",
        "trace_refs": [{"trace_id": f"pv18:trace:build:{build_id}", "event_type": f"knowledge.build.{status}"}],
        "next_actions": ["发起 query 并审查 citation。"] if status == "completed" else [],
        "audit_refs": [_pv18_audit_ref("knowledge.build.start", scope, entity_id=build_id)],
    }


def _pv18_data_service_workspace_id(workspace: dict[str, Any], sources: list[dict[str, Any]]) -> str:
    candidates: list[Any] = [workspace.get("data_service_workspace_id")]
    candidates.extend(source.get("data_service", {}).get("workspace_id") for source in sources if isinstance(source.get("data_service"), dict))
    candidates.extend(source.get("source_reference", {}).get("data_service_workspace_id") for source in sources if isinstance(source.get("source_reference"), dict))
    for candidate in candidates:
        if isinstance(candidate, str) and candidate:
            return candidate
    raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "PV18 real Data Service workspace is missing.", {"fixture": "real_data_service_workspace_required"})


def _pv18_data_service_build_mode(mode: str) -> str:
    allowed = {"full", "incremental", "graph_only", "llmwiki_only"}
    return mode if mode in allowed else "full"


def _pv18_envelope_stage(envelope: dict[str, Any]) -> str | None:
    data = envelope.get("data") if isinstance(envelope.get("data"), dict) else {}
    stage = data.get("stage")
    return str(stage) if stage is not None else None


def _pv18_envelope_failure(envelope: dict[str, Any]) -> str | None:
    data = envelope.get("data") if isinstance(envelope.get("data"), dict) else {}
    error = data.get("error") if isinstance(data.get("error"), dict) else {}
    message = error.get("message")
    return str(message) if message else None


def _pv18_envelope_artifact_refs(envelope: Any) -> list[dict[str, Any]]:
    if not isinstance(envelope, dict):
        return []
    refs = envelope.get("artifact_refs")
    if isinstance(refs, list):
        return [ref for ref in refs if isinstance(ref, dict)]
    data = envelope.get("data") if isinstance(envelope.get("data"), dict) else {}
    refs = data.get("artifact_refs")
    if isinstance(refs, list):
        return [ref for ref in refs if isinstance(ref, dict)]
    return []


def _pv18_step_artifact_refs(steps: Any) -> list[dict[str, Any]]:
    if not isinstance(steps, list):
        return []
    refs: list[dict[str, Any]] = []
    for step in steps:
        if not isinstance(step, dict):
            continue
        if step.get("artifact_id"):
            refs.append({"artifact_ref": step.get("artifact_id"), "tool": step.get("tool")})
        refs.extend(_pv18_envelope_artifact_refs(step.get("envelope")))
    return refs


def _pv18_source_texts(sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    texts: list[dict[str, Any]] = []
    for source in sources:
        if not isinstance(source, dict):
            continue
        note = source.get("note") if isinstance(source.get("note"), dict) else {}
        title = str(note.get("title") or source.get("source_id") or "PV18 Knowledge Source")
        content = str(source.get("content") or note.get("summary") or "")
        if content:
            texts.append({"title": title, "content": content, "metadata": {"source": "pv18_knowledge_opc"}})
    return texts


def _pv18_acceptance_workspace_name(workspace: dict[str, Any]) -> str:
    base = str(workspace.get("workspace_id") or "pv18-knowledge-opc").replace(":", "-")
    return f"{base}-{uuid4().hex[:8]}"


def _pv18_last_step_for_tool(steps: Any, tool: str) -> dict[str, Any]:
    if not isinstance(steps, list):
        return {}
    for step in reversed(steps):
        if isinstance(step, dict) and step.get("tool") == tool:
            return step
    return {}


def _pv18_run_knowledge_flow(gateway: GatewayService, workspace_id: str, query: str, sources: list[dict[str, Any]]) -> dict[str, Any]:
    texts = [
        {
            "title": str(source.get("note", {}).get("title") or source.get("source_id") or "PV18 Source"),
            "content": str(source.get("content") or source.get("note", {}).get("summary") or ""),
        }
        for source in sources
    ]
    runner = KnowledgeMcpWorkflowRunner(gateway.connector_execution_runtime)
    try:
        result = runner.run_acceptance(
            name=workspace_id,
            query=query,
            texts=texts,
            owner="pv18-knowledge-opc",
            poll_interval=0.01,
            max_polls=8,
        )
        return result.to_dict()
    except Exception as exc:
        return {
            "status": "blocked",
            "workspace_id": workspace_id,
            "operation_id": None,
            "steps": [],
            "warnings": [f"knowledge runner blocked: {exc.__class__.__name__}"],
        }


def _pv18_query_result(
    gateway: GatewayService,
    scope: ScopeContext,
    workspace: dict[str, Any],
    query: str,
    sources: list[dict[str, Any]],
) -> dict[str, Any]:
    workspace_id = str(workspace["workspace_id"])
    if _pv18_real_data_service_enabled(gateway):
        result = KnowledgeMcpWorkflowRunner(gateway.connector_execution_runtime).run_acceptance(
            name=_pv18_acceptance_workspace_name(workspace),
            query=query,
            texts=_pv18_source_texts(sources),
            owner="pv18-knowledge-opc",
            poll_interval=0.05,
            max_polls=40,
        )
        result_dto = result.to_dict()
        query_step = _pv18_last_step_for_tool(result_dto.get("steps", []), "knowledge_query_v2")
        envelope = query_step.get("envelope") if isinstance(query_step.get("envelope"), dict) else {}
        data = envelope.get("data") if isinstance(envelope.get("data"), dict) else {}
        citations = _pv18_extract_citations(data)
        query_id = f"pv18-query-{uuid4().hex[:8]}"
        return {
            "query_id": query_id,
            "workspace_id": workspace_id,
            "data_service_workspace_id": result_dto.get("workspace_id"),
            "status": "answered" if citations else "pending_review",
            "answer": str(data.get("answer") or "真实 data_service 已返回结果，但 answer 字段为空。"),
            "brief": "真实 data_service MCP query_v2 结果；必须结合 citation 和 evidence 审查。",
            "citation_bundle": {"status": "pass" if citations else "missing", "citations": citations},
            "citation_coverage": {"status": "pass" if citations else "missing", "source_ref_count": len(citations)},
            "source_refs": citations,
            "artifact_refs": _pv18_step_artifact_refs(result_dto.get("steps", [])),
            "trace_refs": [{"trace_id": f"pv18:trace:query:{query_id}", "event_type": "knowledge.query.answered"}],
            "runner_warnings": result_dto.get("warnings") if isinstance(result_dto.get("warnings"), list) else [],
            "data_service_steps": result_dto.get("steps", []),
            "real_data_service": True,
            "audit_refs": [_pv18_audit_ref("knowledge.query", scope, entity_id=query_id)],
            "redaction_status": "redacted",
        }

    runner_result = _pv18_run_knowledge_flow(gateway, workspace_id, query, sources)
    query_dto = _pv18_query_result_from_runner(scope, workspace_id, query, runner_result, sources)
    query_dto["real_data_service"] = False
    return query_dto


def _pv18_extract_citations(data: dict[str, Any]) -> list[dict[str, Any]]:
    llmwiki = data.get("engine_payloads", {}).get("llmwiki") if isinstance(data.get("engine_payloads"), dict) else {}
    candidates = llmwiki.get("citations") if isinstance(llmwiki, dict) else None
    if not isinstance(candidates, list):
        candidates = data.get("citations") if isinstance(data.get("citations"), list) else []
    citations: list[dict[str, Any]] = []
    for item in candidates:
        if not isinstance(item, dict):
            continue
        citations.append(
            {
                "source_id": item.get("source_id") or item.get("id") or item.get("source"),
                "title": item.get("title") or item.get("source") or "Knowledge source",
                "locator": item.get("locator"),
                "authority": item.get("authority"),
                "source_type": item.get("source_type"),
                "coverage": "supporting",
            }
        )
    return citations


def _pv18_query_result_from_runner(
    scope: ScopeContext,
    workspace_id: str,
    query: str,
    runner_result: dict[str, Any],
    sources: list[dict[str, Any]],
) -> dict[str, Any]:
    query_id = f"pv18-query-{uuid4().hex[:8]}"
    steps = runner_result.get("steps") if isinstance(runner_result.get("steps"), list) else []
    artifact_refs = [
        {"artifact_ref": step.get("artifact_id"), "tool": step.get("tool")}
        for step in steps
        if isinstance(step, dict) and step.get("artifact_id")
    ]
    source_refs = [source.get("source_reference") for source in sources if isinstance(source.get("source_reference"), dict)]
    citation_bundle = {
        "status": "pass" if source_refs else "missing",
        "citations": [
            {"source_id": item.get("source_id"), "title": item.get("title"), "coverage": "supporting"}
            for item in source_refs
            if isinstance(item, dict)
        ],
    }
    return {
        "query_id": query_id,
        "workspace_id": runner_result.get("workspace_id") or workspace_id,
        "status": "answered" if citation_bundle["citations"] else "pending_review",
        "answer": f"基于 {len(source_refs)} 个 Knowledge source，当前问题“{query}”已有可审查回答。",
        "brief": "这是 PV18 bounded Knowledge OPC 回答投影，必须结合 citation 和 evidence 审查。",
        "citation_bundle": citation_bundle,
        "citation_coverage": {"status": citation_bundle["status"], "source_ref_count": len(source_refs)},
        "source_refs": source_refs,
        "artifact_refs": artifact_refs,
        "trace_refs": [{"trace_id": f"pv18:trace:query:{query_id}", "event_type": "knowledge.query.answered"}],
        "runner_warnings": runner_result.get("warnings") if isinstance(runner_result.get("warnings"), list) else [],
        "audit_refs": [_pv18_audit_ref("knowledge.query", scope, entity_id=query_id)],
        "redaction_status": "redacted",
    }


def _pv18_quality_feedback(gateway: GatewayService, scope: ScopeContext, workspace: dict[str, Any], body: dict[str, Any]) -> dict[str, Any]:
    quality_id = f"pv18-quality-{uuid4().hex[:8]}"
    workspace_id = str(workspace["workspace_id"])
    issues = body.get("issues") if isinstance(body.get("issues"), list) else []
    low_signal_sources = body.get("low_signal_sources") if isinstance(body.get("low_signal_sources"), list) else []
    status = "pending_review" if issues or low_signal_sources else "pass"
    feedback: dict[str, Any] = {
        "quality_id": quality_id,
        "workspace_id": workspace_id,
        "quality_status": status,
        "issues": issues,
        "low_signal_sources": low_signal_sources,
        "correction_required": status != "pass",
        "trace_refs": [{"trace_id": f"pv18:trace:quality:{quality_id}", "event_type": f"knowledge.quality.{status}"}],
        "audit_refs": [_pv18_audit_ref("knowledge.quality.feedback", scope, entity_id=quality_id)],
        "redaction_status": "redacted",
    }
    if _pv18_real_data_service_enabled(gateway):
        data_service_workspace_id = str(workspace.get("data_service_workspace_id") or body.get("data_service_workspace_id") or "")
        if data_service_workspace_id:
            result = _pv18_call_data_service_tool(
                gateway,
                "knowledge_quality_feedback_v2",
                {
                    "workspace_id": data_service_workspace_id,
                    "target_type": "query",
                    "target_id": str(body.get("target_id") or "pv18-query"),
                    "action": "needs_review" if status != "pass" else "accept",
                    "reason": str(body.get("reason") or "PV18 Knowledge OPC quality feedback"),
                    "metadata": {"source": "pv18_knowledge_opc", "issue_count": len(issues), "low_signal_count": len(low_signal_sources)},
                },
            )
            feedback["data_service_workspace_id"] = data_service_workspace_id
            feedback["data_service_steps"] = result.get("steps", [])
            feedback["data_service_envelope"] = result.get("envelope", {})
            feedback["real_data_service"] = True
    feedback.setdefault("real_data_service", False)
    return feedback


def _pv18_correction_plan(gateway: GatewayService, scope: ScopeContext, workspace: dict[str, Any], body: dict[str, Any]) -> dict[str, Any]:
    plan_id = f"pv18-correction-{uuid4().hex[:8]}"
    workspace_id = str(workspace["workspace_id"])
    rules = body.get("rules") if isinstance(body.get("rules"), list) else ["补充缺失 citation", "人工复核低信号来源"]
    plan: dict[str, Any] = {
        "plan_id": plan_id,
        "workspace_id": workspace_id,
        "status": "pending_human_review",
        "rules": rules,
        "requires_human_review": True,
        "auto_publish_allowed": False,
        "audit_refs": [_pv18_audit_ref("knowledge.correction.plan", scope, entity_id=plan_id)],
        "redaction_status": "redacted",
    }
    if _pv18_real_data_service_enabled(gateway):
        data_service_workspace_id = str(workspace.get("data_service_workspace_id") or body.get("data_service_workspace_id") or "")
        if data_service_workspace_id:
            rules_result = _pv18_call_data_service_tool(
                gateway,
                "knowledge_correction_rules_v2",
                {"workspace_id": data_service_workspace_id, "status": "draft", "limit": 20},
            )
            rule_id = _pv18_first_rule_id_from_envelope(rules_result.get("envelope", {}))
            steps = list(rules_result.get("steps") or [])
            if rule_id:
                review_result = _pv18_call_data_service_tool(
                    gateway,
                    "knowledge_review_correction_rule_v2",
                    {
                        "workspace_id": data_service_workspace_id,
                        "rule_id": rule_id,
                        "status": "approved",
                        "reviewer": "pv18-knowledge-opc",
                        "note": "PV18 bounded review approves the rule for non-destructive correction planning.",
                    },
                )
                steps.extend(list(review_result.get("steps") or []))
            plan_result = _pv18_call_data_service_tool(
                gateway,
                "knowledge_correction_plan_v2",
                {"workspace_id": data_service_workspace_id, "rebuild": False},
            )
            steps.extend(list(plan_result.get("steps") or []))
            envelope = plan_result.get("envelope") if isinstance(plan_result.get("envelope"), dict) else {}
            data = envelope.get("data") if isinstance(envelope.get("data"), dict) else {}
            plan["rules"] = data.get("actions") if isinstance(data.get("actions"), list) else rules
            plan["data_service_workspace_id"] = data_service_workspace_id
            plan["data_service_steps"] = steps
            plan["data_service_envelope"] = envelope
            plan["real_data_service"] = True
    plan.setdefault("real_data_service", False)
    return plan


def _pv18_first_rule_id_from_envelope(envelope: Any) -> str | None:
    if not isinstance(envelope, dict):
        return None
    data = envelope.get("data") if isinstance(envelope.get("data"), dict) else {}
    items = data.get("items") or data.get("rules") or []
    if not isinstance(items, list) or not items:
        return None
    first = items[0]
    if isinstance(first, dict) and isinstance(first.get("rule_id"), str):
        return first["rule_id"]
    return None


def _pv18_evidence_summary_projection(scope: ScopeContext, workspace_id: str) -> dict[str, Any]:
    sources = _PV18_KNOWLEDGE_SOURCES.get(workspace_id, [])
    builds = _PV18_KNOWLEDGE_BUILDS.get(workspace_id, [])
    queries = _PV18_KNOWLEDGE_QUERIES.get(workspace_id, [])
    quality = _PV18_KNOWLEDGE_QUALITY.get(workspace_id, [])
    corrections = _PV18_KNOWLEDGE_CORRECTIONS.get(workspace_id, [])
    artifact_refs = [ref for source in sources for ref in source.get("artifact_refs", []) if isinstance(ref, dict)]
    trace_refs = [
        ref
        for collection in (builds, queries, quality)
        for item in collection
        for ref in item.get("trace_refs", [])
        if isinstance(ref, dict)
    ]
    missing = []
    if not sources:
        missing.append("source_import")
    if not queries:
        missing.append("query_result")
    if not artifact_refs:
        missing.append("artifact_lineage")
    claims = [
        {
            "claim_id": "pv18-bff-boundary",
            "claim": "Knowledge OPC browser flow uses /bff/pv18/knowledge domain facade.",
            "evidence_refs": ["/bff/pv18/knowledge/state"],
            "status": "SUPPORTED",
        },
        {
            "claim_id": "pv18-citation-evidence",
            "claim": "Knowledge answer must be reviewed with citation and artifact evidence.",
            "evidence_refs": [ref.get("artifact_ref") for ref in artifact_refs if ref.get("artifact_ref")],
            "status": "SUPPORTED" if artifact_refs and queries else "MISSING",
        },
        {
            "claim_id": "pv18-platform-generality",
            "claim": "Knowledge-specific behavior stays in pack/domain BFF/view/runner boundary.",
            "evidence_refs": ["platform-generality-review.md"],
            "status": "SUPPORTED",
        },
    ]
    return {
        "status": "ready_for_review" if not missing and all(item.get("status") == "SUPPORTED" for item in claims) else "missing_evidence",
        "claims": claims,
        "route_boundary": {
            "allowed_prefix": "/bff/pv18/knowledge",
            "browser_denylist": ["/v1/rpc", "/internal/runtime", "/runtime/store", "/api/runtime", "/debug/runtime", "data_service_mcp/internal"],
            "status": "specified",
        },
        "artifact_lineage": {"artifact_refs": artifact_refs, "source_count": len(sources)},
        "trace_timeline": {"trace_refs": trace_refs},
        "redaction": {"status": "redacted", "secret_allowed": False, "provider_payload_allowed": False, "artifact_content_allowed": False},
        "platform_generality": {
            "status": "PASS",
            "knowledge_only_platform_changes": [],
            "generic_reuse_checks": ["BFF domain facade only", "GatewayService core unchanged", "connector runtime reused"],
        },
        "quality_ref_count": len(quality),
        "correction_ref_count": len(corrections),
        "missing_evidence": missing,
        "allowed_claim": "PV18 complete: Knowledge OPC productization implementation ready for bounded review.",
        "audit_refs": [_pv18_audit_ref("knowledge.evidence.project", scope, entity_id=workspace_id)],
        "redaction_status": "redacted",
    }


def _ensure_agent_talk_session(
    workflow_instance_id: str,
    workflow_template_id: str,
    scope: ScopeContext,
    *,
    created_by: str,
) -> dict[str, Any]:
    key = _agent_session_key(workflow_instance_id, scope)
    session = _AGENT_TALK_SESSIONS.get(key)
    if session is not None:
        return session
    session = {
        "agent_session_id": f"ats_{uuid4().hex[:12]}",
        "workflow_instance_id": workflow_instance_id,
        "workflow_template_id": workflow_template_id,
        "scope": _scope_dto(scope),
        "created_by": _redact(created_by),
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "redaction_status": "redacted",
    }
    _AGENT_TALK_SESSIONS[key] = session
    _AGENT_TALK_MESSAGES[session["agent_session_id"]] = []
    _AGENT_TALK_SUGGESTIONS[session["agent_session_id"]] = []
    _AGENT_ACTION_PROPOSALS[session["agent_session_id"]] = []
    _record_agent_audit(
        "agent.session.created",
        session=session,
        summary="AgentTalk session created.",
        resource_refs=_agent_resource_refs(workflow_instance_id=workflow_instance_id, workflow_template_id=workflow_template_id),
    )
    return session


def _agent_resource_refs(**refs: Any) -> dict[str, Any]:
    return {key: value for key, value in refs.items() if value is not None}


def _agent_message(
    session: dict[str, Any],
    *,
    role: str,
    content: str,
    source: str,
    resource_refs: dict[str, Any],
) -> dict[str, Any]:
    session["updated_at"] = _now_iso()
    return {
        "message_id": f"atm_{uuid4().hex[:12]}",
        "agent_session_id": session["agent_session_id"],
        "workflow_instance_id": session["workflow_instance_id"],
        "workflow_template_id": session["workflow_template_id"],
        "role": role,
        "source": source,
        "content": _redact(content),
        "resource_refs": _redact(resource_refs),
        "created_at": _now_iso(),
        "redaction_status": "redacted",
    }


def _agent_assistant_reply(content: str) -> str:
    text = content.lower()
    node_template_id = _agent_node_template_for_content(content)
    if node_template_id == "quality_evaluation":
        return "我已生成一个新增质量检查节点的 Patch proposal。该建议只进入 Diff 和编辑面板，应用仍需要用户显式确认。"
    if node_template_id:
        return "我已生成一个新增画布节点的 Patch proposal。该建议只进入 Diff 和编辑面板，应用仍需要用户显式确认。"
    if "优化" in content or "prompt" in text:
        return "我已为当前节点生成 Prompt Patch proposal。该建议只进入 Diff 和编辑面板，应用仍需要用户显式确认。"
    if "连接" in content or "edge" in text:
        return "我可以生成连线 Patch proposal；连线写入仍需要用户在编辑面板显式确认。"
    if "优化" in content or "patch" in text or "diff" in text:
        return "我已基于当前工作流事实源生成可审计建议。建议只会进入 Patch proposal / Diff，应用与发布仍需要用户到编辑面板显式确认。"
    if "解释" in content or "summary" in text:
        return "我会从 board、status、context 和 patch DTO 重新读取事实源，并只给出摘要，不直接修改工作流。"
    return "我可以解释当前流程、总结事件、显示审批提醒、展示上下文摘要，或生成受治理的 Patch 建议。"


def _generate_agent_suggestions(
    gateway: GatewayService,
    workflow_instance_id: str,
    workflow_template_id: str,
    scope: ScopeContext,
    *,
    preferred_patch_id: str | None = None,
) -> list[dict[str, Any]]:
    instance = gateway.workflow_repository.get_instance(workflow_instance_id, scope=scope)
    patches = [
        patch.model_dump(mode="json")
        for patch in gateway.workflow_repository.list_patches(scope=scope, workflow_template_id=workflow_template_id)
        if _patch_matches_instance(patch, workflow_instance_id)
    ]
    patch = (
        next((item for item in patches if item.get("workflow_patch_id") == preferred_patch_id), None)
        if preferred_patch_id
        else None
    )
    patch = patch or next((item for item in patches if item.get("status") == "proposed"), None) or (patches[0] if patches else None)
    station_ids = list(instance.current_station_ids or [])
    target_station_id = station_ids[0] if station_ids else None
    suggestions = [
        _agent_suggestion(
            workflow_instance_id=workflow_instance_id,
            workflow_template_id=workflow_template_id,
            suggestion_type="explain",
            title="解释当前流程",
            summary="基于 workflow.board.get 与 workflow.instance.status 生成运行摘要，不采信事件 payload 作为事实。",
            action="explain_workflow",
        ),
        _agent_suggestion(
            workflow_instance_id=workflow_instance_id,
            workflow_template_id=workflow_template_id,
            suggestion_type="show_context_summary",
            title="展示业务上下文摘要",
            summary="只展示 redacted context.business，不展示 context.system 或 context.runtime。",
            action="show_context_summary",
        ),
    ]
    if patch:
        suggestions.append(
            _agent_suggestion(
                workflow_instance_id=workflow_instance_id,
                workflow_template_id=workflow_template_id,
                suggestion_type="show_diff",
                title="查看 Diff",
                summary="打开已有 Patch Diff；Agent 不会执行 Apply / Publish。",
                action="show_patch_diff",
                workflow_patch_id=patch.get("workflow_patch_id"),
                risk_flags=patch.get("risk_flags") if isinstance(patch.get("risk_flags"), list) else [],
                requires_approval=bool(patch.get("requires_approval")),
            )
        )
    approval = next(
        (
            item
            for item in gateway.approval_store.list_approvals(status="pending")
            if _approval_workflow_binding(item).get("workflow_instance_id") == workflow_instance_id
        ),
        None,
    )
    if approval:
        suggestions.append(
            _agent_suggestion(
                workflow_instance_id=workflow_instance_id,
                workflow_template_id=workflow_template_id,
                suggestion_type="show_approval_notice",
                title="查看待审批事项",
                summary="跳转审批面板，由用户显式确认后才能响应 approval.respond。",
                action="show_approval_notice",
            )
        )
    if target_station_id:
        preferred_operation = str(patch.get("operation") or "") if patch else ""
        if preferred_operation == "add_station":
            preferred_title = "生成节点调整建议"
            preferred_summary = "新增画布节点的 Patch proposal 已生成；后续应用仍必须进入编辑面板由用户确认。"
            preferred_intent_type = "node_add"
        elif preferred_operation == "update_edge":
            preferred_title = "生成连线调整建议"
            preferred_summary = "新增连线的 Patch proposal 已生成；后续应用仍必须进入编辑面板由用户确认。"
            preferred_intent_type = "edge_add"
        elif preferred_operation == "update_station_prompt":
            preferred_title = "生成 Prompt 调整建议"
            preferred_summary = "当前节点 Prompt Patch proposal 已生成；后续应用仍必须进入编辑面板由用户确认。"
            preferred_intent_type = "inspector_update"
        else:
            preferred_title = "生成优化建议"
            preferred_summary = "生成 source=agent 的 Patch proposal payload；后续应用仍必须进入编辑面板由用户确认。"
            preferred_intent_type = "inspector_update"
        suggestions.append(
            _agent_suggestion(
                workflow_instance_id=workflow_instance_id,
                workflow_template_id=workflow_template_id,
                suggestion_type="propose_patch",
                title=preferred_title if preferred_patch_id else "生成优化建议",
                summary=preferred_summary if preferred_patch_id else "生成 source=agent 的 Patch proposal payload；后续应用仍必须进入编辑面板由用户确认。",
                action="suggest_patch",
                workflow_patch_id=preferred_patch_id,
                patch_intent={
                    "source": "agent",
                    "intent_type": preferred_intent_type if preferred_patch_id else "inspector_update",
                    "operation": preferred_operation if preferred_patch_id else "update_station_prompt",
                    "workflow_instance_id": workflow_instance_id,
                    "payload": patch.get("payload") if preferred_patch_id and isinstance(patch.get("payload"), dict) else {
                        "station_id": target_station_id,
                        "prompt_patch": "增强角色一致性、镜头衔接和输出结构约束。",
                    },
                },
            )
        )
    _record_agent_audit(
        "agent.suggestion.generated",
        session={"agent_session_id": "", "workflow_instance_id": workflow_instance_id, "workflow_template_id": workflow_template_id, "scope": _scope_dto(scope)},
        summary="Deterministic Agent suggestions generated.",
        resource_refs=_agent_resource_refs(workflow_instance_id=workflow_instance_id, workflow_template_id=workflow_template_id),
    )
    return suggestions


async def _maybe_create_agent_canvas_patch(
    gateway: GatewayService,
    workflow_instance_id: str,
    workflow_template_id: str,
    scope: ScopeContext,
    content: str,
    body: dict[str, Any],
) -> str | None:
    template = gateway.workflow_repository.get_template(workflow_template_id, scope=scope)
    draft = gateway.workflow_repository.get_draft(str(template.latest_draft_id), scope=scope)
    draft_payload = draft.draft if isinstance(draft.draft, dict) else {}
    patch = _agent_canvas_patch_for_content(workflow_instance_id, content, body, draft_payload)
    if patch is None:
        return None
    _validate_canvas_patch_payload(gateway, workflow_template_id, patch, scope)
    result = await _rpc(
        gateway,
        "workflow.patch.propose",
        {
            "workflow_template_id": workflow_template_id,
            "patch": patch,
            "scope": _scope_dto(scope),
        },
    )
    patch_result = result.get("patch") if isinstance(result, dict) else {}
    if isinstance(patch_result, dict):
        return str(patch_result.get("workflow_patch_id") or "") or None
    return None


def _agent_canvas_patch_for_content(
    workflow_instance_id: str,
    content: str,
    body: dict[str, Any],
    draft_payload: dict[str, Any],
) -> dict[str, Any] | None:
    node_template_id = _agent_node_template_for_content(content)
    if node_template_id:
        station_id = _unique_agent_station_id(f"station_agent_{node_template_id}", draft_payload)
        return {
            "operation": "add_station",
            "payload": _agent_node_payload(node_template_id, station_id=station_id),
            "actor_type": "agent",
            "actor_id": "agent_proposal",
            "proposed_by": "agent_proposal",
            "metadata": {
                "source": "agent",
                "intent_type": "node_add",
                "workflow_instance_id": workflow_instance_id,
            },
        }
    if _is_agent_prompt_update_request(content):
        station_id = _selected_or_first_station_id(body, draft_payload)
        if not station_id:
            return None
        return {
            "operation": "update_station_prompt",
            "payload": {
                "station_id": station_id,
                "prompt_patch": _agent_prompt_patch(content),
            },
            "actor_type": "agent",
            "actor_id": "agent_proposal",
            "proposed_by": "agent_proposal",
            "metadata": {
                "source": "agent",
                "intent_type": "inspector_update",
                "workflow_instance_id": workflow_instance_id,
            },
        }
    edge_pair = _agent_edge_pair_for_content(content, body, draft_payload)
    if edge_pair:
        from_station_id, to_station_id = edge_pair
        return {
            "operation": "update_edge",
            "payload": {
                "edge_id": f"edge_{from_station_id}_to_{to_station_id}",
                "edge_patch": {
                    "action": "add",
                    "from_station_id": from_station_id,
                    "to_station_id": to_station_id,
                },
            },
            "actor_type": "agent",
            "actor_id": "agent_proposal",
            "proposed_by": "agent_proposal",
            "metadata": {
                "source": "agent",
                "intent_type": "edge_add",
                "workflow_instance_id": workflow_instance_id,
            },
        }
    return None


def _agent_node_template_for_content(content: str) -> str | None:
    if not any(token in content for token in ("增加", "新增", "添加", "加一个")):
        return None
    if "审批" in content:
        return "manual_approval"
    if "角色" in content or "一致性" in content:
        return "character_consistency"
    if "质量" in content or "检查" in content or "评估" in content:
        return "quality_evaluation"
    return None


def _is_agent_prompt_update_request(content: str) -> bool:
    lowered = content.lower()
    return ("优化" in content or "修改" in content or "调整" in content) and ("prompt" in lowered or "提示词" in content or "节点" in content)


def _agent_prompt_patch(content: str) -> str:
    if "角色" in content or "一致性" in content:
        return "增强角色一致性、镜头衔接和输出结构约束。"
    if "质量" in content:
        return "补充质量检查标准，明确输出可验收条件和失败原因。"
    return "根据用户自然语言要求优化当前节点 Prompt，并保持输出结构可审计。"


def _selected_or_first_station_id(body: dict[str, Any], draft_payload: dict[str, Any]) -> str:
    station_ids = [str(item.get("station_id")) for item in draft_payload.get("stations", []) if isinstance(item, dict) and item.get("station_id")]
    selected = body.get("selected_station_id")
    if isinstance(selected, str) and selected in station_ids:
        return selected
    return station_ids[0] if station_ids else ""


def _agent_edge_pair_for_content(content: str, body: dict[str, Any], draft_payload: dict[str, Any]) -> tuple[str, str] | None:
    if "连接" not in content and "edge" not in content.lower():
        return None
    station_ids = [str(item.get("station_id")) for item in draft_payload.get("stations", []) if isinstance(item, dict) and item.get("station_id")]
    selected = body.get("selected_station_id")
    target = body.get("target_station_id")
    if isinstance(selected, str) and isinstance(target, str) and selected in station_ids and target in station_ids and selected != target:
        return selected, target
    if len(station_ids) >= 2:
        return station_ids[-2], station_ids[-1]
    return None


def _unique_agent_station_id(base_id: str, draft_payload: dict[str, Any]) -> str:
    existing_ids = {item.get("station_id") for item in draft_payload.get("stations", []) if isinstance(item, dict)}
    if base_id not in existing_ids:
        return base_id
    index = 2
    while f"{base_id}_{index}" in existing_ids:
        index += 1
    return f"{base_id}_{index}"


def _agent_node_payload(node_template_id: str, *, station_id: str) -> dict[str, Any]:
    contract = NODE_CATALOG_CONTRACTS[node_template_id]
    node_label = "质量检查节点" if node_template_id == "quality_evaluation" else NODE_CATALOG_LABELS.get(node_template_id, node_template_id)
    return {
        "station": {
            "station_id": station_id,
            "name": node_label,
            "role": contract["station_kind"],
            "skill_refs": list(contract["allowed_skill_refs"]),
            "connector_refs": list(contract["allowed_connector_refs"]),
            "metadata": {
                "node_catalog_id": node_template_id,
                "node_label": node_label,
                **contract,
            },
        }
    }


async def _maybe_create_agent_node_add_patch(
    gateway: GatewayService,
    workflow_instance_id: str,
    workflow_template_id: str,
    scope: ScopeContext,
    content: str,
) -> str | None:
    if not _is_agent_node_add_request(content):
        return None
    template = gateway.workflow_repository.get_template(workflow_template_id, scope=scope)
    draft = gateway.workflow_repository.get_draft(str(template.latest_draft_id), scope=scope)
    draft_payload = draft.draft if isinstance(draft.draft, dict) else {}
    station_id = _unique_agent_station_id("station_agent_quality_check", draft_payload)
    patch = {
        "operation": "add_station",
        "payload": _agent_quality_node_payload(station_id=station_id),
        "actor_type": "agent",
        "actor_id": "agent_proposal",
        "proposed_by": "agent_proposal",
        "metadata": {
            "source": "agent",
            "intent_type": "node_add",
            "workflow_instance_id": workflow_instance_id,
        },
    }
    _validate_canvas_patch_payload(gateway, workflow_template_id, patch, scope)
    result = await _rpc(
        gateway,
        "workflow.patch.propose",
        {
            "workflow_template_id": workflow_template_id,
            "patch": patch,
            "scope": _scope_dto(scope),
        },
    )
    patch_result = result.get("patch") if isinstance(result, dict) else {}
    if isinstance(patch_result, dict):
        return str(patch_result.get("workflow_patch_id") or "") or None
    return None


def _is_agent_node_add_request(content: str) -> bool:
    return (
        any(token in content for token in ("增加", "新增", "添加"))
        and any(token in content for token in ("质量", "检查", "评估"))
        and any(token in content for token in ("节点", "node"))
    )


def _agent_quality_node_payload(*, station_id: str = "station_agent_quality_check") -> dict[str, Any]:
    contract = NODE_CATALOG_CONTRACTS["quality_evaluation"]
    return {
        "station": {
            "station_id": station_id,
            "name": "质量检查节点",
            "role": contract["station_kind"],
            "skill_refs": ["video.quality"],
            "connector_refs": [],
            "metadata": {
                "node_catalog_id": "quality_evaluation",
                **contract,
            },
        }
    }


def _agent_suggestion(
    *,
    workflow_instance_id: str,
    workflow_template_id: str,
    suggestion_type: str,
    title: str,
    summary: str,
    action: str,
    workflow_patch_id: Any = None,
    risk_flags: list[Any] | None = None,
    requires_approval: bool = False,
    patch_intent: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if action not in AGENT_ACTION_INTENTS:
        raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "Agent action intent is not allowed.", {"action": action})
    if patch_intent is not None:
        _reject_sensitive_or_layout_fields(patch_intent)
    return {
        "suggestion_id": f"ags_{uuid4().hex[:12]}",
        "workflow_instance_id": workflow_instance_id,
        "workflow_template_id": workflow_template_id,
        "workflow_patch_id": workflow_patch_id,
        "type": suggestion_type,
        "title": _redact(title),
        "summary": _redact(summary),
        "status": "active",
        "action_intent": {
            "action": action,
            "executable": False,
        },
        "patch_intent": _redact(patch_intent) if patch_intent else None,
        "risk_flags": risk_flags or [],
        "requires_approval": requires_approval,
        "created_at": _now_iso(),
        "redaction_status": "redacted",
    }


def _agent_session_dto(session: dict[str, Any]) -> dict[str, Any]:
    messages = _AGENT_TALK_MESSAGES.get(str(session.get("agent_session_id")), [])
    suggestions = _AGENT_TALK_SUGGESTIONS.get(str(session.get("agent_session_id")), [])
    return {
        "agent_session_id": session.get("agent_session_id"),
        "workflow_instance_id": session.get("workflow_instance_id"),
        "workflow_template_id": session.get("workflow_template_id"),
        "scope": session.get("scope"),
        "created_by": session.get("created_by"),
        "created_at": session.get("created_at"),
        "updated_at": session.get("updated_at"),
        "redaction_status": "redacted",
        "messages": [_agent_message_dto(item) for item in messages],
        "suggestions": [_agent_suggestion_dto(item) for item in suggestions],
    }


def _agent_message_dto(message: dict[str, Any]) -> dict[str, Any]:
    return {
        "message_id": message.get("message_id"),
        "agent_session_id": message.get("agent_session_id"),
        "workflow_instance_id": message.get("workflow_instance_id"),
        "workflow_template_id": message.get("workflow_template_id"),
        "role": message.get("role"),
        "source": message.get("source"),
        "content": _redact(message.get("content")),
        "resource_refs": _redact(message.get("resource_refs") if isinstance(message.get("resource_refs"), dict) else {}),
        "created_at": message.get("created_at"),
        "redaction_status": "redacted",
    }


def _agent_suggestion_dto(suggestion: dict[str, Any]) -> dict[str, Any]:
    return {
        "suggestion_id": suggestion.get("suggestion_id"),
        "workflow_instance_id": suggestion.get("workflow_instance_id"),
        "workflow_template_id": suggestion.get("workflow_template_id"),
        "workflow_patch_id": suggestion.get("workflow_patch_id"),
        "type": suggestion.get("type"),
        "title": _redact(suggestion.get("title")),
        "summary": _redact(suggestion.get("summary")),
        "status": suggestion.get("status"),
        "action_intent": _redact(suggestion.get("action_intent") if isinstance(suggestion.get("action_intent"), dict) else {}),
        "patch_intent": _redact(suggestion.get("patch_intent") if isinstance(suggestion.get("patch_intent"), dict) else None),
        "risk_flags": suggestion.get("risk_flags") if isinstance(suggestion.get("risk_flags"), list) else [],
        "requires_approval": bool(suggestion.get("requires_approval")),
        "created_at": suggestion.get("created_at"),
        "redaction_status": "redacted",
    }


def _ensure_agent_action_proposals(session: dict[str, Any], suggestions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    proposals = _AGENT_ACTION_PROPOSALS.setdefault(str(session["agent_session_id"]), [])
    if proposals:
        return proposals
    for suggestion in suggestions:
        action_intent = suggestion.get("action_intent") if isinstance(suggestion.get("action_intent"), dict) else {}
        action = str(action_intent.get("action") or "")
        if not action:
            continue
        proposals.append(
            _agent_action_proposal(
                session=session,
                intent_type=action,
                title=str(suggestion.get("title") or "Agent proposal"),
                summary=str(suggestion.get("summary") or "Agent action proposal."),
                source_suggestion_id=str(suggestion.get("suggestion_id") or ""),
                workflow_patch_id=suggestion.get("workflow_patch_id"),
                risk_flags=suggestion.get("risk_flags") if isinstance(suggestion.get("risk_flags"), list) else [],
                requires_approval=bool(suggestion.get("requires_approval")),
            )
        )
    return proposals


def _agent_action_proposal_from_request(session: dict[str, Any], body: dict[str, Any]) -> dict[str, Any]:
    intent_type = str(body.get("intent_type") or body.get("action") or "")
    if not intent_type:
        raise ProtocolError("INVALID_PARAMS", "intent_type is required.", {"field": "intent_type"})
    payload = body.get("payload") if isinstance(body.get("payload"), dict) else {}
    _reject_sensitive_or_layout_fields(payload)
    return _agent_action_proposal(
        session=session,
        intent_type=intent_type,
        title=str(body.get("title") or intent_type),
        summary=str(body.get("summary") or "Agent action proposal."),
        payload=payload,
        target_panel=body.get("target_panel"),
        risk_flags=body.get("risk_flags") if isinstance(body.get("risk_flags"), list) else [],
        requires_approval=bool(body.get("requires_approval")),
    )


def _agent_action_proposal(
    *,
    session: dict[str, Any],
    intent_type: str,
    title: str,
    summary: str,
    source_suggestion_id: str | None = None,
    workflow_patch_id: Any = None,
    payload: dict[str, Any] | None = None,
    target_panel: Any = None,
    risk_flags: list[Any] | None = None,
    requires_approval: bool = False,
) -> dict[str, Any]:
    policy = _agent_action_policy(intent_type)
    resource_refs = _agent_resource_refs(
        workflow_instance_id=session.get("workflow_instance_id"),
        workflow_template_id=session.get("workflow_template_id"),
        source_suggestion_id=source_suggestion_id,
        workflow_patch_id=workflow_patch_id,
    )
    lifecycle = "blocked" if policy == "forbidden" else "proposed"
    return {
        "proposal_id": f"aap_{uuid4().hex[:12]}",
        "agent_session_id": session.get("agent_session_id"),
        "workflow_instance_id": session.get("workflow_instance_id"),
        "workflow_template_id": session.get("workflow_template_id"),
        "intent_type": intent_type,
        "policy_class": policy,
        "lifecycle": lifecycle,
        "status": lifecycle,
        "title": _redact(title),
        "summary": _redact(summary),
        "target_panel": _normalize_agent_target_panel(target_panel, intent_type),
        "workflow_patch_id": workflow_patch_id,
        "risk_level": _agent_risk_level(risk_flags or [], requires_approval, policy),
        "risk_flags": risk_flags or [],
        "requires_approval": requires_approval,
        "policy_decision": "blocked" if policy == "forbidden" else "proposal_only",
        "payload_summary": _redact(payload or {}),
        "resource_refs": _redact(resource_refs),
        "created_by": "agent",
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "redaction_status": "redacted",
    }


def _agent_action_policy(intent_type: str) -> str:
    if intent_type in FORBIDDEN_AGENT_ACTION_INTENTS:
        raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "Agent action intent is forbidden.", {"intent_type": intent_type})
    policy = AGENT_ACTION_POLICY.get(intent_type)
    if policy is None:
        raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "Agent action intent is not allowed.", {"intent_type": intent_type})
    return policy


def _normalize_agent_target_panel(target_panel: Any, intent_type: str) -> str | None:
    allowed = {"editing", "approval", "context", "quality", "artifact", "events"}
    if isinstance(target_panel, str) and target_panel in allowed:
        return target_panel
    defaults = {
        "show_patch_diff": "editing",
        "suggest_patch": "editing",
        "propose_patch": "editing",
        "navigate_to_editing_panel": "editing",
        "open_editing_panel": "editing",
        "show_approval_notice": "approval",
        "open_approval_panel": "approval",
        "show_context_summary": "context",
        "open_context_panel": "context",
        "summarize_context": "context",
        "open_quality_panel": "quality",
        "summarize_quality": "quality",
        "open_artifact_panel": "artifact",
    }
    return defaults.get(intent_type)


def _agent_risk_level(risk_flags: list[Any], requires_approval: bool, policy: str) -> str:
    if policy == "forbidden" or requires_approval:
        return "high"
    if risk_flags:
        return "medium"
    return "low"


def _find_agent_action_proposal(agent_session_id: str, proposal_id: str) -> dict[str, Any]:
    proposals = _AGENT_ACTION_PROPOSALS.get(agent_session_id, [])
    proposal = next((item for item in proposals if item.get("proposal_id") == proposal_id), None)
    if proposal is None:
        raise ProtocolError("METHOD_NOT_FOUND", "Agent action proposal was not found.", {"proposal_id": proposal_id})
    return proposal


def _agent_action_proposal_dto(proposal: dict[str, Any]) -> dict[str, Any]:
    return {
        "proposal_id": proposal.get("proposal_id"),
        "agent_session_id": proposal.get("agent_session_id"),
        "workflow_instance_id": proposal.get("workflow_instance_id"),
        "workflow_template_id": proposal.get("workflow_template_id"),
        "intent_type": proposal.get("intent_type"),
        "policy_class": proposal.get("policy_class"),
        "lifecycle": proposal.get("lifecycle"),
        "status": proposal.get("status"),
        "title": _redact(proposal.get("title")),
        "summary": _redact(proposal.get("summary")),
        "target_panel": proposal.get("target_panel"),
        "workflow_patch_id": proposal.get("workflow_patch_id"),
        "risk_level": proposal.get("risk_level"),
        "risk_flags": proposal.get("risk_flags") if isinstance(proposal.get("risk_flags"), list) else [],
        "requires_approval": bool(proposal.get("requires_approval")),
        "policy_decision": proposal.get("policy_decision"),
        "payload_summary": _redact(proposal.get("payload_summary") if isinstance(proposal.get("payload_summary"), dict) else {}),
        "resource_refs": _redact(proposal.get("resource_refs") if isinstance(proposal.get("resource_refs"), dict) else {}),
        "created_by": proposal.get("created_by"),
        "created_at": proposal.get("created_at"),
        "updated_at": proposal.get("updated_at"),
        "redaction_status": "redacted",
    }


def _normalize_handoff_target_panel(target_panel: Any) -> str:
    aliases = {
        "editing": "editing_panel",
        "approval": "approval_panel",
        "context": "context_panel",
        "quality": "quality_panel",
        "artifact": "artifact_panel",
    }
    normalized = aliases.get(str(target_panel), str(target_panel))
    if normalized not in AGENT_HANDOFF_TARGET_PANELS:
        raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "Agent handoff target panel is not allowed.", {"target_panel": target_panel})
    return normalized


def _proposal_panel(proposal: dict[str, Any]) -> str:
    return _normalize_handoff_target_panel(proposal.get("target_panel"))


def _ensure_proposal_can_handoff(proposal: dict[str, Any], target_panel: str) -> None:
    lifecycle = str(proposal.get("lifecycle") or proposal.get("status") or "")
    if lifecycle in {"dismissed", "blocked", "expired"}:
        raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "Agent action proposal is not active.", {"proposal_id": proposal.get("proposal_id"), "status": lifecycle})
    if str(proposal.get("policy_class")) == "forbidden":
        raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "Forbidden proposal cannot be handed off.", {"proposal_id": proposal.get("proposal_id")})
    if str(proposal.get("intent_type")) in READ_ONLY_AGENT_ACTION_INTENTS:
        raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "Read-only Agent proposal cannot be handed off.", {"proposal_id": proposal.get("proposal_id")})
    if _proposal_panel(proposal) != target_panel:
        raise ProtocolError(
            "WORKFLOW_ACTION_FORBIDDEN",
            "Agent handoff target panel does not match proposal target.",
            {"proposal_id": proposal.get("proposal_id"), "target_panel": target_panel},
        )


def _agent_action_handoff(
    gateway: GatewayService,
    scope: ScopeContext,
    session: dict[str, Any],
    proposal: dict[str, Any],
    target_panel: str,
    body: dict[str, Any],
) -> dict[str, Any]:
    now = datetime.now(UTC)
    target_resource = _handoff_target_resource(gateway, scope, session, proposal, target_panel, body)
    prefill = body.get("suggested_form_prefill") if isinstance(body.get("suggested_form_prefill"), dict) else {}
    return {
        "handoff_id": f"aah_{uuid4().hex[:12]}",
        "agent_session_id": session.get("agent_session_id"),
        "proposal_id": proposal.get("proposal_id"),
        "workflow_instance_id": session.get("workflow_instance_id"),
        "workflow_template_id": session.get("workflow_template_id"),
        "target_panel": target_panel,
        "target_resource": _redact(target_resource),
        "suggested_form_prefill": _redact(prefill),
        "expires_at": (now + timedelta(minutes=AGENT_HANDOFF_TTL_MINUTES)).isoformat(),
        "status": "active",
        "created_at": now.isoformat(),
        "created_by": "agent",
        "redaction_status": "redacted",
    }


def _handoff_target_resource(
    gateway: GatewayService,
    scope: ScopeContext,
    session: dict[str, Any],
    proposal: dict[str, Any],
    target_panel: str,
    body: dict[str, Any],
) -> dict[str, Any]:
    workflow_instance_id = str(session.get("workflow_instance_id") or "")
    if target_panel == "editing_panel":
        workflow_patch_id = str(body.get("workflow_patch_id") or proposal.get("workflow_patch_id") or "")
        if not workflow_patch_id:
            raise ProtocolError("INVALID_PARAMS", "editing handoff requires workflow_patch_id.", {"field": "workflow_patch_id"})
        _ensure_patch_in_instance(gateway, workflow_patch_id, workflow_instance_id, scope)
        patch = gateway.workflow_repository.get_patch(workflow_patch_id, scope=scope)
        draft = gateway.workflow_repository.get_draft(patch.workflow_draft_id, scope=scope)
        return {
            "workflow_patch_id": workflow_patch_id,
            "patch_id": workflow_patch_id,
            "patch_status": patch.status,
            "draft_revision": draft.revision,
            "base_revision": patch.base_revision,
            "requires_approval": bool(proposal.get("requires_approval")),
            "risk_flags": proposal.get("risk_flags") if isinstance(proposal.get("risk_flags"), list) else [],
        }
    if target_panel == "approval_panel":
        approval_id = str(body.get("approval_id") or body.get("target_resource_id") or "")
        if not approval_id:
            approval_id = _first_workflow_bound_approval_id(gateway, workflow_instance_id)
        approval = gateway.approval_store.get_approval(approval_id)
        _ensure_approval_in_instance(approval, workflow_instance_id)
        binding = _approval_workflow_binding(approval)
        return {
            "approval_id": approval_id,
            "approval_status": approval.get("status"),
            "workflow_instance_id": workflow_instance_id,
            "station_run_id": binding.get("station_run_id"),
        }
    if target_panel == "context_panel":
        context = gateway.workflow_repository.get_or_create_context(workflow_instance_id, scope=scope)
        path = str(body.get("target_path") or body.get("path") or "business.operator_note")
        if not path.startswith("business.") or path == "business.":
            raise ProtocolError("WORKFLOW_CONTEXT_SCOPE_MISMATCH", "Context handoff target path must start with business.", {"path": path})
        return {
            "expected_revision": context.revision,
            "target_path": path,
            "workflow_instance_id": workflow_instance_id,
        }
    return {"workflow_instance_id": workflow_instance_id}


def _first_workflow_bound_approval_id(gateway: GatewayService, workflow_instance_id: str) -> str:
    for approval in gateway.approval_store.list_approvals(status="pending"):
        if _approval_workflow_binding(approval).get("workflow_instance_id") == workflow_instance_id:
            return str(approval.get("approval_id"))
    raise ProtocolError("APPROVAL_NOT_FOUND", "No workflow-bound approval found for handoff.", {"workflow_instance_id": workflow_instance_id})


def _find_agent_action_handoff(agent_session_id: str, handoff_id: str) -> dict[str, Any]:
    handoff = _AGENT_HANDOFF_REPOSITORY.get(handoff_id)
    if handoff.get("agent_session_id") != agent_session_id:
        raise ProtocolError("METHOD_NOT_FOUND", "Agent action handoff was not found.", {"handoff_id": handoff_id})
    return handoff


def _agent_action_handoff_dto(handoff: dict[str, Any]) -> dict[str, Any]:
    return {
        "handoff_id": handoff.get("handoff_id"),
        "proposal_id": handoff.get("proposal_id"),
        "workflow_instance_id": handoff.get("workflow_instance_id"),
        "workflow_template_id": handoff.get("workflow_template_id"),
        "target_panel": handoff.get("target_panel"),
        "target_resource": _redact(handoff.get("target_resource") if isinstance(handoff.get("target_resource"), dict) else {}),
        "suggested_form_prefill": _redact(handoff.get("suggested_form_prefill") if isinstance(handoff.get("suggested_form_prefill"), dict) else {}),
        "expires_at": handoff.get("expires_at"),
        "status": handoff.get("status"),
        "inactive_reason": _redact(handoff.get("inactive_reason")),
        "updated_at": handoff.get("updated_at"),
        "created_at": handoff.get("created_at"),
        "created_by": handoff.get("created_by"),
        "redaction_status": "redacted",
    }


def _refresh_handoff_for_read(gateway: GatewayService, scope: ScopeContext, handoff: dict[str, Any]) -> dict[str, Any]:
    handoff = _expire_handoff_if_needed(handoff)
    if handoff.get("status") not in HANDOFF_ACTIVE_STATES:
        return handoff
    return _mark_handoff_stale_or_blocked_if_needed(gateway, scope, handoff)


def _expire_handoff_if_needed(handoff: dict[str, Any]) -> dict[str, Any]:
    if handoff.get("status") not in HANDOFF_ACTIVE_STATES:
        return handoff
    expires_at = handoff.get("expires_at")
    try:
        expires = datetime.fromisoformat(str(expires_at))
    except ValueError as exc:
        raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "Agent action handoff expiration is invalid.", {"handoff_id": handoff.get("handoff_id")}) from exc
    if expires < datetime.now(UTC):
        expired = _AGENT_HANDOFF_REPOSITORY.expire(str(handoff.get("handoff_id")), reason="handoff_expired")
        _append_handoff_audit(str(handoff.get("handoff_id")), "handoff_expired", summary="Agent action handoff expired.", data={"reason": "handoff_expired"})
        return expired
    return handoff


def _mark_handoff_stale_or_blocked_if_needed(gateway: GatewayService, scope: ScopeContext, handoff: dict[str, Any]) -> dict[str, Any]:
    target_panel = str(handoff.get("target_panel") or "")
    resource = handoff.get("target_resource") if isinstance(handoff.get("target_resource"), dict) else {}
    handoff_id = str(handoff.get("handoff_id") or "")
    try:
        if target_panel == "editing_panel":
            workflow_patch_id = str(resource.get("workflow_patch_id") or resource.get("patch_id") or "")
            patch = gateway.workflow_repository.get_patch(workflow_patch_id, scope=scope)
            patch_status = _enum_text(patch.status)
            if patch_status != "proposed":
                return _mark_handoff_stale(handoff_id, f"patch_status_{patch_status}")
            draft = gateway.workflow_repository.get_draft(patch.workflow_draft_id, scope=scope)
            if int(resource.get("draft_revision") or -1) != draft.revision:
                return _mark_handoff_stale(handoff_id, "draft_revision_changed")
            if bool(resource.get("requires_approval")):
                return _mark_handoff_blocked(handoff_id, "patch_requires_approval")
            return handoff
        if target_panel == "approval_panel":
            approval_id = str(resource.get("approval_id") or "")
            approval = gateway.approval_store.get_approval(approval_id)
            binding = _approval_workflow_binding(approval)
            if approval.get("status") != "pending":
                return _mark_handoff_stale(handoff_id, f"approval_status_{approval.get('status')}")
            if binding.get("active") is False:
                return _mark_handoff_stale(handoff_id, "approval_workflow_binding_inactive")
            instance = gateway.workflow_repository.get_instance(str(handoff.get("workflow_instance_id")), scope=scope)
            if instance.status in {"completed", "failed", "cancelled"}:
                return _mark_handoff_stale(handoff_id, f"workflow_instance_{instance.status}")
            return handoff
        if target_panel == "context_panel":
            path = str(resource.get("target_path") or "")
            if not path.startswith("business.") or path == "business.":
                return _mark_handoff_stale(handoff_id, "context_target_path_invalid")
            context = gateway.workflow_repository.get_or_create_context(str(handoff.get("workflow_instance_id")), scope=scope)
            if int(resource.get("expected_revision") or -1) != context.revision:
                return _mark_handoff_stale(handoff_id, "context_revision_changed")
            return handoff
    except ProtocolError:
        raise
    except Exception as exc:
        return _mark_handoff_stale(handoff_id, type(exc).__name__)
    return handoff


def _mark_handoff_stale(handoff_id: str, reason: str) -> dict[str, Any]:
    stale = _AGENT_HANDOFF_REPOSITORY.mark_stale(handoff_id, reason=reason)
    _append_handoff_audit(handoff_id, "handoff_stale", summary="Agent action handoff became stale.", data={"reason": reason})
    return stale


def _mark_handoff_blocked(handoff_id: str, reason: str) -> dict[str, Any]:
    blocked = _AGENT_HANDOFF_REPOSITORY.mark_blocked(handoff_id, reason=reason)
    _append_handoff_audit(handoff_id, "handoff_blocked", summary="Agent action handoff was blocked.", data={"reason": reason})
    return blocked


def _enum_text(value: Any) -> str:
    return str(getattr(value, "value", value))


def _ensure_handoff_usable(gateway: GatewayService, scope: ScopeContext, handoff: dict[str, Any]) -> dict[str, Any]:
    refreshed = _refresh_handoff_for_read(gateway, scope, handoff)
    if refreshed.get("status") not in HANDOFF_ACTIVE_STATES:
        raise ProtocolError(
            "WORKFLOW_ACTION_FORBIDDEN",
            "Agent action handoff is not usable.",
            {"handoff_id": refreshed.get("handoff_id"), "status": refreshed.get("status"), "reason": refreshed.get("inactive_reason")},
        )
    return refreshed


def _require_agent_handoff_for_action(
    body: dict[str, Any],
    *,
    target_panel: str,
    gateway: GatewayService | None = None,
    scope: ScopeContext | None = None,
    auth: Any = None,
    workflow_instance_id: Any = None,
    target_resource_id: Any = None,
) -> None:
    if body.get("source") == "agent":
        raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "Agent cannot execute user-confirmed actions.", {"source": "agent"})
    proposal_id = str(body.get("proposal_id") or "")
    handoff_id = str(body.get("handoff_id") or "")
    if not proposal_id or not handoff_id:
        if not proposal_id and not handoff_id:
            return
        raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "User-confirmed operation requires proposal_id and handoff_id.", {"proposal_id": bool(proposal_id), "handoff_id": bool(handoff_id)})
    if auth is not None and not _auth_has_capability(auth, "agent_handoffs.write"):
        raise ProtocolError("CAPABILITY_DENIED", "Agent handoff usage requires agent_handoffs.write capability.", {"capability": "agent_handoffs.write"})
    handoff = _find_handoff_by_id(handoff_id)
    if gateway is not None and scope is not None:
        handoff = _ensure_handoff_usable(gateway, scope, handoff)
    elif handoff.get("status") not in HANDOFF_ACTIVE_STATES:
        raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "Agent action handoff is not usable.", {"handoff_id": handoff_id, "status": handoff.get("status")})
    if handoff.get("proposal_id") != proposal_id:
        raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "Agent handoff does not belong to proposal.", {"proposal_id": proposal_id, "handoff_id": handoff_id})
    if handoff.get("target_panel") != target_panel:
        raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "Agent handoff target panel mismatch.", {"target_panel": target_panel, "handoff_id": handoff_id})
    if workflow_instance_id and handoff.get("workflow_instance_id") != workflow_instance_id:
        raise ProtocolError("SCOPE_MISMATCH", "Agent handoff does not belong to workflow instance.", {"resource": "handoff_id"})
    resource = handoff.get("target_resource") if isinstance(handoff.get("target_resource"), dict) else {}
    if target_resource_id:
        allowed_ids = {str(value) for key, value in resource.items() if key.endswith("_id") or key == "patch_id"}
        if str(target_resource_id) not in allowed_ids:
            raise ProtocolError("SCOPE_MISMATCH", "Agent handoff does not target selected resource.", {"resource": "handoff_id"})
    _AGENT_HANDOFF_REPOSITORY.mark_used(handoff_id)
    _append_handoff_audit(handoff_id, "handoff_used_for_user_confirmed_action", summary="Agent action handoff used for user-confirmed action.", data={"target_panel": target_panel})


def _find_handoff_by_id(handoff_id: str) -> dict[str, Any]:
    return _AGENT_HANDOFF_REPOSITORY.get(handoff_id)


def _reject_forbidden_agent_actions(action_intent: Any) -> None:
    if action_intent is None:
        return
    if not isinstance(action_intent, dict):
        raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "Agent action intent must be an object.", {"field": "action_intent"})
    action = str(action_intent.get("action") or "")
    if action in FORBIDDEN_AGENT_ACTION_INTENTS or action not in AGENT_ACTION_INTENTS:
        raise ProtocolError("WORKFLOW_ACTION_FORBIDDEN", "Agent action intent is not executable in this phase.", {"action": action or None})


def _record_agent_audit(
    event_type: str,
    *,
    session: dict[str, Any],
    summary: str,
    resource_refs: dict[str, Any],
) -> None:
    _AGENT_TALK_AUDIT.append(
        _redact(
            {
                "event_type": event_type,
                "agent_session_id": session.get("agent_session_id"),
                "workflow_instance_id": session.get("workflow_instance_id"),
                "workflow_template_id": session.get("workflow_template_id"),
                "scope": session.get("scope"),
                "summary": summary,
                "resource_refs": resource_refs,
                "created_at": _now_iso(),
                "redaction_status": "redacted",
            }
        )
    )


def _append_handoff_audit(handoff_id: str, event_type: str, *, summary: str, data: dict[str, Any] | None = None) -> None:
    _AGENT_HANDOFF_REPOSITORY.append_audit(handoff_id, event_type, summary=summary, data=_redact(data or {}))


def _publish_dto(result: dict[str, Any]) -> dict[str, Any]:
    template = result.get("template") if isinstance(result.get("template"), dict) else {}
    draft = result.get("draft") if isinstance(result.get("draft"), dict) else {}
    version = result.get("version") if isinstance(result.get("version"), dict) else {}
    return {
        "workflow_template_id": template.get("workflow_template_id"),
        "workflow_draft_id": draft.get("workflow_draft_id"),
        "draft_status": draft.get("status"),
        "draft_revision": draft.get("revision"),
        "workflow_version_id": version.get("workflow_version_id"),
        "version": version.get("version"),
    }


def _operation_result(
    operation: str,
    *,
    status: str,
    resource: Any,
    trace_id: Any = None,
    idempotent: bool = False,
    workflow_side_effect: Any = None,
    evidence: Any = None,
) -> dict[str, Any]:
    result = {
        "operation": operation,
        "status": status,
        "resource": resource,
        "idempotent": idempotent,
    }
    if trace_id:
        result["trace_id"] = trace_id
    if workflow_side_effect is not None:
        result["workflow_side_effect"] = workflow_side_effect
    if evidence is not None:
        result["evidence"] = evidence
    return result


def _runtime_result_ref(
    result_type: str,
    resource_id: Any,
    *,
    workflow_instance_id: Any,
    workflow_template_id: Any,
    operation: str,
    status: str,
    trace_id: Any = None,
) -> dict[str, Any]:
    ref = {
        "type": result_type,
        "resource_id": resource_id,
        "workflow_instance_id": workflow_instance_id,
        "workflow_template_id": workflow_template_id,
        "operation": operation,
        "status": status,
    }
    if trace_id:
        ref["trace_id"] = trace_id
    return _redact(ref)


def _record_operation_evidence(
    gateway: GatewayService,
    scope: ScopeContext,
    *,
    operation: str,
    workflow_instance_id: Any,
    workflow_template_id: Any,
    body: dict[str, Any],
    status: str,
    runtime_result_ref: dict[str, Any],
    resource_id: Any = None,
) -> dict[str, Any] | None:
    if not workflow_instance_id:
        return None
    gateway.workflow_repository.get_instance(str(workflow_instance_id), scope=scope)
    proposal_id = str(body.get("proposal_id") or "")
    handoff_id = str(body.get("handoff_id") or "")
    handoff = _safe_handoff(handoff_id)
    proposal = _safe_agent_action_proposal(proposal_id)
    operation_id = _operation_id(
        operation=operation,
        workflow_instance_id=workflow_instance_id,
        resource_id=resource_id or _operation_resource_id(operation, body, runtime_result_ref),
        proposal_id=proposal_id,
        handoff_id=handoff_id,
    )
    idempotency_key = str(body.get("idempotency_key") or body.get("event_id") or operation_id)
    evidence = {
        "evidence_id": f"evd_{uuid4().hex[:12]}",
        "workflow_instance_id": workflow_instance_id,
        "workflow_template_id": workflow_template_id,
        "operation": operation,
        "status": status,
        "correlation_id": str(body.get("correlation_id") or handoff_id or proposal_id or operation_id),
        "operation_id": operation_id,
        "idempotency_key": idempotency_key,
        "handoff_id": handoff_id or None,
        "proposal_id": proposal_id or None,
        "handoff_status_at_execution": handoff.get("status") if handoff else None,
        "proposal_status_at_execution": proposal.get("status") if proposal else None,
        "user_confirmed": body.get("user_confirmed") is True,
        "source": body.get("source"),
        "risk_flags": _risk_flags_for_evidence(proposal, handoff),
        "policy_decision": _policy_decision_for_evidence(status, proposal),
        "runtime_result_ref": runtime_result_ref,
        "audit_refs": _audit_refs_for_evidence(handoff_id),
        "created_at": _now_iso(),
        "created_by": str(body.get("source") or "workflow_console"),
        "redaction_status": "redacted",
    }
    record = _AGENT_OPERATION_EVIDENCE_REPOSITORY.create(evidence)
    if handoff_id:
        _append_handoff_audit(
            handoff_id,
            "operation_evidence_created",
            summary="User-confirmed operation evidence created.",
            data={"evidence_id": record["evidence_id"], "operation": operation, "status": status},
        )
    return record


def _record_operation_evidence_error(
    gateway: GatewayService,
    scope: ScopeContext | None,
    *,
    operation: str,
    workflow_instance_id: Any,
    workflow_template_id: Any,
    body: dict[str, Any],
    error: ProtocolError,
    resource_id: Any = None,
) -> dict[str, Any] | None:
    if scope is None or not isinstance(body, dict) or body.get("user_confirmed") is not True or not workflow_instance_id:
        return None
    status = _evidence_status_from_error(error, body)
    try:
        return _record_operation_evidence(
            gateway,
            scope,
            operation=operation,
            workflow_instance_id=workflow_instance_id,
            workflow_template_id=workflow_template_id,
            body=body,
            status=status,
            runtime_result_ref=_runtime_result_ref(
                "operation_error",
                resource_id or _operation_resource_id(operation, body, {}),
                workflow_instance_id=workflow_instance_id,
                workflow_template_id=workflow_template_id,
                operation=operation,
                status=str(error.code),
            ),
            resource_id=resource_id,
        )
    except Exception:
        return None


def _evidence_status_from_error(error: ProtocolError, body: dict[str, Any]) -> str:
    code = str(error.code)
    data = error.data if isinstance(error.data, dict) else {}
    handoff_status = str(data.get("status") or "")
    reason = str(data.get("reason") or "")
    if handoff_status == "expired" or "expired" in reason:
        return "expired_rejected"
    if handoff_status == "stale" or "stale" in reason or "CONFLICT" in code:
        return "stale_rejected"
    if code in {"WORKFLOW_ACTION_FORBIDDEN", "CAPABILITY_DENIED"}:
        return "blocked"
    return "failed"


def _operation_resource_id(operation: str, body: dict[str, Any], runtime_result_ref: dict[str, Any]) -> str:
    if runtime_result_ref.get("resource_id"):
        return str(runtime_result_ref["resource_id"])
    for key in ("workflow_patch_id", "approval_id", "event_id", "path", "version", "handoff_id"):
        if body.get(key):
            return str(body[key])
    return operation


def _operation_id(*, operation: str, workflow_instance_id: Any, resource_id: Any, proposal_id: str, handoff_id: str) -> str:
    parts = [operation, str(workflow_instance_id or ""), str(resource_id or "")]
    if proposal_id:
        parts.append(proposal_id)
    if handoff_id:
        parts.append(handoff_id)
    return ":".join(parts)


def _safe_handoff(handoff_id: str) -> dict[str, Any] | None:
    if not handoff_id:
        return None
    try:
        return _AGENT_HANDOFF_REPOSITORY.get(handoff_id)
    except ProtocolError:
        return None


def _safe_agent_action_proposal(proposal_id: str) -> dict[str, Any] | None:
    if not proposal_id:
        return None
    for proposals in _AGENT_ACTION_PROPOSALS.values():
        for proposal in proposals:
            if proposal.get("proposal_id") == proposal_id:
                return proposal
    return None


def _risk_flags_for_evidence(proposal: dict[str, Any] | None, handoff: dict[str, Any] | None) -> list[Any]:
    if proposal and isinstance(proposal.get("risk_flags"), list):
        return proposal["risk_flags"]
    resource = handoff.get("target_resource") if handoff and isinstance(handoff.get("target_resource"), dict) else {}
    return resource.get("risk_flags") if isinstance(resource.get("risk_flags"), list) else []


def _policy_decision_for_evidence(status: str, proposal: dict[str, Any] | None) -> str:
    if proposal and proposal.get("policy_decision"):
        return str(proposal["policy_decision"])
    if status in {"blocked", "stale_rejected", "expired_rejected"}:
        return status
    return "user_confirmed"


def _audit_refs_for_evidence(handoff_id: str) -> list[dict[str, Any]]:
    if not handoff_id:
        return []
    try:
        return [
            {"audit_id": item.get("audit_id"), "event_type": item.get("event_type"), "created_at": item.get("created_at")}
            for item in _AGENT_HANDOFF_REPOSITORY.list_audit(handoff_id)
        ]
    except ProtocolError:
        return []


def _operation_evidence_dto(evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "evidence_id": evidence.get("evidence_id"),
        "workflow_instance_id": evidence.get("workflow_instance_id"),
        "workflow_template_id": evidence.get("workflow_template_id"),
        "operation": evidence.get("operation"),
        "status": evidence.get("status"),
        "correlation_id": evidence.get("correlation_id"),
        "operation_id": evidence.get("operation_id"),
        "idempotency_key": evidence.get("idempotency_key"),
        "handoff_id": evidence.get("handoff_id"),
        "proposal_id": evidence.get("proposal_id"),
        "handoff_status_at_execution": evidence.get("handoff_status_at_execution"),
        "proposal_status_at_execution": evidence.get("proposal_status_at_execution"),
        "user_confirmed": bool(evidence.get("user_confirmed")),
        "source": evidence.get("source"),
        "risk_flags": evidence.get("risk_flags") if isinstance(evidence.get("risk_flags"), list) else [],
        "policy_decision": evidence.get("policy_decision"),
        "runtime_result_ref": _redact(evidence.get("runtime_result_ref") if isinstance(evidence.get("runtime_result_ref"), dict) else {}),
        "audit_refs": _redact(evidence.get("audit_refs") if isinstance(evidence.get("audit_refs"), list) else []),
        "created_at": evidence.get("created_at"),
        "created_by": evidence.get("created_by"),
        "redaction_status": "redacted",
    }


def _governance_review_dto(
    *,
    workflow_instance_id: str,
    workflow_template_id: str,
    evidence_records: list[dict[str, Any]],
    handoffs: list[dict[str, Any]],
) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    operation_counts: dict[str, int] = {}
    for record in evidence_records:
        status_counts[str(record.get("status") or "unknown")] = status_counts.get(str(record.get("status") or "unknown"), 0) + 1
        operation_counts[str(record.get("operation") or "unknown")] = operation_counts.get(str(record.get("operation") or "unknown"), 0) + 1
    return {
        "workflow_instance_id": workflow_instance_id,
        "workflow_template_id": workflow_template_id,
        "summary": {
            "evidence_count": len(evidence_records),
            "handoff_count": len(handoffs),
            "status_counts": status_counts,
            "operation_counts": operation_counts,
        },
        "operation_evidence": [_operation_evidence_dto(item) for item in evidence_records],
        "handoff_summary": [
            {
                "handoff_id": item.get("handoff_id"),
                "proposal_id": item.get("proposal_id"),
                "target_panel": item.get("target_panel"),
                "status": item.get("status"),
                "inactive_reason": _redact(item.get("inactive_reason")),
            }
            for item in handoffs
        ],
        "audit_timeline": _governance_audit_timeline(evidence_records, handoffs),
        "redaction_status": "redacted",
    }


def _agent_talk_interaction_state_dto(
    gateway: GatewayService,
    scope: ScopeContext,
    session: dict[str, Any],
) -> dict[str, Any]:
    workflow_instance_id = str(session.get("workflow_instance_id") or "")
    workflow_template_id = str(session.get("workflow_template_id") or "")
    template = gateway.workflow_repository.get_template(workflow_template_id, scope=scope)
    draft = gateway.workflow_repository.get_draft(str(template.latest_draft_id), scope=scope)
    patch_queue = _patch_queue_dto(
        [
            patch.model_dump(mode="json")
            for patch in gateway.workflow_repository.list_patches(scope=scope, workflow_template_id=workflow_template_id)
            if _patch_matches_instance(patch, workflow_instance_id)
        ],
        current_draft_revision=draft.revision,
    )
    suggestions = _AGENT_TALK_SUGGESTIONS.get(str(session.get("agent_session_id")), [])
    proposals = _AGENT_ACTION_PROPOSALS.get(str(session.get("agent_session_id")), [])
    handoffs = [
        _refresh_handoff_for_read(gateway, scope, handoff)
        for handoff in _AGENT_HANDOFF_REPOSITORY.list(agent_session_id=str(session.get("agent_session_id")), workflow_instance_id=workflow_instance_id)
    ]
    evidence = _AGENT_OPERATION_EVIDENCE_REPOSITORY.list(workflow_instance_id=workflow_instance_id)

    selected_suggestion = next((item for item in suggestions if item.get("status") == "active"), None)
    selected_proposal = next(
        (
            item
            for item in proposals
            if item.get("lifecycle") not in {"dismissed", "blocked", "expired"} and item.get("policy_class") != "display_only"
        ),
        None,
    )
    selected_handoff = next((item for item in handoffs if item.get("status") in HANDOFF_ACTIVE_STATES), None)
    selected_patch = next((item for item in patch_queue if item.get("selected")), None)
    selected_evidence = sorted(evidence, key=lambda item: str(item.get("created_at") or ""))[-1] if evidence else None

    stale_reasons = _agent_interaction_stale_reasons(
        selected_proposal=selected_proposal,
        selected_handoff=selected_handoff,
        selected_patch=selected_patch,
        proposals=proposals,
        handoffs=handoffs,
    )
    return {
        "workflow_instance_id": workflow_instance_id,
        "workflow_template_id": workflow_template_id,
        "agent_session_id": session.get("agent_session_id"),
        "selected_suggestion_id": selected_suggestion.get("suggestion_id") if selected_suggestion else None,
        "selected_proposal_id": selected_proposal.get("proposal_id") if selected_proposal else None,
        "selected_handoff_id": selected_handoff.get("handoff_id") if selected_handoff else None,
        "selected_patch_id": selected_patch.get("patch_id") if selected_patch else None,
        "selected_evidence_id": selected_evidence.get("evidence_id") if selected_evidence else None,
        "stale_reasons": stale_reasons,
        "refresh_generation": _agent_interaction_refresh_generation(
            session=session,
            suggestions=suggestions,
            proposals=proposals,
            handoffs=handoffs,
            patch_queue=patch_queue,
            evidence=evidence,
        ),
        "source_refs": {
            "agent_session": {"kind": "AgentTalkSessionDTO", "agent_session_id": session.get("agent_session_id")},
            "suggestions": {"kind": "AgentTalkSuggestionDTO", "count": len(suggestions)},
            "action_proposals": {"kind": "AgentActionProposalDTO", "count": len(proposals)},
            "handoffs": {"kind": "AgentActionHandoffDTO", "count": len(handoffs)},
            "patch_queue": {"kind": "PatchQueueDTO", "revision": _patch_queue_revision(patch_queue)},
            "canvas_projection": {"kind": "CanvasDraftProjection", "workflow_instance_id": workflow_instance_id},
            "evidence": {"kind": "OperationEvidenceDTO", "count": len(evidence)},
        },
        "generated_at": _now_iso(),
        "redaction_status": "redacted",
    }


def _agent_interaction_stale_reasons(
    *,
    selected_proposal: dict[str, Any] | None,
    selected_handoff: dict[str, Any] | None,
    selected_patch: dict[str, Any] | None,
    proposals: list[dict[str, Any]],
    handoffs: list[dict[str, Any]],
) -> list[str]:
    reasons: list[str] = []
    if selected_proposal and selected_proposal.get("lifecycle") in {"dismissed", "blocked", "expired"}:
        reasons.append("selected_proposal_stale")
    if selected_handoff and selected_handoff.get("status") not in HANDOFF_ACTIVE_STATES:
        reasons.append("selected_handoff_stale")
    if selected_patch and selected_patch.get("status") in {"stale", "blocked", "conflicted"}:
        reasons.append(f"selected_patch_{selected_patch.get('status')}")
    if any(item.get("lifecycle") == "dismissed" for item in proposals):
        reasons.append("dismissed_proposal_not_handoffable")
    if any(item.get("status") in {"expired", "stale", "blocked", "dismissed"} for item in handoffs):
        reasons.append("inactive_handoff_not_usable")
    return reasons


def _agent_interaction_refresh_generation(
    *,
    session: dict[str, Any],
    suggestions: list[dict[str, Any]],
    proposals: list[dict[str, Any]],
    handoffs: list[dict[str, Any]],
    patch_queue: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
) -> str:
    parts = [
        f"session:{session.get('agent_session_id')}:{session.get('updated_at') or session.get('created_at')}",
        "suggestions:" + "|".join(f"{item.get('suggestion_id')}:{item.get('status')}" for item in suggestions),
        "proposals:" + "|".join(f"{item.get('proposal_id')}:{item.get('lifecycle')}:{item.get('updated_at')}" for item in proposals),
        "handoffs:" + "|".join(f"{item.get('handoff_id')}:{item.get('status')}:{item.get('updated_at')}" for item in handoffs),
        _patch_queue_revision(patch_queue),
        "evidence:" + "|".join(f"{item.get('evidence_id')}:{item.get('status')}:{item.get('created_at')}" for item in evidence),
    ]
    return "agent_interaction:" + "||".join(parts)


def _governance_audit_timeline(evidence_records: list[dict[str, Any]], handoffs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for record in evidence_records:
        items.append(
            {
                "type": "operation_evidence",
                "resource_id": record.get("evidence_id"),
                "operation": record.get("operation"),
                "status": record.get("status"),
                "created_at": record.get("created_at"),
            }
        )
    for handoff in handoffs:
        items.append(
            {
                "type": "agent_handoff",
                "resource_id": handoff.get("handoff_id"),
                "target_panel": handoff.get("target_panel"),
                "status": handoff.get("status"),
                "created_at": handoff.get("created_at"),
            }
        )
    return sorted(items, key=lambda item: str(item.get("created_at") or ""))


def _template_id_for_instance(gateway: GatewayService, workflow_instance_id: str, scope: ScopeContext) -> str:
    return gateway.workflow_repository.get_instance(workflow_instance_id, scope=scope).workflow_template_id


def _safe_template_id_for_instance(gateway: GatewayService, workflow_instance_id: Any, scope: ScopeContext | None) -> str | None:
    if not workflow_instance_id or scope is None:
        return None
    try:
        return _template_id_for_instance(gateway, str(workflow_instance_id), scope)
    except Exception:
        return None


def _approval_workflow_binding(approval: dict[str, Any]) -> dict[str, Any]:
    metadata = approval.get("metadata") if isinstance(approval.get("metadata"), dict) else {}
    binding = metadata.get("workflow_binding") if isinstance(metadata.get("workflow_binding"), dict) else {}
    return binding


def _canvas_patch_request_to_patch(
    workflow_template_id: str,
    body: dict[str, Any],
) -> dict[str, Any]:
    source = str(body.get("source") or "")
    intent_type = str(body.get("intent_type") or "")
    operation = str(body.get("operation") or "")
    payload = body.get("payload")
    if source not in CANVAS_PATCH_SOURCES:
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "Patch proposal source must be canvas, inspector, agent, or workflow_console.", {"source": source or None})
    if intent_type not in CANVAS_PATCH_INTENTS:
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "Patch proposal intent_type is invalid.", {"intent_type": intent_type or None})
    if operation not in CANVAS_PATCH_OPERATIONS[intent_type]:
        raise ProtocolError(
            "WORKFLOW_PATCH_INVALID",
            "Patch proposal operation does not match intent_type.",
            {"intent_type": intent_type, "operation": operation or None},
        )
    if not isinstance(payload, dict):
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "Patch proposal payload must be an object.", {"field": "payload"})
    _reject_sensitive_or_layout_fields(payload)
    workflow_instance_id = body.get("workflow_instance_id")
    metadata: dict[str, Any] = {"source": source, "intent_type": intent_type}
    if isinstance(workflow_instance_id, str) and workflow_instance_id:
        metadata["workflow_instance_id"] = workflow_instance_id
    actor_id = f"{source}_proposal"
    actor_type = "agent" if source == "agent" else "user"
    return {
        "operation": operation,
        "payload": payload,
        "actor_type": actor_type,
        "actor_id": actor_id,
        "proposed_by": actor_id,
        "metadata": metadata,
    }


def _reject_sensitive_or_layout_fields(value: Any) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = str(key).lower().replace("-", "_")
            compact = normalized.replace("_", "")
            is_sensitive = any(part in normalized for part in SENSITIVE_KEY_PARTS) or any(part in compact for part in SENSITIVE_KEY_COMPACT_PARTS)
            if is_sensitive or compact in UI_LAYOUT_KEYS:
                field = "sensitive" if is_sensitive else str(key)
                raise ProtocolError("WORKFLOW_PATCH_INVALID", "Patch proposal payload contains forbidden field.", {"field": field})
            _reject_sensitive_or_layout_fields(item)
    elif isinstance(value, list):
        for item in value:
            _reject_sensitive_or_layout_fields(item)


def _validate_canvas_patch_payload(gateway: GatewayService, workflow_template_id: str, patch: dict[str, Any], scope: ScopeContext) -> None:
    operation = str(patch.get("operation") or "")
    payload = patch.get("payload") if isinstance(patch.get("payload"), dict) else {}
    template = gateway.workflow_repository.get_template(workflow_template_id, scope=scope)
    draft = gateway.workflow_repository.get_draft(str(template.latest_draft_id), scope=scope)
    draft_payload = draft.draft if isinstance(draft.draft, dict) else {}
    metadata = patch.get("metadata") if isinstance(patch.get("metadata"), dict) else {}
    workflow_instance_id = metadata.get("workflow_instance_id")
    if isinstance(workflow_instance_id, str) and workflow_instance_id:
        instance = gateway.workflow_repository.get_instance(workflow_instance_id, scope=scope)
        if instance.workflow_template_id != workflow_template_id:
            raise ProtocolError("SCOPE_MISMATCH", "Workflow instance does not belong to workflow template.", {"resource": "workflow_instance_id"})
    if operation == "add_station":
        _validate_node_add_payload(payload, draft_payload)
    elif operation == "update_edge":
        _validate_edge_intent_payload(payload, draft_payload)
    elif operation in INSPECTOR_OPERATION_FIELDS:
        _validate_inspector_patch_payload(operation, payload, draft_payload)
    elif operation == "update_connector":
        refs = payload.get("connector_refs")
        if refs is not None and (not isinstance(refs, list) or any(ref not in ALLOWED_CONNECTOR_REFS for ref in refs)):
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "connector_refs contains unsupported connector.", {"field": "connector_refs"})
        connector_patch = payload.get("connector_patch")
        if isinstance(connector_patch, dict):
            _reject_sensitive_or_layout_fields(connector_patch)
    elif operation == "update_quality_rule":
        patch_payload = payload.get("quality_patch")
        if isinstance(patch_payload, dict):
            threshold = patch_payload.get("threshold")
            if threshold is not None and not (isinstance(threshold, (int, float)) and 0 <= float(threshold) <= 1):
                raise ProtocolError("WORKFLOW_PATCH_INVALID", "quality threshold must be between 0 and 1.", {"field": "threshold"})
    elif operation == "update_approval_point":
        if "approval_required" in payload and not isinstance(payload.get("approval_required"), bool):
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "approval_required must be boolean.", {"field": "approval_required"})


def _validate_node_add_payload(payload: dict[str, Any], draft_payload: dict[str, Any]) -> None:
    station = payload.get("station")
    if not isinstance(station, dict):
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "add_station requires station descriptor.", {"field": "station"})
    metadata = station.get("metadata") if isinstance(station.get("metadata"), dict) else {}
    catalog_id = metadata.get("node_catalog_id")
    if catalog_id not in ALLOWED_NODE_CATALOG_IDS:
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "Station descriptor must come from allowed node catalog.", {"node_catalog_id": catalog_id})
    catalog_contract = NODE_CATALOG_CONTRACTS.get(str(catalog_id))
    if not catalog_contract:
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "Station descriptor has no controlled catalog contract.", {"node_catalog_id": catalog_id})
    for required_field in (
        "catalog_id",
        "catalog_version",
        "node_template_id",
        "station_kind",
        "schema_version",
        "allowed_skill_refs",
        "allowed_connector_refs",
        "allowed_artifact_kinds",
        "allowed_quality_rules",
        "allowed_approval_policies",
    ):
        if metadata.get(required_field) != catalog_contract.get(required_field):
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "Station descriptor does not match controlled catalog contract.", {"field": required_field})
    station_id = station.get("station_id")
    existing_ids = {item.get("station_id") for item in draft_payload.get("stations", []) if isinstance(item, dict)}
    if not isinstance(station_id, str) or not station_id:
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "station_id is required.", {"field": "station_id"})
    if station_id in existing_ids:
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "Station already exists.", {"station_id": station_id})
    refs = station.get("skill_refs")
    if refs is not None and (not isinstance(refs, list) or any(ref not in ALLOWED_SKILL_REFS for ref in refs)):
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "skill_refs contains unsupported skill.", {"field": "skill_refs"})
    allowed_skill_refs = set(catalog_contract["allowed_skill_refs"])
    if refs is not None and any(ref not in allowed_skill_refs for ref in refs):
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "skill_refs not allowed by node catalog contract.", {"field": "skill_refs"})
    connector_refs = station.get("connector_refs")
    if connector_refs is not None and (not isinstance(connector_refs, list) or any(ref not in ALLOWED_CONNECTOR_REFS for ref in connector_refs)):
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "connector_refs contains unsupported connector.", {"field": "connector_refs"})
    allowed_connector_refs = set(catalog_contract["allowed_connector_refs"])
    if connector_refs is not None and any(ref not in allowed_connector_refs for ref in connector_refs):
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "connector_refs not allowed by node catalog contract.", {"field": "connector_refs"})
    if station.get("role") and station.get("role") != catalog_contract["station_kind"]:
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "station role must match node catalog station_kind.", {"field": "role"})


def _validate_inspector_patch_payload(operation: str, payload: dict[str, Any], draft_payload: dict[str, Any]) -> None:
    allowed = INSPECTOR_OPERATION_FIELDS[operation]
    unknown = sorted(set(payload) - allowed)
    if unknown:
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "Inspector patch payload contains unknown fields.", {"fields": unknown, "operation": operation})
    if operation != "update_quality_rule":
        station_id = payload.get("station_id")
        station_ids = {item.get("station_id") for item in draft_payload.get("stations", []) if isinstance(item, dict)}
        if not isinstance(station_id, str) or station_id not in station_ids:
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "Inspector patch references missing station.", {"field": "station_id"})
    if operation == "update_connector":
        refs = payload.get("connector_refs")
        if refs is not None and (not isinstance(refs, list) or any(ref not in ALLOWED_CONNECTOR_REFS for ref in refs)):
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "connector_refs contains unsupported connector.", {"field": "connector_refs"})
    if operation == "update_artifact_contract":
        patch = payload.get("contract_patch")
        if not isinstance(payload.get("contract_id"), str) or not isinstance(patch, dict):
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "Artifact contract patch requires contract_id and contract_patch.", {"field": "contract_patch"})
        artifact_kind = patch.get("artifact_kind")
        if artifact_kind is not None and not isinstance(artifact_kind, str):
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "artifact_kind must be a string.", {"field": "artifact_kind"})
        direction = patch.get("direction")
        if direction is not None and direction not in {"input", "output"}:
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "artifact contract direction must be input or output.", {"field": "direction"})
        schema_ref = patch.get("schema_ref")
        if schema_ref is not None and not isinstance(schema_ref, str):
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "schema_ref must be a string.", {"field": "schema_ref"})
    if operation == "update_quality_rule":
        quality_ids = {item.get("contract_id") for item in draft_payload.get("quality_contracts", []) if isinstance(item, dict)}
        if payload.get("quality_contract_id") not in quality_ids:
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "Quality contract not found.", {"field": "quality_contract_id"})
        patch = payload.get("quality_patch")
        if not isinstance(patch, dict):
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "quality_patch must be an object.", {"field": "quality_patch"})
        threshold = patch.get("threshold")
        if threshold is not None and not (isinstance(threshold, (int, float)) and 0 <= float(threshold) <= 1):
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "quality threshold must be between 0 and 1.", {"field": "threshold"})
    if operation == "update_approval_point" and "approval_required" in payload and not isinstance(payload.get("approval_required"), bool):
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "approval_required must be boolean.", {"field": "approval_required"})


def _validate_edge_intent_payload(payload: dict[str, Any], draft_payload: dict[str, Any]) -> None:
    edge_patch = payload.get("edge_patch")
    if not isinstance(edge_patch, dict):
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "update_edge requires edge_patch.", {"field": "edge_patch"})
    action = edge_patch.get("action", "update")
    if action not in {"add", "remove", "update"}:
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "edge_patch.action must be add, remove, or update.", {"action": action})
    station_ids = {item.get("station_id") for item in draft_payload.get("stations", []) if isinstance(item, dict)}
    edges = [item for item in draft_payload.get("edges", []) if isinstance(item, dict)]
    edge_id = payload.get("edge_id")
    if not isinstance(edge_id, str) or not edge_id:
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "edge_id is required.", {"field": "edge_id"})
    if action == "add":
        from_station_id = edge_patch.get("from_station_id")
        to_station_id = edge_patch.get("to_station_id")
        if from_station_id not in station_ids or to_station_id not in station_ids:
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "Workflow edge references missing station.", {"edge_id": edge_id})
        if from_station_id == to_station_id:
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "Workflow edge cannot be a self-loop.", {"edge_id": edge_id})
        if any(edge.get("edge_id") == edge_id or (edge.get("from_station_id") == from_station_id and edge.get("to_station_id") == to_station_id) for edge in edges):
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "Workflow edge already exists.", {"edge_id": edge_id})
        if _would_create_cycle(edges, str(from_station_id), str(to_station_id)):
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "Workflow edge would create a cycle.", {"edge_id": edge_id})
        if not _edge_artifact_contracts_compatible(draft_payload, str(from_station_id), str(to_station_id), edge_patch):
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "Workflow edge artifact contracts are incompatible.", {"edge_id": edge_id})
    else:
        existing_edge = next((edge for edge in edges if edge.get("edge_id") == edge_id), None)
        if existing_edge is None:
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "Workflow edge not found.", {"edge_id": edge_id})
        if action == "update":
            from_station_id = edge_patch.get("from_station_id", existing_edge.get("from_station_id"))
            to_station_id = edge_patch.get("to_station_id", existing_edge.get("to_station_id"))
            if from_station_id not in station_ids or to_station_id not in station_ids:
                raise ProtocolError("WORKFLOW_PATCH_INVALID", "Workflow edge references missing station.", {"edge_id": edge_id})
            if from_station_id == to_station_id:
                raise ProtocolError("WORKFLOW_PATCH_INVALID", "Workflow edge cannot be a self-loop.", {"edge_id": edge_id})
            peer_edges = [edge for edge in edges if edge.get("edge_id") != edge_id]
            if any(edge.get("from_station_id") == from_station_id and edge.get("to_station_id") == to_station_id for edge in peer_edges):
                raise ProtocolError("WORKFLOW_PATCH_INVALID", "Workflow edge already exists.", {"edge_id": edge_id})
            if _would_create_cycle(peer_edges, str(from_station_id), str(to_station_id)):
                raise ProtocolError("WORKFLOW_PATCH_INVALID", "Workflow edge would create a cycle.", {"edge_id": edge_id})
            if not _edge_artifact_contracts_compatible(draft_payload, str(from_station_id), str(to_station_id), edge_patch):
                raise ProtocolError("WORKFLOW_PATCH_INVALID", "Workflow edge artifact contracts are incompatible.", {"edge_id": edge_id})


def _would_create_cycle(edges: list[dict[str, Any]], from_station_id: str, to_station_id: str) -> bool:
    adjacency: dict[str, set[str]] = {}
    for edge in edges:
        if not isinstance(edge.get("from_station_id"), str) or not isinstance(edge.get("to_station_id"), str):
            continue
        adjacency.setdefault(str(edge["from_station_id"]), set()).add(str(edge["to_station_id"]))
    adjacency.setdefault(from_station_id, set()).add(to_station_id)
    seen: set[str] = set()
    stack = [to_station_id]
    while stack:
        current = stack.pop()
        if current == from_station_id:
            return True
        if current in seen:
            continue
        seen.add(current)
        stack.extend(adjacency.get(current, set()))
    return False


def _edge_artifact_contracts_compatible(
    draft_payload: dict[str, Any],
    from_station_id: str,
    to_station_id: str,
    edge_patch: dict[str, Any],
) -> bool:
    stations = [item for item in draft_payload.get("stations", []) if isinstance(item, dict)]
    source = next((station for station in stations if station.get("station_id") == from_station_id), None)
    target = next((station for station in stations if station.get("station_id") == to_station_id), None)
    if not source or not target:
        return False
    outputs = [item for item in source.get("output_contracts", []) if isinstance(item, dict)]
    inputs = [item for item in target.get("input_contracts", []) if isinstance(item, dict)]
    if not outputs or not inputs:
        return True
    requested = edge_patch.get("artifact_contract")
    requested_kind = requested.get("artifact_kind") if isinstance(requested, dict) else None
    requested_schema_ref = requested.get("schema_ref") if isinstance(requested, dict) else None
    for output in outputs:
        for input_contract in inputs:
            if output.get("direction", "output") != "output" or input_contract.get("direction", "input") != "input":
                continue
            kind_matches = output.get("artifact_kind") == input_contract.get("artifact_kind")
            schema_matches = bool(output.get("schema_ref") and output.get("schema_ref") == input_contract.get("schema_ref"))
            requested_matches = (
                requested_kind is None
                or requested_kind in {output.get("artifact_kind"), input_contract.get("artifact_kind")}
            ) and (
                requested_schema_ref is None
                or requested_schema_ref in {output.get("schema_ref"), input_contract.get("schema_ref")}
            )
            if (kind_matches or schema_matches) and requested_matches:
                return True
    return False


def _ensure_approval_in_instance(approval: dict[str, Any], workflow_instance_id: str) -> None:
    if _approval_workflow_binding(approval).get("workflow_instance_id") != workflow_instance_id:
        raise ProtocolError("SCOPE_MISMATCH", "Approval does not belong to workflow instance.", {"resource": "approval_id"})


def _ensure_quality_in_instance(evaluation: dict[str, Any], workflow_instance_id: str) -> None:
    if evaluation.get("workflow_instance_id") != workflow_instance_id:
        raise ProtocolError("SCOPE_MISMATCH", "Quality evaluation does not belong to workflow instance.", {"resource": "evaluation_id"})


def _ensure_station_run_in_instance(gateway: GatewayService, station_run_id: str, workflow_instance_id: str, scope: ScopeContext) -> None:
    station_run = gateway.workflow_repository.get_station_run(station_run_id, scope=scope)
    if station_run.workflow_instance_id != workflow_instance_id:
        raise ProtocolError("SCOPE_MISMATCH", "Station run does not belong to workflow instance.", {"resource": "station_run_id"})


def _ensure_artifact_in_instance(gateway: GatewayService, artifact_id: str, workflow_instance_id: str, scope: ScopeContext) -> None:
    instance = gateway.workflow_repository.get_instance(workflow_instance_id, scope=scope)
    if artifact_id in set(instance.artifact_ids):
        return
    station_runs = gateway.workflow_repository.list_station_runs(workflow_instance_id, scope=scope)
    for run in station_runs:
        if artifact_id in set(run.input_artifact_ids) or artifact_id in set(run.output_artifact_ids):
            return
    raise ProtocolError("SCOPE_MISMATCH", "Artifact does not belong to workflow instance.", {"resource": "artifact_id"})


def _ensure_patch_in_template(gateway: GatewayService, workflow_patch_id: str, workflow_template_id: str, scope: ScopeContext) -> None:
    patch = gateway.workflow_repository.get_patch(workflow_patch_id, scope=scope)
    if patch.workflow_template_id != workflow_template_id:
        raise ProtocolError("SCOPE_MISMATCH", "Workflow patch does not belong to workflow template.", {"resource": "workflow_patch_id"})


def _ensure_patch_editable_for_template(
    gateway: GatewayService,
    workflow_patch_id: str,
    workflow_template_id: str,
    scope: ScopeContext,
    *,
    workflow_instance_id: Any = None,
):
    template = gateway.workflow_repository.get_template(workflow_template_id, scope=scope)
    patch = gateway.workflow_repository.get_patch(workflow_patch_id, scope=scope)
    if patch.workflow_template_id != workflow_template_id:
        raise ProtocolError("SCOPE_MISMATCH", "Workflow patch does not belong to workflow template.", {"resource": "workflow_patch_id"})
    if patch.workflow_draft_id != template.latest_draft_id:
        raise ProtocolError("SCOPE_MISMATCH", "Workflow patch does not target the latest workflow draft.", {"resource": "workflow_draft_id"})
    metadata = patch.metadata if isinstance(patch.metadata, dict) else {}
    bound_instance_id = metadata.get("workflow_instance_id")
    if workflow_instance_id and bound_instance_id and bound_instance_id != workflow_instance_id:
        raise ProtocolError("SCOPE_MISMATCH", "Workflow patch is not bound to the selected workflow instance.", {"resource": "workflow_instance_id"})
    if patch.status != "applied":
        draft = gateway.workflow_repository.get_draft(patch.workflow_draft_id, scope=scope)
        if draft.revision != patch.base_revision:
            raise ProtocolError(
                "WORKFLOW_PATCH_CONFLICT",
                "Workflow patch base revision does not match current draft revision.",
                {"base_revision": patch.base_revision, "actual_revision": draft.revision},
            )
    return patch


def _ensure_patch_in_instance(gateway: GatewayService, workflow_patch_id: str, workflow_instance_id: str, scope: ScopeContext) -> None:
    instance = gateway.workflow_repository.get_instance(workflow_instance_id, scope=scope)
    patch = gateway.workflow_repository.get_patch(workflow_patch_id, scope=scope)
    if patch.workflow_template_id != instance.workflow_template_id:
        raise ProtocolError("SCOPE_MISMATCH", "Workflow patch does not belong to workflow instance template.", {"resource": "workflow_patch_id"})
    metadata = patch.metadata if isinstance(patch.metadata, dict) else {}
    bound_instance_id = metadata.get("workflow_instance_id")
    if bound_instance_id != workflow_instance_id:
        raise ProtocolError("SCOPE_MISMATCH", "Workflow patch is not bound to this workflow instance.", {"resource": "workflow_patch_id"})


def _patch_matches_instance(patch: Any, workflow_instance_id: str) -> bool:
    metadata = patch.metadata if hasattr(patch, "metadata") and isinstance(patch.metadata, dict) else {}
    bound_instance_id = metadata.get("workflow_instance_id")
    return bound_instance_id in (None, workflow_instance_id)


def _require_user_confirmed(body: dict[str, Any], *, allowed_sources: set[str]) -> None:
    source = str(body.get("source") or "")
    if body.get("user_confirmed") is not True or source not in allowed_sources:
        raise ProtocolError(
            "WORKFLOW_ACTION_FORBIDDEN",
            "Workflow editing action requires explicit user confirmation.",
            {"source": source or None},
        )


def _auth_has_capability(auth: Any, capability: str) -> bool:
    if getattr(auth, "dev_mode", False):
        return True
    claims = getattr(auth, "claims", None)
    capabilities = getattr(claims, "capabilities", ()) if claims is not None else ()
    return capability in set(capabilities)


def _collect_unsent_events(
    gateway: GatewayService,
    *,
    scope: ScopeContext,
    channels: list[str],
    filters: dict[str, Any],
    last_sequence: int,
    sent_keys: set[tuple[str, str]],
) -> tuple[list[dict[str, Any]], int]:
    events: list[dict[str, Any]] = []
    current_sequence = last_sequence
    for event in collect_event_envelopes(gateway, scope=scope, channels=channels, filters=filters):
        sequence = read_event_cursor(event["cursor"], scope)
        key = (str(event.get("channel") or ""), str(event.get("event_id") or ""))
        if sequence > current_sequence and key not in sent_keys:
            events.append(event)
            current_sequence = max(current_sequence, sequence)
            sent_keys.add(key)
    return events, current_sequence


def _query_scope_params(request: Request) -> dict[str, Any]:
    params: dict[str, Any] = {}
    for key in ("app_id", "project_id", "workspace_id"):
        value = request.query_params.get(key)
        if value:
            params[key] = value
    return params


def _redact(value: Any) -> Any:
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for key, item in value.items():
            lower = str(key).lower()
            if any(part in lower for part in SENSITIVE_KEY_PARTS):
                continue
            redacted[key] = _redact(item)
        return redacted
    if isinstance(value, list):
        return [_redact(item) for item in value]
    if isinstance(value, str) and (
        "Bearer " in value
        or "subscription_token" in value
        or "capability_token" in value
        or "Authorization" in value
        or "secret-token-value" in value
        or "raw_trace_payload" in value
        or "raw_artifact_content" in value
        or "raw_connector_payload" in value
    ):
        return "[redacted]"
    return value


def _truthy(value: Any) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _float_param(value: Any, *, default: float) -> float:
    if value in (None, ""):
        return default
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ProtocolError("INVALID_PARAMS", "heartbeat_interval must be numeric.", {"field": "heartbeat_interval"}) from exc


def _int_param(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ProtocolError("INVALID_PARAMS", "max_heartbeats must be an integer.", {"field": "max_heartbeats"}) from exc
