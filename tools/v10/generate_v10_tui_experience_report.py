from __future__ import annotations

import json
from html import escape
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
V10_ROOT = ROOT / "docs" / "design" / "V10.x"
OUT_DIR = V10_ROOT / "evidence" / "v10-0-tui-experience-planning"
SUPERSEDED_COCKPIT_REF = "docs/history/design/V10.x/superseded/v10-0-cockpit-first/host-generated-cockpit.png"
SUPERSEDED_COCKPIT_PATH = ROOT / SUPERSEDED_COCKPIT_REF


OPTIONS: list[dict[str, Any]] = [
    {
        "id": "option-react-ink-cli-native",
        "name": "React/Ink 终端原生 TUI",
        "recommendation": "selected",
        "summary": "新建 HarnessOS-native Mission TUI，但首屏保持 Codex CLI / Claude Code 类似的单列消息流、底部输入框、工具块和审批提示。",
        "advantages": ["最贴近目标基础体验", "键盘优先", "易做快照测试", "可逐步接入工作流解释块"],
        "tradeoffs": ["需要 Node/Ink 包", "需要 runtime bridge", "媒体展示能力有限"],
    },
    {
        "id": "option-textual-compat",
        "name": "Python Textual 兼容修补",
        "recommendation": "fallback",
        "summary": "保留现有 OpenHarness-compatible Textual TUI，作为兼容入口和回退，不作为 V10 主品牌体验。",
        "advantages": ["复用当前 runtime", "风险较低", "可快速修复文案"],
        "tradeoffs": ["OpenHarness 痕迹深", "交互质感难追平 Codex/Claude", "组件测试颗粒度较弱"],
    },
    {
        "id": "option-html-explainer",
        "name": "HTML 解释页辅助",
        "recommendation": "supporting",
        "summary": "动态 HTML 用于上手、审计和多媒体结果汇报；它不是主交互界面，也不能冒充真实 TUI 截图。",
        "advantages": ["审计清晰", "适合图片/报告展示", "复用 V9 证据链"],
        "tradeoffs": ["不是实时 TUI", "不能替代创建/修改入口", "必须标明 runtime evidence 边界"],
    },
]


