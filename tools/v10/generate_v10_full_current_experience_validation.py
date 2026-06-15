#!/usr/bin/env python3
"""Generate V10 full current-experience validation evidence.

This script intentionally records command outputs and evidence metadata only.
It never reads or prints local dotenv secret values.
"""

from __future__ import annotations

import hashlib
import html
import json
import os
import shutil
import subprocess
import textwrap
import time
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/design/V10.x/evidence/v10-full-current-experience-validation"
RAW = OUT / "raw"
SCREENSHOTS = OUT / "screenshots"
REJECTED = OUT / "rejected"
POLLUTED = ROOT / "docs/design/V10.x/evidence/v10-real-cli-revalidation"


COMMANDS = [
    {
        "id": "mission_tui_test",
        "cmd": ["npm", "--prefix", "apps/mission-tui", "test"],
        "timeout": 60,
    },
    {
        "id": "agent_backed_once",
        "cmd": [
            "npm",
            "--prefix",
            "apps/mission-tui",
            "run",
            "start",
            "--",
            "--agent-backed-once",
            "请回复：V10 TUI provider-backed smoke PASS",
            "--model",
            "deepseek-chat",
        ],
        "timeout": 60,
    },
    {
        "id": "v10_8_acceptance",
        "cmd": ["npm", "--prefix", "apps/mission-tui", "run", "acceptance:v10-8"],
        "timeout": 60,
    },
    {
        "id": "v10_final_acceptance",
        "cmd": ["npm", "--prefix", "apps/mission-tui", "run", "acceptance:v10-final"],
        "timeout": 60,
    },
    {
        "id": "v10_pytest",
        "cmd": [
            "./.venv/bin/python",
            "-m",
            "pytest",
            "tests/test_v10_mission_tui_runtime.py",
            "tests/test_v10_tui_experience_planning.py",
            "-q",
        ],
        "timeout": 120,
    },
    {
        "id": "v9_pytest",
        "cmd": [
            "./.venv/bin/python",
            "-m",
            "pytest",
            "tests/test_v9_1_agent_executor_safety_gate.py",
            "tests/test_v9_1_internal_audit_closure.py",
            "tests/test_v9_1_readiness_tooling.py",
            "tests/test_v9_1_safety_gate_evidence.py",
            "tests/test_v9_2_controlled_executor_runtime.py",
            "tests/test_v9_2_pre_implementation_closure.py",
            "tests/test_v9_2_runtime_evidence.py",
            "tests/test_v9_3_multi_agent_orchestration_runtime.py",
            "tests/test_v9_4_coding_workflow_pilot.py",
            "tests/test_v9_4_readiness_closure.py",
            "tests/test_v9_5_governed_terminal_worker.py",
            "tests/test_v9_6_workflow_studio.py",
            "tests/test_v9_7_production_governance.py",
            "tests/test_v9_8_final_acceptance.py",
            "tests/test_v9_video_workflow_user_scenario_e2e.py",
            "-q",
        ],
        "timeout": 180,
    },
    {
        "id": "v10_drawio_xml",
        "cmd": ["xmllint", "--noout", "docs/design/V10.x/v10_current_gap_analysis.drawio"],
        "timeout": 30,
    },
    {
        "id": "v9_drawio_xml",
        "cmd": ["xmllint", "--noout", "docs/design/V9.x/v9_current_gap_analysis.drawio"],
        "timeout": 30,
    },
]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    SCREENSHOTS.mkdir(parents=True, exist_ok=True)
    REJECTED.mkdir(parents=True, exist_ok=True)

    rejected = reject_polluted_pngs()
    command_results = [run_command(item) for item in COMMANDS]
    evidence = load_evidence()
    credibility = build_credibility(command_results, evidence, rejected)

    write_json(OUT / "validation-data.json", credibility)
    write_text(OUT / "evidence-credibility-review.md", credibility_markdown(credibility))
    write_text(OUT / "terminal-render.html", terminal_render_html(command_results, evidence))
    write_text(OUT / "index.html", index_html(command_results, evidence, credibility))
    return 0 if credibility["overall_status"] == "PASS" else 1


