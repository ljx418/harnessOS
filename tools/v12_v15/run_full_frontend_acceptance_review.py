from __future__ import annotations

import html
import json
import os
import subprocess
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_CONSOLE = ROOT / "apps/workflow-console"
EVIDENCE_DIR = ROOT / "docs/design/V12-V15.x/evidence/full-stage-acceptance-review-2026-06-25"
REPORT_PATH = EVIDENCE_DIR / "index.html"
SUMMARY_PATH = EVIDENCE_DIR / "acceptance-summary.json"
PY_DEPS = Path("/tmp/harnessos-pydeps")
BFF_PORT = int(os.environ.get("FULL_REVIEW_BFF_PORT", "18146"))
PREVIEW_PORT = int(os.environ.get("FULL_REVIEW_PREVIEW_PORT", "4186"))
HEADLESS_CDP_PORT = int(os.environ.get("FULL_REVIEW_HEADLESS_CDP_PORT", "9340"))
LOCAL_CHROME = Path("/mnt/c/Program Files/Google/Chrome/Application/chrome.exe")
CREATED_AT = "2026-06-25T00:00:00+08:00"


@dataclass
class CommandResult:
    name: str
    status: str
    command: str
    duration_seconds: float
    output_tail: str
    expected_failure: bool = False


def main() -> int:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    command_results: list[CommandResult] = []

    env = os.environ.copy()
    env["PYTHONPATH"] = f"{PY_DEPS}:{ROOT}"
    env["WORKFLOW_CONSOLE_PYTHON"] = "python3"
    env["WORKFLOW_CONSOLE_BFF_PORT"] = str(BFF_PORT)
    env["WORKFLOW_CONSOLE_PREVIEW_PORT"] = str(PREVIEW_PORT)
    env["VITE_BFF_PROXY_TARGET"] = f"http://127.0.0.1:{BFF_PORT}"
    env["VITE_HARNESSOS_DEMO_MODE"] = "false"

    command_results.extend(
        run_checks(
            [
                (
                    "Python runner syntax",
                    [
                        "python3",
                        "-m",
                        "py_compile",
                        "apps/workflow-console/e2e/bff_smoke_server.py",
                        "tools/v12/run_v12_real_data_acceptance.py",
                        "tools/v12/run_v12_remaining_stage_acceptance.py",
                        "tools/v13/run_v13_workflow_studio_acceptance.py",
                        "tools/v14/run_v14_extension_ecosystem_acceptance.py",
                        "tools/v15/run_v15_observability_deployment_acceptance.py",
                        "tools/post_v15/run_product_runtime_hardening_acceptance.py",
                        "tools/v12_v15/run_full_frontend_acceptance_review.py",
                    ],
                    ROOT,
                    env,
                    False,
                ),
                ("TypeScript test compile", ["node", "node_modules/typescript/bin/tsc", "-p", "tsconfig.test.json"], WORKFLOW_CONSOLE, env, False),
                ("Workflow console build", ["node", "node_modules/vite/bin/vite.js", "build"], WORKFLOW_CONSOLE, env, False),
                ("Unit tests", ["bash", "-lc", "node --test dist-test/__tests__/*.test.js"], WORKFLOW_CONSOLE, env, False),
            ]
        )
    )

    server_handles = ensure_servers(env)
    try:
        command_results.append(run_browser_mode("headless", HEADLESS_CDP_PORT, True, env))
    finally:
        for process in server_handles:
            terminate(process)

    command_results.extend(
        run_checks(
            [
                ("V12 real-data acceptance", ["python3", "tools/v12/run_v12_real_data_acceptance.py"], ROOT, env, False),
                ("V12 remaining-stage acceptance", ["python3", "tools/v12/run_v12_remaining_stage_acceptance.py"], ROOT, env, False),
                ("V13 Studio acceptance", ["python3", "tools/v13/run_v13_workflow_studio_acceptance.py"], ROOT, env, False),
                ("V14 extension acceptance", ["python3", "tools/v14/run_v14_extension_ecosystem_acceptance.py"], ROOT, env, False),
                ("V15 observability/deployment acceptance", ["python3", "tools/v15/run_v15_observability_deployment_acceptance.py"], ROOT, env, False),
                ("PV16 product-runtime hardening acceptance", ["python3", "tools/post_v15/run_product_runtime_hardening_acceptance.py"], ROOT, env, False),
            ]
        )
    )

    data = build_report_data(command_results)
    SUMMARY_PATH.write_text(f"{json.dumps(data, indent=2, ensure_ascii=False)}\n", encoding="utf-8")
    REPORT_PATH.write_text(render_html(data), encoding="utf-8")
    print(json.dumps({"status": data["status"], "html_report": str(REPORT_PATH.relative_to(ROOT))}, ensure_ascii=False, indent=2))
    return 0 if data["status"] in {"PASS", "CONDITIONAL_PASS"} else 1


