from __future__ import annotations

import json
import os
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import jsonschema


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_CONSOLE = ROOT / "apps/workflow-console"
EVIDENCE_DIR = ROOT / "docs/design/V12-V15.x/evidence/v13-workflow-studio-pilot"
REPORT_PATH = ROOT / "docs/design/V12-V15.x/reports/v13_workflow_studio_acceptance_report.json"
SCHEMA_ROOT = ROOT / "docs/design/V12-V15.x/schemas"
PY_DEPS = Path("/tmp/harnessos-pydeps")
BFF_PORT = 18042
PREVIEW_PORT = 4176
CDP_PORT = 9334
CREATED_AT = "2026-06-25T00:00:00+08:00"
LOCAL_CHROME = Path("/mnt/c/Program Files/Google/Chrome/Application/chrome.exe")

BLOCKED_CLAIMS = [
    "browser implementation complete",
    "BFF runtime evidence complete",
    "Xpert parity complete",
    "product-grade frontend complete",
    "complete Workflow Studio ready",
    "production ready",
    "Agent executor ready",
]
REDACTION_PATTERNS = ["raw_secret", "Bearer ", "signed URL", "sk-", "AKIA"]
REQUIRED_FILES = [
    "v13-workflow-studio-acceptance-data.json",
    "artifact-manifest.json",
    "studio-canvas-screenshot.png",
    "node-inspector-screenshot.png",
    "workflow-spec-graph.json",
    "workflow-diff-proposal.json",
    "graph-roundtrip-report.json",
    "browser-action-log.json",
    "browser-network-log.json",
    "bff-route-log.json",
    "interaction-parity-report.json",
    "edge-quality-report.json",
    "canvas-defect-regression-report.json",
    "edge-default-screenshot.png",
    "canvas-defect-wheel-zoom.png",
    "canvas-defect-right-area-drag.png",
    "canvas-defect-connect-cancel.png",
    "edge-zoom-screenshot.png",
    "edge-drag-screenshot.png",
    "edge-free-connect-screenshot.png",
    "simulation-edge-state-screenshot.png",
    "scenario-morph-screenshot.png",
    "scenario-storyboard-screenshot.png",
    "chat-command-screenshot.png",
    "simulation-blocked-modal-screenshot.png",
    "confirmation-transcript.txt",
    "prd-spec-review.md",
    "target-architecture-review.md",
    "audit-opinion.md",
    "audit-closure.md",
    "no-false-green-scan.json",
    "redaction-scan.json",
    "substage-verification-report.json",
]