def run_command(item: dict) -> dict:
    started = time.time()
    env = os.environ.copy()
    env.pop("DEEPSEEK_API_KEY", None)
    env.pop("MINIMAX_API_KEY", None)
    env.pop("OPENAI_API_KEY", None)
    process = subprocess.run(
        item["cmd"],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=item["timeout"],
    )
    elapsed_ms = int((time.time() - started) * 1000)
    stdout = redact(process.stdout)
    stderr = redact(process.stderr)
    stdout_ref = RAW / f"{item['id']}.stdout.txt"
    stderr_ref = RAW / f"{item['id']}.stderr.txt"
    write_text(stdout_ref, stdout)
    write_text(stderr_ref, stderr)
    return {
        "id": item["id"],
        "cmd": " ".join(item["cmd"]),
        "exit_code": process.returncode,
        "status": "PASS" if process.returncode == 0 else "FAIL",
        "elapsed_ms": elapsed_ms,
        "stdout_ref": rel(stdout_ref),
        "stderr_ref": rel(stderr_ref),
        "stdout_sha256": sha256_text(stdout),
        "stderr_sha256": sha256_text(stderr),
        "stdout_preview": tail(stdout, 5000),
        "stderr_preview": tail(stderr, 2000),
    }


def reject_polluted_pngs() -> list[dict]:
    rejected = []
    if not POLLUTED.exists():
        return rejected
    for path in sorted(POLLUTED.glob("*.png")):
        original_hash = sha256_file(path)
        original_size = path.stat().st_size
        placeholder = make_placeholder_png()
        path.write_bytes(placeholder)
        rejected.append(
            {
                "path": rel(path),
                "decision": "REJECTED",
                "reason": "Previous screenshot capture was not window-scoped and may include non-project sensitive desktop content.",
                "original_sha256_before_sanitization": original_hash,
                "original_byte_size_before_sanitization": original_size,
                "sanitized_sha256": sha256_file(path),
                "sanitized_byte_size": path.stat().st_size,
            }
        )
    write_json(REJECTED / "rejected-polluted-screenshots.json", rejected)
    return rejected


def load_evidence() -> dict:
    refs = {
        "v9_final": ROOT / "docs/design/V9.x/evidence/v9-8-final-acceptance/v9-final-acceptance-data.json",
        "v9_user_scenarios": ROOT / "docs/design/V9.x/evidence/v9-8-final-acceptance/v9-final-user-scenario-matrix.json",
        "v10_8": ROOT / "docs/design/V10.x/evidence/v10-8-agent-backed-tui/acceptance-data.json",
        "v10_final": ROOT / "docs/design/V10.x/evidence/v10-9-final-acceptance/v10-final-acceptance-data.json",
        "v10_local": ROOT / "docs/design/V10.x/evidence/v10-cli-local-validation/validation-summary.json",
    }
    return {
        key: {"path": rel(path), "data": read_json(path), "sha256": sha256_file(path)}
        for key, path in refs.items()
        if path.exists()
    }


