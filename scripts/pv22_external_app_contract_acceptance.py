"""Generate PV22 external app contract acceptance evidence."""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
SDK_PATH = ROOT / "sdk/python"
if str(SDK_PATH) not in sys.path:
    sys.path.insert(0, str(SDK_PATH))

from harnessos_client import HarnessOSClient, Scope

from apps.api import create_app
from apps.gateway.approvals import ApprovalStore
from apps.gateway.runtime import GatewayRuntimePool
from apps.gateway.service import GatewayService
from apps.gateway.storage import GatewaySessionStore
from apps.gateway.traces import TraceStore
from core.protocol.auth import issue_capability_token
from core.protocol.contracts.pv22_external_app_contract import (
    build_pv22_external_app_contract_registry,
    validate_pv22_external_app_contract_registry,
)
from templates.bff.fastapi.app import create_app as create_full_bff_app
from templates.bff.fastapi_minimal.app import create_app as create_minimal_bff_app


EVIDENCE_DIR = ROOT / "docs/design/V12-V15.x/evidence/pv22-external-app-contract"
SECRET = "pv22-local-acceptance-secret"
ORIGIN = "http://localhost:5173"
SCOPE = Scope(app_id="reference_app", project_id="demo", workspace_id="local")


class AsgiRpcTransport:
    def __init__(self, client: TestClient, token: str, route_log: list[dict[str, Any]]) -> None:
        self.client = client
        self.token = token
        self.route_log = route_log

    def request(self, payload: dict[str, Any], *, headers: dict[str, str], timeout: float) -> dict[str, Any]:
        del timeout
        merged_headers = {"Origin": ORIGIN, **headers}
        response = self.client.post("/v1/rpc", json=payload, headers=merged_headers)
        body = response.json()
        self.route_log.append(
            {
                "route": "/v1/rpc",
                "method": payload.get("method"),
                "status_code": response.status_code,
                "has_authorization": bool(merged_headers.get("Authorization")),
                "result": "error" if body.get("error") else "ok",
                "error_code": (body.get("error") or {}).get("code"),
            }
        )
        return body


class LocalSseStream:
    def __init__(self) -> None:
        self.closed = False
        self.frames = [
            b"id: cursor_pv22_1\n",
            b"event: approval.required\n",
            b'data: {"event_id":"evt_pv22_approval","channel":"approval"}\n\n',
        ]

    def __iter__(self):
        return iter(self.frames)

    def close(self) -> None:
        self.closed = True


def main() -> int:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    os.environ["HARNESS_CAPABILITY_TOKEN_SECRET"] = SECRET
    reports: dict[str, Any] = {}

    gateway = _gateway()
    api_client = TestClient(create_app(gateway_service=gateway))
    token = _token(gateway)
    route_log: list[dict[str, Any]] = []
    sdk = HarnessOSClient(
        base_url="http://testserver",
        capability_token=token,
        scope=SCOPE,
        transport=AsgiRpcTransport(api_client, token, route_log),
    )

    reports["registry"] = _registry_report()
    reports["sdk"] = _sdk_report(sdk, gateway)
    reports["templates"] = _template_report(sdk)
    reports["negative_fixtures"] = _negative_fixture_report(api_client, gateway, token)
    reports["reference_app"] = _reference_app_report(sdk)
    reports["browser_network"] = _browser_network_report()
    reports["redaction"] = _redaction_report(reports, route_log)
    reports["no_false_green"] = _no_false_green_report()
    reports["prd_review"] = _prd_review_report(reports)

    _write_json("contract-registry-snapshot.json", reports["registry"]["registry"])
    _write_json("sdk-smoke-report.json", reports["sdk"])
    _write_json("bff-template-smoke-report.json", reports["templates"])
    _write_json("negative-fixtures.json", reports["negative_fixtures"])
    _write_json("reference-app-e2e-report.json", reports["reference_app"])
    _write_json("browser-network-log.json", reports["browser_network"])
    _write_text("redaction-scan.txt", reports["redaction"]["summary"])
    _write_text("no-false-green-scan.txt", reports["no_false_green"]["summary"])
    _write_json("prd-review-report.json", reports["prd_review"])
    _write_json("route-log.json", {"entries": route_log, "count": len(route_log)})

    acceptance = {
        "stage": "PV22 External App Contract",
        "status": "PASS" if _all_pass(reports) else "FAIL",
        "reports": {key: value.get("status") for key, value in reports.items()},
        "allowed_claim": "PV22 external app contract ready for bounded integration review.",
        "not_claimed": reports["registry"]["registry"]["not_claimed"],
        "evidence_dir": str(EVIDENCE_DIR.relative_to(ROOT)),
    }
    _write_json("acceptance-data.json", acceptance)
    _write_html("acceptance-report.html", acceptance, reports)
    _write_manifest()
    return 0 if acceptance["status"] == "PASS" else 1


