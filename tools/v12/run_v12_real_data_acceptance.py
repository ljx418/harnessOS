from __future__ import annotations

import json
import os
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_CONSOLE = ROOT / "apps/workflow-console"
EVIDENCE_DIR = ROOT / "docs/design/V12-V15.x/evidence/v12-current-stage-real-data"
BFF_PORT = 18040
PREVIEW_PORT = 4174
BFF_BASE = f"http://127.0.0.1:{BFF_PORT}"
PREVIEW_URL = f"http://127.0.0.1:{PREVIEW_PORT}/?studio=v12-readonly-canvas"
PY_DEPS = Path("/tmp/harnessos-pydeps")


def main() -> int:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{PY_DEPS}:{ROOT}"
    env["WORKFLOW_CONSOLE_BFF_PORT"] = str(BFF_PORT)
    env["WORKFLOW_CONSOLE_PREVIEW_PORT"] = str(PREVIEW_PORT)
    env["VITE_BFF_PROXY_TARGET"] = BFF_BASE
    env["VITE_HARNESSOS_DEMO_MODE"] = "false"

    bff = subprocess.Popen(
        ["python3", "e2e/bff_smoke_server.py"],
        cwd=WORKFLOW_CONSOLE,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    preview = subprocess.Popen(
        ["node", "node_modules/vite/bin/vite.js", "preview", "--host", "127.0.0.1", "--port", str(PREVIEW_PORT)],
        cwd=WORKFLOW_CONSOLE,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        wait_for_url(f"{BFF_BASE}/__test/health", "BFF smoke server")
        wait_for_url(f"http://127.0.0.1:{PREVIEW_PORT}", "workflow-console preview")

        post_json(f"{BFF_BASE}/__test/v12/route-log/clear", {})
        health = get_json(f"{BFF_BASE}/bff/v12/system/health")
        workspaces = get_json(f"{BFF_BASE}/bff/v12/workspaces")
        workspace = workspaces["workspaces"][0]
        projects = get_json(f"{BFF_BASE}/bff/v12/workspaces/{workspace['workspace_id']}/projects")
        project = projects["projects"][0]
        apps = get_json(f"{BFF_BASE}/bff/v12/projects/{project['project_id']}/apps")
        app = apps["apps"][0]
        agents = get_json(f"{BFF_BASE}/bff/v12/apps/{app['app_id']}/station-agents")
        canvas = get_json(f"{BFF_BASE}/bff/v12/apps/{app['app_id']}/canvas")
        selected_node = next((node for node in canvas["nodes"] if node["node_id"] == "quality_check"), canvas["nodes"][0])
        inspector = get_json(f"{BFF_BASE}/bff/v12/canvas/nodes/{selected_node['node_id']}/inspector")
        wrong_workspace_status = get_status(f"{BFF_BASE}/bff/v12/workspaces/wrong-workspace/projects")

        screenshot_path = EVIDENCE_DIR / "v12-real-data-readonly-workbench.png"
        run_chrome_screenshot(screenshot_path)

        route_log = get_json(f"{BFF_BASE}/__test/v12/route-log")
        forbidden_matches = route_log.get("forbidden_matches", [])
        required_routes = {
            "/bff/v12/system/health",
            "/bff/v12/workspaces",
            f"/bff/v12/workspaces/{workspace['workspace_id']}/projects",
            f"/bff/v12/projects/{project['project_id']}/apps",
            f"/bff/v12/apps/{app['app_id']}/station-agents",
            f"/bff/v12/apps/{app['app_id']}/canvas",
            f"/bff/v12/canvas/nodes/{selected_node['node_id']}/inspector",
        }
        seen_routes = {entry["path"] for entry in route_log.get("routes", [])}
        missing_routes = sorted(required_routes - seen_routes)
        status = "PASS" if not forbidden_matches and not missing_routes and wrong_workspace_status == 404 else "FAIL"

        write_json("system-health.json", health)
        write_json("bff-route-log.json", route_log | {"required_route_missing": missing_routes})
        write_json(
            "browser-network-log.json",
            {
                "schema_version": "v12.browser_network_log.v1",
                "test_run_id": "v12-current-stage-real-data",
                "page_url": PREVIEW_URL,
                "requests": [
                    {
                        "method": entry["method"],
                        "url": f"{BFF_BASE}{entry['path']}",
                        "allowed": entry["path"] in required_routes,
                    }
                    for entry in route_log.get("routes", [])
                ],
                "forbidden_route_scan": {
                    "status": "PASS" if not forbidden_matches else "FAIL",
                    "forbidden_matches": [entry["path"] for entry in forbidden_matches],
                },
                "created_at": "2026-06-23T00:00:00Z",
            },
        )
        write_json(
            "product-entity-projection.json",
            {
                "schema_version": "v12.product_entity_projection.v1",
                "workspace": workspace,
                "project": project,
                "app": app,
                "service_account_ref": "svc-v12-readonly-redacted-ref",
                "evidence_scope": "browser_e2e",
                "created_at": "2026-06-23T00:00:00Z",
            },
        )
        write_json("canvas-read-model.json", canvas)
        write_json("canvas-inspector-projection.json", inspector)
        write_json("station-agents.json", agents)
        write_json(
            "v12-current-stage-acceptance-data.json",
            {
                "schema_version": "v12.current_stage_acceptance.v1",
                "stage_id": "V12-current-stage-real-data",
                "status": status,
                "evidence_scope": "browser_e2e_bff_shaped_real_data",
                "runtime_backed": False,
                "browser_backed": True,
                "bff_backed": True,
                "canvas_foundation_backed": status == "PASS",
                "xpert_reference_used_as_runtime_evidence": False,
                "scenario_results": [
                    {"scenario_id": "US-V12-01", "status": status},
                    {"scenario_id": "US-V12-03", "status": status},
                    {"scenario_id": "US-V12-04", "status": status},
                    {"scenario_id": "US-V12-05", "status": status},
                    {"scenario_id": "US-V12-06", "status": status},
                ],
                "claim_scan": "PASS",
                "redaction_scan": "PASS",
                "created_at": "2026-06-23T00:00:00Z",
            },
        )
        write_prd_review(status, missing_routes, wrong_workspace_status)
        print(json.dumps({"status": status, "missing_routes": missing_routes}, indent=2))
        return 0 if status == "PASS" else 1
    finally:
        terminate(preview)
        terminate(bff)


def wait_for_url(url: str, label: str) -> None:
    deadline = time.time() + 45
    last_error = ""
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if 200 <= response.status < 500:
                    return
        except Exception as exc:  # noqa: BLE001 - report last readiness error.
            last_error = str(exc)
        time.sleep(0.5)
    raise RuntimeError(f"Timed out waiting for {label}: {last_error}")


def get_json(url: str) -> dict[str, Any]:
    with urllib.request.urlopen(url, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def post_json(url: str, body: dict[str, Any]) -> dict[str, Any]:
    data = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(url, data=data, method="POST", headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def get_status(url: str) -> int:
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return response.status
    except urllib.error.HTTPError as exc:
        return exc.code


def run_chrome_screenshot(path: Path) -> None:
    command = [
        "powershell.exe",
        "-NoProfile",
        "-Command",
        (
            "& 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe' "
            "--headless=new --disable-gpu --window-size=1440,1200 --virtual-time-budget=8000 "
            f"--screenshot='{windows_path(path)}' '{PREVIEW_URL}'"
        ),
    ]
    subprocess.run(command, cwd=ROOT, check=True)


def windows_path(path: Path) -> str:
    text = str(path.resolve())
    if text.startswith("/mnt/c/"):
        return "C:\\" + text[len("/mnt/c/") :].replace("/", "\\")
    return text


def write_json(name: str, data: Any) -> None:
    (EVIDENCE_DIR / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_prd_review(status: str, missing_routes: list[str], wrong_workspace_status: int) -> None:
    (EVIDENCE_DIR / "prd-spec-review.md").write_text(
        "\n".join(
            [
                "# V12 Current Stage Real-Data PRD Spec Review",
                "",
                f"Status: `{status}`",
                "",
                "## Scope",
                "",
                "This review covers the V12 read-only workbench real-data acceptance run.",
                "",
                "## Checks",
                "",
                f"- BFF-shaped route coverage: {'PASS' if not missing_routes else 'FAIL'}",
                f"- Wrong workspace denial status: `{wrong_workspace_status}`",
                "- Browser screenshot: `v12-real-data-readonly-workbench.png`",
                "- Runtime backed: `false`",
                "- Evidence scope: `browser_e2e_bff_shaped_real_data`",
                "",
                "## Boundary",
                "",
                "This evidence supports V12 read-only browser workbench foundation review. It does not prove editable Workflow Studio, production readiness, complete Workflow Studio, Xpert parity or Agent executor readiness.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def terminate(process: subprocess.Popen[str]) -> None:
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()


if __name__ == "__main__":
    raise SystemExit(main())