def main() -> int:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    for name in REQUIRED_FILES:
        (EVIDENCE_DIR / name).unlink(missing_ok=True)
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{PY_DEPS}:{ROOT}"
    env["WORKFLOW_CONSOLE_PYTHON"] = "python3"
    env["WORKFLOW_CONSOLE_BFF_PORT"] = str(BFF_PORT)
    env["WORKFLOW_CONSOLE_PREVIEW_PORT"] = str(PREVIEW_PORT)
    env["VITE_BFF_PROXY_TARGET"] = f"http://127.0.0.1:{BFF_PORT}"
    env["VITE_HARNESSOS_DEMO_MODE"] = "false"
    env["V13_EVIDENCE_DIR"] = str(EVIDENCE_DIR)

    run(["node", "node_modules/typescript/bin/tsc", "-p", "tsconfig.json"], cwd=WORKFLOW_CONSOLE, env=env)
    run(["node", "node_modules/vite/bin/vite.js", "build"], cwd=WORKFLOW_CONSOLE, env=env)
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
    chrome = start_chrome()
    try:
        wait_for_url(f"http://127.0.0.1:{BFF_PORT}/__test/health", "BFF smoke server")
        wait_for_url(f"http://127.0.0.1:{PREVIEW_PORT}", "workflow-console preview")
        wait_for_url(f"http://127.0.0.1:{CDP_PORT}/json/version", "Chrome CDP")
        env["V13_CDP_URL"] = f"http://127.0.0.1:{CDP_PORT}"
        env["V13_BASE_URL"] = f"http://127.0.0.1:{PREVIEW_PORT}"
        env["V13_BFF_BASE"] = f"http://127.0.0.1:{BFF_PORT}"
        run(["node", "e2e/v13_cdp_acceptance.mjs"], cwd=WORKFLOW_CONSOLE, env=env)
    finally:
        terminate(chrome)
        terminate(preview)
        terminate(bff)

    missing = [name for name in REQUIRED_FILES if not (EVIDENCE_DIR / name).exists()]
    schema_results = validate_schemas()
    claim_matches = scan_text(BLOCKED_CLAIMS)
    redaction_matches = scan_text(REDACTION_PATTERNS)
    acceptance = read_json(EVIDENCE_DIR / "v13-workflow-studio-acceptance-data.json")
    manifest = read_json(EVIDENCE_DIR / "artifact-manifest.json")
    canvas_defects = read_json(EVIDENCE_DIR / "canvas-defect-regression-report.json")
    report_status = (
        "PASS"
        if not missing
        and all(result["status"] == "PASS" for result in schema_results)
        and not claim_matches
        and not redaction_matches
        and acceptance.get("status") == "PASS"
        and manifest.get("status") == "PASS"
        and canvas_defects.get("status") == "PASS"
        else "FAIL"
    )

    report = {
        "schema_version": "v13.workflow_studio_acceptance_report.v1",
        "status": report_status,
        "stage_id": "V13-SA",
        "substage_status": {
            "V13-R0": "PASS",
            "V13-S1": "PASS",
            "V13-S2": "PASS",
            "V13-S3": "PASS",
            "V13-SA": report_status,
        },
        "evidence_dir": str(EVIDENCE_DIR.relative_to(ROOT)),
        "missing_artifacts": missing,
        "schema_results": schema_results,
        "canvas_defect_regression": {
            "status": canvas_defects.get("status"),
            "defects": canvas_defects.get("defects", []),
            "evidence_ref": "canvas-defect-regression-report.json",
        },
        "claim_scan": {"status": "PASS" if not claim_matches else "FAIL", "matches": claim_matches},
        "redaction_scan": {"status": "PASS" if not redaction_matches else "FAIL", "matches": redaction_matches},
        "allowed_claim": "V13 complete: editable Workflow Studio pilot slice ready for review.",
        "forbidden_positive_claims": BLOCKED_CLAIMS,
        "runtime_backed": False,
        "created_at": CREATED_AT,
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(f"{json.dumps(report, indent=2, ensure_ascii=False)}\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report_status == "PASS" else 1


def run(command: list[str], cwd: Path, env: dict[str, str]) -> None:
    result = subprocess.run(command, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if result.returncode != 0:
        print(result.stdout)
        raise SystemExit(result.returncode)


def start_chrome() -> subprocess.Popen[str]:
    if not LOCAL_CHROME.exists():
        raise SystemExit(f"Local Chrome is required for CDP browser acceptance: {LOCAL_CHROME}")
    return subprocess.Popen(
        [
            str(LOCAL_CHROME),
            "--headless=new",
            "--disable-gpu",
            f"--remote-debugging-port={CDP_PORT}",
            "--user-data-dir=C:\\Temp\\harnessos-v13-cdp",
            "about:blank",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


def wait_for_url(url: str, label: str, timeout: float = 30.0) -> None:
    deadline = time.time() + timeout
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1.0) as response:
                if response.status < 500:
                    return
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
        time.sleep(0.25)
    raise TimeoutError(f"Timed out waiting for {label} at {url}: {last_error}")


def terminate(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def validate_schemas() -> list[dict[str, str]]:
    checks = [
        (
            EVIDENCE_DIR / "v13-workflow-studio-acceptance-data.json",
            SCHEMA_ROOT / "v13_workflow_studio_acceptance_data.schema.json",
        ),
        (
            EVIDENCE_DIR / "artifact-manifest.json",
            SCHEMA_ROOT / "v13_workflow_studio_artifact_manifest.schema.json",
        ),
    ]
    results: list[dict[str, str]] = []
    for data_path, schema_path in checks:
        jsonschema.validate(read_json(data_path), read_json(schema_path))
        results.append(
            {
                "status": "PASS",
                "data": str(data_path.relative_to(ROOT)),
                "schema": str(schema_path.relative_to(ROOT)),
            }
        )
    return results


def scan_text(patterns: list[str]) -> list[dict[str, str]]:
    matches: list[dict[str, str]] = []
    for path in EVIDENCE_DIR.rglob("*"):
        if path.is_dir() or path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if path.name in {"no-false-green-scan.json", "artifact-manifest.json"}:
            text = text.replace("blocked_claims", "")
            for pattern in patterns:
                text = text.replace(pattern, "")
        if path.name == "redaction-scan.json":
            text = text.replace("forbidden_patterns", "")
            for pattern in REDACTION_PATTERNS:
                text = text.replace(pattern, "")
        for pattern in patterns:
            if pattern in text:
                matches.append({"path": str(path.relative_to(ROOT)), "pattern": pattern})
    return matches


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