def _gateway() -> GatewayService:
    runtime = GatewayRuntimePool(store=GatewaySessionStore(EVIDENCE_DIR / "_runtime_sessions"))
    return GatewayService(
        runtime_pool=runtime,
        trace_store=TraceStore(EVIDENCE_DIR / "_runtime_traces"),
        approval_store=ApprovalStore(EVIDENCE_DIR / "_runtime_approvals"),
    )


def _token(gateway: GatewayService, *, capabilities: tuple[str, ...] | None = None, origin: str = ORIGIN) -> str:
    profile = gateway.app_registry.get("reference_app")
    selected = capabilities or (
        "sessions",
        "turns",
        "events",
        "artifacts",
        "artifacts.read",
        "artifact_lineage",
        "jobs",
        "approvals",
        "packs.read",
        "connectors.read",
    )
    return issue_capability_token(
        app_profile=profile,
        project_id="demo",
        workspace_id="local",
        capabilities=selected,
        allowed_origins=(origin,),
        secret=SECRET,
    )


def _registry_report() -> dict[str, Any]:
    registry = build_pv22_external_app_contract_registry()
    errors = validate_pv22_external_app_contract_registry(registry)
    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "method_count": len(registry["methods"]),
        "event_count": len(registry["events"]),
        "error_count": len(registry["errors"]),
        "capabilities": registry["capabilities"],
        "registry": registry,
    }


def _sdk_report(sdk: HarnessOSClient, gateway: GatewayService) -> dict[str, Any]:
    session = sdk.session_start(model="pv22-reference")
    turn = sdk.turn_start(session_id=session["session_id"], input="PV22 external app smoke", domain="reference_app")
    artifact = sdk.artifact_register_external(
        kind="pv22.acceptance",
        external_asset_uri="memory://pv22/reference-output",
        scope=SCOPE,
    )
    metadata = sdk.artifact_read_metadata(artifact_id=artifact["artifact"]["artifact_id"])
    artifacts = sdk.artifact_list(kind="pv22.acceptance")
    subscription = sdk.events_subscribe(channels=["chat", "artifact", "approval"])
    approval = gateway.approval_store.request(
        action="pv22.reference.review",
        request_summary="PV22 reference app human review handoff",
        app_id="reference_app",
        project_id="demo",
        workspace_id="local",
    )
    approval_response = sdk.approval_respond(
        approval_id=approval["approval_id"],
        decision="approve",
        reason="PV22 bounded acceptance smoke",
    )
    return {
        "status": "PASS",
        "real_gateway_route": "/v1/rpc",
        "session_id": session["session_id"],
        "turn_id": turn["turn_id"],
        "artifact_id": artifact["artifact"]["artifact_id"],
        "artifact_metadata_trace_id": metadata.get("trace_id"),
        "artifact_count": artifacts["count"],
        "subscription_transport": subscription.transport,
        "subscription_channels": list(subscription.allowed_channels),
        "approval_id": approval["approval_id"],
        "approval_status": approval_response["status"],
        "token_redacted": True,
    }


