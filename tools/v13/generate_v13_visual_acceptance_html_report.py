from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = ROOT / "docs/design/V12-V15.x/evidence/v13-workflow-studio-pilot"
REPORT_JSON = ROOT / "docs/design/V12-V15.x/reports/v13_workflow_studio_acceptance_report.json"
REPORT_HTML = ROOT / "docs/design/V12-V15.x/reports/v13_visual_acceptance_report.html"
REPORT_DATE = "2026-06-25"


SCREENSHOTS = [
    {
        "title": "默认画布与连接线端口对齐",
        "file": "edge-default-screenshot.png",
        "caption": "展示 V13 Studio 默认拓扑、选中节点、静态蓝色选中路径和端口贴合连线。",
    },
    {
        "title": "缩放后的连接线稳定性",
        "file": "edge-zoom-screenshot.png",
        "caption": "自动化在键盘缩放后验证 SVG path 起止点仍贴合对应 port。",
    },
    {
        "title": "普通滚轮缩放缺陷回归",
        "file": "canvas-defect-wheel-zoom.png",
        "caption": "自动化在画布内直接使用鼠标滚轮缩放，并验证缩放后连线和箭头仍可见。",
    },
    {
        "title": "右侧空白区域节点拖放",
        "file": "canvas-defect-right-area-drag.png",
        "caption": "自动化将节点拖入右侧可见空白区域，验证该区域不再只是背景。",
    },
    {
        "title": "自由连线取消路径",
        "file": "canvas-defect-connect-cancel.png",
        "caption": "自动化覆盖 Esc 和释放到空白的取消路径，确认取消不会创建新边。",
    },
    {
        "title": "拖拽后的画布几何",
        "file": "edge-drag-screenshot.png",
        "caption": "自动化拖拽节点后重新检测端口距离，防止视觉节点与 DTO 坐标分离。",
    },
    {
        "title": "端口拖拽自由连接",
        "file": "edge-free-connect-screenshot.png",
        "caption": "自动化从输出端口拖到输入端口，创建一条新的 WorkflowSpecGraph proposal 边。",
    },
    {
        "title": "场景切换：视频分镜工作流",
        "file": "scenario-storyboard-screenshot.png",
        "caption": "验证 L1/L2 场景切换会重组 6 站拓扑和 inspector 内容。",
    },
    {
        "title": "Chat Workbench 指令路径",
        "file": "chat-command-screenshot.png",
        "caption": "验证 /help 指令追加回复，并保留 proposal-only 边界。",
    },
    {
        "title": "仿真阻断状态下的边线语义",
        "file": "simulation-edge-state-screenshot.png",
        "caption": "展示 completed/blocked 边线状态，强调只做设计期仿真与人工交接。",
    },
    {
        "title": "高风险交接确认弹层",
        "file": "simulation-blocked-modal-screenshot.png",
        "caption": "验证第 6 站进入人工确认卡口，不触发 publish/run。",
    },
    {
        "title": "节点 Inspector 投影",
        "file": "node-inspector-screenshot.png",
        "caption": "验证选中节点 inspector 能展示角色、目标、工具、技能、MCP 与存证关系。",
    },
]


def main() -> int:
    acceptance_report = read_json(REPORT_JSON)
    edge_report = read_json(EVIDENCE_DIR / "edge-quality-report.json")
    canvas_defect_report = read_json(EVIDENCE_DIR / "canvas-defect-regression-report.json")
    interaction_report = read_json(EVIDENCE_DIR / "interaction-parity-report.json")
    graph = read_json(EVIDENCE_DIR / "workflow-spec-graph.json")
    diff = read_json(EVIDENCE_DIR / "workflow-diff-proposal.json")
    health = read_json(EVIDENCE_DIR / "system-health.json")
    manifest = read_json(EVIDENCE_DIR / "artifact-manifest.json")

    REPORT_HTML.parent.mkdir(parents=True, exist_ok=True)
    REPORT_HTML.write_text(
        render_html(
            acceptance_report=acceptance_report,
            edge_report=edge_report,
            canvas_defect_report=canvas_defect_report,
            interaction_report=interaction_report,
            graph=graph,
            diff=diff,
            health=health,
            manifest=manifest,
        ),
        encoding="utf-8",
    )
    print(str(REPORT_HTML.relative_to(ROOT)))
    return 0


