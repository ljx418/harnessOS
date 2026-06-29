"""PV20 Agent execution contract BFF route tests."""

from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient

from apps.api import create_app
from core.config import DataServiceMcpConfig
from v4_0_reference_support import SCOPE_QUERY, assert_no_forbidden_text, build_gateway


def _client(monkeypatch, tmp_path) -> TestClient:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    return TestClient(create_app(gateway_service=service))


def _configure_data_service_mcp_fixture(service, tmp_path: Path) -> None:
    mcp_package = tmp_path / "data_service"
    mcp_package.mkdir()
    (mcp_package / "__init__.py").write_text("", encoding="utf-8")
    (mcp_package / "mcp_stdio.py").write_text(
        """
import json
import sys

for line in sys.stdin:
    request = json.loads(line)
    method = request.get("method")
    request_id = request.get("id")
    if method == "initialize":
        result = {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}}
    elif method == "tools/call":
        params = request.get("params") or {}
        result = {
            "content": [{
                "type": "text",
                "text": json.dumps({
                    "workspace_id": "pv20-agent-executor-fixture",
                    "status": "ok",
                    "warnings": [],
                    "artifact_refs": [],
                    "data": {
                        "tool": params.get("name"),
                        "arguments": params.get("arguments"),
                    },
                }),
            }],
            "isError": False,
        }
    else:
        result = {}
    print(json.dumps({"jsonrpc": "2.0", "id": request_id, "result": result}), flush=True)
""".strip()
        + "\n",
        encoding="utf-8",
    )
    service.connector_registry.data_service_config = DataServiceMcpConfig(
        cwd=str(tmp_path),
        command=sys.executable,
        args="-m data_service.mcp_stdio",
        execution="stdio",
        request_timeout=5,
        workspace_root=str(tmp_path / "managed"),
        allowed_workspace_roots=str(tmp_path),
        allowed_source_roots=str(tmp_path),
    )


def test_pv20_agent_execution_contract_read_model(monkeypatch, tmp_path) -> None:
    client = _client(monkeypatch, tmp_path)

    state = client.get(f"/bff/pv20/agent-executor/state{SCOPE_QUERY}").json()
    assert state["schema_version"] == "pv20.agent_executor_contract.v1"
    assert state["stage"] == "PV20-S1"
    assert state["status"] == "contract_ready"
    assert state["entry"]["implementation_status"] == "contract_read_model_only"

    run_id = state["workflow_instance"]["workflow_instance_id"]
    assert run_id
    contract = client.get(f"/bff/pv20/runs/{run_id}/agent-execution-contract{SCOPE_QUERY}").json()
    envelope = contract["agent_execution_contract"]
    result = contract["agent_execution_result"]

    assert envelope["workflow_instance_id"] == run_id
    assert envelope["station_run_id"] == contract["station_run"]["station_run_id"]
    assert envelope["agent_id"].startswith("pv20_agent:")
    assert envelope["operation"] == "agent.contract.readiness"
    assert envelope["execution_authority"]["durable_mutation_allowed"] is False
    assert envelope["execution_authority"]["browser_direct_execution_allowed"] is False
    assert "workflow.template.publish" in envelope["forbidden_operation_refs"]
    assert "approval.respond" in envelope["forbidden_operation_refs"]

    assert result["status"] == "contract_ready"
    assert result["execution_status"] == "not_executed_in_s1"
    assert result["tool_call_refs"] == []
    assert result["skill_call_refs"] == []
    assert result["mcp_call_refs"] == []

    evidence = client.get(f"/bff/pv20/runs/{run_id}/agent-execution-evidence{SCOPE_QUERY}").json()
    assert evidence["status"] == "PASS"
    assert evidence["route_boundary"]["allowed_prefix"] == "/bff/pv20"
    assert evidence["missing_evidence"] == []
    assert evidence["allowed_claim"] == "PV20-S1 complete: governed Agent execution contract ready for bounded review."
    assert "unrestricted_tool_execution_readiness" in evidence["not_claimed"]
    assert "unrestricted_mcp_execution_readiness" in evidence["not_claimed"]

    assert_no_forbidden_text({"state": state, "contract": contract, "evidence": evidence})


