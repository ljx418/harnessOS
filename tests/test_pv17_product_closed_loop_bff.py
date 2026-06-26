"""PV17 Product Closed Loop formal BFF route tests."""

from __future__ import annotations

import asyncio

from fastapi.testclient import TestClient

from apps.api import create_app
from v4_0_reference_support import SCOPE_QUERY, assert_no_forbidden_text, build_gateway, seed_reference_console


def _client(monkeypatch, tmp_path, template_id: str):
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    seeded = asyncio.run(seed_reference_console(service, template_id=template_id))
    return TestClient(create_app(gateway_service=service)), seeded


def test_pv17_product_console_and_entity_mutation_routes(monkeypatch, tmp_path) -> None:
    client, seeded = _client(monkeypatch, tmp_path, "pv17_console_state")

    health = client.get(f"/bff/pv17/system/health{SCOPE_QUERY}").json()
    assert health["schema_version"] == "pv17.product_closed_loop.v1"
    assert health["status"] == "ok"
    assert health["gateway_status"] == "ok"

    state = client.get(f"/bff/pv17/product-console/state{SCOPE_QUERY}").json()
    assert state["workflow" + "s"][0]["workflow_template_id"] == seeded["template"]["workflow_template_id"]
    assert state["active_run"]["workflow_instance_id"] == seeded["instance"]["workflow_instance_id"]
    assert state["station_agents"]

    accepted = client.post(
        f"/bff/pv17/entities/station-agents{SCOPE_QUERY}",
        json={
            "scope": {"app_id": "reference_app", "project_id": "demo_a", "workspace_id": "local"},
            "entity_kind": "station_agent",
            "operation": "upsert",
            "user_confirmed": True,
            "source": "product_console",
            "idempotency_key": "pv17-agent-1",
            "payload": {
                "entity_id": "station_agent:reviewer",
                "display_name": "审查 Station Agent",
                "role": "reviewer",
                "goal": "审查 PV17 runtime refs 和 evidence refs。",
                "model_refs": ["model:redacted"],
                "skill_refs": ["governance.review"],
            },
        },
    ).json()
    assert accepted["status"] == "accepted"
    assert accepted["entity_ref"]["entity_kind"] == "station_agent"
    assert accepted["audit_ref"]["operation"] == "product_entity.station_agent.upsert"

    denied = client.post(
        f"/bff/pv17/entities/projects{SCOPE_QUERY}",
        json={
            "entity_kind": "project",
            "operation": "upsert",
            "user_confirmed": True,
            "source": "product_console",
            "idempotency_key": "pv17-denied-project",
            "payload": {"entity_id": "demo_b", "owner_project_id": "demo_b"},
        },
    ).json()
    assert denied["status"] == "denied"
    assert denied["denied_reason"] == "owner_project_scope_mismatch"

    agent_forbidden = client.post(
        f"/bff/pv17/entities/apps{SCOPE_QUERY}",
        json={
            "entity_kind": "app",
            "operation": "upsert",
            "user_confirmed": True,
            "source": "agent",
            "idempotency_key": "pv17-agent-forbidden",
            "payload": {"entity_id": "reference_app"},
        },
    ).json()
    assert agent_forbidden["error"]["code"] == "WORKFLOW_ACTION_FORBIDDEN"
    assert_no_forbidden_text({"health": health, "state": state, "accepted": accepted, "denied": denied})


def test_pv17_studio_runtime_inspect_and_evidence_routes(monkeypatch, tmp_path) -> None:
    client, seeded = _client(monkeypatch, tmp_path, "pv17_runtime_inspect")
    template_id = seeded["template"]["workflow_template_id"]
    instance_id = seeded["instance"]["workflow_instance_id"]

    studio = client.get(f"/bff/pv17/studio/workflows/{template_id}{SCOPE_QUERY}").json()
    assert studio["workflow_template"]["workflow_template_id"] == template_id
    assert studio["graph"]["nodes"]
    assert studio["patch_queue"]

    patch = client.post(
        f"/bff/pv17/studio/workflows/{template_id}/patches{SCOPE_QUERY}",
        json={
            "source": "inspector",
            "intent_type": "inspector_update",
            "operation": "update_station_prompt",
            "workflow_instance_id": instance_id,
            "payload": {"station_id": "station_b", "prompt_ref": "pv17.prompt.v2"},
        },
    ).json()
    assert patch["status"] == "proposed"
    assert patch["workflow_patch"]["workflow_template_id"] == template_id

    run = client.post(
        f"/bff/pv17/runtime/workflows/{template_id}/confirm-run{SCOPE_QUERY}",
        json={
            "user_confirmed": True,
            "source": "run_panel",
            "idempotency_key": "pv17-run-1",
            "workflow_template_id": template_id,
            "workflow_version_id": seeded["version"]["workflow_version_id"],
        },
    ).json()
    assert run["status"] == "started"
    assert run["runtime_event_refs"]
    assert run["trace_refs"]

    new_instance_id = run["workflow_instance"]["workflow_instance_id"]
    inspect = client.get(f"/bff/pv17/runtime/instances/{new_instance_id}/inspect{SCOPE_QUERY}").json()
    assert inspect["workflow_instance"]["workflow_instance_id"] == new_instance_id
    assert inspect["runtime_event_refs"]
    assert inspect["trace_refs"]
    assert inspect["artifact_refs"]
    assert inspect["quality_refs"]

    evidence = client.get(f"/bff/pv17/evidence/instances/{new_instance_id}/summary{SCOPE_QUERY}").json()
    assert evidence["route_boundary"]["allowed_prefix"] == "/bff/pv17"
    assert "/v1/rpc" in evidence["route_boundary"]["browser_denylist"]
    assert evidence["allowed_claim"] == "PV17 complete: product closed loop implementation ready for bounded review."
    assert_no_forbidden_text({"studio": studio, "patch": patch, "run": run, "inspect": inspect, "evidence": evidence})