def render_html(
    *,
    acceptance_report: dict[str, Any],
    edge_report: dict[str, Any],
    canvas_defect_report: dict[str, Any],
    interaction_report: dict[str, Any],
    graph: dict[str, Any],
    diff: dict[str, Any],
    health: dict[str, Any],
    manifest: dict[str, Any],
) -> str:
    artifact_count = len(manifest.get("required_artifacts", []))
    max_edge_distance = max(
        [
            max(edge.get("source_distance_px", 0), edge.get("target_distance_px", 0))
            for check in edge_report.get("checks", [])
            for edge in check.get("edges", [])
        ]
        or [0]
    )
    screenshot_cards = "\n".join(render_screenshot_card(item) for item in SCREENSHOTS)
    interaction_rows = "\n".join(
        f"<tr><td>{escape(check.get('check_id'))}</td><td><span class='badge pass'>{escape(check.get('status'))}</span></td><td>{escape(describe_interaction_check(check))}</td></tr>"
        for check in interaction_report.get("checks", [])
    )
    edge_rows = "\n".join(
        f"<tr><td>{escape(check.get('check_id'))}</td><td><span class='badge {status_class(check.get('status'))}'>{escape(check.get('status'))}</span></td><td>{len(check.get('edges', []))}</td><td>{escape(check.get('threshold_px'))} px</td></tr>"
        for check in edge_report.get("checks", [])
    )
    canvas_defect_rows = "\n".join(
        f"<tr><td>{escape(defect.get('defect_id'))}</td><td>{escape(defect.get('title'))}</td><td><span class='badge {status_class(defect.get('status'))}'>{escape(defect.get('status'))}</span></td><td>{escape(', '.join(defect.get('screenshot_refs', [])))}</td></tr>"
        for defect in canvas_defect_report.get("defects", [])
    )
    command_items = [
        "python3 tools/v13/run_v13_workflow_studio_acceptance.py",
        "node node_modules/typescript/bin/tsc -p tsconfig.json",
        "node node_modules/vite/bin/vite.js build",
        "node e2e/v13_cdp_acceptance.mjs",
        "python3 tools/v13/generate_v13_visual_acceptance_html_report.py",
    ]
    command_list = "\n".join(f"<li><code>{escape(command)}</code></li>" for command in command_items)

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>HarnessOS V13 可视化自动化验收报告</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f5f7fb;
      --panel: #ffffff;
      --ink: #172033;
      --muted: #64748b;
      --line: #dbe3ef;
      --brand: #2563eb;
      --good: #0f9f6e;
      --warn: #b7791f;
      --bad: #c2410c;
      --shadow: 0 18px 48px rgba(15, 23, 42, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: "Segoe UI", "Microsoft YaHei", Arial, sans-serif;
      line-height: 1.62;
    }}
    header {{
      padding: 34px 40px 26px;
      background: #0f172a;
      color: white;
    }}
    header p {{ max-width: 980px; color: #cbd5e1; margin: 10px 0 0; }}
    main {{ max-width: 1240px; margin: 0 auto; padding: 28px 24px 56px; }}
    section {{ margin-top: 22px; }}
    h1, h2, h3 {{ margin: 0; line-height: 1.18; }}
    h1 {{ font-size: 30px; }}
    h2 {{ font-size: 21px; margin-bottom: 12px; }}
    h3 {{ font-size: 15px; }}
    p {{ margin: 8px 0; }}
    code {{ padding: 2px 6px; border-radius: 6px; background: #eef2ff; color: #1e40af; }}
    .grid {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; }}
    .two {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
    .card {{
      border: 1px solid var(--line);
      border-radius: 10px;
      background: var(--panel);
      box-shadow: var(--shadow);
      padding: 18px;
    }}
    .metric strong {{ display: block; color: var(--muted); font-size: 12px; }}
    .metric span {{ display: block; margin-top: 6px; font-size: 24px; font-weight: 800; }}
    .badge {{
      display: inline-flex;
      align-items: center;
      min-height: 24px;
      padding: 2px 9px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 800;
    }}
    .pass {{ background: #dcfce7; color: #047857; }}
    .fail {{ background: #fee2e2; color: #b91c1c; }}
    .warn {{ background: #fef3c7; color: #92400e; }}
    .neutral {{ background: #e2e8f0; color: #334155; }}
    .screenshot-grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; }}
    figure {{ margin: 0; }}
    figure img {{
      width: 100%;
      display: block;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #f8fafc;
    }}
    figcaption {{ margin-top: 8px; color: var(--muted); font-size: 13px; }}
    table {{ width: 100%; border-collapse: collapse; overflow: hidden; border-radius: 8px; }}
    th, td {{ padding: 10px 12px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }}
    th {{ background: #f8fafc; color: #475569; font-size: 12px; }}
    ul {{ padding-left: 20px; }}
    .note {{ border-left: 4px solid var(--brand); background: #eff6ff; }}
    .risk {{ border-left: 4px solid var(--warn); background: #fffbeb; }}
    .footer {{ color: var(--muted); font-size: 13px; }}
    @media (max-width: 900px) {{
      header {{ padding: 26px 20px; }}
      main {{ padding: 20px 14px 40px; }}
      .grid, .two, .screenshot-grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>HarnessOS V13 可视化自动化验收报告</h1>
    <p>报告日期：{REPORT_DATE}。本报告由 headless Chrome/CDP 自动化测试、截图证据、schema 校验、claim scan 与 redaction scan 生成。结论仅覆盖 V13 editable Studio pilot slice ready for review，不声明完整 Workflow Studio、生产可用或 runtime complete。</p>
  </header>
  <main>
    <section class="grid">
      {metric("自动化总状态", acceptance_report.get("status"), "pass" if acceptance_report.get("status") == "PASS" else "fail")}
      {metric("端口连线最大偏差", f"{max_edge_distance:.3f}px", "pass" if max_edge_distance <= 3.5 else "fail")}
      {metric("截图证据", f"{len(SCREENSHOTS)} 张", "neutral")}
      {metric("Manifest Artifact", f"{artifact_count} 项", "neutral")}
    </section>

    <section class="card note">
      <h2>验收结论</h2>
      <p><strong>通过范围：</strong>V13 editable Studio pilot slice 可供审查。用户可以在浏览器中查看 V13 Studio 画布、选择节点、缩放、拖拽、切换场景、使用 Chat Workbench 指令、查看 WorkflowDiff 并走到人工 handoff。</p>
      <p><strong>明确不通过/不声明范围：</strong>不证明完整 Workflow Studio，不证明 runtime execution，不证明 product-grade frontend complete，不证明 Xpert parity，不证明 production ready，不证明 Agent executor ready。</p>
    </section>

    <section class="two">
      <div class="card">
        <h2>目标架构摘要</h2>
        <ul>
          <li>产品目标：从 CLI/TUI-first governed runtime 演进为可审查的 Studio 产品界面。</li>
          <li>浏览器必须经过 Studio BFF 和 DTO，不得直接写 runtime truth。</li>
          <li>V13 目标：editable WorkflowSpecGraph pilot、GraphValidationResult、NodeInspector、WorkflowDiffProposal、handoff-only 确认。</li>
          <li>后续 V14/V15 才覆盖 governed extension ecosystem、trace/metrics/audit/deployment smoke。</li>
        </ul>
      </div>
      <div class="card">
        <h2>当前实现摘要</h2>
        <ul>
          <li>Browser route：<code>?studio=v13-editable-studio</code>。</li>
          <li>BFF route：<code>/bff/v13/*</code> 与测试 route-log 端点。</li>
          <li>DTO：<code>{escape(graph.get("schema_version"))}</code>，节点数 {len(graph.get("nodes", []))}，边数 {len(graph.get("edges", []))}。</li>
          <li>WorkflowDiff：<code>{escape(diff.get("proposal_id"))}</code>，状态 <code>{escape(diff.get("status"))}</code>，<code>publish_or_run_started=false</code>。</li>
          <li>Runtime boundary：<code>runtime_backed={str(graph.get("runtime_backed")).lower()}</code>。</li>
        </ul>
      </div>
    </section>

    <section class="card">
      <h2>自动化测试命令</h2>
      <ul>{command_list}</ul>
      <p>本次自动化使用 headless Chrome/CDP 截图，不会抢占桌面焦点或弹出可见窗口。</p>
    </section>

    <section>
      <h2>用户场景截图证据</h2>
      <div class="screenshot-grid">{screenshot_cards}</div>
    </section>

    <section class="card">
      <h2>连接线几何验收</h2>
      <p>自动化读取 SVG path 起止点和 DOM port 外沿锚点，使用屏幕坐标计算距离。阈值为 3.5px；缺端口、缺箭头 marker 或跳过边都会失败。</p>
      <table>
        <thead><tr><th>检查点</th><th>状态</th><th>边数量</th><th>阈值</th></tr></thead>
        <tbody>{edge_rows}</tbody>
      </table>
    </section>

    <section class="card">
      <h2>画布缺陷回归</h2>
      <p>本区专门覆盖用户指出的四项问题：普通滚轮缩放、右侧可见空白拖放、自由连线取消、首屏连线和箭头可见性。</p>
      <table>
        <thead><tr><th>缺陷编号</th><th>验收目标</th><th>状态</th><th>截图证据</th></tr></thead>
        <tbody>{canvas_defect_rows}</tbody>
      </table>
    </section>

    <section class="card">
      <h2>交互路径验收</h2>
      <table>
        <thead><tr><th>检查项</th><th>状态</th><th>说明</th></tr></thead>
        <tbody>{interaction_rows}</tbody>
      </table>
    </section>

    <section class="two">
      <div class="card">
        <h2>安全与不实声明扫描</h2>
        <ul>
          <li>Claim scan：<span class="badge {status_class(acceptance_report.get("claim_scan", {}).get("status"))}">{escape(acceptance_report.get("claim_scan", {}).get("status"))}</span></li>
          <li>Redaction scan：<span class="badge {status_class(acceptance_report.get("redaction_scan", {}).get("status"))}">{escape(acceptance_report.get("redaction_scan", {}).get("status"))}</span></li>
          <li>Missing artifacts：{len(acceptance_report.get("missing_artifacts", []))}</li>
          <li>Health evidence：<code>{escape(health.get("status", "unknown"))}</code></li>
        </ul>
      </div>
      <div class="card risk">
        <h2>现实风险说明</h2>
        <ul>
          <li>当前报告证明的是 V13 pilot 交互审查路径，不是生产部署验收。</li>
          <li>截图和 DOM 检测不能替代后续 V15 runtime/deployment evidence。</li>
          <li>V14 插件/技能/工具/MCP 生态仍需单独 readiness、实现和验收。</li>
        </ul>
      </div>
    </section>

    <section class="card footer">
      <h2>证据位置</h2>
      <p>HTML 报告：<code>{escape(str(REPORT_HTML.relative_to(ROOT)))}</code></p>
      <p>自动化证据目录：<code>{escape(str(EVIDENCE_DIR.relative_to(ROOT)))}</code></p>
      <p>JSON 验收报告：<code>{escape(str(REPORT_JSON.relative_to(ROOT)))}</code></p>
    </section>
  </main>
</body>
</html>
"""


def metric(label: str, value: Any, tone: str) -> str:
    return f"<div class='card metric'><strong>{escape(label)}</strong><span><span class='badge {tone}'>{escape(value)}</span></span></div>"


def render_screenshot_card(item: dict[str, str]) -> str:
    image_path = f"../evidence/v13-workflow-studio-pilot/{item['file']}"
    return f"""
      <figure class="card">
        <h3>{escape(item["title"])}</h3>
        <img src="{escape(image_path)}" alt="{escape(item["title"])}" />
        <figcaption>{escape(item["caption"])}<br /><code>{escape(item["file"])}</code></figcaption>
      </figure>
    """


def describe_interaction_check(check: dict[str, Any]) -> str:
    check_id = str(check.get("check_id", ""))
    descriptions = {
        "l1_agents_route_updates_l2": "一级导航切到智能体目录，L2 内容更新。",
        "l1_workbench_route_restores_scenarios": "返回工作流平台后场景列表恢复。",
        "scenario_storyboard_morphs_canvas": "切换到视频分镜场景，画布拓扑和文案更新。",
        "scenario_roma_restores_canvas": "切回罗马广场讨论工作流。",
        "keyboard_zoom_and_reset": f"键盘缩放从 {check.get('zoom_before')} 到 {check.get('zoom_after')}，随后复位。",
        "node_drag_updates_canvas_geometry": "节点拖拽后 bounding box 和 edge quality 均更新。",
        "chat_help_command_appends_reply": "Chat Workbench /help 指令追加可见回复。",
        "text_layout_no_visible_overflow": f"扫描 {check.get('scanned_elements')} 个关键文本元素，无可见溢出。",
        "state_menu_updates_api_pill": "状态菜单切换 API 限流 pill。",
        "simulation_reaches_blocked_modal_and_handoff": "仿真进入阻断弹层并完成 handoff-only 确认。",
    }
    return descriptions.get(check_id, "自动化交互检查通过。")


def status_class(status: Any) -> str:
    if status == "PASS":
        return "pass"
    if status == "FAIL":
        return "fail"
    if status in {"BLOCKED", "PARTIAL"}:
        return "warn"
    return "neutral"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def escape(value: Any) -> str:
    return html.escape(str(value), quote=True)


if __name__ == "__main__":
    raise SystemExit(main())
