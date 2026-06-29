"""PV19 runtime-backed workflow platform BFF route tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from apps.api import create_app
from v4_0_reference_support import SCOPE_QUERY, assert_no_forbidden_text, build_gateway


def _client(monkeypatch, tmp_path) -> TestClient:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    return TestClient(create_app(gateway_service=service))


def test_pv19_runtime_workflow_platform_closed_loop(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)

    state = client.get(f"/bff/pv19/workbench/state{SCOPE_QUERY}").json()
    assert state["schema_version"] == "pv19.runtime_workflow_platform.v1"
    assert state["entry"]["route"] == "?studio=pv19-runtime-workflow-platform"
    workflow_id = state["workflow"]["workflow_template_id"]
    draft_revision = state["draft"]["revision"]

    graph = client.get(f"/bff/pv19/workflows/{workflow_id}/graph{SCOPE_QUERY}").json()
    assert graph["graph"]["nodes"]
    assert graph["graph"]["human_gate_nodes"] == ["human_quality_gate"]
    assert graph["platform_contract"]["core_customization_allowed"] is False

    validation = client.post(f"/bff/pv19/workflows/{workflow_id}/graph/validate{SCOPE_QUERY}", json={}).json()
    assert validation["status"] == "valid"
    assert validation["runtime_readiness"]["can_publish"] is True

    diff = client.post(f"/bff/pv19/workflows/{workflow_id}/diff{SCOPE_QUERY}", json={}).json()
    assert diff["workflow_diff"]["workflow_patch_id"]
    assert diff["workflow_diff"]["confirmation_boundary"] == "user_confirmed_required_before_publish"

    published = client.post(
        f"/bff/pv19/workflows/{workflow_id}/versions/publish{SCOPE_QUERY}",
        json={
            "user_confirmed": True,
            "source": "workflow_console",
            "idempotency_key": "pv19-publish-1",
            "expected_draft_revision": draft_revision,
            "workflow_patch_id": diff["workflow_diff"]["workflow_patch_id"],
            "version": "pv19-test-1",
        },
    ).json()
    assert published["status"] == "published"
    version_id = published["workflow_version_id"]

    run = client.post(
        f"/bff/pv19/workflows/{workflow_id}/runs{SCOPE_QUERY}",
        json={
            "user_confirmed": True,
            "source": "run_panel",
            "idempotency_key": "pv19-run-1",
            "workflow_version_id": version_id,
            "input": {"sample": "knowledge_opc", "query": "审查 HarnessOS 工作流平台闭环"},
        },
    ).json()
    assert run["workflow_instance"]["status"] == "waiting_approval"
    assert run["pending_human_gates"]
    run_id = run["workflow_instance"]["workflow_instance_id"]

    before = client.get(f"/bff/pv19/runs/{run_id}/inspect{SCOPE_QUERY}").json()
    assert before["status"]["status"] == "waiting_approval"
    assert before["pending_human_gates"]

    action = client.post(
        f"/bff/pv19/runs/{run_id}/human-actions{SCOPE_QUERY}",
        json={
            "user_confirmed": True,
            "source": "human_gate_panel",
            "idempotency_key": "pv19-approve-1",
            "action_type": "approve",
            "reason": "测试审批通过",
        },
    ).json()
    assert action["before_state"]["status"] == "waiting_approval"
    assert action["after_state"]["status"] == "completed"

    after = client.get(f"/bff/pv19/runs/{run_id}/inspect{SCOPE_QUERY}").json()
    assert after["status"]["status"] == "completed"
    assert after["runtime_event_refs"]
    assert after["trace_refs"]
    assert after["artifact_refs"]
    assert after["quality_refs"]
    assert after["human_gate_refs"]

    evidence = client.get(f"/bff/pv19/runs/{run_id}/evidence{SCOPE_QUERY}").json()
    assert evidence["route_boundary"]["allowed_prefix"] == "/bff/pv19"
    assert evidence["platform_generality"]["status"] == "pass"
    assert evidence["platform_generality"]["core_customization_allowed"] is False
    assert evidence["allowed_claim"] == "PV19 complete: runtime-backed workflow platform closed loop ready for bounded review."
    assert evidence["missing_evidence"] == []
    assert_no_forbidden_text(
        {
            "state": state,
            "graph": graph,
            "validation": validation,
            "diff": diff,
            "published": published,
            "run": run,
            "before": before,
            "action": action,
            "after": after,
            "evidence": evidence,
        }
    )
