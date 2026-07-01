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
