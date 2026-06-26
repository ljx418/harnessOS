"""PV18 Knowledge OPC formal BFF route tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from apps.api import create_app
from v4_0_reference_support import OTHER_SCOPE_QUERY, SCOPE_QUERY, assert_no_forbidden_text, build_gateway


def _client(monkeypatch, tmp_path) -> TestClient:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    return TestClient(create_app(gateway_service=service))


def test_pv18_knowledge_opc_bff_flow(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)

    state = client.get(f"/bff/pv18/knowledge/state{SCOPE_QUERY}").json()
    assert state["schema_version"] == "pv18.knowledge_opc.v1"
    assert state["workspace"]["workspace_id"].startswith("knowledge:")
    assert state["connector_health"]["connector_id"] == "data_service_mcp"

    workspace = client.post(
        f"/bff/pv18/knowledge/workspaces{SCOPE_QUERY}",
        json={"display_name": "PV18 Knowledge OPC Test"},
    ).json()
    assert workspace["status"] == "accepted"
    assert workspace["workspace"]["redaction_status"] == "redacted"

    source = client.post(
        f"/bff/pv18/knowledge/sources/import{SCOPE_QUERY}",
        json={
            "title": "HarnessOS PV18",
            "content": "HarnessOS validates workflow platform capability through bounded business flows.",
        },
    ).json()
    assert source["status"] == "imported"
    assert source["artifact_refs"]
    assert source["lineage_refs"]

    build = client.post(f"/bff/pv18/knowledge/builds/start{SCOPE_QUERY}", json={"mode": "bounded_review"}).json()
    assert build["status"] == "completed"
    assert build["trace_refs"]

    build_status = client.get(f"/bff/pv18/knowledge/builds/{build['build_id']}/status{SCOPE_QUERY}").json()
    assert build_status["build_id"] == build["build_id"]

    query = client.post(
        f"/bff/pv18/knowledge/query{SCOPE_QUERY}",
        json={"query": "How does HarnessOS validate a workflow platform?"},
    ).json()
    assert query["status"] == "answered"
    assert query["citation_coverage"]["status"] == "pass"
    assert query["source_refs"]

    quality = client.post(f"/bff/pv18/knowledge/quality-feedback{SCOPE_QUERY}", json={"issues": []}).json()
    assert quality["quality_status"] == "pass"

    correction = client.post(f"/bff/pv18/knowledge/correction-plan{SCOPE_QUERY}", json={}).json()
    assert correction["requires_human_review"] is True
    assert correction["auto_publish_allowed"] is False

    evidence = client.get(f"/bff/pv18/knowledge/evidence/summary{SCOPE_QUERY}").json()
    assert evidence["route_boundary"]["allowed_prefix"] == "/bff/pv18/knowledge"
    assert evidence["platform_generality"]["status"] == "PASS"
    assert evidence["allowed_claim"] == "PV18 complete: Knowledge OPC productization implementation ready for bounded review."
    assert_no_forbidden_text(
        {
            "state": state,
            "workspace": workspace,
            "source": source,
            "build": build,
            "query": query,
            "quality": quality,
            "correction": correction,
            "evidence": evidence,
        }
    )


def test_pv18_query_requires_source(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)

    result = client.post(f"/bff/pv18/knowledge/query{OTHER_SCOPE_QUERY}", json={"query": "No source"}).json()

    assert result["error"]["code"] == "WORKFLOW_ACTION_FORBIDDEN"
    assert result["error"]["data"]["fixture"] == "source_required"