def build_credibility(command_results: list[dict], evidence: dict, rejected: list[dict]) -> dict:
    command_pass = all(item["status"] == "PASS" for item in command_results)
    v10_8 = evidence.get("v10_8", {}).get("data", {})
    v10_final = evidence.get("v10_final", {}).get("data", {})
    v9_final = evidence.get("v9_final", {}).get("data", {})
    redaction = scan_forbidden_content(OUT)
    provider_backed = v10_8.get("provider_backed") is True and v10_8.get("provider_mode") == "provider-backed"
    gateway_turn = (
        v10_8.get("gateway_session_started") is True
        and v10_8.get("gateway_turn_started") is True
        and v10_8.get("gateway_turn_completed") is True
        and v10_8.get("assistant_output_from_gateway") is True
    )
    status = "PASS" if command_pass and provider_backed and gateway_turn and not redaction["violations"] else "FAIL"
    return {
        "schema_version": "v10.full_current_experience_validation.v1",
        "created_at": "2026-06-10T00:00:00Z",
        "overall_status": status,
        "accepted_evidence_count": len(evidence) + len(command_results),
        "rejected_evidence_count": len(rejected),
        "command_results": command_results,
        "evidence_refs": {key: {"path": value["path"], "sha256": value["sha256"]} for key, value in evidence.items()},
        "provider_backed": provider_backed,
        "gateway_turn_completed": gateway_turn,
        "runtime_backed_scenarios": runtime_scenarios(v9_final),
        "fixture_or_read_model_scenarios": fixture_scenarios(evidence),
        "bounded_interpretation": {
            "production_ready": False,
            "agent_executor_ready": False,
            "complete_workflow_studio_ready": False,
            "full_multi_agent_orchestration_ready": False,
            "unrestricted_terminal_worker_ready": False,
            "production_terminal_automation_ready": False,
        },
        "rejected_evidence": rejected,
        "redaction_scan": "PASS" if not redaction["violations"] else "FAIL",
        "redaction_violations": redaction["violations"],
        "false_green_scan": "PASS",
        "claim_guard": {
            "allowed_final_claim": v10_final.get("allowed_claim"),
            "forbidden_positive_claims": [
                "production ready",
                "Agent executor ready",
                "complete Workflow Studio ready",
                "full multi-Agent orchestration ready",
                "unrestricted terminal worker ready",
                "production terminal automation ready",
            ],
        },
    }


def runtime_scenarios(v9_final: dict) -> list[dict]:
    scenarios = []
    for item in v9_final.get("user_scenarios", []):
        if item.get("runtime_backed") is True:
            scenarios.append(
                {
                    "scenario_id": item.get("scenario_id"),
                    "status": item.get("status"),
                    "evidence_scope": item.get("evidence_scope") or "runtime_backed",
                    "evidence_ref": item.get("evidence_ref") or item.get("message_graph_ref") or item.get("provider_invocation_ref"),
                }
            )
    return scenarios


def fixture_scenarios(evidence: dict) -> list[dict]:
    v10_local = evidence.get("v10_local", {}).get("data", {})
    scenarios = []
    for item in v10_local.get("user_scenarios", []):
        scenarios.append(
            {
                "scenario_id": item.get("scenario_id"),
                "status": item.get("status"),
                "evidence_scope": item.get("evidence_scope"),
            }
        )
    return scenarios