def test_pv20_allowlisted_skill_execution_updates_contract(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("HARNESS_V3_5_DEV_MODE", "1")
    service = build_gateway(tmp_path)
    _configure_data_service_mcp_fixture(service, tmp_path)
    client = TestClient(create_app(gateway_service=service))

    state = client.get(f"/bff/pv20/agent-executor/state{SCOPE_QUERY}").json()
    run_id = state["workflow_instance"]["workflow_instance_id"]

    denied = client.post(
        f"/bff/pv20/runs/{run_id}/agent-skill-executions{SCOPE_QUERY}",
        json={"source": "agent_executor_panel", "skill_name": "plan"},
    )
    assert denied.status_code == 400

    unknown = client.post(
        f"/bff/pv20/runs/{run_id}/agent-skill-executions{SCOPE_QUERY}",
        json={"user_confirmed": True, "source": "agent_executor_panel", "skill_name": "unknown_skill"},
    )
    assert unknown.status_code == 400

    execution = client.post(
        f"/bff/pv20/runs/{run_id}/agent-skill-executions{SCOPE_QUERY}",
        json={"user_confirmed": True, "source": "agent_executor_panel", "skill_name": "plan"},
    ).json()
    assert execution["stage"] == "PV20-S2"
    assert execution["execution"]["status"] == "completed"
    assert execution["execution"]["skill_call_refs"]
    assert execution["execution"]["tool_call_refs"] == []
    assert execution["execution"]["mcp_call_refs"] == []
    assert execution["execution"]["artifact_refs"]

    contract = client.get(f"/bff/pv20/runs/{run_id}/agent-execution-contract{SCOPE_QUERY}").json()
    result = contract["agent_execution_result"]
    assert result["execution_status"] == "completed"
    assert result["skill_call_refs"] == execution["execution"]["skill_call_refs"]
    assert result["tool_call_refs"] == []
    assert result["mcp_call_refs"] == []

    evidence = client.get(f"/bff/pv20/runs/{run_id}/agent-execution-evidence{SCOPE_QUERY}").json()
    assert evidence["status"] == "PASS"
    assert any(item["status"] == "PASS" and "PV20-S2" in item["claim"] for item in evidence["claim_matrix"])

    tool_execution = client.post(
        f"/bff/pv20/runs/{run_id}/agent-tool-executions{SCOPE_QUERY}",
        json={"user_confirmed": True, "source": "agent_executor_panel", "tool_name": "artifact.metadata.read"},
    ).json()
    assert tool_execution["stage"] == "PV20-S3A"
    assert tool_execution["execution"]["status"] == "completed"
    assert tool_execution["execution"]["tool_call_refs"]
    assert tool_execution["execution"]["skill_call_refs"] == []
    assert tool_execution["execution"]["mcp_call_refs"] == []

    contract_after_tool = client.get(f"/bff/pv20/runs/{run_id}/agent-execution-contract{SCOPE_QUERY}").json()
    result_after_tool = contract_after_tool["agent_execution_result"]
    assert result_after_tool["execution_status"] == "completed"
    assert result_after_tool["skill_call_refs"] == execution["execution"]["skill_call_refs"]
    assert result_after_tool["tool_call_refs"] == tool_execution["execution"]["tool_call_refs"]
    assert result_after_tool["mcp_call_refs"] == []

    evidence_after_tool = client.get(f"/bff/pv20/runs/{run_id}/agent-execution-evidence{SCOPE_QUERY}").json()
    assert evidence_after_tool["status"] == "PASS"
    assert evidence_after_tool["allowed_claim"] == "PV20-S3A complete: allowlisted local tool execution ready for bounded review."
    assert any(item["status"] == "PASS" and "PV20-S3A" in item["claim"] for item in evidence_after_tool["claim_matrix"])

    agent_sourced_tool = client.post(
        f"/bff/pv20/runs/{run_id}/agent-tool-executions{SCOPE_QUERY}",
        json={"user_confirmed": True, "source": "agent", "tool_name": "artifact.metadata.read"},
    )
    assert agent_sourced_tool.status_code == 400

    mcp_unconfirmed = client.post(
        f"/bff/pv20/runs/{run_id}/agent-mcp-executions{SCOPE_QUERY}",
        json={"source": "agent_executor_panel", "connector_id": "data_service_mcp", "tool_name": "knowledge_query_v2"},
    )
    assert mcp_unconfirmed.status_code == 400

    mcp_denied = client.post(
        f"/bff/pv20/runs/{run_id}/agent-mcp-executions{SCOPE_QUERY}",
        json={"user_confirmed": True, "source": "agent_executor_panel", "connector_id": "unknown_mcp", "tool_name": "unknown_tool"},
    )
    assert mcp_denied.status_code == 400

    mcp_execution = client.post(
        f"/bff/pv20/runs/{run_id}/agent-mcp-executions{SCOPE_QUERY}",
        json={"user_confirmed": True, "source": "agent_executor_panel", "connector_id": "data_service_mcp", "tool_name": "knowledge_query_v2"},
    ).json()
    assert mcp_execution["stage"] == "PV20-S3B"
    assert mcp_execution["execution"]["status"] == "completed"
    assert mcp_execution["execution"]["mcp_call_refs"]
    assert mcp_execution["execution"]["approval_refs"]
    assert mcp_execution["execution"]["skill_call_refs"] == []
    assert mcp_execution["execution"]["tool_call_refs"] == []

    contract_after_mcp = client.get(f"/bff/pv20/runs/{run_id}/agent-execution-contract{SCOPE_QUERY}").json()
    result_after_mcp = contract_after_mcp["agent_execution_result"]
    assert result_after_mcp["execution_status"] == "completed"
    assert result_after_mcp["skill_call_refs"] == execution["execution"]["skill_call_refs"]
    assert result_after_mcp["tool_call_refs"] == tool_execution["execution"]["tool_call_refs"]
    assert result_after_mcp["mcp_call_refs"] == mcp_execution["execution"]["mcp_call_refs"]
    assert result_after_mcp["approval_refs"] == mcp_execution["execution"]["approval_refs"]

    evidence_after_mcp = client.get(f"/bff/pv20/runs/{run_id}/agent-execution-evidence{SCOPE_QUERY}").json()
    assert evidence_after_mcp["status"] == "PASS"
    assert evidence_after_mcp["allowed_claim"] == "PV20-S4 complete: approval handoff and denied mutation fixtures ready for bounded review."
    assert any(item["status"] == "PASS" and "PV20-S4" in item["claim"] for item in evidence_after_mcp["claim_matrix"])
    assert_no_forbidden_text({"execution": execution, "tool_execution": tool_execution, "mcp_execution": mcp_execution, "contract": contract_after_mcp, "evidence": evidence_after_mcp})