PROMPTS = {
    "terminal_message_stream": "A realistic terminal-native HarnessOS CLI interface inspired by Codex CLI and Claude Code, no brand logos. Show a single-column conversation stream, bottom prompt composer, compact status line, Chinese UI labels, tool call blocks, plan/todo block, permission mode, workspace path. It should look like an actual terminal screenshot, not a dashboard.",
    "command_palette_onboarding": "A realistic terminal-native command palette overlay for HarnessOS CLI. Show slash commands like /new, /plan, /stations, /evidence, /diff, /help; Chinese descriptions; bottom prompt composer remains visible. Minimal dark terminal UI, no dashboard, no browser chrome, no logos.",
    "tool_permission_blocks": "A realistic terminal UI mockup showing governed tool execution blocks: tool started, command preview, approval prompt, allow/deny keys, sandbox mode, forbidden reason, evidence ref. Chinese labels. Minimal developer CLI style, no marketing cockpit, no browser dashboard.",
    "station_output_preview": "A realistic terminal-native workflow review screen showing station output preview, quality check result, evidence links, WorkflowDiff proposal, and expand/collapse hints. Chinese UI labels. Single-column CLI first, optional narrow status rail only when wide.",
    "workflowdiff_review": "A realistic terminal-native WorkflowDiff review screen in HarnessOS CLI. Show natural language modification request, proposed station changes, risk level, evidence refs, confirm/revise/reject actions, source=agent durable mutation denied until user confirmation. Chinese UI labels, dark terminal theme.",
}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    _write_json(
        OUT_DIR / "acceptance-data.json",
        {
            "schema_version": "v10_0.cli_native_tui_planning.v2",
            "status": "PASS",
            "stage_id": "V10-0R",
            "selected_route": "React/Ink CLI-native Mission TUI",
            "visual_direction": "Codex/ClaudeCode-like terminal-native baseline",
            "supersedes": "V10-0 cockpit-first concept package",
            "concept_prompts_written": True,
            "local_concept_svgs_written": True,
            "host_generated_image_ref": None,
            "superseded_host_generated_image_ref": SUPERSEDED_COCKPIT_REF
            if SUPERSEDED_COCKPIT_PATH.exists()
            else None,
            "html_report_written": True,
            "runtime_implementation_started": False,
            "concept_images_are_runtime_evidence": False,
            "html_explainer_is_primary_tui": False,
            "terminal_native_acceptance": {
                "single_column_stream_first": True,
                "bottom_composer_required": True,
                "tool_blocks_required": True,
                "permission_prompt_required": True,
                "evidence_links_inline": True,
                "command_palette_required": True,
                "workflowdiff_preview_required": True,
                "interaction_design_board_required": True,
                "real_tui_screenshots_required_for_v10_1": True,
            },
            "milestone_roadmap": [
                "M0 planning correction",
                "M1 CLI-native shell screenshots",
                "M2 tool permission plan blocks",
                "M3 workflow station explainability blocks",
                "M4 output quality preview",
                "M5 WorkflowDiff proposal preview",
                "M6 HTML explainer export",
                "M7 final UX acceptance",
            ],
            "user_scenario_matrix": [
                "US-V10-01 local Markdown workflow",
                "US-V10-02 Roman Forum parallel Agent discussion",
                "US-V10-03 video storyboard workflow",
                "US-V10-04 coding proposal workflow",
                "US-V10-05 natural-language workflow revision",
            ],
            "forbidden_claims": {
                "production_ready": False,
                "agent_executor_ready": False,
                "complete_workflow_studio_ready": False,
                "full_multi_agent_orchestration_ready": False,
            },
        },
    )
    for slug, prompt in PROMPTS.items():
        (OUT_DIR / f"prompt-{slug}.md").write_text(f"# {slug}\n\n{prompt}\n", encoding="utf-8")
    (OUT_DIR / "concept-terminal-message-stream.svg").write_text(_svg_terminal_stream(), encoding="utf-8")
    (OUT_DIR / "concept-command-palette-onboarding.svg").write_text(_svg_command_palette(), encoding="utf-8")
    (OUT_DIR / "concept-tool-permission-blocks.svg").write_text(_svg_tool_permissions(), encoding="utf-8")
    (OUT_DIR / "concept-station-output-preview.svg").write_text(_svg_station_preview(), encoding="utf-8")
    (OUT_DIR / "concept-workflowdiff-review.svg").write_text(_svg_workflowdiff_review(), encoding="utf-8")
    (OUT_DIR / "concept-cli-native-interaction-board.html").write_text(_render_design_board_html(), encoding="utf-8")
    (OUT_DIR / "index.html").write_text(_render_html(), encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(OUT_DIR / "index.html")}, ensure_ascii=False, indent=2))
    return 0