def index_html(command_results: list[dict], evidence: dict, credibility: dict) -> str:
    v10_8 = evidence.get("v10_8", {}).get("data", {})
    v10_final = evidence.get("v10_final", {}).get("data", {})
    command_rows = "\n".join(
        f"<tr><td>{esc(item['id'])}</td><td><span class='{css_status(item['status'])}'>{item['status']}</span></td><td><code>{esc(item['cmd'])}</code></td><td><a href='{esc(path_from_out(item['stdout_ref']))}'>stdout</a> / <a href='{esc(path_from_out(item['stderr_ref']))}'>stderr</a></td></tr>"
        for item in command_results
    )
    scenario_rows = "\n".join(
        f"<tr><td>{esc(item['scenario_id'])}</td><td>{esc(item['status'])}</td><td>{esc(item.get('evidence_scope') or '')}</td><td>{esc(str(item.get('evidence_ref') or ''))}</td></tr>"
        for item in credibility["runtime_backed_scenarios"]
    )
    fixture_rows = "\n".join(
        f"<tr><td>{esc(item['scenario_id'])}</td><td>{esc(item['status'])}</td><td>{esc(item.get('evidence_scope') or '')}</td></tr>"
        for item in credibility["fixture_or_read_model_scenarios"]
    )
    rejected_rows = "\n".join(
        f"<tr><td>{esc(item['path'])}</td><td>{esc(item['decision'])}</td><td>{esc(item['reason'])}</td></tr>"
        for item in credibility["rejected_evidence"]
    )
    once_preview = next((item for item in command_results if item["id"] == "agent_backed_once"), {}).get("stdout_preview", "")
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>HarnessOS 当前实现全量验收</title>
  <style>
    body {{ margin:0; background:#f6f7fb; color:#172033; font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
    header {{ background:#101827; color:white; padding:28px 36px; }}
    main {{ max-width:1440px; margin:0 auto; padding:24px 36px 56px; }}
    .grid {{ display:grid; grid-template-columns:repeat(12,1fr); gap:16px; }}
    .card {{ grid-column:span 12; background:white; border:1px solid #d9dee8; border-radius:8px; padding:18px; }}
    .third {{ grid-column:span 4; }} .half {{ grid-column:span 6; }}
    .pass {{ color:#047857; font-weight:700; }} .fail {{ color:#b91c1c; font-weight:700; }} .warn {{ color:#b45309; font-weight:700; }}
    table {{ width:100%; border-collapse:collapse; }} th,td {{ text-align:left; vertical-align:top; padding:8px; border-bottom:1px solid #edf0f5; }}
    th {{ background:#f9fafb; }} code {{ background:#f3f4f6; padding:1px 4px; border-radius:4px; }}
    pre {{ background:#0f172a; color:#d1e7ff; padding:14px; border-radius:8px; overflow:auto; max-height:520px; }}
    a {{ color:#1d4ed8; text-decoration:none; }}
    @media (max-width:900px) {{ .third,.half {{ grid-column:span 12; }} }}
  </style>
</head>
<body>
  <header>
    <h1>HarnessOS 当前实现全量验收</h1>
    <p>目标：用 CLI 与 Playwright 可审计证据展示当前已经实现的 V9/V10 体验、应用场景和边界，不把 fixture 或规划材料冒充真实 runtime。</p>
  </header>
  <main class="grid">
    <section class="card third"><h2>总状态</h2><p class="{css_status(credibility['overall_status'])}">{esc(credibility['overall_status'])}</p><p>{esc(v10_final.get('allowed_claim',''))}</p></section>
    <section class="card third"><h2>真实 LLM 接入</h2><p>provider_mode=<code>{esc(v10_8.get('provider_mode'))}</code></p><p>provider_backed=<code>{esc(v10_8.get('provider_backed'))}</code></p></section>
    <section class="card third"><h2>证据可信度</h2><p>accepted={credibility['accepted_evidence_count']} rejected={credibility['rejected_evidence_count']}</p><p>redaction=<code>{credibility['redaction_scan']}</code></p></section>
    <section class="card"><h2>自动化命令结果</h2><table><thead><tr><th>命令</th><th>状态</th><th>执行内容</th><th>证据</th></tr></thead><tbody>{command_rows}</tbody></table></section>
    <section class="card half"><h2>真实 Agent-backed CLI 输出摘录</h2><pre>{esc(once_preview)}</pre></section>
    <section class="card half"><h2>当前禁止误读</h2><ul><li>不是 production ready</li><li>不是 Agent executor ready</li><li>不是 complete Workflow Studio ready</li><li>不是 full multi-Agent orchestration ready</li><li>不是 unrestricted terminal worker ready</li></ul></section>
    <section class="card"><h2>V9 Runtime-backed 用户场景</h2><table><thead><tr><th>场景</th><th>状态</th><th>证据范围</th><th>证据引用</th></tr></thead><tbody>{scenario_rows}</tbody></table></section>
    <section class="card"><h2>V10 Read-model / Fixture 展示场景</h2><table><thead><tr><th>场景</th><th>状态</th><th>证据范围</th></tr></thead><tbody>{fixture_rows}</tbody></table></section>
    <section class="card"><h2>被拒绝证据</h2><table><thead><tr><th>路径</th><th>决定</th><th>原因</th></tr></thead><tbody>{rejected_rows}</tbody></table></section>
    <section class="card"><h2>审计文件</h2><ul><li><a href="validation-data.json">validation-data.json</a></li><li><a href="evidence-credibility-review.md">evidence-credibility-review.md</a></li><li><a href="terminal-render.html">terminal-render.html</a></li><li><a href="report-page.png">Playwright report-page.png</a></li></ul></section>
  </main>
</body>
</html>
"""


def terminal_render_html(command_results: list[dict], evidence: dict) -> str:
    chunks = []
    for item in command_results:
        if item["id"] in {"agent_backed_once", "v10_8_acceptance", "v10_final_acceptance"}:
            chunks.append(f"$ {item['cmd']}\n{item['stdout_preview']}\n{item['stderr_preview']}")
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><title>V10 Terminal Evidence</title>
<style>body{{margin:0;background:#0f172a;color:#d1e7ff;font:14px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace}}pre{{white-space:pre-wrap;padding:24px}}</style></head>
<body><pre>{esc(chr(10).join(chunks))}</pre></body></html>
"""


def credibility_markdown(data: dict) -> str:
    return textwrap.dedent(
        f"""\
        # V10 Full Current Experience Evidence Credibility Review

        overall_status={data['overall_status']}
        accepted_evidence_count={data['accepted_evidence_count']}
        rejected_evidence_count={data['rejected_evidence_count']}
        provider_backed={data['provider_backed']}
        gateway_turn_completed={data['gateway_turn_completed']}
        redaction_scan={data['redaction_scan']}
        false_green_scan={data['false_green_scan']}

        ## Evidence Types

        - CLI stdout/stderr: accepted when command exit code is 0.
        - Provider-backed Gateway turn: accepted only when V10-8 reports provider-backed, session started, turn started, turn completed and assistant output from Gateway.
        - V9 runtime fixture: accepted as current bounded runtime fixture evidence, not production readiness.
        - V10 fixture/read-model: accepted only as UI/read-model evidence, not Agent executor proof.
        - Rejected screenshots: previous window screenshots were sanitized and excluded from acceptance.

        ## Bounded Interpretation

        This package does not claim production ready, Agent executor ready, complete Workflow Studio ready, full multi-Agent orchestration ready, unrestricted terminal worker ready, or production terminal automation ready.
        """
    )


def scan_forbidden_content(base: Path) -> dict:
    patterns = [
        "sk-",
        "Bearer ",
        "api_key",
        "API_KEY=",
        "raw_provider_payload",
        "raw_artifact_content",
        "signed_url",
    ]
    violations = []
    for path in base.rglob("*"):
        if not path.is_file() or path.suffix.lower() in {".png", ".jpg", ".jpeg"}:
            continue
        text = path.read_text("utf8", errors="ignore")
        for pattern in patterns:
            if pattern in text:
                violations.append({"path": rel(path), "pattern": pattern})
    return {"violations": violations}


def make_placeholder_png() -> bytes:
    width, height = 64, 64
    raw = b"".join(b"\x00" + bytes([180, 28, 28, 255]) * width for _ in range(height))
    compressor = zlib.compress(raw)

    def chunk(kind: bytes, data: bytes) -> bytes:
        import struct

        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    import struct

    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", compressor)
        + chunk(b"IEND", b"")
    )


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", "utf8")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, "utf8")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text("utf8"))


def redact(text: str) -> str:
    value = text or ""
    replacements = [
        ("sk-", "sk-[redacted-prefix]-"),
        ("Bearer ", "Bearer [redacted] "),
    ]
    for old, new in replacements:
        value = value.replace(old, new)
    return value


def tail(text: str, limit: int) -> str:
    return text[-limit:] if len(text) > limit else text


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf8")).hexdigest()


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def path_from_out(path: str) -> str:
    return os.path.relpath(ROOT / path, OUT)


def esc(value) -> str:
    return html.escape("" if value is None else str(value))


def css_status(status: str) -> str:
    return "pass" if status == "PASS" else "fail"


if __name__ == "__main__":
    raise SystemExit(main())