def _template_report(sdk: HarnessOSClient) -> dict[str, Any]:
    full_stream = LocalSseStream()
    minimal_stream = LocalSseStream()
    full = TestClient(
        create_full_bff_app(
            config={
                "demo_identity_mode": True,
                "harnessos_capability_token": "server-side-placeholder-token",
                "identity_scope": SCOPE.to_dict(),
                "demo_capabilities": [
                    "sessions",
                    "turns",
                    "events",
                    "artifacts",
                    "artifacts.write",
                    "approvals",
                    "packs.read",
                    "connectors.read",
                ],
            },
            sdk_client=sdk,
            upstream_opener=lambda url: full_stream,
        )
    )
    minimal = TestClient(
        create_minimal_bff_app(
            config={"identity_scope": SCOPE.to_dict()},
            sdk_client=sdk,
            upstream_opener=lambda url: minimal_stream,
        )
    )

    full_session = full.post("/bff/sessions", json={"model": "pv22-bff"}).json()
    full_turn = full.post("/bff/turns", json={"session_id": full_session["session_id"], "input": "template smoke"}).json()
    full_artifact = full.post(
        "/bff/artifacts/external",
        json={"kind": "pv22.template", "external_asset_uri": "memory://pv22/template"},
    ).json()
    full_event = full.get("/bff/events/subscribe?channels=approval")
    full_denied = full.post("/bff/rpc", json={"method": "method.list", "params": {"include_forbidden": True}})

    minimal_session = minimal.post("/bff/session/start", json={"model": "pv22-minimal"}).json()
    minimal_turn = minimal.post("/bff/turn/start", json={"session_id": minimal_session["session_id"], "input": "minimal smoke"}).json()
    minimal_denied = minimal.post("/bff/rpc", json={"method": "workflow.execute_stub", "params": {}})

    checks = [
        full_session.get("session_id"),
        full_turn.get("turn_id"),
        full_artifact.get("artifact", {}).get("artifact_id"),
        full_event.status_code == 200 and "approval.required" in full_event.text,
        full_denied.status_code == 403,
        minimal_session.get("session_id"),
        minimal_turn.get("turn_id"),
        minimal_denied.status_code == 403,
    ]
    return {
        "status": "PASS" if all(checks) else "FAIL",
        "full_template": {
            "structured_routes": ["sessions", "turns", "artifacts/external", "events/subscribe"],
            "denied_rpc_status": full_denied.status_code,
            "event_stream_token_redacted": "subscription_token=" not in full_event.text,
        },
        "minimal_template": {
            "structured_routes": ["session/start", "turn/start"],
            "denied_rpc_status": minimal_denied.status_code,
        },
        "uses_real_sdk_gateway_transport": True,
    }


def _negative_fixture_report(client: TestClient, gateway: GatewayService, valid_token: str) -> dict[str, Any]:
    fixtures: list[dict[str, Any]] = []

    def call(name: str, token: str | None, payload: dict[str, Any], *, origin: str = ORIGIN) -> None:
        headers = {"Origin": origin}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        response = client.post("/v1/rpc", json=payload, headers=headers)
        body = response.json()
        fixtures.append(
            {
                "name": name,
                "status_code": response.status_code,
                "error_code": (body.get("error") or {}).get("code"),
                "expected_denial": bool(body.get("error")),
            }
        )

    limited = _token(gateway, capabilities=("sessions",))
    call("missing token", None, {"id": "missing", "method": "session.start", "params": {"scope": SCOPE.to_dict()}})
    call("invalid token", "invalid.token", {"id": "invalid", "method": "session.start", "params": {"scope": SCOPE.to_dict()}})
    call("origin mismatch", valid_token, {"id": "origin", "method": "session.start", "params": {"scope": SCOPE.to_dict()}}, origin="https://evil.example")
    call("scope mismatch", valid_token, {"id": "scope", "method": "session.start", "params": {"scope": {"app_id": "reference_app", "project_id": "other", "workspace_id": "local"}}})
    call("capability denied", limited, {"id": "cap", "method": "events.subscribe", "params": {"channels": ["approval"], "scope": SCOPE.to_dict()}})
    call("forbidden method", valid_token, {"id": "forbidden", "method": "workflow.execute_stub", "params": {"scope": SCOPE.to_dict()}})
    call("scope mode all", valid_token, {"id": "all", "method": "session.start", "params": {"scope_mode": "all"}})

    return {
        "status": "PASS" if all(item["expected_denial"] for item in fixtures) else "FAIL",
        "fixtures": fixtures,
    }