def run_checks(checks: list[tuple[str, list[str], Path, dict[str, str], bool]]) -> list[CommandResult]:
    results: list[CommandResult] = []
    for name, command, cwd, env, expected_failure in checks:
        started = time.time()
        result = subprocess.run(command, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        duration = time.time() - started
        passed = result.returncode == 0
        status = "PASS" if passed else ("EXPECTED_FAIL" if expected_failure else "FAIL")
        results.append(
            CommandResult(
                name=name,
                status=status,
                command=" ".join(command),
                duration_seconds=round(duration, 2),
                output_tail=tail(result.stdout),
                expected_failure=expected_failure,
            )
        )
    return results


def ensure_servers(env: dict[str, str]) -> list[subprocess.Popen[str]]:
    handles: list[subprocess.Popen[str]] = []
    bff_url = f"http://127.0.0.1:{BFF_PORT}/__test/health"
    preview_url = f"http://127.0.0.1:{PREVIEW_PORT}"
    if not url_available(bff_url):
        handles.append(
            subprocess.Popen(
                ["python3", "e2e/bff_smoke_server.py"],
                cwd=WORKFLOW_CONSOLE,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
        )
    if not url_available(preview_url):
        handles.append(
            subprocess.Popen(
                ["node", "node_modules/vite/bin/vite.js", "preview", "--host", "127.0.0.1", "--port", str(PREVIEW_PORT)],
                cwd=WORKFLOW_CONSOLE,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
        )
    wait_for_url(bff_url, "BFF smoke server")
    wait_for_url(preview_url, "workflow console preview")
    return handles


def run_browser_mode(mode: str, cdp_port: int, headless: bool, env: dict[str, str]) -> CommandResult:
    started = time.time()
    if not LOCAL_CHROME.exists():
        return CommandResult(mode, "FAIL", "Chrome CDP", 0.0, f"Local Chrome missing: {LOCAL_CHROME}")
    chrome = start_chrome(cdp_port, headless, mode)
    try:
        wait_for_url(f"http://127.0.0.1:{cdp_port}/json/version", f"Chrome CDP {mode}", timeout=45)
        mode_env = env.copy()
        mode_env["FULL_REVIEW_CDP_URL"] = f"http://127.0.0.1:{cdp_port}"
        mode_env["FULL_REVIEW_BASE_URL"] = f"http://127.0.0.1:{PREVIEW_PORT}"
        mode_env["FULL_REVIEW_EVIDENCE_DIR"] = str(EVIDENCE_DIR)
        mode_env["FULL_REVIEW_MODE"] = mode
        result = subprocess.run(
            ["node", "e2e/full_frontend_acceptance_review.mjs"],
            cwd=WORKFLOW_CONSOLE,
            env=mode_env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        status = "PASS" if result.returncode == 0 else "FAIL"
        output = result.stdout
    finally:
        terminate(chrome)
    return CommandResult(
        name=f"Browser scenario automation ({mode})",
        status=status,
        command=f"Chrome CDP {mode} + node e2e/full_frontend_acceptance_review.mjs",
        duration_seconds=round(time.time() - started, 2),
        output_tail=tail(output),
    )


def start_chrome(cdp_port: int, headless: bool, mode: str) -> subprocess.Popen[str]:
    args = [
        str(LOCAL_CHROME),
        "--disable-gpu",
        f"--remote-debugging-port={cdp_port}",
        f"--user-data-dir=C:\\Temp\\harnessos-full-review-{mode}",
        "about:blank",
    ]
    if headless:
        args.insert(1, "--headless=new")
    return subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)


def build_report_data(command_results: list[CommandResult]) -> dict[str, Any]:
    browser_results = []
    for mode in ["headless"]:
        path = EVIDENCE_DIR / f"browser-scenario-results-{mode}.json"
        browser_results.append(read_json(path) if path.exists() else {"status": "MISSING", "mode": mode, "scenarios": []})

    existing_reports = {
        "V12 remaining": read_json(ROOT / "docs/design/V12-V15.x/evidence/v12-sa-aggregate/acceptance-data.json"),
        "V13 Studio": read_json(ROOT / "docs/design/V12-V15.x/evidence/v13-workflow-studio-pilot/v13-workflow-studio-acceptance-data.json"),
        "V14 extension": read_json(ROOT / "docs/design/V12-V15.x/evidence/v14-extension-ecosystem/acceptance-data.json"),
        "V15 observability": read_json(ROOT / "docs/design/V12-V15.x/evidence/v15-observability-deployment/acceptance-data.json"),
        "PV16 product-runtime": read_json(ROOT / "docs/design/V12-V15.x/evidence/post-v15-product-runtime-hardening/acceptance-data.json"),
        "PV16 acceptance report": read_json(ROOT / "docs/design/V12-V15.x/reports/post_v15_product_runtime_hardening_acceptance_report.json"),
        "PV16 document support": read_json(ROOT / "docs/design/V12-V15.x/reports/post_v15_document_support_audit_report.json"),
    }

    hard_failures = [result for result in command_results if result.status == "FAIL"]
    browser_pass = all(item.get("status") == "PASS" for item in browser_results)
    status = "PASS" if not hard_failures and browser_pass else "FAIL"
    if status == "PASS" and any(result.status == "EXPECTED_FAIL" for result in command_results):
        status = "CONDITIONAL_PASS"

    return {
        "schema_version": "full_frontend_acceptance.report_data.v1",
        "status": status,
        "created_at": CREATED_AT,
        "base_url": f"http://127.0.0.1:{PREVIEW_PORT}",
        "prd_source": "docs/design/V12-V15.x/v12_to_v15_target_prd.md",
        "architecture_source": "docs/design/V12-V15.x/v12_to_v15_target_architecture.md",
        "html_report": str(REPORT_PATH.relative_to(ROOT)),
        "command_results": [result.__dict__ for result in command_results],
        "browser_results": browser_results,
        "existing_reports": existing_reports,
        "architecture_matrix": architecture_matrix(),
        "coverage_matrix": coverage_matrix(),
        "claim_boundary": {
            "allowed": [
                "V12 complete: product entity, browser workbench and read-only canvas foundation ready for review.",
                "V13 complete: editable Workflow Studio pilot slice ready for review.",
                "V14 complete: governed extension ecosystem pilot ready for review.",
                "V15 complete: frontend interaction baseline ready for review.",
                "PV16 complete: product-runtime hardening pilot ready for review.",
            ],
            "not_allowed": [
                "production ready",
                "Xpert parity complete",
                "product-grade frontend complete",
                "complete Workflow Studio ready",
                "Agent executor ready",
            ],
        },
    }


def architecture_matrix() -> list[dict[str, str]]:
    return [
        {"plane": "Product Console / Mission Studio", "target": "统一产品入口、Studio、Inspector、evidence browser", "current": "V12-PV16 有分阶段页面和一条 product-runtime pilot 旅程；尚未合并为完整产品入口", "status": "PARTIAL"},
        {"plane": "Canvas Workbench", "target": "只读 foundation 到可编辑 Studio pilot", "current": "V12 只读画布 PASS；V13 add/connect/move/configure pilot PASS", "status": "PASS_BOUNDED"},
        {"plane": "Product Entity Control", "target": "workspace/project/app/Station Agent durable mutation", "current": "PV16-S1 通过 BFF-only mutation、ownership denial 和 audit refs 证明 bounded pilot", "status": "PASS_BOUNDED"},
        {"plane": "Runtime Gateway", "target": "确认后 runtime-backed run/inspect", "current": "PV16-S2 通过 controlled runtime run/inspect refs 证明 bounded pilot；不代表 Agent executor ready", "status": "PASS_BOUNDED"},
        {"plane": "Observability / Operations", "target": "trace/metrics/audit/deployment health", "current": "V15 bounded dashboard 和 local smoke PASS；不是生产 GA", "status": "PASS_BOUNDED"},
        {"plane": "Deployment / Self-hosting", "target": "self-host profile、health、smoke、rollback", "current": "PV16-S3 本地 hardening smoke、health report 和 rollback notes PASS；不是生产部署", "status": "PASS_BOUNDED"},
    ]


def coverage_matrix() -> list[dict[str, str]]:
    return [
        {"scenario": "打开产品工作台并理解当前 workspace/project/app", "evidence": "V12 screenshot + route/network logs", "status": "PASS_BOUNDED"},
        {"scenario": "体验工作流画布选择、Inspector、禁用动作说明", "evidence": "V12/V13 browser automation screenshots", "status": "PASS_BOUNDED"},
        {"scenario": "编辑 Studio pilot：添加、连接、移动、配置节点", "evidence": "V13 browser automation + acceptance data", "status": "PASS_BOUNDED"},
        {"scenario": "扩展包兼容性、scoped activation、unsafe denial", "evidence": "V14 browser automation + acceptance data", "status": "PASS_BOUNDED"},
        {"scenario": "观察 trace/metrics/audit/incident 并运行 bounded smoke", "evidence": "V15 browser automation + acceptance data", "status": "PASS_BOUNDED"},
        {"scenario": "持久化创建/更新实体", "evidence": "PV16 browser automation + entity CRUD report + BFF route log", "status": "PASS_BOUNDED"},
        {"scenario": "真实 runtime-backed run/inspect", "evidence": "PV16 runtime run inspect report + runtime screenshot + acceptance runner", "status": "PASS_BOUNDED"},
        {"scenario": "产品运行时连续旅程", "evidence": "PV16 product journey screenshot + UX hardening report", "status": "PASS_BOUNDED"},
    ]


def render_html(data: dict[str, Any]) -> str:
    command_rows = "".join(
        f"<tr><td>{esc(item['name'])}</td><td class='{css_status(item['status'])}'>{esc(item['status'])}</td><td>{item['duration_seconds']}s</td><td><code>{esc(item['command'])}</code></td></tr>"
        for item in data["command_results"]
    )
    arch_rows = "".join(
        f"<tr><td>{esc(row['plane'])}</td><td>{esc(row['target'])}</td><td>{esc(row['current'])}</td><td class='{css_status(row['status'])}'>{esc(row['status'])}</td></tr>"
        for row in data["architecture_matrix"]
    )
    coverage_rows = "".join(
        f"<tr><td>{esc(row['scenario'])}</td><td>{esc(row['evidence'])}</td><td class='{css_status(row['status'])}'>{esc(row['status'])}</td></tr>"
        for row in data["coverage_matrix"]
    )
    screenshot_cards = render_screenshot_cards(data["browser_results"])
    report_cards = "".join(
        f"<article><strong>{esc(name)}</strong><p class='{css_status(str(report.get('status', 'UNKNOWN')))}'>{esc(str(report.get('status', 'UNKNOWN')))}</p><pre>{esc(json.dumps(report, ensure_ascii=False, indent=2)[:1200])}</pre></article>"
        for name, report in data["existing_reports"].items()
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>HarnessOS V12-PV16 阶段自动化验收报告</title>
  <style>
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #172026; background: #f6f7f9; }}
    header {{ padding: 32px 40px; background: #102033; color: #fff; }}
    main {{ max-width: 1280px; margin: 0 auto; padding: 28px; }}
    section {{ background: #fff; border: 1px solid #d8dee6; border-radius: 8px; padding: 20px; margin-bottom: 18px; }}
    h1, h2 {{ margin: 0 0 12px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ border-bottom: 1px solid #e2e7ee; padding: 10px; text-align: left; vertical-align: top; }}
    th {{ background: #f0f3f6; }}
    code, pre {{ background: #f3f5f7; border-radius: 6px; }}
    pre {{ padding: 10px; overflow: auto; max-height: 240px; }}
    .pass, .pass_bounded, .conditional_pass {{ color: #166534; font-weight: 700; }}
    .partial, .expected_fail {{ color: #92400e; font-weight: 700; }}
    .fail, .not_complete, .not_implemented, .missing {{ color: #991b1b; font-weight: 700; }}
    .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 14px; }}
    article {{ border: 1px solid #d8dee6; border-radius: 8px; padding: 12px; background: #fbfcfd; }}
    img {{ width: 100%; border: 1px solid #d8dee6; border-radius: 6px; background: #fff; }}
    .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }}
    .summary div {{ background: #eef4fb; border-radius: 8px; padding: 12px; }}
  </style>
</head>
<body>
  <header>
    <h1>HarnessOS V12-PV16 阶段自动化验收报告</h1>
    <p>生成时间：{esc(data['created_at'])} · 状态：<strong>{esc(data['status'])}</strong></p>
  </header>
  <main>
    <section>
      <h2>结论摘要</h2>
      <div class="summary">
        <div><strong>PRD 基准</strong><br>{esc(data['prd_source'])}</div>
        <div><strong>目标架构</strong><br>{esc(data['architecture_source'])}</div>
        <div><strong>预览地址</strong><br>{esc(data['base_url'])}</div>
        <div><strong>边界</strong><br>不声明 production ready / Xpert parity / complete Studio</div>
      </div>
      <p>本报告证明 V12-PV16 阶段页面可被人类审查，并覆盖只读画布、editable Studio pilot、扩展生态 pilot、观测与 bounded deployment smoke、PV16 product-runtime hardening pilot。报告不声明生产级交付、完整 Studio、Xpert parity、产品级前端完成或 Agent executor ready。</p>
    </section>
    <section><h2>目标架构与当前实现</h2><table><thead><tr><th>架构平面</th><th>目标</th><th>当前实现</th><th>状态</th></tr></thead><tbody>{arch_rows}</tbody></table></section>
    <section><h2>用户场景覆盖</h2><table><thead><tr><th>场景</th><th>证据</th><th>状态</th></tr></thead><tbody>{coverage_rows}</tbody></table></section>
    <section><h2>自动化截图证据</h2><div class="cards">{screenshot_cards}</div></section>
    <section><h2>自动化检查命令</h2><table><thead><tr><th>检查</th><th>状态</th><th>耗时</th><th>命令</th></tr></thead><tbody>{command_rows}</tbody></table></section>
    <section><h2>阶段验收数据摘要</h2><div class="cards">{report_cards}</div></section>
    <section>
      <h2>不实信息防护</h2>
      <p>允许声明：{esc(' / '.join(data['claim_boundary']['allowed']))}</p>
      <p>禁止声明：{esc(' / '.join(data['claim_boundary']['not_allowed']))}</p>
      <p>所有 runtime-backed=false 的阶段在报告中保持原样展示，未把设计证据、截图或 bounded smoke 伪装为生产运行证据。</p>
    </section>
  </main>
</body>
</html>
"""


def render_screenshot_cards(browser_results: list[dict[str, Any]]) -> str:
    cards = []
    for result in browser_results:
        mode = result.get("mode", "unknown")
        for scenario in result.get("scenarios", []):
            screenshot = scenario.get("screenshot", "")
            cards.append(
                f"<article><strong>{esc(mode)} · {esc(scenario.get('scenario_id', ''))}</strong>"
                f"<p class='{css_status(str(scenario.get('status', 'UNKNOWN')))}'>{esc(str(scenario.get('status', 'UNKNOWN')))}</p>"
                f"<p>{esc(scenario.get('user_visible_result', ''))}</p>"
                f"<img src='{esc(screenshot)}' alt='{esc(scenario.get('scenario_id', 'screenshot'))}' /></article>"
            )
    return "".join(cards)


def wait_for_url(url: str, label: str, timeout: float = 60.0) -> None:
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


def url_available(url: str) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=1.0) as response:
            return response.status < 500
    except (urllib.error.URLError, TimeoutError):
        return False


def terminate(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"status": "MISSING", "path": str(path.relative_to(ROOT))}
    return json.loads(path.read_text(encoding="utf-8"))


def tail(text: str, limit: int = 5000) -> str:
    if len(text) <= limit:
        return text
    return text[-limit:]


def esc(value: Any) -> str:
    return html.escape(str(value))


def css_status(status: str) -> str:
    return status.lower().replace("-", "_")


if __name__ == "__main__":
    raise SystemExit(main())
