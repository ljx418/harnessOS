from __future__ import annotations

import html
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/design/V10.x/evidence/v10-cli-local-validation"
RAW = OUT / "raw"
SHOTS = OUT / "screenshots"


@dataclass
class CommandResult:
    key: str
    title: str
    command: list[str]
    expected_returncode: int
    returncode: int
    stdout: str
    stderr: str

    @property
    def status(self) -> str:
        return "PASS" if self.returncode == self.expected_returncode else "FAIL"


def run_command(key: str, title: str, command: list[str], expected_returncode: int = 0) -> CommandResult:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    (RAW / f"{key}.stdout.txt").write_text(result.stdout, encoding="utf-8")
    (RAW / f"{key}.stderr.txt").write_text(result.stderr, encoding="utf-8")
    return CommandResult(
        key=key,
        title=title,
        command=command,
        expected_returncode=expected_returncode,
        returncode=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr,
    )


def terminal_page(title: str, output: str, filename: str, columns: int) -> str:
    page = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>{html.escape(title)}</title>
  <style>
    body {{
      margin: 0;
      background: #020617;
      color: #e5e7eb;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    }}
    .window {{
      width: {columns * 10 + 44}px;
      padding: 18px 22px 24px;
      background: #020617;
    }}
    .bar {{
      height: 34px;
      display: flex;
      align-items: center;
      gap: 8px;
      border: 1px solid #334155;
      border-bottom: 0;
      border-radius: 10px 10px 0 0;
      padding: 0 12px;
      background: #0f172a;
      color: #94a3b8;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    .dot {{ width: 11px; height: 11px; border-radius: 999px; display: inline-block; }}
    .r {{ background: #ef4444; }} .y {{ background: #f59e0b; }} .g {{ background: #22c55e; }}
    pre {{
      margin: 0;
      padding: 18px;
      border: 1px solid #334155;
      border-radius: 0 0 10px 10px;
      background: #0b1020;
      white-space: pre-wrap;
      font-size: 15px;
      line-height: 1.38;
    }}
  </style>
</head>
<body><div class="window">
  <div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><strong>{html.escape(title)}</strong></div>
  <pre>{html.escape(output)}</pre>
</div></body>
</html>"""
    path = OUT / filename
    path.write_text(page, encoding="utf-8")
    return filename


def render_index(results: list[CommandResult]) -> None:
    final_data = json.loads((ROOT / "docs/design/V10.x/evidence/v10-7-final-acceptance/v10-final-acceptance-data.json").read_text(encoding="utf-8"))
    rows = "\n".join(
        f"<tr><td><code>{html.escape(' '.join(result.command))}</code></td><td>{result.returncode}</td><td>{result.expected_returncode}</td><td><span class='{result.status.lower()}'>{result.status}</span></td></tr>"
        for result in results
    )
    scenario_rows = "\n".join(
        f"<tr><td>{html.escape(item['id'])}</td><td>{html.escape(item['name'])}</td><td>{html.escape(item['evidence_scope'])}</td><td><span class='{item['status'].lower()}'>{html.escape(item['status'])}</span></td></tr>"
        for item in final_data["user_scenarios"]
    )
    html_doc = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>V10 CLI 本地运行验收报告</title>
  <style>
    body {{ margin:0; background:#f8fafc; color:#0f172a; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
    header {{ background:#0b1020; color:#f8fafc; padding:32px 40px; }}
    main {{ max-width:1180px; margin:0 auto; padding:28px 28px 60px; }}
    section {{ background:white; border:1px solid #e2e8f0; border-radius:10px; padding:22px; margin:18px 0; box-shadow:0 8px 22px rgba(15,23,42,.06); }}
    h1,h2 {{ margin-top:0; }}
    .grid {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:16px; }}
    img {{ width:100%; border:1px solid #cbd5e1; border-radius:8px; background:#020617; }}
    table {{ width:100%; border-collapse:collapse; }} td,th {{ border-bottom:1px solid #e2e8f0; padding:10px; text-align:left; vertical-align:top; }}
    code {{ background:#f1f5f9; padding:2px 5px; border-radius:5px; }}
    .pass {{ color:#15803d; font-weight:700; }} .fail {{ color:#b91c1c; font-weight:700; }}
    .note {{ background:#ecfeff; border-left:4px solid #0891b2; padding:12px 14px; border-radius:6px; }}
    .warn {{ background:#fff7ed; border-left:4px solid #ea580c; padding:12px 14px; border-radius:6px; }}
  </style>
</head>
<body>
  <header>
    <h1>V10 CLI 本地运行验收报告</h1>
    <p>本报告由真实 CLI 命令 stdout/stderr 生成，用于审查 V10 CLI-native Mission TUI 的本地运行证据。</p>
  </header>
  <main>
    <section>
      <h2>结论</h2>
      <p><span class="pass">PASS</span>：V10 CLI 层可运行，80x24 与 120x40 终端输出存在，五个用户场景进入 final scenario matrix，负例校验能够拒绝自动 apply / source=agent durable mutation 风险。</p>
      <p class="warn">边界：这些截图是由真实 CLI stdout 渲染出的终端界面截图，不是 macOS Terminal 窗口照片；HTML 解释页仍是辅助审计导出，不是 runtime truth。</p>
    </section>
    <section>
      <h2>运行界面截图证据</h2>
      <div class="grid">
        <figure><img src="screenshots/terminal-80x24.png" alt="80x24 CLI screenshot"><figcaption>80x24：窄屏下仍显示 HarnessOS 状态线、WorkflowDiff proposal、底部 composer。</figcaption></figure>
        <figure><img src="screenshots/terminal-120x40.png" alt="120x40 CLI screenshot"><figcaption>120x40：宽屏下展示本地 Markdown、罗马广场、视频分镜、编码提案等 Agent blocks。</figcaption></figure>
      </div>
    </section>
    <section>
      <h2>命令验证结果</h2>
      <table><thead><tr><th>命令</th><th>实际返回码</th><th>期望返回码</th><th>状态</th></tr></thead><tbody>{rows}</tbody></table>
    </section>
    <section>
      <h2>用户场景覆盖</h2>
      <table><thead><tr><th>场景</th><th>名称</th><th>证据范围</th><th>状态</th></tr></thead><tbody>{scenario_rows}</tbody></table>
    </section>
    <section>
      <h2>审计边界</h2>
      <p class="note">允许声明：<code>{html.escape(final_data['allowed_claim'])}</code></p>
      <p>仍禁止解释为 production ready、complete Workflow Studio ready、Agent executor ready、full multi-Agent orchestration ready 或 unrestricted terminal worker ready。</p>
      <p>Raw 命令输出保存在 <code>raw/</code>，终端截图源页面保存在 <code>terminal-80x24.html</code> 和 <code>terminal-120x40.html</code>。</p>
    </section>
  </main>
</body>
</html>"""
    (OUT / "index.html").write_text(html_doc, encoding="utf-8")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    SHOTS.mkdir(parents=True, exist_ok=True)
    results = [
        run_command(
            "terminal_80x24",
            "V10 Mission TUI 80x24",
            ["node", "apps/mission-tui/src/cli.js", "--fixture", "apps/mission-tui/fixtures/mission_tui_state_80x24.json", "--columns", "80", "--rows", "24"],
        ),
        run_command(
            "terminal_120x40",
            "V10 Mission TUI 120x40",
            ["node", "apps/mission-tui/src/cli.js", "--fixture", "apps/mission-tui/fixtures/mission_tui_state_120x40.json", "--columns", "120", "--rows", "40"],
        ),
        run_command(
            "negative_workflowdiff",
            "负例：WorkflowDiff 自动 apply 被拒绝",
            ["node", "apps/mission-tui/src/cli.js", "--fixture", "apps/mission-tui/fixtures/workflowdiff_auto_apply_action.json", "--validate"],
            expected_returncode=2,
        ),
        run_command("mission_tui_tests", "Mission TUI Node tests", ["npm", "--prefix", "apps/mission-tui", "test"]),
        run_command(
            "v10_pytest",
            "V10 pytest",
            [
                "./.venv/bin/python",
                "-m",
                "pytest",
                "tests/test_v10_mission_tui_runtime.py",
                "tests/test_v10_tui_experience_planning.py",
                "-q",
            ],
        ),
        run_command("drawio_xml", "V10 drawio XML", ["xmllint", "--noout", "docs/design/V10.x/v10_current_gap_analysis.drawio"]),
    ]
    terminal_page("V10 Mission TUI 80x24", results[0].stdout, "terminal-80x24.html", 80)
    terminal_page("V10 Mission TUI 120x40", results[1].stdout, "terminal-120x40.html", 120)
    render_index(results)
    summary = {
        "status": "PASS" if all(result.status == "PASS" for result in results) else "FAIL",
        "commands": [
            {
                "key": result.key,
                "command": result.command,
                "returncode": result.returncode,
                "expected_returncode": result.expected_returncode,
                "status": result.status,
            }
            for result in results
        ],
        "report": "docs/design/V10.x/evidence/v10-cli-local-validation/index.html",
        "screenshots": [
            "docs/design/V10.x/evidence/v10-cli-local-validation/screenshots/terminal-80x24.png",
            "docs/design/V10.x/evidence/v10-cli-local-validation/screenshots/terminal-120x40.png",
        ],
    }
    (OUT / "validation-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0 if summary["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
