"""Test-only BFF server for V4.0-F browser smoke.

This server owns a seeded GatewayService and exposes the normal BFF routes used
by the browser. It is intentionally local to the workflow-console e2e harness.
"""

from __future__ import annotations

import asyncio
import copy
import os
import sys
import tempfile
from pathlib import Path
from typing import Any
from uuid import uuid4

import uvicorn
from fastapi import Request
from fastapi.responses import JSONResponse

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.api import create_app  # noqa: E402
from apps.api.auth import LOCAL_ORIGINS  # noqa: E402
from apps.gateway.protocol import GatewayEvent  # noqa: E402
from tests.v4_0_reference_support import build_gateway, rpc, seed_reference_console  # noqa: E402

os.environ.setdefault("HARNESS_V3_5_DEV_MODE", "1")
os.environ.setdefault("HARNESS_CAPABILITY_TOKEN_SECRET", "browser-smoke-secret")
preview_port = os.environ.get("WORKFLOW_CONSOLE_PREVIEW_PORT", "4174")
LOCAL_ORIGINS.add(f"http://127.0.0.1:{preview_port}")
LOCAL_ORIGINS.add(f"http://localhost:{preview_port}")

DEFAULT_SCOPE = {"app_id": "default", "project_id": None, "workspace_id": None}
TMP_ROOT = Path(tempfile.mkdtemp(prefix="harnessos-v4-browser-smoke-"))
GATEWAY = build_gateway(TMP_ROOT)
SEEDED = asyncio.run(seed_reference_console(GATEWAY, template_id="browser_smoke_console", scope=DEFAULT_SCOPE))
app = create_app(gateway_service=GATEWAY)

V12_WORKSPACE = {
    "schema_version": "v12.product_entity_projection.v1",
    "workspace": {
        "workspace_id": "ws-v12-technical-content-real",
        "name": "技术内容工作室",
    },
    "project": {
        "project_id": "proj-v12-local-knowledge-real",
        "workspace_id": "ws-v12-technical-content-real",
        "name": "本地知识总结项目",
    },
    "app": {
        "app_id": "app-v12-markdown-workflow-real",
        "project_id": "proj-v12-local-knowledge-real",
        "name": "Markdown 工作流应用",
        "app_kind": "workflow_app",
    },
    "service_account_ref": "svc-v12-readonly-redacted-ref",
    "evidence_scope": "browser_e2e",
    "created_at": "2026-06-23T00:00:00Z",
}

V12_CANVAS = {
    "schema_version": "v12.canvas_read_model.v1",
    "canvas_read_model_id": "canvas-v12-local-markdown-summary-real",
    "workspace_id": "ws-v12-technical-content-real",
    "project_id": "proj-v12-local-knowledge-real",
    "app_id": "app-v12-markdown-workflow-real",
    "read_only": True,
    "nodes": [
        {
            "node_id": "folder_input",
            "label": "文件夹输入",
            "node_kind": "input",
            "status": "completed",
            "position": {"x": 0, "y": 80},
            "inspector_ref": "inspector-folder-input",
        },
        {
            "node_id": "quality_check",
            "label": "质量检查 Agent",
            "node_kind": "reviewer",
            "status": "waiting_approval",
            "position": {"x": 840, "y": 300},
            "inspector_ref": "inspector-quality-check",
        },
    ],
    "edges": [
        {
            "edge_id": "folder_input-quality_check",
            "source_node_id": "folder_input",
            "target_node_id": "quality_check",
        }
    ],
    "evidence_refs": ["evidence://v12/current-stage/real-data-readonly-canvas"],
    "created_at": "2026-06-23T00:00:00Z",
}

