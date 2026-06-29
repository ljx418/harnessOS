"""PV21 complete Workflow Studio BFF route tests."""

from __future__ import annotations

from copy import deepcopy

from fastapi.testclient import TestClient

from apps.api import create_app
from v4_0_reference_support import SCOPE_QUERY, assert_no_forbidden_text, build_gateway


def _client(monkeypatch, tmp_path) -> TestClient:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    return TestClient(create_app(gateway_service=service))


def test_pv21_complete_workflow_studio_closed_loop(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)

    state = client.get(f"/bff/pv21/studio/state{SCOPE_QUERY}").json()
    assert state["schema_version"] == "pv21.complete_workflow_studio.v1"
    assert state["entry"]["route"] == "?studio=pv21-complete-workflow-studio"
    assert state["platform_contract"]["workflow_core_customization_allowed"] is False
    assert state["draft_graph"]["nodes"]
    assert state["node_library"]
    workflow_id = state["workflow"]["workflow_template_id"]

    graph = deepcopy(state["draft_graph"])
    graph["nodes"][0]["params"] = {**graph["nodes"][0].get("params", {}), "pv21_test_saved": True}
    graph["nodes"][1]["metadata"] = {
        **graph["nodes"][1].get("metadata", {}),
        "prompt_ref": "pv21.prompt.agent.test.v1",
        "executor_binding": "pv20.governed_agent_executor",
    }
    saved = client.put(f"/bff/pv21/workflows/{workflow_id}/graph{SCOPE_QUERY}", json=graph).json()
    assert saved["schema_version"] == "pv21.complete_workflow_studio.v1"
    assert saved["validation"]["status"] == "valid"
    assert saved["graph"]["draft_revision"] >= graph["draft_revision"]

    validation = client.post(f"/bff/pv21/workflows/{workflow_id}/graph/validate{SCOPE_QUERY}", json={}).json()
    assert validation["status"] == "valid"
    assert validation["runtime_readiness"]["can_publish"] is True
    assert validation["runtime_readiness"]["human_gate_nodes"]

    blocked_publish = client.post(
        f"/bff/pv21/workflows/{workflow_id}/versions/publish{SCOPE_QUERY}",
        json={"source": "workflow_console", "version": "pv21-no-confirm"},
    )
    assert blocked_publish.status_code == 400
    assert blocked_publish.json()["error"]["code"] == "PV21_CONFIRMATION_REQUIRED"

    diff_1 = client.post(
        f"/bff/pv21/workflows/{workflow_id}/diff{SCOPE_QUERY}",
        json={"draft_revision": saved["graph"]["draft_revision"]},
    ).json()
    assert diff_1["diff_id"]
    assert diff_1["user_confirmation_required"] is True
    assert diff_1["publish_blocked"] is False

    published_1 = client.post(
        f"/bff/pv21/workflows/{workflow_id}/versions/publish{SCOPE_QUERY}",
        json={
            "source": "workflow_console",
            "version": "pv21-test-1",
            "draft_revision": saved["graph"]["draft_revision"],
            "diff_id": diff_1["diff_id"],
            "user_confirmation": {"confirmed": True, "actor_id": "tester", "reason": "PV21 test publish 1"},
        },
    ).json()
    version_id_1 = published_1["version"]["workflow_version_id"]
    assert version_id_1.startswith("wfv_")

    graph_2 = client.get(f"/bff/pv21/workflows/{workflow_id}/graph{SCOPE_QUERY}").json()
    graph_2["nodes"][1]["metadata"] = {
        **graph_2["nodes"][1].get("metadata", {}),
        "prompt_ref": "pv21.prompt.agent.test.v2",
        "executor_binding": "pv20.governed_agent_executor",
    }
    saved_2 = client.put(f"/bff/pv21/workflows/{workflow_id}/graph{SCOPE_QUERY}", json=graph_2).json()
    diff_2 = client.post(
        f"/bff/pv21/workflows/{workflow_id}/diff{SCOPE_QUERY}",
        json={"base_version_id": version_id_1, "draft_revision": saved_2["graph"]["draft_revision"]},
    ).json()
    published_2 = client.post(
        f"/bff/pv21/workflows/{workflow_id}/versions/publish{SCOPE_QUERY}",
        json={
            "source": "workflow_console",
            "version": "pv21-test-2",
            "draft_revision": saved_2["graph"]["draft_revision"],
            "diff_id": diff_2["diff_id"],
            "user_confirmed": True,
        },
    ).json()
    version_id_2 = published_2["version"]["workflow_version_id"]
    assert version_id_2 != version_id_1

    versions = client.get(f"/bff/pv21/workflows/{workflow_id}/versions{SCOPE_QUERY}").json()
    assert versions["published_version_id"] == version_id_2
    assert version_id_1 in versions["rollback_candidates"]
    assert len(versions["versions"]) >= 2

    run = client.post(
        f"/bff/pv21/workflows/{workflow_id}/runs{SCOPE_QUERY}",
        json={
            "source": "run_panel",
            "workflow_version_id": version_id_2,
            "input": {"sample": "pv21_complete_workflow_studio", "query": "验证完整工作流平台闭环"},
            "user_confirmation": {"confirmed": True, "actor_id": "tester", "reason": "PV21 test run"},
        },
    ).json()
    assert run["state"] == "waiting_approval"
    assert run["pending_human_gates"]
    run_id = run["run_id"]

    inspected_before = client.get(f"/bff/pv21/runs/{run_id}/inspect{SCOPE_QUERY}").json()
    assert inspected_before["state"] == "waiting_approval"
    assert inspected_before["pending_human_gates"]

    action = client.post(
        f"/bff/pv21/runs/{run_id}/human-actions{SCOPE_QUERY}",
        json={
            "source": "human_gate_panel",
            "station_id": inspected_before["current_human_gate"]["station_id"],
            "decision": "approve",
            "comment": "PV21 测试审批通过",
            "user_confirmation": {"confirmed": True, "actor_id": "tester", "reason": "PV21 approve"},
        },
    ).json()
    assert action["before_state"]["status"] == "waiting_approval"
    assert action["after_state"]["status"] == "completed"
    assert action["resulting_run_state"] == "completed"

    inspected_after = client.get(f"/bff/pv21/runs/{run_id}/inspect{SCOPE_QUERY}").json()
    assert inspected_after["state"] == "completed"
    assert inspected_after["trace_refs"]
    assert inspected_after["artifact_refs"]
    assert inspected_after["quality_refs"]
    assert inspected_after["approval_refs"]

    evidence = client.get(f"/bff/pv21/runs/{run_id}/evidence{SCOPE_QUERY}").json()
    assert evidence["route_boundary"]["allowed_prefix"] == "/bff/pv21"
    assert evidence["platform_generality"]["core_customization_allowed"] is False
    assert evidence["allowed_claim"] == "PV21 workflow studio candidate is ready for bounded review evidence."
    assert evidence["no_false_green_status"] == "pass"
    assert evidence["missing_refs"] == []

    rollback = client.post(
        f"/bff/pv21/workflows/{workflow_id}/versions/{version_id_1}/rollback{SCOPE_QUERY}",
        json={
            "source": "version_panel",
            "reason": "PV21 test rollback",
            "user_confirmation": {"confirmed": True, "actor_id": "tester", "reason": "PV21 rollback"},
        },
    ).json()
    assert rollback["published_version"]["workflow_version_id"] == version_id_1
    assert rollback["previous_version_id"] == version_id_2
    assert rollback["history_preserved"] is True

    versions_after_rollback = client.get(f"/bff/pv21/workflows/{workflow_id}/versions{SCOPE_QUERY}").json()
    assert versions_after_rollback["published_version_id"] == version_id_1

    invalid_graph = deepcopy(saved_2["graph"])
    invalid_graph["nodes"][1]["type"] = "business_specific_core"
    invalid_saved = client.put(f"/bff/pv21/workflows/{workflow_id}/graph{SCOPE_QUERY}", json=invalid_graph).json()
    assert invalid_saved["validation"]["status"] == "invalid"
    assert any(item["code"] == "PV21_UNKNOWN_NODE_TYPE" for item in invalid_saved["validation"]["errors"])

    assert_no_forbidden_text(
        {
            "state": state,
            "saved": saved,
            "validation": validation,
            "diff_1": diff_1,
            "published_1": published_1,
            "published_2": published_2,
            "versions": versions,
            "run": run,
            "inspected_before": inspected_before,
            "action": action,
            "inspected_after": inspected_after,
            "evidence": evidence,
            "rollback": rollback,
            "versions_after_rollback": versions_after_rollback,
            "invalid_saved": invalid_saved,
        }
    )
