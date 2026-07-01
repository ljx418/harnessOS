"""V13 workflow platform baseline BFF route tests."""

from __future__ import annotations

from copy import deepcopy

from fastapi.testclient import TestClient

from apps.api import create_app
from v4_0_reference_support import SCOPE_QUERY, assert_no_forbidden_text, build_gateway


WORKFLOW_ID = "wf-v13-markdown-summary-studio-pilot"
DIFF_ID = "diff-v13-editable-studio-pilot-001"


def _client(monkeypatch, tmp_path) -> TestClient:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    return TestClient(create_app(gateway_service=service))


def test_v13_workflow_platform_design_baseline_routes(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)

    health = client.get(f"/bff/v13/system/health{SCOPE_QUERY}").json()
    assert health["schema_version"] == "v13.system_health.v1"
    assert health["bff_backed"] is True
    assert health["runtime_backed"] is False

    graph = client.get(f"/bff/v13/workflows/{WORKFLOW_ID}/graph{SCOPE_QUERY}").json()
    assert graph["schema_version"] == "v13.workflow_spec_graph.v1"
    assert graph["runtime_backed"] is False
    assert len(graph["nodes"]) >= 6
    assert graph["edges"]

    validation = client.post(f"/bff/v13/workflows/{WORKFLOW_ID}/graph/validate{SCOPE_QUERY}", json={"graph": graph}).json()
    assert validation["status"] == "PASS"
    assert validation["publish_or_run_started"] is False

    invalid_graph = deepcopy(graph)
    invalid_graph["edges"][0]["target_node_id"] = "missing_node"
    invalid = client.post(f"/bff/v13/workflows/{WORKFLOW_ID}/graph/validate{SCOPE_QUERY}", json={"graph": invalid_graph}).json()
    assert invalid["status"] == "FAIL"

    diff = client.post(f"/bff/v13/workflows/{WORKFLOW_ID}/diff{SCOPE_QUERY}", json={"graph": graph}).json()
    assert diff["schema_version"] == "v13.workflow_diff_proposal.v1"
    assert diff["runtime_backed"] is False
    assert diff["publish_or_run_started"] is False
    assert diff["confirmation_boundary"] == "handoff_only_no_publish_no_run"

    inspector = client.get(f"/bff/v13/studio/node-inspector/summary_agent{SCOPE_QUERY}").json()
    assert inspector["schema_version"] == "v13.studio_node_inspector.v1"
    assert inspector["runtime_backed"] is False

    handoff = client.post(f"/bff/v13/workflow-diff/{DIFF_ID}/confirm-publish-handoff{SCOPE_QUERY}", json={}).json()
    assert handoff["decision"] == "handoff_confirmed"
    assert handoff["handoff_ref"].startswith("handoff://v13/")
    assert handoff["runtime_backed"] is False
    assert handoff["publish_or_run_started"] is False
    assert_no_forbidden_text([health, graph, validation, invalid, diff, inspector, handoff])


def test_workflow_platform_wp_m5a_business_projection_routes(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)

    projection = client.get(f"/bff/workflow-platform/scenarios{SCOPE_QUERY}").json()
    assert projection["schema_version"] == "workflow_platform.scenario_projection.v1"
    assert projection["source"] == "bff_projection"
    assert projection["fallback_used"] is False
    assert projection["scenario_count"] == 3
    assert {item["scenario_id"] for item in projection["scenarios"]} == {"document_summary", "code_review", "meeting_brief"}
    assert projection["mock_reduction_boundary"]["scenarioData"] == "fallback_or_visual_reference_only"

    outputs = []
    for scenario_id in ["document_summary", "code_review", "meeting_brief"]:
        output = client.get(f"/bff/workflow-platform/scenarios/{scenario_id}/outputs{SCOPE_QUERY}").json()
        outputs.append(output)
        assert output["schema_version"] == "workflow_platform.business_output.v1"
        assert output["scenario_id"] == scenario_id
        assert output["status"] == "ready_for_human_review"
        assert output["output_summary"]["artifact_refs"]
        assert output["output_summary"]["human_review_ref"].startswith("human-review://wp-m5a/")
        assert set(output["evidence_refs"]) == {"artifact", "trace", "quality", "audit", "claim", "redaction"}
        assert all(output["evidence_refs"][key] for key in output["evidence_refs"])
        assert "not_production_ready" in output["non_claims"]
        assert "not_complete_workflow_studio_ga" in output["non_claims"]

    assert_no_forbidden_text([projection, *outputs])


def test_workflow_platform_wp_m6_to_m11_frontend_completion_facade_routes(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)

    data_source = client.get(f"/bff/workflow-platform/frontend-data-source-closure{SCOPE_QUERY}").json()
    assert data_source["schema_version"] == "workflow_platform.frontend_data_source_closure.v1"
    assert data_source["stage"] == "WP-M6"
    assert data_source["status"] == "PASS"
    assert data_source["normal_path_static_sources"] == 0
    assert {item["source_id"] for item in data_source["blocked_static_sources"]} >= {"scenarioData", "fallbackGraph", "static_timeline", "static_inspector", "proposal_only_chat"}
    assert all(item["normal_path_usage"] is False for item in data_source["blocked_static_sources"])

    artifacts = client.get(f"/bff/workflow-platform/artifacts{SCOPE_QUERY}").json()
    assert artifacts["schema_version"] == "workflow_platform.business_artifact_closure.v1"
    assert artifacts["stage"] == "WP-M9"
    assert artifacts["status"] == "PASS"
    assert {item["scenario_id"] for item in artifacts["artifacts"]} == {"document_summary", "code_review", "meeting_brief"}
    assert all(item["artifact_ref"].startswith("artifact://wp-m9/") for item in artifacts["artifacts"])
    assert all(item["human_review_refs"] for item in artifacts["artifacts"])

    quality = client.get(f"/bff/workflow-platform/quality-states{SCOPE_QUERY}").json()
    assert quality["schema_version"] == "workflow_platform.frontend_quality_state.v1"
    assert quality["stage"] == "WP-M10"
    assert quality["status"] == "PASS"
    assert {item["state_id"] for item in quality["states"]} >= {
        "loading",
        "empty",
        "error",
        "permission_denied",
        "bff_offline",
        "validation_failure",
        "human_reject",
        "cancel_retry",
    }

    claims = client.get(f"/bff/workflow-platform/claim-evidence-matrix{SCOPE_QUERY}").json()
    assert claims["schema_version"] == "workflow_platform.claim_evidence_matrix.v1"
    assert claims["stage"] == "WP-M11"
    assert claims["status"] == "PASS"
    assert claims["missing_evidence_blocks_pass"] is True
    assert {item["requirement_id"] for item in claims["requirements"]} == {f"WP-FR-{index}" for index in range(1, 21)}
    assert all(item["evidence_refs"] for item in claims["requirements"])

    assert_no_forbidden_text([data_source, artifacts, quality, claims])