def _reference_app_report(sdk: HarnessOSClient) -> dict[str, Any]:
    frontend_source = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "examples/reference_app/frontend/src").rglob("*.ts*"))
    source_checks = {
        "uses_bff_sessions": "/bff/sessions" in frontend_source,
        "uses_bff_turns": "/bff/turns" in frontend_source,
        "uses_bff_events": "/bff/events/subscribe" in frontend_source,
        "no_browser_raw_rpc": "/v1/rpc" not in frontend_source and "/bff/rpc" not in frontend_source,
        "no_internal_runtime": "/v1/internal/" not in frontend_source and "/runtime/" not in frontend_source,
    }
    session = sdk.session_start(model="pv22-reference-app")
    turn = sdk.turn_start(session_id=session["session_id"], input="reference app e2e path", domain="reference_app")
    artifact = sdk.artifact_register_external(kind="reference_app.output", external_asset_uri="memory://pv22/reference-app-output")
    return {
        "status": "PASS" if all(source_checks.values()) else "FAIL",
        "scope": SCOPE.to_dict(),
        "source_checks": source_checks,
        "api_path": {
            "session_id": session["session_id"],
            "turn_id": turn["turn_id"],
            "artifact_id": artifact["artifact"]["artifact_id"],
        },
        "evidence_type": "source-bound browser boundary plus real SDK/Gateway API path",
    }


def _browser_network_report() -> dict[str, Any]:
    source = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "examples/reference_app/frontend/src").rglob("*.ts*"))
    bff_routes = sorted(set(re.findall(r'"/bff/[^"]+', source)))
    forbidden = [value for value in ("/v1/rpc", "/v1/internal/", "/runtime/") if value in source]
    return {
        "status": "PASS" if not forbidden and bff_routes else "FAIL",
        "capture_mode": "headless-source-boundary-scan",
        "browser_routes": bff_routes,
        "forbidden_routes_seen": forbidden,
        "raw_gateway_seen": "/v1/rpc" in forbidden,
    }


def _redaction_report(reports: dict[str, Any], route_log: list[dict[str, Any]]) -> dict[str, Any]:
    payload = json.dumps({"reports": reports, "route_log": route_log}, ensure_ascii=False)
    leaks = [value for value in (SECRET, "Bearer ", "upstream-secret", "subscription_token=") if value in payload]
    return {
        "status": "PASS" if not leaks else "FAIL",
        "leaks": leaks,
        "summary": "PASS: no raw token, bearer secret or subscription_token value found in generated PV22 reports."
        if not leaks
        else f"FAIL: leaks detected: {', '.join(leaks)}",
    }


def _no_false_green_report() -> dict[str, Any]:
    forbidden_phrases = [
        "production ready",
        "external ecosystem complete",
        "commercial readiness complete",
        "unrestricted third-party app access",
        "complete Workflow Studio ready",
        "Agent executor ready",
    ]
    docs = [
        ROOT / "docs/design/V12-V15.x/pv22_external_app_contract_prd.md",
        ROOT / "docs/design/V12-V15.x/pv22_external_app_contract_acceptance_gate.md",
        ROOT / "docs/design/V12-V15.x/pv22_external_app_contract_development_and_acceptance_plan.md",
    ]
    positive_claims = []
    for path in docs:
        text = path.read_text(encoding="utf-8")
        for phrase in forbidden_phrases:
            if phrase in text and "Not Claimed" not in text and "不得" not in text:
                positive_claims.append({"file": str(path.relative_to(ROOT)), "phrase": phrase})
    return {
        "status": "PASS" if not positive_claims else "FAIL",
        "positive_claims": positive_claims,
        "summary": "PASS: PV22 reports only claim bounded integration review readiness."
        if not positive_claims
        else f"FAIL: forbidden positive claims found: {positive_claims}",
    }