def _render_html() -> str:
    option_cards = "".join(_option_card(option) for option in OPTIONS)
    prompt_links = "".join(f'<li><a href="prompt-{escape(slug)}.md">{escape(slug)}</a></li>' for slug in PROMPTS)
    superseded = ""
    rendered_board = ""
    if (OUT_DIR / "concept-cli-native-interaction-board.png").exists():
        rendered_board = """
    <section>
      <h2>交互概念总览图</h2>
      <p class="muted">该 PNG 由本地 HTML/CSS 设计板截图生成，是 V10-0R 的交互概念图，不是 runtime TUI 截图。</p>
      <img src="concept-cli-native-interaction-board.png" alt="V10 CLI-native interaction concept board" />
      <p><a href="concept-cli-native-interaction-board.html">打开可复现 HTML 设计板</a></p>
    </section>
        """
    else:
        rendered_board = """
    <section>
      <h2>交互概念总览图</h2>
      <p class="muted">可复现 HTML 设计板已生成；如果需要 PNG，可对该 HTML 执行本地截图。</p>
      <p><a href="concept-cli-native-interaction-board.html">打开可复现 HTML 设计板</a></p>
    </section>
        """
    if SUPERSEDED_COCKPIT_PATH.exists():
        superseded = """
    <section>
      <h2>已废弃的旧概念图</h2>
      <p class="warning">旧的 cockpit 图保留为历史证据，但它不是新的 V10 方向，也不能冒充真实 TUI 运行截图。</p>
      <p class="muted">文件：docs/history/design/V10.x/superseded/v10-0-cockpit-first/host-generated-cockpit.png</p>
    </section>
        """
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>V10-0R CLI-native TUI 体验修订</title>
  <style>
    body {{ margin: 0; background: #0b1020; color: #d7dee8; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", sans-serif; }}
    header {{ padding: 34px 44px; background: #080c16; border-bottom: 1px solid #263244; }}
    main {{ max-width: 1380px; margin: 0 auto; padding: 24px; }}
    section, article {{ background: #111827; border: 1px solid #263244; border-radius: 8px; padding: 18px; margin: 16px 0; box-shadow: 0 14px 36px rgba(0,0,0,.22); }}
    h1 {{ margin: 0 0 10px; font-size: 32px; color: #f8fafc; }}
    h2, h3 {{ color: #f8fafc; }}
    .grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }}
    .two {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }}
    .badge {{ display: inline-block; border-radius: 999px; padding: 3px 10px; font-weight: 700; font-size: 12px; background: #bbf7d0; color: #14532d; }}
    .muted {{ color: #9aa8ba; }}
    .warning {{ color: #fde68a; }}
    img {{ width: 100%; border: 1px solid #334155; border-radius: 8px; background: #020617; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    td, th {{ border-bottom: 1px solid #263244; padding: 9px; text-align: left; vertical-align: top; }}
    code {{ background: #020617; color: #bfdbfe; padding: 1px 5px; border-radius: 4px; }}
    @media (max-width: 960px) {{ .grid, .two {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <header>
    <h1>V10-0R CLI-native TUI 体验修订</h1>
    <p>目标：先把 HarnessOS 的基础 TUI 做成接近 Codex CLI / Claude Code 的稳固终端工作台，再逐步接入工作流解释、产物预览和审计导出。</p>
  </header>
  <main>
    <section>
      <h2>修订结论</h2>
      <p><span class="badge">PASS</span> V10 主方向从“工作流 cockpit”修正为“终端原生 Mission TUI”。</p>
      <p class="muted">V10-0R 只证明规划修订 ready for review，不证明 runtime TUI 已完成。V10-1 才能开始真实 TUI shell 实现。</p>
    </section>
    <section>
      <h2>基础体验基线</h2>
      <table><thead><tr><th>区域</th><th>目标体验</th><th>验收重点</th></tr></thead><tbody>
        <tr><td>顶部状态线</td><td>显示 workspace / model / mode / sandbox / evidence status。</td><td>一行内可读，80 列终端不溢出。</td></tr>
        <tr><td>主消息流</td><td>用户、助手、计划、工具、产物、错误都以块状消息出现。</td><td>单列优先，不默认大 dashboard。</td></tr>
        <tr><td>底部输入框</td><td>自然语言目标、slash command、快捷键提示。</td><td>始终可见，执行中有明确 busy 状态。</td></tr>
        <tr><td>工具/审批块</td><td>命令预览、allow/deny、forbidden reason、evidence ref。</td><td>用户确认前不发生 durable mutation。</td></tr>
        <tr><td>工作流解释块</td><td>station role / goal / tools / quality / evidence 可展开。</td><td>来自 read model，不构造 runtime truth。</td></tr>
      </tbody></table>
    </section>
    <section>
      <h2>交互概念设计</h2>
      <table><thead><tr><th>交互对象</th><th>用户动作</th><th>TUI 反馈</th><th>安全边界</th></tr></thead><tbody>
        <tr><td>Composer</td><td>输入自然语言或 slash command</td><td>创建消息块，显示 plan/todo 或 command palette</td><td>只提交 intent，不直接执行 durable mutation</td></tr>
        <tr><td>Tool Block</td><td>展开工具详情或批准/拒绝</td><td>显示命令预览、sandbox、risk、evidence ref</td><td>高风险动作必须 human confirmation</td></tr>
        <tr><td>Station Block</td><td>展开工位产物</td><td>显示 Agent role/goal/tools、产物摘要、质量结果</td><td>产物必须带 artifact/evidence refs</td></tr>
        <tr><td>WorkflowDiff Block</td><td>确认、修改或拒绝变更</td><td>显示 affected stations、risk、forbidden reasons</td><td>确认前不得 apply / publish / run</td></tr>
      </tbody></table>
    </section>
    <section>
      <h2>方案对比</h2>
      <div class="grid">{option_cards}</div>
    </section>
    <section>
      <h2>修订后的概念图</h2>
      <div class="grid">
        <article><h3>单列消息流 + Composer</h3><img src="concept-terminal-message-stream.svg" alt="Terminal message stream concept" /></article>
        <article><h3>Slash Command 面板</h3><img src="concept-command-palette-onboarding.svg" alt="Command palette onboarding concept" /></article>
        <article><h3>工具块 + 审批提示</h3><img src="concept-tool-permission-blocks.svg" alt="Tool permission block concept" /></article>
        <article><h3>工位产物 + 质量预览</h3><img src="concept-station-output-preview.svg" alt="Station output preview concept" /></article>
        <article><h3>WorkflowDiff 修改审查</h3><img src="concept-workflowdiff-review.svg" alt="WorkflowDiff review concept" /></article>
      </div>
    </section>
    {rendered_board}
    {superseded}
    <section>
      <h2>V10 用户场景验收</h2>
      <table><thead><tr><th>场景</th><th>用户看到什么</th><th>必须证明</th></tr></thead><tbody>
        <tr><td>第一次创建工作流</td><td>输入自然语言目标后，TUI 显示计划块、WorkflowSpec 草案和“等待确认”。</td><td>未确认前无 durable mutation。</td></tr>
        <tr><td>观察多 Agent 工作流</td><td>消息流中出现每个 station 的 Agent 角色、状态、产物摘要和证据链接。</td><td>每个状态来自 read model / evidence refs。</td></tr>
        <tr><td>审查产物质量</td><td>展开 station 块后看到质量 Agent 检查、失败原因、建议修复。</td><td>产物预览必须带 quality_ref 和 evidence_ref。</td></tr>
        <tr><td>自然语言修改工作流</td><td>系统先输出 WorkflowDiff proposal，并提示 confirm / revise / reject。</td><td>proposal-first，不自动 apply。</td></tr>
      </tbody></table>
    </section>
    <section>
      <h2>gpt-image-2 / imag2 Prompt</h2>
      <p class="muted">这些 prompt 是后续生成真实风格概念图的输入；当前 SVG 是本地可复现规划证据，不是 runtime evidence。</p>
      <ul>{prompt_links}</ul>
    </section>
    <section>
      <h2>Forbidden Claims / 边界</h2>
      <p>本报告不得解释为 production ready、Agent executor ready、complete Workflow Studio ready、unrestricted terminal worker ready 或 full multi-Agent orchestration ready。</p>
    </section>
  </main>
</body>
</html>
"""


def _option_card(option: dict[str, Any]) -> str:
    return (
        "<article>"
        f"<h3>{escape(option['name'])}</h3>"
        f"<p><span class=\"badge\">{escape(option['recommendation'])}</span></p>"
        f"<p>{escape(option['summary'])}</p>"
        f"<p><strong>优势</strong></p><ul>{_items(option['advantages'])}</ul>"
        f"<p><strong>代价</strong></p><ul>{_items(option['tradeoffs'])}</ul>"
        "</article>"
    )


def _items(values: list[str]) -> str:
    return "".join(f"<li>{escape(value)}</li>" for value in values)


def _render_design_board_html() -> str:
    return """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>V10 CLI-native Interaction Board</title>
  <style>
    * { box-sizing: border-box; }
    body { margin: 0; background: #080c16; color: #e5edf7; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace; }
    .board { width: 1600px; min-height: 1180px; padding: 38px; background: radial-gradient(circle at 20% 0%, #13233b 0, #080c16 42%, #050816 100%); }
    .title { display: flex; justify-content: space-between; align-items: end; margin-bottom: 24px; }
    h1 { margin: 0; font-size: 34px; letter-spacing: 0; }
    .subtitle { color: #9fb0c4; font-size: 16px; }
    .grid { display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 22px; }
    .stack { display: grid; gap: 22px; }
    .terminal { border: 1px solid #334155; border-radius: 14px; background: #0b1020; overflow: hidden; box-shadow: 0 24px 80px rgba(0,0,0,.45); }
    .terminal.large { min-height: 560px; }
    .bar { height: 42px; display: flex; align-items: center; gap: 8px; padding: 0 16px; background: #111827; border-bottom: 1px solid #263244; color: #94a3b8; font-size: 13px; }
    .dot { width: 10px; height: 10px; border-radius: 50%; background: #ef4444; }
    .dot:nth-child(2) { background: #f59e0b; }
    .dot:nth-child(3) { background: #22c55e; }
    .status { margin-left: auto; color: #8bdaff; }
    .content { padding: 18px; font-size: 17px; line-height: 1.55; }
    .line { margin: 8px 0; white-space: pre-wrap; }
    .user { color: #f8fafc; }
    .assistant { color: #bfdbfe; }
    .muted { color: #94a3b8; }
    .ok { color: #bbf7d0; }
    .warn { color: #fde68a; }
    .danger { color: #fecaca; }
    .block { margin: 14px 0; padding: 14px; border: 1px solid #334155; border-radius: 10px; background: #111827; }
    .block h3 { margin: 0 0 8px; font-size: 18px; color: #f8fafc; }
    .composer { margin-top: 18px; padding: 12px 14px; border: 1px solid #475569; border-radius: 10px; color: #dbeafe; background: #020617; }
    .palette { display: grid; gap: 8px; }
    .cmd { display: grid; grid-template-columns: 110px 1fr; gap: 12px; padding: 8px 10px; border-radius: 8px; background: #0f172a; }
    .cmd b { color: #bbf7d0; }
    .actions { margin-top: 12px; display: flex; gap: 10px; flex-wrap: wrap; }
    .key { border: 1px solid #475569; background: #020617; color: #e5edf7; border-radius: 7px; padding: 6px 10px; }
    .callout { margin-top: 22px; display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }
    .card { border: 1px solid #263244; background: #0f172a; border-radius: 12px; padding: 14px; min-height: 128px; }
    .card h3 { margin: 0 0 10px; font-size: 17px; color: #f8fafc; }
    .card p { margin: 0; color: #a8b6c8; font-size: 14px; line-height: 1.45; }
  </style>
</head>
<body>
  <main class="board">
    <div class="title">
      <div>
        <h1>HarnessOS V10 CLI-native TUI 交互概念</h1>
        <div class="subtitle">目标：先做扎实的 Codex/ClaudeCode 类终端基础体验，再接入工作流解释与产物审查。</div>
      </div>
      <div class="subtitle">V10-0R planning concept · not runtime screenshot</div>
    </div>
    <section class="grid">
      <div class="terminal large">
        <div class="bar"><span class="dot"></span><span class="dot"></span><span class="dot"></span><span>harnessOS mission</span><span class="status">workspace-write · mode: plan · evidence: ready</span></div>
        <div class="content">
          <div class="line user">你 > 我有一个视频点子：雨夜里的小型 AI 工作室。请创建工作流，但先给我看计划。</div>
          <div class="block">
            <h3>assistant ▸ 计划</h3>
            <div class="line ok">✓ 捕获目标与约束</div>
            <div class="line">1. 起草 WorkflowSpec</div>
            <div class="line">2. 建立分镜、图像提示词、质检三个工位</div>
            <div class="line">3. 展示产物预览与证据链</div>
            <div class="line warn">等待用户确认前不会写入 runtime truth</div>
          </div>
          <div class="block">
            <h3>tool ▸ workflow.spec.draft</h3>
            <div class="line">risk: low · mutation: false · evidence: evd_v10_001</div>
            <div class="line ok">status: completed</div>
          </div>
          <div class="block">
            <h3>station ▣ 分镜设计师</h3>
            <div class="line">role: Storyboard Agent · goal: 产出 6 个镜头草图提示词</div>
            <div class="line">quality: pending · artifact: artifact-ref://storyboard-draft</div>
          </div>
          <div class="composer">› 输入自然语言目标或 /command</div>
        </div>
      </div>
      <div class="stack">
        <div class="terminal">
          <div class="bar"><span class="dot"></span><span class="dot"></span><span class="dot"></span><span>slash commands</span></div>
          <div class="content palette">
            <div class="cmd"><b>/new</b><span>从自然语言目标创建工作流草案</span></div>
            <div class="cmd"><b>/plan</b><span>展开当前计划和 todo</span></div>
            <div class="cmd"><b>/stations</b><span>查看工位与 Agent 状态</span></div>
            <div class="cmd"><b>/evidence</b><span>打开证据链与 runtime report</span></div>
            <div class="cmd"><b>/diff</b><span>查看待确认 WorkflowDiff</span></div>
            <div class="cmd"><b>/help</b><span>显示快捷键与安全边界</span></div>
          </div>
        </div>
        <div class="terminal">
          <div class="bar"><span class="dot"></span><span class="dot"></span><span class="dot"></span><span>permission prompt</span></div>
          <div class="content">
            <div class="block">
              <h3 class="danger">permission ▸ 需要确认</h3>
              <div class="line">tool: terminal.readonly_shell</div>
              <div class="line">command: ls docs/design/V9.x/evidence</div>
              <div class="line">risk: low · sandbox: workspace-readonly</div>
              <div class="line">evidence: evd_tool_019</div>
              <div class="actions"><span class="key">y allow</span><span class="key">n deny</span><span class="key">? details</span></div>
            </div>
          </div>
        </div>
      </div>
    </section>
    <section class="callout">
      <div class="card"><h3>工位产物预览</h3><p>每个 station 块展示 Agent role、goal、产物摘要、quality_ref、evidence_ref，用户可展开审查。</p></div>
      <div class="card"><h3>WorkflowDiff 审查</h3><p>自然语言修改只生成 proposal，显示 affected stations、risk、confirm/revise/reject。</p></div>
      <div class="card"><h3>安全边界可见</h3><p>source=agent durable mutation denied until user confirmation，不能隐藏在日志里。</p></div>
      <div class="card"><h3>HTML 只做导出</h3><p>富媒体解释页用于审计和上手，不替代真实 TUI，也不能冒充运行截图。</p></div>
    </section>
  </main>
</body>
</html>
"""


def _svg_terminal_stream() -> str:
    lines = [
        ("harnessOS  /Users/Zhuanz/workspace  model:gpt-5.5  mode:plan  sandbox:workspace-write", 28, "#8bdaff"),
        ("你 > 帮我把视频点子拆成工作流，并先给我看计划", 72, "#f8fafc"),
        ("assistant ▸ 计划", 118, "#bbf7d0"),
        ("  1. 捕获目标  2. 起草 WorkflowSpec  3. 生成分镜工位  4. 等待确认", 150, "#d7dee8"),
        ("tool ▸ workflow.spec.draft  status: completed  evidence: evd_v10_001", 206, "#fde68a"),
        ("station ▸ 分镜设计师  role: Storyboard Agent  quality: pending", 250, "#d7dee8"),
        ("输入消息或 /command", 374, "#94a3b8"),
    ]
    return _svg_terminal("CLI-native Mission TUI", lines, footer="单列消息流 + 底部 composer 是默认体验")


def _svg_tool_permissions() -> str:
    lines = [
        ("harnessOS  permission: on-request  sandbox: workspace-write", 28, "#8bdaff"),
        ("tool ▸ terminal.readonly_shell", 78, "#fde68a"),
        ("  command: ls docs/design/V9.x/evidence", 112, "#d7dee8"),
        ("  risk: low  mutation: false  evidence: evd_tool_019", 144, "#d7dee8"),
        ("permission ▸ 需要确认", 204, "#fecaca"),
        ("  reason: 即将读取工作区证据目录", 238, "#f8fafc"),
        ("  [y] allow   [n] deny   [?] details", 272, "#bbf7d0"),
        ("denied reason 和 evidence ref 必须可见，不能隐藏在日志里", 358, "#94a3b8"),
    ]
    return _svg_terminal("Tool Block And Permission Prompt", lines, footer="工具块、审批提示、forbidden reason 是一等 UI 元素")


def _svg_command_palette() -> str:
    lines = [
        ("harnessOS  /Users/Zhuanz/workspace  mode:default  evidence:ready", 28, "#8bdaff"),
        ("你 > /", 78, "#f8fafc"),
        ("command palette", 118, "#bbf7d0"),
        ("  /new        从自然语言目标创建工作流草案", 150, "#d7dee8"),
        ("  /plan       展开当前计划 / todo", 182, "#d7dee8"),
        ("  /stations   查看所有工位与 Agent 状态", 214, "#d7dee8"),
        ("  /evidence   打开证据链与 runtime report", 246, "#d7dee8"),
        ("  /diff       查看待确认 WorkflowDiff", 278, "#d7dee8"),
        ("  /help       快捷键与安全边界", 310, "#94a3b8"),
        ("输入消息或 /command", 374, "#94a3b8"),
    ]
    return _svg_terminal("Slash Command Onboarding", lines, footer="新用户先靠 /commands 上手，不需要理解内部文档")


def _svg_station_preview() -> str:
    lines = [
        ("harnessOS  workflow: video-storyboard-v1  run: local-fixture", 28, "#8bdaff"),
        ("station ▣ 分镜设计师  status: done", 78, "#bbf7d0"),
        ("  output: 6 个镜头草图提示词，统一角色：银色雨衣女孩", 112, "#d7dee8"),
        ("  quality: PASS  consistency: 0.91  evidence: evd_quality_022", 146, "#fde68a"),
        ("station ▣ 质检 Agent  status: done", 204, "#bbf7d0"),
        ("  finding: 第 4 镜头背景色偏离，建议 revise", 238, "#f8fafc"),
        ("WorkflowDiff proposal", 292, "#fecaca"),
        ("  + 调整 scene_04.background_palette -> neon-blue/rain", 326, "#d7dee8"),
        ("  [enter] expand  [c] confirm  [r] revise  [x] reject", 374, "#94a3b8"),
    ]
    return _svg_terminal("Station Output And Quality Preview", lines, footer="产物、质量、Diff 先以终端块预览；HTML 仅用于富媒体审计")


def _svg_workflowdiff_review() -> str:
    lines = [
        ("harnessOS  workflow: roman-forum-v1  diff: pending  mode:review", 28, "#8bdaff"),
        ("你 > 把哲学讨论增加一个怀疑主义者 Agent，并让质检总结分歧", 78, "#f8fafc"),
        ("WorkflowDiff proposal", 118, "#fecaca"),
        ("  + station: skeptical_philosopher  role: 怀疑主义者", 150, "#d7dee8"),
        ("  + edge: skeptical_philosopher -> moderator_summary", 182, "#d7dee8"),
        ("  ~ quality_check: 增加观点覆盖率与冲突解释", 214, "#d7dee8"),
        ("policy ▸ source=agent durable mutation denied until user confirmation", 258, "#fde68a"),
        ("evidence ▸ evd_diff_041  risk: medium  affected stations: 2", 292, "#bbf7d0"),
        ("[c] confirm  [r] revise  [x] reject  [enter] details", 374, "#94a3b8"),
    ]
    return _svg_terminal("WorkflowDiff Review", lines, footer="自然语言优化必须先变成 proposal；确认前不写 runtime truth")


def _svg_terminal(title: str, lines: list[tuple[str, int, str]], *, footer: str) -> str:
    rows = []
    for text, y, color in lines:
        rows.append(f'<text x="34" y="{y}" font-size="18" fill="{color}">{escape(text)}</text>')
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 980 460">'
        '<rect width="980" height="460" rx="0" fill="#020617" />'
        '<rect x="18" y="18" width="944" height="380" rx="10" fill="#0b1020" stroke="#334155" />'
        f'<text x="34" y="52" font-size="20" font-weight="800" fill="#f8fafc">{escape(title)}</text>'
        '<line x1="34" y1="58" x2="940" y2="58" stroke="#263244" />'
        + "".join(rows)
        + '<rect x="34" y="340" width="890" height="42" rx="8" fill="#111827" stroke="#475569" />'
        '<text x="50" y="367" font-size="17" fill="#94a3b8">›</text>'
        f'<text x="34" y="430" font-size="15" fill="#94a3b8">{escape(footer)}</text>'
        + "</svg>"
    )


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