V12_INSPECTOR = {
    "schema_version": "v12.canvas_inspector_projection.v1",
    "inspector_projection_ref": "inspector-quality-check",
    "selected_node_ref": "quality_check",
    "entity_type": "station_agent",
    "role": "reviewer",
    "goal": "检查总结质量并生成可审计 quality report",
    "memory_policy_ref": "memory-v12-quality-agent-redacted",
    "model_profile_ref": "provider_ref:minimax-or-deepseek-redacted",
    "tool_binding_refs": ["tool:quality.review"],
    "skill_binding_refs": ["skill:markdown.summary"],
    "mcp_binding_refs": ["mcp:readonly-docs"],
    "quality_refs": ["quality:v12-readonly-gate"],
    "evidence_refs": ["evidence://v12/current-stage/quality-check"],
    "redaction_status": "PASS",
    "audit_ref": "audit://v12/current-stage/inspector-quality-check",
}
V12_WORKBENCH_CONVERSATION = {
    "schema_version": "v12.workbench_conversation.v1",
    "conversation_id": "conv-v12-markdown-summary-goal-real",
    "workspace_id": V12_WORKSPACE["workspace"]["workspace_id"],
    "project_id": V12_WORKSPACE["project"]["project_id"],
    "app_id": V12_WORKSPACE["app"]["app_id"],
    "participant_refs": ["actor:local-reviewer", "assistant:v12-workbench"],
    "goal_summary": "把本地 Markdown 技术文档总结成可审计工作流",
    "messages": [
        {
            "message_id": "msg-v12-user-goal-real",
            "role": "user",
            "redacted_text_ref": "text_ref:v12-goal-markdown-summary-redacted",
            "summary": "总结本地 Markdown 技术文档，并在质量检查后输出证据包。",
            "created_at": "2026-06-23T00:00:00Z",
        },
        {
            "message_id": "msg-v12-assistant-proposal-real",
            "role": "assistant",
            "redacted_text_ref": "text_ref:v12-assistant-proposal-redacted",
            "summary": "已生成只读 WorkflowDiff 提案，等待人工确认交接。",
            "created_at": "2026-06-23T00:00:10Z",
        },
    ],
    "proposal_timeline_ref": "timeline-v12-markdown-summary-real",
    "evidence_scope": "proposal_only_not_runtime",
    "audit_ref": "audit://v12/current-stage/workbench-conversation",
    "created_at": "2026-06-23T00:00:00Z",
}
V12_PROPOSAL_TIMELINE = {
    "schema_version": "v12.workbench_proposal_timeline.v1",
    "proposal_timeline_id": "timeline-v12-markdown-summary-real",
    "conversation_id": V12_WORKBENCH_CONVERSATION["conversation_id"],
    "workflow_diff_proposal_ref": "diff-v12-readonly-proposal-ref",
    "current_state": "awaiting_user_confirmation",
    "events": [
        {
            "event_id": "evt-v12-goal-received",
            "label": "目标已接收",
            "state": "goal_received",
            "risk_level": "low",
            "created_at": "2026-06-23T00:00:00Z",
        },
        {
            "event_id": "evt-v12-proposal-ready",
            "label": "WorkflowDiff 提案已生成",
            "state": "proposal_ready",
            "risk_level": "medium",
            "created_at": "2026-06-23T00:00:10Z",
        },
        {
            "event_id": "evt-v12-awaiting-confirmation",
            "label": "等待人工确认交接",
            "state": "awaiting_user_confirmation",
            "risk_level": "medium",
            "created_at": "2026-06-23T00:00:20Z",
        },
    ],
    "changed_node_refs": ["folder_input", "quality_check"],
    "blocked_runtime_actions": ["publish", "run", "apply_to_workflow_spec_graph"],
    "audit_ref": "audit://v12/current-stage/proposal-timeline",
}
V12_WORKFLOW_DIFF = {
    "schema_version": "v12.workflow_diff_proposal_ref.v1",
    "proposal_id": "diff-v12-readonly-proposal-ref",
    "status": "awaiting_user_confirmation",
    "before_graph_ref": "canvas-read-model:v12-current-stage",
    "after_graph_ref": "workflow-diff-preview:v12-markdown-summary",
    "changed_node_refs": ["folder_input", "quality_check"],
    "confirmation_boundary": "handoff_only_no_publish_no_run",
    "runtime_backed": False,
    "audit_ref": "audit://v12/current-stage/workflow-diff-ref",
}
V12_INTERACTION_TRACE = {
    "schema_version": "v12.canvas_interaction_trace.v1",
    "trace_id": "trace-v12-interaction-depth-real",
    "selected_node_ref": "quality_check",
    "inspector_projection_ref": V12_INSPECTOR["inspector_projection_ref"],
    "disabled_action_reasons": [
        {
            "action_id": "add_node",
            "label": "添加节点",
            "reason": "V12 只读画布阶段：需要 V13 WorkflowDiff 确认后才允许编辑",
        },
        {
            "action_id": "publish_run",
            "label": "发布 / 运行",
            "reason": "V12 不允许发布或运行工作流",
        },
        {
            "action_id": "auto_layout",
            "label": "自动布局",
            "reason": "V12 仅记录布局意图，不写入 WorkflowSpecGraph",
        },
    ],
    "state_fixtures": [
        {"state": "selected", "visible": True, "description": "quality_check 节点高亮并同步 Inspector"},
        {"state": "denied", "visible": True, "description": "发布/运行动作被边界策略阻止"},
        {"state": "loading", "visible": True, "description": "BFF projection 加载中状态可见"},
        {"state": "failure", "visible": True, "description": "BFF projection 失败时回退到本地只读投影"},
    ],
    "focus_targets": ["v12-goal-input", "v12-revise-proposal", "v12-reject-proposal", "v12-open-graph-review"],
    "audit_ref": "audit://v12/current-stage/interaction-trace",
}
V12_ROUTE_LOG: list[dict[str, Any]] = []
V13_WORKFLOW_ID = "wf-v13-markdown-summary-studio-pilot"
V13_GRAPH = {
    "schema_version": "v13.workflow_spec_graph.v1",
    "workflow_id": V13_WORKFLOW_ID,
    "workspace_id": V12_WORKSPACE["workspace"]["workspace_id"],
    "project_id": V12_WORKSPACE["project"]["project_id"],
    "app_id": V12_WORKSPACE["app"]["app_id"],
    "version_ref": "workflow-version:v13-draft-001",
    "runtime_backed": False,
    "nodes": [
        {
            "node_id": "start_goal",
            "label": "目标输入",
            "node_kind": "start",
            "status": "configured",
            "position": {"x": 0, "y": 120},
        },
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
        {
            "node_id": "quality_branch",
            "label": "质量分支",
            "node_kind": "fan_out",
            "status": "configured",
            "position": {"x": 800, "y": 120},
        },
        {
            "node_id": "quality_gate",
            "label": "质量检查",
            "node_kind": "quality_gate",
            "status": "configured",
            "capability_ref": "tool:quality.review",
            "position": {"x": 1060, "y": 40},
        },
        {
            "node_id": "evidence_review",
            "label": "证据审查",
            "node_kind": "evidence",
            "status": "configured",
            "position": {"x": 1060, "y": 210},
        },
        {
            "node_id": "merge_review",
            "label": "审查汇合",
            "node_kind": "fan_in",
            "status": "configured",
            "position": {"x": 1330, "y": 120},
        },
        {
            "node_id": "final_markdown",
            "label": "输出 Markdown 总结",
            "node_kind": "end",
            "status": "configured",
            "position": {"x": 1600, "y": 120},
        },
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
    "proposal_id": "diff-v13-editable-studio-pilot-001",
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
V13_ROUTE_LOG: list[dict[str, Any]] = []
V14_AGENT_ID = "agent-v12-quality-reviewer-real"
V14_STATION_ID = "quality_check"
V14_SCOPE = {
    "workspace_id": V12_WORKSPACE["workspace"]["workspace_id"],
    "project_id": V12_WORKSPACE["project"]["project_id"],
    "app_id": V12_WORKSPACE["app"]["app_id"],
    "agent_id": V14_AGENT_ID,
    "station_id": V14_STATION_ID,
}
V14_APPROVED_PACKAGE_ID = "pkg-v14-tool-quality-review-pack"
V14_UNSAFE_PACKAGE_ID = "pkg-v14-unsafe-shell-executor"
V14_PACKAGES = {
    V14_APPROVED_PACKAGE_ID: {
        "schema_version": "v14.extension_package_manifest.v1",
        "package_id": V14_APPROVED_PACKAGE_ID,
        "display_name": "质量审查扩展包",
        "package_kind": "tool_capability",
        "publisher": "HarnessOS Local Review",
        "version": "0.14.0-review",
        "trust_level": "reviewed_local",
        "status": "approved",
        "requested_permissions": ["read:artifact_summary", "write:evidence_note"],
        "required_credential_refs": ["credential_ref:v14-quality-review-redacted"],
        "redacted_config_refs": ["config_ref:v14-quality-review-redacted"],
        "capability_refs": ["tool:quality.review", "skill:markdown.summary", "mcp:readonly-docs"],
        "scope_requirements": ["workspace", "project", "app", "agent", "station"],
        "audit_ref": "audit://v14/extension/pkg-quality-review",
        "created_at": "2026-06-24T00:00:00Z",
    },
    "pkg-v14-plugin-evidence-annotator": {
        "schema_version": "v14.extension_package_manifest.v1",
        "package_id": "pkg-v14-plugin-evidence-annotator",
        "display_name": "证据标注插件",
        "package_kind": "plugin",
        "publisher": "HarnessOS Local Review",
        "version": "0.14.0-review",
        "trust_level": "reviewed_local",
        "status": "approved",
        "requested_permissions": ["read:evidence_refs", "write:review_note"],
        "required_credential_refs": [],
        "redacted_config_refs": ["config_ref:v14-evidence-annotator-redacted"],
        "capability_refs": ["plugin:evidence.annotator"],
        "scope_requirements": ["workspace", "project", "app"],
        "audit_ref": "audit://v14/extension/plugin-evidence-annotator",
        "created_at": "2026-06-24T00:00:00Z",
    },
    "pkg-v14-skill-summary-guard": {
        "schema_version": "v14.extension_package_manifest.v1",
        "package_id": "pkg-v14-skill-summary-guard",
        "display_name": "总结质量守护 Skill",
        "package_kind": "skill",
        "publisher": "HarnessOS Local Review",
        "version": "0.14.0-review",
        "trust_level": "reviewed_local",
        "status": "approved",
        "requested_permissions": ["read:workflow_diff", "write:quality_hint"],
        "required_credential_refs": [],
        "redacted_config_refs": ["config_ref:v14-summary-guard-redacted"],
        "capability_refs": ["skill:markdown.summary.guard"],
        "scope_requirements": ["workspace", "project", "app", "agent"],
        "audit_ref": "audit://v14/extension/skill-summary-guard",
        "created_at": "2026-06-24T00:00:00Z",
    },
    "pkg-v14-mcp-readonly-docs": {
        "schema_version": "v14.extension_package_manifest.v1",
        "package_id": "pkg-v14-mcp-readonly-docs",
        "display_name": "只读文档 MCP Connector",
        "package_kind": "mcp_connector",
        "publisher": "HarnessOS Local Review",
        "version": "0.14.0-review",
        "trust_level": "reviewed_local",
        "status": "approved",
        "requested_permissions": ["read:document_index"],
        "required_credential_refs": ["credential_ref:v14-docs-mcp-redacted"],
        "redacted_config_refs": ["config_ref:v14-docs-mcp-redacted"],
        "capability_refs": ["mcp:readonly-docs"],
        "scope_requirements": ["workspace", "project"],
        "audit_ref": "audit://v14/extension/mcp-readonly-docs",
        "created_at": "2026-06-24T00:00:00Z",
    },
    V14_UNSAFE_PACKAGE_ID: {
        "schema_version": "v14.extension_package_manifest.v1",
        "package_id": V14_UNSAFE_PACKAGE_ID,
        "display_name": "未审 Shell 执行器",
        "package_kind": "tool_capability",
        "publisher": "Unknown Local Package",
        "version": "0.0.1-unreviewed",
        "trust_level": "unreviewed",
        "status": "unsafe_denied",
        "requested_permissions": ["execute:shell", "read:secret_ref_probe", "scope:global"],
        "required_credential_refs": ["credential_ref:v14-unsafe-redacted"],
        "redacted_config_refs": ["config_ref:v14-unsafe-redacted"],
        "capability_refs": ["tool:unsafe.shell"],
        "scope_requirements": ["global"],
        "blocked_fields": ["unknown_executable_payload", "unreviewed_permission", "scope_escalation_request"],
        "audit_ref": "audit://v14/extension/unsafe-shell-executor",
        "created_at": "2026-06-24T00:00:00Z",
    },
}
V14_PLUGIN_MANIFEST = {
    "schema_version": "v14.plugin_package_manifest.v1",
    "package": V14_PACKAGES["pkg-v14-plugin-evidence-annotator"],
    "extension_points": ["agent_inspector.note", "evidence.review"],
    "runtime_backed": False,
}
V14_SKILL_MANIFEST = {
    "schema_version": "v14.skill_package_manifest.v1",
    "package": V14_PACKAGES["pkg-v14-skill-summary-guard"],
    "skill_refs": ["skill:markdown.summary.guard"],
    "runtime_backed": False,
}
V14_TOOL_MANIFEST = {
    "schema_version": "v14.tool_capability_manifest.v1",
    "package": V14_PACKAGES[V14_APPROVED_PACKAGE_ID],
    "tool_refs": ["tool:quality.review"],
    "runtime_backed": False,
}
V14_MCP_MANIFEST = {
    "schema_version": "v14.mcp_connector_manifest.v1",
    "package": V14_PACKAGES["pkg-v14-mcp-readonly-docs"],
    "connector_refs": ["mcp:readonly-docs"],
    "runtime_backed": False,
}
V14_ACTIVATION_DECISION = {
    "schema_version": "v14.extension_activation_decision.v1",
    "package_id": V14_APPROVED_PACKAGE_ID,
    "decision": "activated_for_scope",
    "scope": V14_SCOPE,
    "active_capability_refs": ["tool:quality.review", "skill:markdown.summary", "mcp:readonly-docs"],
    "global_activation": False,
    "runtime_backed": False,
    "audit_ref": "audit://v14/extension/activation-quality-review",
    "created_at": "2026-06-24T00:00:00Z",
}
V14_SCOPED_BINDING = {
    "schema_version": "v14.scoped_capability_binding.v1",
    "agent_id": V14_AGENT_ID,
    "station_id": V14_STATION_ID,
    "scope": V14_SCOPE,
    "bound_capabilities": [
        {
            "capability_ref": "tool:quality.review",
            "package_id": V14_APPROVED_PACKAGE_ID,
            "activation_ref": "activation:v14-quality-review-scope",
            "allowed_actions": ["inspect_summary", "write_evidence_note"],
        }
    ],
    "denied_global_capabilities": ["tool:unsafe.shell"],
    "runtime_backed": False,
    "audit_ref": "audit://v14/extension/binding-quality-review",
    "created_at": "2026-06-24T00:00:00Z",
}
V14_ROUTE_LOG: list[dict[str, Any]] = []
V15_RUN_REF = "run-v15-final-interaction-review"
V15_REQUEST_ID = "req-v15-local-ops-review"
V15_CORRELATION_ID = "corr-v15-local-ops-review"
V15_TRACE_TIMELINE = {
    "schema_version": "v15.trace_timeline.v1",
    "workspace_id": V12_WORKSPACE["workspace"]["workspace_id"],
    "project_id": V12_WORKSPACE["project"]["project_id"],
    "app_id": V12_WORKSPACE["app"]["app_id"],
    "run_ref": V15_RUN_REF,
    "request_id": V15_REQUEST_ID,
    "correlation_id": V15_CORRELATION_ID,
    "evidence_scope": "browser_e2e",
    "events": [
        {
            "event_id": "trace-v15-v12-workbench",
            "stage": "V12",
            "status": "PASS",
            "label": "V12 product entity and read-only workbench evidence accepted",
            "evidence_ref": "docs/design/V12-V15.x/evidence/v12-sa-aggregate/acceptance-data.json",
            "occurred_at": "2026-06-24T00:00:00Z",
        },
        {
            "event_id": "trace-v15-v13-studio",
            "stage": "V13",
            "status": "PASS",
            "label": "V13 editable Studio pilot evidence accepted",
            "evidence_ref": "docs/design/V12-V15.x/evidence/v13-workflow-studio-pilot/v13-workflow-studio-acceptance-data.json",
            "occurred_at": "2026-06-24T00:01:00Z",
        },
        {
            "event_id": "trace-v15-v14-extension",
            "stage": "V14",
            "status": "PASS",
            "label": "V14 governed extension ecosystem evidence accepted",
            "evidence_ref": "docs/design/V12-V15.x/evidence/v14-extension-ecosystem/acceptance-data.json",
            "occurred_at": "2026-06-24T00:02:00Z",
        },
        {
            "event_id": "trace-v15-ops-review",
            "stage": "V15",
            "status": "READY_FOR_REVIEW",
            "label": "V15 operations and deployment baseline is under browser review",
            "evidence_ref": "docs/design/V12-V15.x/evidence/v15-observability-deployment/acceptance-data.json",
            "occurred_at": "2026-06-24T00:03:00Z",
        },
    ],
    "runtime_backed": False,
    "audit_ref": "audit://v15/observability/trace-timeline",
    "created_at": "2026-06-24T00:00:00Z",
}
V15_METRICS_SNAPSHOT = {
    "schema_version": "v15.metrics_snapshot.v1",
    "workspace_id": V12_WORKSPACE["workspace"]["workspace_id"],
    "project_id": V12_WORKSPACE["project"]["project_id"],
    "app_id": V12_WORKSPACE["app"]["app_id"],
    "run_ref": V15_RUN_REF,
    "request_id": V15_REQUEST_ID,
    "correlation_id": V15_CORRELATION_ID,
    "evidence_scope": "browser_e2e",
    "metrics": {
        "accepted_stage_count": 3,
        "v15_scenario_count": 8,
        "failed_scenario_count": 0,
        "blocked_scenario_count": 0,
        "redaction_scan_status": "PASS",
        "claim_scan_status": "PASS",
    },
    "runtime_backed": False,
    "audit_ref": "audit://v15/observability/metrics-snapshot",
    "created_at": "2026-06-24T00:00:00Z",
}
V15_AUDIT_EXPORT = {
    "schema_version": "v15.audit_export_package.v1",
    "workspace_id": V12_WORKSPACE["workspace"]["workspace_id"],
    "project_id": V12_WORKSPACE["project"]["project_id"],
    "app_id": V12_WORKSPACE["app"]["app_id"],
    "run_ref": V15_RUN_REF,
    "request_id": V15_REQUEST_ID,
    "correlation_id": V15_CORRELATION_ID,
    "evidence_scope": "browser_e2e",
    "export_ref": "audit-export://v15/local-review/redacted",
    "included_evidence_refs": [
        "docs/design/V12-V15.x/evidence/v12-sa-aggregate/acceptance-data.json",
        "docs/design/V12-V15.x/evidence/v13-workflow-studio-pilot/v13-workflow-studio-acceptance-data.json",
        "docs/design/V12-V15.x/evidence/v14-extension-ecosystem/acceptance-data.json",
    ],
    "redaction_status": "PASS",
    "runtime_backed": False,
    "audit_ref": "audit://v15/observability/audit-export",
    "created_at": "2026-06-24T00:00:00Z",
}
V15_INCIDENT_TIMELINE = {
    "schema_version": "v15.incident_timeline.v1",
    "workspace_id": V12_WORKSPACE["workspace"]["workspace_id"],
    "project_id": V12_WORKSPACE["project"]["project_id"],
    "app_id": V12_WORKSPACE["app"]["app_id"],
    "run_ref": V15_RUN_REF,
    "request_id": V15_REQUEST_ID,
    "correlation_id": V15_CORRELATION_ID,
    "evidence_scope": "browser_e2e",
    "incidents": [
        {
            "incident_id": "incident-v15-none",
            "severity": "info",
            "status": "closed",
            "summary": "No failed V12-V15 acceptance dependency detected in local review evidence.",
            "evidence_ref": "docs/design/V12-V15.x/reports/v14_extension_ecosystem_acceptance_report.json",
        }
    ],
    "runtime_backed": False,
    "audit_ref": "audit://v15/observability/incident-timeline",
    "created_at": "2026-06-24T00:00:00Z",
}
V15_DEPLOYMENT_PROFILE = {
    "schema_version": "v15.deployment_profile.v1",
    "workspace_id": V12_WORKSPACE["workspace"]["workspace_id"],
    "project_id": V12_WORKSPACE["project"]["project_id"],
    "app_id": V12_WORKSPACE["app"]["app_id"],
    "run_ref": V15_RUN_REF,
    "request_id": V15_REQUEST_ID,
    "correlation_id": V15_CORRELATION_ID,
    "evidence_scope": "browser_e2e",
    "profile_id": "deployment-profile:v15-local-bounded-review",
    "profile_kind": "local_bounded_smoke",
    "frontend_base_url_ref": "http://127.0.0.1:4178",
    "bff_base_url_ref": "http://127.0.0.1:18044",
    "checks": ["bff_health", "frontend_shell", "v15_observability_routes", "evidence_dependencies"],
    "rollback_notes": "Stop preview and test-only BFF processes; no production resource is changed.",
    "not_production_ga": True,
    "runtime_backed": False,
    "audit_ref": "audit://v15/deployment/profile",
    "created_at": "2026-06-24T00:00:00Z",
}
V15_FINAL_SCENARIO_MATRIX = {
    "schema_version": "v15.final_scenario_matrix.v1",
    "workspace_id": V12_WORKSPACE["workspace"]["workspace_id"],
    "project_id": V12_WORKSPACE["project"]["project_id"],
    "app_id": V12_WORKSPACE["app"]["app_id"],
    "run_ref": V15_RUN_REF,
    "request_id": V15_REQUEST_ID,
    "correlation_id": V15_CORRELATION_ID,
    "evidence_scope": "browser_e2e",
    "scenarios": [
        {
            "scenario_id": "v12_product_workbench",
            "label": "V12 product workbench and read-only canvas foundation",
            "status": "PASS",
            "evidence_ref": "docs/design/V12-V15.x/evidence/v12-sa-aggregate/acceptance-data.json",
        },
        {
            "scenario_id": "v13_editable_studio_pilot",
            "label": "V13 editable Workflow Studio pilot slice",
            "status": "PASS",
            "evidence_ref": "docs/design/V12-V15.x/evidence/v13-workflow-studio-pilot/v13-workflow-studio-acceptance-data.json",
        },
        {
            "scenario_id": "v14_extension_ecosystem_pilot",
            "label": "V14 governed extension ecosystem pilot",
            "status": "PASS",
            "evidence_ref": "docs/design/V12-V15.x/evidence/v14-extension-ecosystem/acceptance-data.json",
        },
        {
            "scenario_id": "v15_observability_review",
            "label": "V15 trace, metrics, audit and incident review",
            "status": "PASS",
            "evidence_ref": "docs/design/V12-V15.x/evidence/v15-observability-deployment/trace-timeline.json",
        },
        {
            "scenario_id": "v15_deployment_smoke",
            "label": "V15 bounded local deployment smoke",
            "status": "PASS",
            "evidence_ref": "docs/design/V12-V15.x/evidence/v15-observability-deployment/deployment-smoke-output.txt",
        },
    ],
    "allowed_claim": "V15 frontend interaction baseline ready for review.",
    "runtime_backed": False,
    "audit_ref": "audit://v15/final-scenario-matrix",
    "created_at": "2026-06-24T00:00:00Z",
}
V15_ROUTE_LOG: list[dict[str, Any]] = []
PV16_CREATED_AT = "2026-06-25T00:00:00Z"
PV16_SCOPE = {
    "workspace_id": V12_WORKSPACE["workspace"]["workspace_id"],
    "project_id": V12_WORKSPACE["project"]["project_id"],
    "app_id": V12_WORKSPACE["app"]["app_id"],
    "agent_id": V14_AGENT_ID,
    "station_id": V14_STATION_ID,
}
PV16_ENTITY_STATE = {
    "schema_version": "pv16.product_entity_state.v1",
    "workspace": {
        **V12_WORKSPACE["workspace"],
        "status": "active",
        "audit_ref": "audit://pv16/entity/workspace/current",
    },
    "project": {
        **V12_WORKSPACE["project"],
        "status": "active",
        "audit_ref": "audit://pv16/entity/project/current",
    },
    "app": {
        **V12_WORKSPACE["app"],
        "status": "active",
        "audit_ref": "audit://pv16/entity/app/current",
    },
    "station_agent": {
        "agent_id": V14_AGENT_ID,
        "station_id": V14_STATION_ID,
        "display_name": "质量检查 Agent",
        "role": "reviewer",
        "goal": "检查总结质量并生成可审计 quality report",
        "memory_policy_ref": "memory-v12-quality-agent-redacted",
        "model_profile_ref": "provider_ref:minimax-or-deepseek-redacted",
        "tool_binding_refs": ["tool:quality.review"],
        "skill_binding_refs": ["skill:markdown.summary"],
        "mcp_binding_refs": ["mcp:readonly-docs"],
        "audit_ref": "audit://pv16/entity/station-agent/current",
    },
    "ownership_result": "PASS",
    "policy_result": "PASS",
    "redaction_status": "PASS",
    "runtime_backed": False,
    "created_at": PV16_CREATED_AT,
}
PV16_WORKFLOW_SPEC = {
    "schema_version": "pv16.workflow_spec_handoff.v1",
    "workflow_id": V13_WORKFLOW_ID,
    "workflow_version_ref": V13_GRAPH["version_ref"],
    "workflow_diff_ref": V13_WORKFLOW_DIFF["proposal_id"],
    "confirmation_state": "confirmed_for_runtime_pilot",
    "runtime_gateway": "GatewayService",
    "audit_ref": "audit://pv16/runtime/workflow-spec-handoff",
    "created_at": PV16_CREATED_AT,
}
PV16_DEPLOYMENT_PROFILE = {
    "schema_version": "pv16.deployment_hardening_profile.v1",
    "profile_id": "deployment-profile:pv16-local-hardening",
    "profile_kind": "local_non_destructive_hardening_smoke",
    "checks": ["bff_health", "frontend_shell", "runtime_gateway_status", "evidence_artifacts", "redaction_scan"],
    "rollback_notes": "Stop preview and test-only BFF processes; no persistent production resource is changed.",
    "not_production_ga": True,
    "audit_ref": "audit://pv16/deployment/profile",
    "created_at": PV16_CREATED_AT,
}
PV16_JOURNEY = {
    "schema_version": "pv16.product_runtime_journey.v1",
    "status": "PASS",
    "steps": [
        {"step_id": "setup", "label": "产品实体创建/更新", "status": "PASS", "evidence_ref": "entity-crud-report.json"},
        {"step_id": "studio", "label": "Studio WorkflowSpec 确认", "status": "PASS", "evidence_ref": "runtime-run-inspect-report.json"},
        {"step_id": "run_review", "label": "运行进度与证据检视", "status": "PASS", "evidence_ref": "runtime-inspect-screenshot.png"},
        {"step_id": "operations", "label": "部署 hardening smoke", "status": "PASS", "evidence_ref": "deployment-health-report.json"},
    ],
    "allowed_claim": "PV16 complete: product-runtime hardening pilot ready for review.",
    "created_at": PV16_CREATED_AT,
}
PV16_ROUTE_LOG: list[dict[str, Any]] = []
PV18_ROUTE_LOG: list[dict[str, Any]] = []


def build_v14_compatibility_decision(package_id: str) -> dict[str, Any]:
    """Return a deterministic V14 compatibility decision for local acceptance."""
    package = V14_PACKAGES.get(package_id)
    if package is None:
        return {
            "schema_version": "v14.extension_compatibility_decision.v1",
            "package_id": package_id,
            "status": "denied",
            "compatible": False,
            "reasons": ["包不存在或未进入本地审查注册表"],
            "blocked_permissions": ["unknown_package"],
            "required_scope": V14_SCOPE,
            "runtime_backed": False,
            "audit_ref": "audit://v14/extension/compatibility/unknown-package",
            "created_at": "2026-06-24T00:00:00Z",
        }
    if package_id == V14_UNSAFE_PACKAGE_ID:
        return {
            "schema_version": "v14.extension_compatibility_decision.v1",
            "package_id": package_id,
            "status": "denied",
            "compatible": False,
            "reasons": ["包含未审执行载荷", "请求全局作用域", "包含未审权限"],
            "blocked_permissions": ["execute:shell", "scope:global"],
            "required_scope": V14_SCOPE,
            "runtime_backed": False,
            "audit_ref": "audit://v14/extension/compatibility/unsafe-shell-executor",
            "created_at": "2026-06-24T00:00:00Z",
        }
    return {
        "schema_version": "v14.extension_compatibility_decision.v1",
        "package_id": package_id,
        "status": "approved",
        "compatible": True,
        "reasons": ["权限已知", "配置仅包含脱敏引用", "激活需要明确作用域"],
        "blocked_permissions": [],
        "required_scope": V14_SCOPE,
        "runtime_backed": False,
        "audit_ref": f"audit://v14/extension/compatibility/{package_id}",
        "created_at": "2026-06-24T00:00:00Z",
    }


def build_v14_unsafe_denial() -> dict[str, Any]:
    """Return the unsafe package denial DTO used by browser and evidence tests."""
    return {
        "schema_version": "v14.unsafe_package_denial.v1",
        "package_id": V14_UNSAFE_PACKAGE_ID,
        "status": "denied",
        "denial_reason": "未审执行载荷、全局作用域请求和未知权限被策略拒绝",
        "blocked_fields": V14_PACKAGES[V14_UNSAFE_PACKAGE_ID]["blocked_fields"],
        "blocked_permissions": ["execute:shell", "scope:global"],
        "active_capability_created": False,
        "runtime_backed": False,
        "audit_ref": "audit://v14/extension/unsafe-shell-executor",
        "created_at": "2026-06-24T00:00:00Z",
    }


def validate_v13_graph(graph: dict[str, Any]) -> dict[str, Any]:
    """Validate the V13 pilot WorkflowSpecGraph without mutating runtime truth."""
    errors: list[dict[str, str]] = []
    allowed_kinds = {"start", "tool", "station", "fan_out", "fan_in", "quality_gate", "evidence", "end"}
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    node_ids = {node.get("node_id") for node in nodes}

    if graph.get("schema_version") != "v13.workflow_spec_graph.v1":
        errors.append({"code": "SCHEMA_VERSION_INVALID", "message": "schema_version must be v13.workflow_spec_graph.v1"})
    if len([node for node in nodes if node.get("node_kind") == "start"]) != 1:
        errors.append({"code": "START_NODE_COUNT_INVALID", "message": "graph must contain exactly one start node"})
    if not [node for node in nodes if node.get("node_kind") == "end"]:
        errors.append({"code": "END_NODE_MISSING", "message": "graph must contain at least one end node"})
    for node in nodes:
        node_id = str(node.get("node_id") or "")
        node_kind = str(node.get("node_kind") or "")
        if not node_id:
            errors.append({"code": "NODE_ID_MISSING", "message": "node_id is required"})
        if node_kind not in allowed_kinds:
            errors.append({"code": "NODE_KIND_INVALID", "message": f"{node_id} has unsupported node_kind {node_kind}"})
        if node_kind == "station" and not node.get("agent_profile_ref"):
            errors.append({"code": "STATION_AGENT_REF_MISSING", "message": f"{node_id} must include agent_profile_ref"})
        if node_kind in {"tool", "quality_gate"} and not node.get("capability_ref"):
            errors.append({"code": "CAPABILITY_REF_MISSING", "message": f"{node_id} must include capability_ref"})
    for edge in edges:
        source_id = edge.get("source_node_id")
        target_id = edge.get("target_node_id")
        if source_id not in node_ids or target_id not in node_ids:
            errors.append(
                {
                    "code": "DANGLING_EDGE",
                    "message": f"{edge.get('edge_id', 'edge')} references missing source or target node",
                }
            )
    return {
        "schema_version": "v13.workflow_graph_validation_result.v1",
        "workflow_id": graph.get("workflow_id", V13_WORKFLOW_ID),
        "status": "FAIL" if errors else "PASS",
        "errors": errors,
        "runtime_backed": False,
        "audit_ref": "audit://v13/studio-pilot/graph-validation",
        "created_at": "2026-06-24T00:00:00Z",
    }


@app.middleware("http")
async def record_staged_route_log(request: Request, call_next: Any) -> Any:
    """Record staged BFF route usage for browser acceptance evidence."""
    response = await call_next(request)
    if request.url.path.startswith("/bff/v12"):
        V12_ROUTE_LOG.append(
            {
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "user_agent": request.headers.get("user-agent", ""),
            }
        )
    if request.url.path.startswith("/bff/v13"):
        V13_ROUTE_LOG.append(
            {
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "user_agent": request.headers.get("user-agent", ""),
            }
        )
    if request.url.path.startswith("/bff/v14"):
        V14_ROUTE_LOG.append(
            {
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "user_agent": request.headers.get("user-agent", ""),
            }
        )
    if request.url.path.startswith("/bff/v15"):
        V15_ROUTE_LOG.append(
            {
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "user_agent": request.headers.get("user-agent", ""),
            }
        )
    if request.url.path.startswith("/bff/pv16"):
        PV16_ROUTE_LOG.append(
            {
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "user_agent": request.headers.get("user-agent", ""),
            }
        )
    if request.url.path.startswith("/bff/pv18"):
        PV18_ROUTE_LOG.append(
            {
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "user_agent": request.headers.get("user-agent", ""),
            }
        )
    return response


@app.get("/__test/health")
async def test_health() -> dict[str, Any]:
    """Return seeded fixture ids for the Playwright harness."""
    return {
        "status": "ok",
        "workflow_instance_id": SEEDED["instance"]["workflow_instance_id"],
        "approval_id": SEEDED["approval"]["approval_id"],
        "workflow_template_id": SEEDED["template"]["workflow_template_id"],
        "patch_id": SEEDED["patch"]["workflow_patch_id"],
    }


@app.post("/__test/v12/route-log/clear")
async def clear_v12_route_log() -> dict[str, Any]:
    """Clear V12 route log before a browser acceptance run."""
    V12_ROUTE_LOG.clear()
    return {"status": "cleared"}


@app.get("/__test/v12/route-log")
async def get_v12_route_log() -> dict[str, Any]:
    """Return V12 route log captured by the BFF smoke server."""
    return {
        "schema_version": "v12.current_stage_route_log.v1",
        "status": "PASS",
        "routes": V12_ROUTE_LOG,
        "forbidden_matches": [
            entry
            for entry in V12_ROUTE_LOG
            if "/v1/rpc" in entry["path"] or "/v1/events/subscribe" in entry["path"] or "/v1/internal" in entry["path"]
        ],
    }


@app.post("/__test/v13/route-log/clear")
async def clear_v13_route_log() -> dict[str, Any]:
    """Clear V13 route log before a browser acceptance run."""
    V13_ROUTE_LOG.clear()
    return {"status": "cleared"}


@app.get("/__test/v13/route-log")
async def get_v13_route_log() -> dict[str, Any]:
    """Return V13 route log captured by the BFF smoke server."""
    return {
        "schema_version": "v13.studio_route_log.v1",
        "status": "PASS",
        "routes": V13_ROUTE_LOG,
        "forbidden_matches": [
            entry
            for entry in V13_ROUTE_LOG
            if "/v1/rpc" in entry["path"] or "/v1/events/subscribe" in entry["path"] or "/v1/internal" in entry["path"]
        ],
    }


@app.post("/__test/v14/route-log/clear")
async def clear_v14_route_log() -> dict[str, Any]:
    """Clear V14 route log before browser acceptance runs."""
    V14_ROUTE_LOG.clear()
    return {"status": "cleared"}


@app.get("/__test/v14/route-log")
async def get_v14_route_log() -> dict[str, Any]:
    """Return V14 route log captured by the BFF smoke server."""
    return {
        "schema_version": "v14.extension_route_log.v1",
        "status": "PASS",
        "routes": V14_ROUTE_LOG,
        "forbidden_matches": [
            entry
            for entry in V14_ROUTE_LOG
            if "/v1/rpc" in entry["path"] or "/v1/events/subscribe" in entry["path"] or "/v1/internal" in entry["path"]
        ],
    }


@app.post("/__test/v15/route-log/clear")
async def clear_v15_route_log() -> dict[str, Any]:
    """Clear V15 route log before browser acceptance runs."""
    V15_ROUTE_LOG.clear()
    return {"status": "cleared"}


@app.get("/__test/v15/route-log")
async def get_v15_route_log() -> dict[str, Any]:
    """Return V15 route log captured by the BFF smoke server."""
    return {
        "schema_version": "v15.observability_route_log.v1",
        "status": "PASS",
        "routes": V15_ROUTE_LOG,
        "forbidden_matches": [
            entry
            for entry in V15_ROUTE_LOG
            if "/v1/rpc" in entry["path"] or "/v1/events/subscribe" in entry["path"] or "/v1/internal" in entry["path"]
        ],
    }


@app.post("/__test/pv16/route-log/clear")
async def clear_pv16_route_log() -> dict[str, Any]:
    """Clear PV16 route log before product-runtime hardening acceptance runs."""
    PV16_ROUTE_LOG.clear()
    return {"status": "cleared"}


@app.get("/__test/pv16/route-log")
async def get_pv16_route_log() -> dict[str, Any]:
    """Return PV16 route log captured by the BFF smoke server."""
    return {
        "schema_version": "pv16.product_runtime_route_log.v1",
        "status": "PASS",
        "routes": PV16_ROUTE_LOG,
        "forbidden_matches": [
            entry
            for entry in PV16_ROUTE_LOG
            if "/v1/rpc" in entry["path"]
            or "/internal/runtime" in entry["path"]
            or "/runtime/store" in entry["path"]
            or "/api/runtime" in entry["path"]
            or "/debug/runtime" in entry["path"]
        ],
    }


@app.post("/__test/pv18/route-log/clear")
async def clear_pv18_route_log() -> dict[str, Any]:
    """Clear PV18 route log before Knowledge OPC acceptance runs."""
    PV18_ROUTE_LOG.clear()
    return {"status": "cleared"}


@app.get("/__test/pv18/route-log")
async def get_pv18_route_log() -> dict[str, Any]:
    """Return PV18 route log captured by the BFF smoke server."""
    return {
        "schema_version": "pv18.knowledge_opc_route_log.v1",
        "status": "PASS",
        "routes": PV18_ROUTE_LOG,
        "forbidden_matches": [
            entry
            for entry in PV18_ROUTE_LOG
            if "/v1/rpc" in entry["path"]
            or "/internal/runtime" in entry["path"]
            or "/runtime/store" in entry["path"]
            or "/api/runtime" in entry["path"]
            or "/debug/runtime" in entry["path"]
            or "data_service_mcp/internal" in entry["path"]
        ],
    }


@app.get("/bff/v12/system/health")
async def v12_system_health() -> dict[str, Any]:
    """Return V12 BFF health for the read-only workbench acceptance path."""
    return {
        "schema_version": "v12.system_health.v1",
        "status": "ok",
        "bff_backed": True,
        "runtime_backed": False,
        "evidence_scope": "browser_e2e",
        "created_at": "2026-06-23T00:00:00Z",
    }


@app.get("/bff/v12/workspaces")
async def v12_workspaces() -> dict[str, Any]:
    """Return V12 workspace inventory from a BFF-shaped route."""
    return {
        "schema_version": "v12.workspace_list.v1",
        "workspaces": [V12_WORKSPACE["workspace"]],
        "created_at": "2026-06-23T00:00:00Z",
    }


@app.get("/bff/v12/workspaces/{workspace_id}/projects")
async def v12_workspace_projects(workspace_id: str) -> JSONResponse:
    """Return projects for a V12 workspace, denying wrong workspace scope."""
    if workspace_id != V12_WORKSPACE["workspace"]["workspace_id"]:
        return JSONResponse({"error": "WORKSPACE_NOT_FOUND", "workspace_id": workspace_id}, status_code=404)
    return JSONResponse(
        {
            "schema_version": "v12.project_list.v1",
            "workspace_id": workspace_id,
            "projects": [V12_WORKSPACE["project"]],
            "created_at": "2026-06-23T00:00:00Z",
        }
    )


@app.get("/bff/v12/projects/{project_id}/apps")
async def v12_project_apps(project_id: str) -> JSONResponse:
    """Return apps for a V12 project, denying wrong project scope."""
    if project_id != V12_WORKSPACE["project"]["project_id"]:
        return JSONResponse({"error": "PROJECT_NOT_FOUND", "project_id": project_id}, status_code=404)
    return JSONResponse(
        {
            "schema_version": "v12.app_list.v1",
            "project_id": project_id,
            "apps": [V12_WORKSPACE["app"]],
            "created_at": "2026-06-23T00:00:00Z",
        }
    )


@app.get("/bff/v12/apps/{app_id}/station-agents")
async def v12_station_agents(app_id: str) -> JSONResponse:
    """Return station Agent profiles for the V12 read-only workbench."""
    if app_id != V12_WORKSPACE["app"]["app_id"]:
        return JSONResponse({"error": "APP_NOT_FOUND", "app_id": app_id}, status_code=404)
    return JSONResponse(
        {
            "schema_version": "v12.station_agent_list.v1",
            "app_id": app_id,
            "agents": [
                {
                    "agent_profile_id": "agent-v12-quality-reviewer-real",
                    "station_id": "quality_check",
                    "role": "reviewer",
                    "goal": "检查总结质量并生成可审计 quality report",
                    "memory_policy_ref": "memory-v12-quality-agent-redacted",
                    "model_profile_ref": "provider_ref:minimax-or-deepseek-redacted",
                    "tool_binding_refs": ["tool:quality.review"],
                    "skill_binding_refs": ["skill:markdown.summary"],
                    "mcp_binding_refs": ["mcp:readonly-docs"],
                    "credential_ref_policy": "redacted_refs_only",
                    "audit_ref": "audit://v12/current-stage/agent-quality-reviewer",
                    "created_at": "2026-06-23T00:00:00Z",
                }
            ],
            "created_at": "2026-06-23T00:00:00Z",
        }
    )


@app.get("/bff/v12/apps/{app_id}/canvas")
async def v12_canvas(app_id: str) -> JSONResponse:
    """Return V12 CanvasReadModel through the BFF boundary."""
    if app_id != V12_WORKSPACE["app"]["app_id"]:
        return JSONResponse({"error": "APP_NOT_FOUND", "app_id": app_id}, status_code=404)
    return JSONResponse(V12_CANVAS)


@app.get("/bff/v12/canvas/nodes/{node_ref}/inspector")
async def v12_canvas_inspector(node_ref: str) -> JSONResponse:
    """Return selected-node inspector projection through the BFF boundary."""
    if node_ref != V12_INSPECTOR["selected_node_ref"]:
        return JSONResponse({"error": "NODE_NOT_FOUND", "node_ref": node_ref}, status_code=404)
    return JSONResponse(V12_INSPECTOR)


@app.get("/bff/v12/apps/{app_id}/workbench/conversations")
async def v12_workbench_conversations(app_id: str) -> JSONResponse:
    """Return V12 workbench conversation and proposal-only timeline."""
    if app_id != V12_WORKSPACE["app"]["app_id"]:
        return JSONResponse({"error": "APP_NOT_FOUND", "app_id": app_id}, status_code=404)
    return JSONResponse(
        {
            "schema_version": "v12.workbench_conversation_list.v1",
            "app_id": app_id,
            "conversations": [V12_WORKBENCH_CONVERSATION],
            "proposal_timeline": V12_PROPOSAL_TIMELINE,
            "created_at": "2026-06-23T00:00:00Z",
        }
    )


@app.post("/bff/v12/workbench/messages")
async def v12_workbench_messages(request: Request) -> JSONResponse:
    """Accept a V12 goal message and return a proposal-only handoff ref."""
    body = await request.json()
    return JSONResponse(
        {
            "schema_version": "v12.workbench_message_result.v1",
            "status": "proposal_ready",
            "conversation_id": V12_WORKBENCH_CONVERSATION["conversation_id"],
            "redacted_text_ref": "text_ref:v12-user-message-redacted",
            "received_goal_summary": body.get("goal_summary", V12_WORKBENCH_CONVERSATION["goal_summary"]),
            "proposal_timeline": V12_PROPOSAL_TIMELINE,
            "workflow_diff": V12_WORKFLOW_DIFF,
            "runtime_backed": False,
            "audit_ref": "audit://v12/current-stage/workbench-message",
        }
    )


@app.post("/bff/v12/workbench/proposals/{proposal_id}/revise")
async def v12_revise_proposal(proposal_id: str) -> JSONResponse:
    """Return a bounded revise decision without applying workflow changes."""
    if proposal_id != V12_WORKFLOW_DIFF["proposal_id"]:
        return JSONResponse({"error": "PROPOSAL_NOT_FOUND", "proposal_id": proposal_id}, status_code=404)
    return JSONResponse(
        {
            "schema_version": "v12.proposal_decision.v1",
            "proposal_id": proposal_id,
            "decision": "revised",
            "runtime_backed": False,
            "publish_or_run_started": False,
            "audit_ref": "audit://v12/current-stage/proposal-revise",
        }
    )


@app.post("/bff/v12/workbench/proposals/{proposal_id}/reject")
async def v12_reject_proposal(proposal_id: str) -> JSONResponse:
    """Return a bounded reject decision without applying workflow changes."""
    if proposal_id != V12_WORKFLOW_DIFF["proposal_id"]:
        return JSONResponse({"error": "PROPOSAL_NOT_FOUND", "proposal_id": proposal_id}, status_code=404)
    return JSONResponse(
        {
            "schema_version": "v12.proposal_decision.v1",
            "proposal_id": proposal_id,
            "decision": "rejected",
            "runtime_backed": False,
            "publish_or_run_started": False,
            "audit_ref": "audit://v12/current-stage/proposal-reject",
        }
    )


@app.post("/bff/v12/workbench/proposals/{proposal_id}/confirm-handoff")
async def v12_confirm_handoff(proposal_id: str) -> JSONResponse:
    """Return governed handoff evidence only; do not publish or run."""
    if proposal_id != V12_WORKFLOW_DIFF["proposal_id"]:
        return JSONResponse({"error": "PROPOSAL_NOT_FOUND", "proposal_id": proposal_id}, status_code=404)
    return JSONResponse(
        {
            "schema_version": "v12.proposal_handoff.v1",
            "proposal_id": proposal_id,
            "handoff_state": "handoff_ready",
            "handoff_ref": "handoff:v12-workflowdiff-readonly-review",
            "runtime_backed": False,
            "publish_or_run_started": False,
            "audit_ref": "audit://v12/current-stage/confirm-handoff",
        }
    )


@app.get("/bff/v12/workflow-diff/{proposal_id}")
async def v12_workflow_diff(proposal_id: str) -> JSONResponse:
    """Return bounded WorkflowDiff proposal ref for V12 review."""
    if proposal_id != V12_WORKFLOW_DIFF["proposal_id"]:
        return JSONResponse({"error": "PROPOSAL_NOT_FOUND", "proposal_id": proposal_id}, status_code=404)
    return JSONResponse(V12_WORKFLOW_DIFF)


@app.get("/bff/v12/apps/{app_id}/interaction-trace")
async def v12_interaction_trace(app_id: str) -> JSONResponse:
    """Return V12 interaction-depth trace fixtures for acceptance evidence."""
    if app_id != V12_WORKSPACE["app"]["app_id"]:
        return JSONResponse({"error": "APP_NOT_FOUND", "app_id": app_id}, status_code=404)
    return JSONResponse(V12_INTERACTION_TRACE)


@app.get("/bff/v13/system/health")
async def v13_system_health() -> dict[str, Any]:
    """Return V13 BFF health for the editable Studio pilot acceptance path."""
    return {
        "schema_version": "v13.system_health.v1",
        "status": "ok",
        "bff_backed": True,
        "runtime_backed": False,
        "evidence_scope": "browser_e2e",
        "created_at": "2026-06-24T00:00:00Z",
    }


@app.get("/bff/v13/workflows/{workflow_id}/graph")
async def v13_workflow_graph(workflow_id: str) -> JSONResponse:
    """Return the V13 pilot WorkflowSpecGraph through the BFF boundary."""
    if workflow_id != V13_WORKFLOW_ID:
        return JSONResponse({"error": "WORKFLOW_NOT_FOUND", "workflow_id": workflow_id}, status_code=404)
    return JSONResponse(copy.deepcopy(V13_GRAPH))


@app.post("/bff/v13/workflows/{workflow_id}/graph/validate")
async def v13_validate_workflow_graph(workflow_id: str, request: Request) -> JSONResponse:
    """Validate a V13 pilot WorkflowSpecGraph draft without applying it."""
    if workflow_id != V13_WORKFLOW_ID:
        return JSONResponse({"error": "WORKFLOW_NOT_FOUND", "workflow_id": workflow_id}, status_code=404)
    body = await request.json()
    graph = body.get("graph", body)
    return JSONResponse(validate_v13_graph(graph))


@app.post("/bff/v13/workflows/{workflow_id}/diff")
async def v13_workflow_diff_from_graph(workflow_id: str, request: Request) -> JSONResponse:
    """Create a bounded WorkflowDiff proposal from a local graph draft."""
    if workflow_id != V13_WORKFLOW_ID:
        return JSONResponse({"error": "WORKFLOW_NOT_FOUND", "workflow_id": workflow_id}, status_code=404)
    body = await request.json()
    graph = body.get("graph", body)
    validation = validate_v13_graph(graph)
    proposal = copy.deepcopy(V13_WORKFLOW_DIFF)
    proposal["validation_status"] = validation["status"]
    proposal["changed_node_refs"] = [
        node.get("node_id")
        for node in graph.get("nodes", [])
        if node.get("node_id") not in {baseline.get("node_id") for baseline in V13_GRAPH["nodes"]}
        or node.get("status") != "configured"
    ][:8] or V13_WORKFLOW_DIFF["changed_node_refs"]
    proposal["changed_edge_refs"] = [
        edge.get("edge_id")
        for edge in graph.get("edges", [])
        if edge.get("edge_id") not in {baseline.get("edge_id") for baseline in V13_GRAPH["edges"]}
    ][:8] or V13_WORKFLOW_DIFF["changed_edge_refs"]
    proposal["graph_validation"] = validation
    return JSONResponse(proposal)


@app.get("/bff/v13/workflow-diff/{proposal_id}")
async def v13_workflow_diff(proposal_id: str) -> JSONResponse:
    """Return the bounded V13 WorkflowDiff proposal."""
    if proposal_id != V13_WORKFLOW_DIFF["proposal_id"]:
        return JSONResponse({"error": "PROPOSAL_NOT_FOUND", "proposal_id": proposal_id}, status_code=404)
    return JSONResponse(copy.deepcopy(V13_WORKFLOW_DIFF))


@app.post("/bff/v13/workflow-diff/{proposal_id}/revise")
async def v13_revise_workflow_diff(proposal_id: str) -> JSONResponse:
    """Return a revise decision without publishing or running the workflow."""
    if proposal_id != V13_WORKFLOW_DIFF["proposal_id"]:
        return JSONResponse({"error": "PROPOSAL_NOT_FOUND", "proposal_id": proposal_id}, status_code=404)
    return JSONResponse(
        {
            "schema_version": "v13.workflow_diff_decision.v1",
            "proposal_id": proposal_id,
            "decision": "revised",
            "runtime_backed": False,
            "publish_or_run_started": False,
            "audit_ref": "audit://v13/studio-pilot/diff-revise",
        }
    )


@app.post("/bff/v13/workflow-diff/{proposal_id}/reject")
async def v13_reject_workflow_diff(proposal_id: str) -> JSONResponse:
    """Return a reject decision without publishing or running the workflow."""
    if proposal_id != V13_WORKFLOW_DIFF["proposal_id"]:
        return JSONResponse({"error": "PROPOSAL_NOT_FOUND", "proposal_id": proposal_id}, status_code=404)
    return JSONResponse(
        {
            "schema_version": "v13.workflow_diff_decision.v1",
            "proposal_id": proposal_id,
            "decision": "rejected",
            "runtime_backed": False,
            "publish_or_run_started": False,
            "audit_ref": "audit://v13/studio-pilot/diff-reject",
        }
    )


@app.post("/bff/v13/workflow-diff/{proposal_id}/confirm-publish-handoff")
async def v13_confirm_publish_handoff(proposal_id: str) -> JSONResponse:
    """Return governed publish handoff evidence only; do not publish or run."""
    if proposal_id != V13_WORKFLOW_DIFF["proposal_id"]:
        return JSONResponse({"error": "PROPOSAL_NOT_FOUND", "proposal_id": proposal_id}, status_code=404)
    return JSONResponse(
        {
            "schema_version": "v13.workflow_diff_handoff.v1",
            "proposal_id": proposal_id,
            "handoff_state": "handoff_ready",
            "handoff_ref": "handoff:v13-workflowdiff-publish-review",
            "runtime_backed": False,
            "publish_or_run_started": False,
            "audit_ref": "audit://v13/studio-pilot/confirm-publish-handoff",
        }
    )


@app.get("/bff/v13/studio/node-inspector/{node_id}")
async def v13_node_inspector(node_id: str) -> JSONResponse:
    """Return a V13 editable Studio node inspector DTO through the BFF boundary."""
    inspector = V13_INSPECTORS.get(node_id)
    if inspector is None:
        return JSONResponse({"error": "NODE_NOT_FOUND", "node_id": node_id}, status_code=404)
    return JSONResponse(copy.deepcopy(inspector))


@app.get("/bff/v14/system/health")
async def v14_system_health() -> dict[str, Any]:
    """Return V14 BFF health for governed extension ecosystem acceptance."""
    return {
        "schema_version": "v14.system_health.v1",
        "status": "ok",
        "bff_backed": True,
        "runtime_backed": False,
        "evidence_scope": "browser_e2e",
        "created_at": "2026-06-24T00:00:00Z",
    }


@app.get("/bff/v14/extensions/packages")
async def v14_extension_packages() -> dict[str, Any]:
    """Return the local governed extension package registry."""
    return {
        "schema_version": "v14.extension_package_registry.v1",
        "workspace_id": V14_SCOPE["workspace_id"],
        "project_id": V14_SCOPE["project_id"],
        "app_id": V14_SCOPE["app_id"],
        "packages": list(copy.deepcopy(V14_PACKAGES).values()),
        "runtime_backed": False,
        "audit_ref": "audit://v14/extension/package-registry",
        "created_at": "2026-06-24T00:00:00Z",
    }


@app.get("/bff/v14/extensions/packages/{package_id}")
async def v14_extension_package_detail(package_id: str) -> JSONResponse:
    """Return a single V14 extension package manifest."""
    package = V14_PACKAGES.get(package_id)
    if package is None:
        return JSONResponse({"error": "PACKAGE_NOT_FOUND", "package_id": package_id}, status_code=404)
    return JSONResponse(copy.deepcopy(package))


@app.post("/bff/v14/extensions/packages/{package_id}/compatibility-check")
async def v14_extension_compatibility_check(package_id: str) -> JSONResponse:
    """Return a compatibility decision without installing or executing the package."""
    decision = build_v14_compatibility_decision(package_id)
    status_code = 200 if package_id in V14_PACKAGES else 404
    return JSONResponse(decision, status_code=status_code)


@app.post("/bff/v14/extensions/packages/{package_id}/install-decision")
async def v14_extension_install_decision(package_id: str, request: Request) -> JSONResponse:
    """Return an install decision for an approved package without runtime execution."""
    body = await request.json()
    decision = build_v14_compatibility_decision(package_id)
    if not decision["compatible"]:
        return JSONResponse(
            {
                "schema_version": "v14.extension_install_decision.v1",
                "package_id": package_id,
                "decision": "denied",
                "scope": body.get("scope", V14_SCOPE),
                "reasons": decision["reasons"],
                "runtime_backed": False,
                "audit_ref": decision["audit_ref"],
                "created_at": "2026-06-24T00:00:00Z",
            },
            status_code=403,
        )
    return JSONResponse(
        {
            "schema_version": "v14.extension_install_decision.v1",
            "package_id": package_id,
            "decision": "approved_for_scoped_activation",
            "scope": body.get("scope", V14_SCOPE),
            "requires_user_confirmation": True,
            "runtime_backed": False,
            "audit_ref": "audit://v14/extension/install-quality-review",
            "created_at": "2026-06-24T00:00:00Z",
        }
    )


@app.post("/bff/v14/extensions/packages/{package_id}/activate")
async def v14_extension_activate(package_id: str, request: Request) -> JSONResponse:
    """Activate an approved package only for the submitted scope."""
    body = await request.json()
    decision = build_v14_compatibility_decision(package_id)
    if not decision["compatible"]:
        return JSONResponse(build_v14_unsafe_denial(), status_code=403)
    activation = copy.deepcopy(V14_ACTIVATION_DECISION)
    activation["scope"] = body.get("scope", V14_SCOPE)
    return JSONResponse(activation)


@app.get("/bff/v14/agents/{agent_id}/capability-bindings")
async def v14_agent_capability_bindings(agent_id: str) -> JSONResponse:
    """Return scoped capabilities for a V14 Agent/Station inspector."""
    if agent_id != V14_AGENT_ID:
        return JSONResponse({"error": "AGENT_NOT_FOUND", "agent_id": agent_id}, status_code=404)
    return JSONResponse(copy.deepcopy(V14_SCOPED_BINDING))


@app.post("/bff/v14/agents/{agent_id}/capability-bindings")
async def v14_agent_capability_binding_decision(agent_id: str, request: Request) -> JSONResponse:
    """Bind an approved capability to a selected Agent/Station scope."""
    if agent_id != V14_AGENT_ID:
        return JSONResponse({"error": "AGENT_NOT_FOUND", "agent_id": agent_id}, status_code=404)
    body = await request.json()
    binding = copy.deepcopy(V14_SCOPED_BINDING)
    binding["scope"] = body.get("scope", V14_SCOPE)
    binding["activation_ref"] = body.get("activation_ref", "activation:v14-quality-review-scope")
    return JSONResponse(binding)


@app.post("/bff/v14/extensions/packages/{package_id}/unsafe-denial")
async def v14_extension_unsafe_denial(package_id: str) -> JSONResponse:
    """Return a policy denial for unsafe packages."""
    if package_id != V14_UNSAFE_PACKAGE_ID:
        return JSONResponse(
            {
                "schema_version": "v14.unsafe_package_denial.v1",
                "package_id": package_id,
                "status": "not_applicable",
                "denial_reason": "该扩展包未触发 unsafe denial 场景",
                "blocked_fields": [],
                "blocked_permissions": [],
                "active_capability_created": False,
                "runtime_backed": False,
                "audit_ref": f"audit://v14/extension/unsafe-denial/{package_id}",
                "created_at": "2026-06-24T00:00:00Z",
            }
        )
    return JSONResponse(build_v14_unsafe_denial())


@app.get("/bff/v14/extensions/audit/{audit_ref:path}")
async def v14_extension_audit(audit_ref: str) -> dict[str, Any]:
    """Return redacted policy audit details for V14 extension review."""
    return {
        "schema_version": "v14.extension_policy_audit_ref.v1",
        "audit_ref": f"audit://{audit_ref}" if not audit_ref.startswith("audit://") else audit_ref,
        "status": "recorded",
        "policy_refs": ["policy:v14-known-permissions", "policy:v14-scoped-activation", "policy:v14-redacted-config"],
        "redaction_status": "PASS",
        "runtime_backed": False,
        "created_at": "2026-06-24T00:00:00Z",
    }


@app.get("/bff/v15/system/health")
async def v15_system_health() -> dict[str, Any]:
    """Return V15 BFF health for observability and deployment acceptance."""
    return {
        "schema_version": "v15.system_health.v1",
        "status": "ok",
        "bff_backed": True,
        "runtime_backed": False,
        "evidence_scope": "browser_e2e",
        "dependencies": {
            "v12": "PASS",
            "v13": "PASS",
            "v14": "PASS",
        },
        "created_at": "2026-06-24T00:00:00Z",
    }


@app.get("/bff/v15/observability/trace-timeline")
async def v15_trace_timeline() -> dict[str, Any]:
    """Return read-only V15 trace timeline evidence."""
    return copy.deepcopy(V15_TRACE_TIMELINE)


@app.get("/bff/v15/observability/metrics-snapshot")
async def v15_metrics_snapshot() -> dict[str, Any]:
    """Return read-only V15 metrics snapshot evidence."""
    return copy.deepcopy(V15_METRICS_SNAPSHOT)


@app.get("/bff/v15/observability/audit-export")
async def v15_audit_export() -> dict[str, Any]:
    """Return redacted V15 audit export package evidence."""
    return copy.deepcopy(V15_AUDIT_EXPORT)


@app.get("/bff/v15/observability/incidents")
async def v15_incidents() -> dict[str, Any]:
    """Return read-only V15 incident timeline evidence."""
    return copy.deepcopy(V15_INCIDENT_TIMELINE)


@app.get("/bff/v15/deployment/profile")
async def v15_deployment_profile() -> dict[str, Any]:
    """Return the bounded local deployment profile for V15 smoke."""
    return copy.deepcopy(V15_DEPLOYMENT_PROFILE)


@app.post("/bff/v15/deployment/health-check")
async def v15_deployment_health_check() -> dict[str, Any]:
    """Return local health diagnostics without claiming production readiness."""
    return {
        "schema_version": "v15.health_check_result.v1",
        "workspace_id": V12_WORKSPACE["workspace"]["workspace_id"],
        "project_id": V12_WORKSPACE["project"]["project_id"],
        "app_id": V12_WORKSPACE["app"]["app_id"],
        "run_ref": V15_RUN_REF,
        "request_id": V15_REQUEST_ID,
        "correlation_id": V15_CORRELATION_ID,
        "evidence_scope": "browser_e2e",
        "status": "PASS",
        "checks": [
            {"check_id": "bff_health", "status": "PASS", "output": "GET /bff/v15/system/health -> 200"},
            {"check_id": "frontend_api_config", "status": "PASS", "output": "VITE_BFF_PROXY_TARGET uses local test-only BFF"},
            {"check_id": "dependency_evidence", "status": "PASS", "output": "V12/V13/V14 evidence reports present in repo"},
        ],
        "not_production_ga": True,
        "runtime_backed": False,
        "audit_ref": "audit://v15/deployment/health-check",
        "created_at": "2026-06-24T00:00:00Z",
    }


@app.post("/bff/v15/deployment/smoke")
async def v15_deployment_smoke() -> dict[str, Any]:
    """Return bounded local smoke output with concrete command text."""
    return {
        "schema_version": "v15.deployment_smoke_result.v1",
        "workspace_id": V12_WORKSPACE["workspace"]["workspace_id"],
        "project_id": V12_WORKSPACE["project"]["project_id"],
        "app_id": V12_WORKSPACE["app"]["app_id"],
        "run_ref": V15_RUN_REF,
        "request_id": V15_REQUEST_ID,
        "correlation_id": V15_CORRELATION_ID,
        "evidence_scope": "browser_e2e",
        "status": "PASS",
        "command": "python3 tools/v15/run_v15_observability_deployment_acceptance.py",
        "command_output": [
            "GET http://127.0.0.1:18044/bff/v15/system/health -> 200",
            "GET http://127.0.0.1:4178/?studio=v15-observability-deployment -> 200",
            "V15 bounded local smoke completed with test-only BFF and browser preview",
        ],
        "rollback_notes": V15_DEPLOYMENT_PROFILE["rollback_notes"],
        "not_production_ga": True,
        "runtime_backed": False,
        "audit_ref": "audit://v15/deployment/smoke",
        "created_at": "2026-06-24T00:00:00Z",
    }


@app.get("/bff/v15/final-scenario-matrix")
async def v15_final_scenario_matrix() -> dict[str, Any]:
    """Return final V12-V15 scenario matrix evidence."""
    return copy.deepcopy(V15_FINAL_SCENARIO_MATRIX)


@app.get("/bff/pv16/system/health")
async def pv16_system_health() -> dict[str, Any]:
    """Return PV16 BFF health for product-runtime hardening acceptance."""
    return {
        "schema_version": "pv16.system_health.v1",
        "status": "ok",
        "bff_backed": True,
        "runtime_gateway_available": True,
        "evidence_scope": "browser_e2e",
        "dependencies": {
            "v12": "PASS",
            "v13": "PASS",
            "v14": "PASS",
            "v15": "PASS",
        },
        "created_at": PV16_CREATED_AT,
    }


@app.get("/bff/pv16/product-runtime/state")
async def pv16_product_runtime_state() -> dict[str, Any]:
    """Return current PV16 product entity and journey state."""
    return {
        "schema_version": "pv16.product_runtime_state.v1",
        "entities": copy.deepcopy(PV16_ENTITY_STATE),
        "workflow_spec": copy.deepcopy(PV16_WORKFLOW_SPEC),
        "deployment_profile": copy.deepcopy(PV16_DEPLOYMENT_PROFILE),
        "journey": copy.deepcopy(PV16_JOURNEY),
        "created_at": PV16_CREATED_AT,
    }


@app.post("/bff/pv16/entities/mutate")
async def pv16_mutate_entities(request: Request) -> JSONResponse:
    """Apply a local durable product-entity mutation through the BFF boundary."""
    body = await request.json()
    scope = body.get("scope", PV16_SCOPE)
    policy_ref = body.get("policy_ref")
    if scope.get("workspace_id") != PV16_SCOPE["workspace_id"]:
        return JSONResponse(
            {
                "schema_version": "pv16.entity_mutation_result.v1",
                "status": "DENIED",
                "reason": "workspace ownership mismatch",
                "ownership_result": "FAIL",
                "policy_result": "BLOCKED",
                "audit_ref": "audit://pv16/entity/denied/ownership",
                "created_at": PV16_CREATED_AT,
            },
            status_code=403,
        )
    if not policy_ref:
        return JSONResponse(
            {
                "schema_version": "pv16.entity_mutation_result.v1",
                "status": "DENIED",
                "reason": "policy_ref is required for durable mutation",
                "ownership_result": "PASS",
                "policy_result": "FAIL",
                "audit_ref": "audit://pv16/entity/denied/policy",
                "created_at": PV16_CREATED_AT,
            },
            status_code=400,
        )

    mutation = body.get("mutation", {})
    display_name = str(mutation.get("station_agent_display_name") or PV16_ENTITY_STATE["station_agent"]["display_name"])
    goal = str(mutation.get("goal") or PV16_ENTITY_STATE["station_agent"]["goal"])
    PV16_ENTITY_STATE["station_agent"]["display_name"] = display_name
    PV16_ENTITY_STATE["station_agent"]["goal"] = goal
    PV16_ENTITY_STATE["station_agent"]["audit_ref"] = "audit://pv16/entity/station-agent/mutation-pass"
    PV16_ENTITY_STATE["last_mutation_ref"] = "mutation://pv16/entity/station-agent/update-001"
    PV16_ENTITY_STATE["policy_ref"] = policy_ref
    return JSONResponse(
        {
            "schema_version": "pv16.entity_mutation_result.v1",
            "status": "PASS",
            "durable_entity_mutation": True,
            "mutated_entity_refs": [
                PV16_ENTITY_STATE["workspace"]["audit_ref"],
                PV16_ENTITY_STATE["project"]["audit_ref"],
                PV16_ENTITY_STATE["app"]["audit_ref"],
                PV16_ENTITY_STATE["station_agent"]["audit_ref"],
            ],
            "entities": copy.deepcopy(PV16_ENTITY_STATE),
            "ownership_result": "PASS",
            "policy_result": "PASS",
            "redaction_status": "PASS",
            "audit_ref": "audit://pv16/entity/mutation-pass",
            "created_at": PV16_CREATED_AT,
        }
    )


@app.post("/bff/pv16/entities/ownership-denial")
async def pv16_entity_ownership_denial() -> JSONResponse:
    """Return a deterministic ownership-denial fixture through the PV16 BFF."""
    return JSONResponse(
        {
            "schema_version": "pv16.entity_mutation_result.v1",
            "status": "DENIED",
            "reason": "workspace ownership mismatch",
            "ownership_result": "FAIL",
            "policy_result": "BLOCKED",
            "audit_ref": "audit://pv16/entity/denied/ownership",
            "created_at": PV16_CREATED_AT,
        },
        status_code=403,
    )


@app.get("/bff/pv16/workflow-spec")
async def pv16_workflow_spec() -> dict[str, Any]:
    """Return the confirmed WorkflowSpec handoff used by PV16 runtime pilot."""
    return copy.deepcopy(PV16_WORKFLOW_SPEC)


@app.post("/bff/pv16/runtime/confirm-run")
async def pv16_confirm_runtime_run() -> dict[str, Any]:
    """Confirm a local controlled runtime run and return runtime-backed refs."""
    workflow_status = await _workflow_status(SEEDED)
    run_ref = f"runtime-run:pv16:{workflow_status['workflow_instance_id']}"
    return {
        "schema_version": "pv16.runtime_run_inspect_report.v1",
        "status": "PASS",
        "run_ref": run_ref,
        "workflow_instance_id": workflow_status["workflow_instance_id"],
        "workflow_version_ref": workflow_status["workflow_version_id"],
        "runtime_backed": True,
        "runtime_status": workflow_status["runtime_status"],
        "runtime_event_refs": [
            f"gateway-event://{workflow_status['workflow_instance_id']}/turn.started",
            f"gateway-event://{workflow_status['workflow_instance_id']}/turn.completed",
        ],
        "trace_refs": [f"trace://pv16/runtime/{workflow_status['workflow_instance_id']}"],
        "artifact_refs": [f"artifact://pv16/runtime/output-{workflow_status['output_artifact_count']}"],
        "quality_refs": ["quality://pv16/runtime/local-smoke"],
        "audit_ref": "audit://pv16/runtime/confirm-run",
        "created_at": PV16_CREATED_AT,
    }


@app.get("/bff/pv16/runtime/inspect/{run_ref:path}")
async def pv16_runtime_inspect(run_ref: str) -> dict[str, Any]:
    """Return runtime-backed run inspection details for a confirmed local run."""
    workflow_status = await _workflow_status(SEEDED)
    return {
        "schema_version": "pv16.runtime_inspection.v1",
        "status": "PASS",
        "run_ref": run_ref,
        "runtime_backed": True,
        "progress": [
            {"step": "workspace_loaded", "status": "PASS", "evidence_ref": "entity-crud-report.json"},
            {"step": "workflow_confirmed", "status": "PASS", "evidence_ref": PV16_WORKFLOW_SPEC["workflow_diff_ref"]},
            {"step": "runtime_events_collected", "status": "PASS", "evidence_ref": f"trace://pv16/runtime/{workflow_status['workflow_instance_id']}"},
            {"step": "artifact_refs_attached", "status": "PASS", "evidence_ref": f"artifact://pv16/runtime/output-{workflow_status['output_artifact_count']}"},
        ],
        "audit_ref": "audit://pv16/runtime/inspect",
        "created_at": PV16_CREATED_AT,
    }


@app.get("/bff/pv16/deployment/profile")
async def pv16_deployment_profile() -> dict[str, Any]:
    """Return the PV16 non-destructive deployment hardening profile."""
    return copy.deepcopy(PV16_DEPLOYMENT_PROFILE)


@app.post("/bff/pv16/deployment/hardening-smoke")
async def pv16_deployment_hardening_smoke() -> dict[str, Any]:
    """Return non-destructive local hardening smoke output."""
    return {
        "schema_version": "pv16.deployment_hardening_smoke.v1",
        "status": "PASS",
        "command": "COMMAND: python3 tools/post_v15/run_product_runtime_hardening_acceptance.py",
        "command_output": [
            "GET http://127.0.0.1:18040/bff/pv16/system/health -> 200",
            "GET http://127.0.0.1:4174/?studio=pv16-product-runtime-hardening -> 200",
            "health: PASS",
            "runtime_gateway: PASS",
            "redaction: PASS",
        ],
        "health_checks": [
            {"check_id": "bff_health", "status": "PASS", "output": "GET /bff/pv16/system/health -> 200"},
            {"check_id": "runtime_gateway", "status": "PASS", "output": "GatewayService local seeded workflow inspectable"},
            {"check_id": "frontend_route", "status": "PASS", "output": "PV16 product-runtime page loaded"},
            {"check_id": "redaction", "status": "PASS", "output": "Only redacted refs are exposed"},
        ],
        "rollback_notes": PV16_DEPLOYMENT_PROFILE["rollback_notes"],
        "not_production_ga": True,
        "audit_ref": "audit://pv16/deployment/hardening-smoke",
        "created_at": PV16_CREATED_AT,
    }


@app.get("/bff/pv16/product-runtime/journey")
async def pv16_product_runtime_journey() -> dict[str, Any]:
    """Return the PV16 setup-to-operations journey read model."""
    return copy.deepcopy(PV16_JOURNEY)


@app.get("/__test/simple-workflow/status")
async def simple_workflow_status() -> dict[str, Any]:
    """Return the dev/local simple workflow deployment and runtime state."""
    return await _workflow_status(SEEDED)


@app.post("/__test/simple-workflow/deploy")
async def deploy_simple_workflow() -> dict[str, Any]:
    """Seed an isolated dev/local workflow for visible acceptance tests."""
    seeded = await seed_reference_console(GATEWAY, template_id=f"visible_acceptance_{uuid4().hex[:8]}", scope=DEFAULT_SCOPE)
    return await _workflow_status(seeded)


async def _workflow_status(seeded: dict[str, Any]) -> dict[str, Any]:
    instance_id = seeded["instance"]["workflow_instance_id"]
    status = await rpc(GATEWAY, "workflow.instance.status", {"workflow_instance_id": instance_id, "scope": DEFAULT_SCOPE})
    board = await rpc(GATEWAY, "workflow.board.get", {"workflow_instance_id": instance_id, "scope": DEFAULT_SCOPE})
    completed_runs = [
        run
        for station in board["board"].get("stations", [])
        for run in station.get("runs", [])
        if run.get("status") == "completed"
    ]
    output_artifacts = [
        artifact_id
        for station in board["board"].get("stations", [])
        for run in station.get("runs", [])
        for artifact_id in run.get("output_artifact_ids", [])
    ]
    return {
        "status": "ok",
        "workflow_template_id": seeded["template"]["workflow_template_id"],
        "workflow_version_id": seeded["version"]["workflow_version_id"],
        "workflow_instance_id": instance_id,
        "runtime_status": status["status"]["status"],
        "station_count": len(board["board"].get("stations", [])),
        "completed_run_count": len(completed_runs),
        "output_artifact_count": len(output_artifacts),
    }


@app.post("/__test/emit-fake-status-event")
async def emit_fake_status_event(request: Request) -> JSONResponse:
    """Emit a controlled event whose status payload must not become UI truth."""
    body = await request.json()
    workflow_instance_id = str(body.get("workflow_instance_id") or SEEDED["instance"]["workflow_instance_id"])
    fake_status = str(body.get("status") or "forged_failed")
    event = GatewayEvent(
        type="workflow.context.updated",
        app_id="default",
        project_id=None,
        workspace_id=None,
        data={
            "workflow_instance_id": workflow_instance_id,
            "context_revision": body.get("context_revision") or 999,
            "status": fake_status,
            "source": "browser_smoke_fake_event",
        },
    )
    trace = GATEWAY.trace_store.record_event(event)
    GATEWAY.core_service.record_gateway_trace(trace)
    return JSONResponse({"status": "emitted", "workflow_instance_id": workflow_instance_id, "fake_status": fake_status})


@app.post("/__test/emit-fake-agent-event")
async def emit_fake_agent_event(request: Request) -> JSONResponse:
    """Emit a fake Agent payload that must only trigger UI refresh."""
    body = await request.json()
    workflow_instance_id = str(body.get("workflow_instance_id") or SEEDED["instance"]["workflow_instance_id"])
    event_type = str(body.get("type") or "agent.action_proposal.created")
    event = GatewayEvent(
        type=event_type,
        app_id="default",
        project_id=None,
        workspace_id=None,
        data={
            "workflow_instance_id": workflow_instance_id,
            "selected_proposal_id": "fake_proposal_from_event",
            "selected_patch_id": "fake_patch_from_event",
            "selected_evidence_id": "fake_evidence_from_event",
            "raw_trace_payload": "secret-token-value",
        },
    )
    trace = GATEWAY.trace_store.record_event(event)
    GATEWAY.core_service.record_gateway_trace(trace)
    return JSONResponse({"status": "emitted", "workflow_instance_id": workflow_instance_id, "event_type": event_type})


if __name__ == "__main__":
    port = int(os.environ.get("WORKFLOW_CONSOLE_BFF_PORT", "18040"))
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")