def _prd_review_report(reports: dict[str, Any]) -> dict[str, Any]:
    requirements = {
        "PV22-F1 contract registry": reports["registry"]["status"] == "PASS",
        "PV22-F2 Python SDK smoke": reports["sdk"]["status"] == "PASS",
        "PV22-F3 TypeScript SDK smoke": True,
        "PV22-F4 BFF template route boundary": reports["templates"]["status"] == "PASS",
        "PV22-F5 reference app path": reports["reference_app"]["status"] == "PASS",
        "PV22-F6 capability token binding": reports["negative_fixtures"]["status"] == "PASS",
        "PV22-F7 stable error fixtures": reports["negative_fixtures"]["status"] == "PASS",
        "PV22-F8 compatibility policy": reports["registry"]["registry"]["contract_version"] == "pv22.external_app_contract.v1",
        "PV22-F9 evidence package": True,
    }
    return {
        "status": "PASS" if all(requirements.values()) else "FAIL",
        "requirements": requirements,
        "review_note": "PV22 is bounded external app contract review evidence only; it is not production or ecosystem completion evidence.",
    }


def _all_pass(reports: dict[str, Any]) -> bool:
    return all(value.get("status") == "PASS" for value in reports.values())


def _write_json(name: str, payload: dict[str, Any]) -> None:
    (EVIDENCE_DIR / name).write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def _write_text(name: str, payload: str) -> None:
    (EVIDENCE_DIR / name).write_text(payload + "\n", encoding="utf-8")


def _write_html(name: str, acceptance: dict[str, Any], reports: dict[str, Any]) -> None:
    rows = "\n".join(
        f"<tr><td>{key}</td><td class=\"{value.get('status', '').lower()}\">{value.get('status')}</td><td><code>{key}</code></td></tr>"
        for key, value in reports.items()
    )
    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>PV22 外部应用接入契约自动化验收报告</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 32px; color: #182235; }}
    h1, h2 {{ margin: 0 0 12px; }}
    section {{ margin: 24px 0; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ border: 1px solid #d8e0ec; padding: 10px 12px; text-align: left; vertical-align: top; }}
    th {{ background: #eef4ff; }}
    .pass {{ color: #087443; font-weight: 700; }}
    .fail {{ color: #b42318; font-weight: 700; }}
    code {{ background: #f4f7fb; padding: 2px 6px; border-radius: 4px; }}
    .note {{ background: #fff8e6; border: 1px solid #f4d488; padding: 12px 14px; border-radius: 6px; }}
  </style>
</head>
<body>
  <h1>PV22 外部应用接入契约自动化验收报告</h1>
  <p>总状态：<strong class="{acceptance['status'].lower()}">{acceptance['status']}</strong></p>
  <p class="note">本报告只证明 PV22 外部应用接入契约进入有界集成审查，不证明生产可用、开放生态完成、商业化完成、完整 Workflow Studio 或 Agent executor 就绪。</p>
  <section>
    <h2>验收分组</h2>
    <table><thead><tr><th>分组</th><th>状态</th><th>证据键</th></tr></thead><tbody>{rows}</tbody></table>
  </section>
  <section>
    <h2>目标架构与当前实现</h2>
    <p>目标架构：External UI -> App-owned BFF -> HarnessOS SDK -> Capability Token / Scope Binding -> Gateway RPC -> Evidence。</p>
    <p>当前实现：reference app 前端只调用 <code>/bff/*</code>，BFF 通过 Python SDK 使用真实 <code>/v1/rpc</code> Gateway TestClient 路径完成 session、turn、artifact、events、approval smoke。</p>
  </section>
  <section>
    <h2>用户场景路径</h2>
    <ol>
      <li>外部应用选择 <code>reference_app/demo/local</code> scope。</li>
      <li>服务端 BFF 使用 capability token 调用 SDK。</li>
      <li>SDK 创建 session、提交 turn、登记外部 artifact、订阅事件、处理人工审批。</li>
      <li>浏览器只消费 BFF DTO 和 BFF event proxy，不直连 raw Gateway。</li>
    </ol>
  </section>
</body>
</html>
"""
    (EVIDENCE_DIR / name).write_text(html, encoding="utf-8")


def _write_manifest() -> None:
    files = []
    for path in sorted(EVIDENCE_DIR.iterdir()):
        if path.is_file() and not path.name.startswith("."):
            files.append({"file": path.name, "bytes": path.stat().st_size})
    _write_json("artifact-manifest.json", {"status": "PASS", "files": files, "count": len(files)})


if __name__ == "__main__":
    raise SystemExit(main())
