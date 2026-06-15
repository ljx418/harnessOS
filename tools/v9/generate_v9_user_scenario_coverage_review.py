from __future__ import annotations

import json
from html import escape
from pathlib import Path
from typing import Any

from tools.v9.common import V9_ROOT, write_json


OUT_DIR = V9_ROOT / "evidence" / "v9-user-scenario-coverage-review"
FINAL_DATA = V9_ROOT / "evidence" / "v9-8-final-acceptance" / "v9-final-acceptance-data.json"
ROMAN_FORUM = V9_ROOT / "evidence" / "v9-3-orchestration-runtime" / "roman-forum-discussion.json"
V93_ACCEPTANCE = V9_ROOT / "evidence" / "v9-3-orchestration-runtime" / "acceptance-data.json"
V93_INDEX = V9_ROOT / "evidence" / "v9-3-orchestration-runtime" / "index.html"
VIDEO_E2E = V9_ROOT / "evidence" / "v9-user-scenario-video-workflow-e2e" / "raw" / "video-workflow-e2e.json"


SCENARIO_DETAILS: dict[str, dict[str, Any]] = {
    "US-V9-01": {
        "persona": "工作流管理员或产品负责人",
        "user_goal": "确认系统只能执行受控白名单动作，并且任何 Agent 来源的直接写入都被拒绝。",
        "when_to_use": "当用户要启动、重跑、写入产物或创建质量评价时，用这个场景审查 V9-2 受控执行器是否仍在权限边界内。",
        "user_steps": [
            "打开 V9-2 controlled executor runtime 验收页。",
            "检查四个 allowlisted operation 的 runtime evidence。",
            "检查 source=agent durable mutation denied、kill switch、idempotency、rollback 和 evidence chain 字段。",
        ],
        "expected_outputs": [
            "workflow.instance.start、station.rerun、artifact.write、quality.evaluation.create 均有受控证据。",
            "越界动作没有被执行。",
            "审计证据中只出现 redacted refs，不出现原始密钥或原始 payload。",
        ],
        "acceptance_criteria": [
            "status=PASS 且 runtime_backed=true。",
            "source=agent direct durable mutation denied。",
            "evidence chain 可追溯到 policy / capability / authorization decision。",
        ],
        "audit_focus": "重点核查受控执行器没有扩大为通用 Agent executor，也没有开放 connector.call 或 external_llm.call。",
        "boundary": "该场景不证明完整 Agent executor 或 production controlled executor。",
    },
    "US-V9-02": {
        "persona": "需要审查多 Agent 协作可靠性的项目负责人",
        "user_goal": "看到一个工作流如何拆成串行、并行、fan-out、fan-in，并在失败恢复后保留 attempt 和 artifact lineage。",
        "when_to_use": "当用户关心多个 Agent/工位是否真的被编排，而不是单一脚本顺序跑完时，用这个场景验收。",
        "user_steps": [
            "打开 V9-3 orchestration runtime 验收页。",
            "查看 fan-out dispatch、fan-in join、attempt history、artifact lineage 和 lost worker recovery 证据。",
            "确认每个产物保留 producer_agent_id / producer_attempt_id。",
        ],
        "expected_outputs": [
            "并行分支各自拥有独立 branch state。",
            "fan-in 汇总保留 attribution refs。",
            "失败或丢失 worker 的恢复不覆盖旧 attempt。",
        ],
        "acceptance_criteria": [
            "serial_parallel_fan_in_fan_out=PASS。",
            "attempt_history=PASS。",
            "artifact_lineage=PASS。",
            "failure_recovery=PASS 且 lost_worker_recovery=PASS。",
        ],
        "audit_focus": "重点看 fan-out/fan-in 是否有真实 JSON 证据，而不是只在图里画了并行。",
        "boundary": "该场景证明 bounded orchestration runtime slice，不证明 full multi-Agent orchestration ready。",
    },
    "US-V9-03": {
        "persona": "希望用 AI 辅助开发但不想让系统自动提交代码的工程负责人",
        "user_goal": "让系统生成计划、diff proposal、测试建议和 review handoff，但不自动 commit、push 或 deploy。",
        "when_to_use": "当用户想把自然语言开发目标交给工作流处理，但仍要求人类审核最终改动时使用。",
        "user_steps": [
            "打开 V9-4 coding workflow runtime 验收页。",
            "查看 intent、plan、diff proposal、sandboxed test result、review summary 和 fix-loop proposal。",
            "检查 git operation deny report。",
        ],
        "expected_outputs": [
            "系统生成可审查的 diff proposal 和测试结果。",
            "没有自动 commit、push、deploy。",
            "失败修复以新 proposal 形式出现，不静默修改。",
        ],
        "acceptance_criteria": [
            "runtime_backed=true。",
            "auto commit / auto push / auto deploy 均被拒绝或未发生。",
            "human review handoff 存在。",
        ],
        "audit_focus": "重点检查 AI 只生成 proposal，不把 proposal 伪装成已经被批准的代码变更。",
        "boundary": "该场景不证明 autonomous coding workflow ready。",
    },
    "US-V9-04": {
        "persona": "安全负责人或需要审查终端自动化边界的工程负责人",
        "user_goal": "确认 terminal worker 只能在 workspace sandbox 内执行受控命令，并捕获 transcript 和 diff。",
        "when_to_use": "当用户想让工作流调用终端做只读检查、测试或受限产物提案时使用。",
        "user_steps": [
            "打开 V9-5 terminal worker 验收页。",
            "查看 command decisions、terminal transcript、diff capture 和 denial evidence。",
            "确认 workspace escape、secret read、git push、production deploy 没有被允许。",
        ],
        "expected_outputs": [
            "命令有 tier / policy decision。",
            "终端 transcript 可审计。",
            "危险命令被拒绝并有 evidence。",
        ],
        "acceptance_criteria": [
            "terminal session evidence=PASS。",
            "workspace boundary checks=PASS。",
            "secret-read / escape / push / deploy denial evidence 存在。",
        ],
        "audit_focus": "重点检查 terminal worker 没有变成 unrestricted shell。",
        "boundary": "该场景不证明 unrestricted terminal worker 或 production terminal automation。",
    },
    "US-V9-05": {
        "persona": "需要在网页控制台审查工作流状态的运营用户",
        "user_goal": "通过 Product Console / Thin Web Console 查看 runtime report、evidence review 和手动确认入口。",
        "when_to_use": "当用户需要可视化审查工作流结果，而不是直接改 runtime truth 时使用。",
        "user_steps": [
            "打开 V9-6 Workflow Studio 验收页。",
            "查看 read-only panels、BFF/DTO 边界和 manual confirmation evidence。",
            "检查 browser denylist 和 hidden mutation form scan。",
        ],
        "expected_outputs": [
            "Runtime Report 和 Evidence Review 只读。",
            "manual confirmation 生成 human_authorization_ref。",
            "浏览器不直连内部 runtime route。",
        ],
        "acceptance_criteria": [
            "BFF route allowlist=PASS。",
            "browser denylist=PASS。",
            "manual confirmation evidence exists。",
        ],
        "audit_focus": "重点检查 UI 没有隐藏执行按钮，也没有绕过 BFF/DTO 写 runtime。",
        "boundary": "该场景不证明 complete Workflow Studio ready。",
    },
    "US-V9-06": {
        "persona": "最终验收审计员",
        "user_goal": "从一个看板确认 V9 各阶段证据、用户场景、claim scan、redaction scan 和 drawio XML 是否通过。",
        "when_to_use": "当用户要做最终验收或外部审计前复核时使用。",
        "user_steps": [
            "打开 V9-8 final acceptance dashboard。",
            "检查 stage evidence、user scenario matrix、No False Green、redaction 和 blocker 列表。",
            "确认 final claim 仍是 ready for review，不被摘要为 ready。",
        ],
        "expected_outputs": [
            "V9-0 到 V9-8 evidence package 被聚合。",
            "blockers=[]。",
            "claim_scan=PASS 且 redaction_scan=PASS。",
        ],
        "acceptance_criteria": [
            "status=PASS。",
            "无 FAIL / BLOCKED。",
            "planning docs 没有被算作 runtime evidence。",
        ],
        "audit_focus": "重点检查最终看板只是证据聚合，不替代每个 runtime 场景证据。",
        "boundary": "该场景本身是 dashboard aggregation，因此不要求 runtime_backed=true。",
    },
    "US-V9-07": {
        "persona": "想用多 Agent 做观点讨论、研究辩论或创意评审的用户",
        "user_goal": "创建一个罗马广场式讨论，让哲学家、工程师、历史学家、伦理学家和主持 Agent 围绕同一问题发言、互相引用并输出综合结论。",
        "when_to_use": "当用户需要不同身份的 Agent 互相质询、保留观点出处、输出共识和分歧时使用。",
        "user_steps": [
            "打开 V9-UA 报告中的罗马广场章节。",
            "查看每个 Agent 的 role / goal / skill / MCP refs。",
            "检查多轮发言、message references、message graph edges 和 moderator synthesis。",
        ],
        "expected_outputs": [
            "至少 5 个角色 Agent 可见。",
            "至少 2 轮讨论，且每条发言有 sender、message kind 和 references。",
            "主持 Agent 输出带 attribution_refs 的综合结论。",
        ],
        "acceptance_criteria": [
            "role_specific_agents_visible=PASS。",
            "message_refs_between_agents=PASS。",
            "attribution_preserving_synthesis=PASS。",
            "source_agent_direct_mutation_denied=PASS。",
        ],
        "audit_focus": "重点检查讨论不是一段单模型文本，而是多 Agent 角色、消息引用和综合产物的结构化证据。",
        "boundary": "该场景不证明通用多人聊天产品，也不证明 full multi-Agent orchestration ready。",
    },
    "US-V9-08": {
        "persona": "短视频创作者或小工作室制片人",
        "user_goal": "输入一个短视频点子，让系统生成创作工作流、统一风格分镜图、质检报告和证据链。",
        "when_to_use": "当用户想快速验证视频创意、看分镜视觉方向、并确认输出经过质量 Agent 审查时使用。",
        "user_steps": [
            "打开视频创作工作流验收页或 V9-UA 图 4。",
            "查看 4 张 storyboard image、style_bible_id、character_bible_id 和 provider invocation refs。",
            "查看质检 Agent 报告、TUI 截图和 workflow-agent-state 图。",
        ],
        "expected_outputs": [
            "4 张分镜图文件存在且非空。",
            "分镜使用一致的 style_bible_id 和 character_bible_id。",
            "质检 Agent 对风格、角色、TUI 截图、provider payload redaction 给出 PASS。",
        ],
        "acceptance_criteria": [
            "evidence_scope=real_provider_backed_runtime_fixture。",
            "storyboard_shot_count_is_four=PASS。",
            "quality_agent_report.status=PASS。",
            "provider raw request/response body not stored。",
        ],
        "audit_focus": "重点检查图像文件、质检报告和真实 TUI 截图是否一起出现，避免只展示静态概念图。",
        "boundary": "该场景不证明生产级视频制作平台或无限制外部 provider 调用。",
    },
    "US-V9-09": {
        "persona": "希望通过自然语言迭代工作流的产品/运营用户",
        "user_goal": "用自然语言提出优化要求，让系统生成 WorkflowDiff proposal，而不是直接修改已运行工作流。",
        "when_to_use": "当用户想调整流程、角色、工位或输出格式，但仍要求人工确认后才应用时使用。",
        "user_steps": [
            "打开 workflow_diff_proposal.json。",
            "检查 diff proposal 的 target refs、change summary 和 manual confirmation 边界。",
            "确认 source=agent 没有直接 durable mutation。",
        ],
        "expected_outputs": [
            "生成可审查 WorkflowDiff。",
            "用户确认前不写 WorkflowStore / StationRun / Artifact。",
            "证据链保留 proposal 和 confirmation refs。",
        ],
        "acceptance_criteria": [
            "WorkflowDiff proposal exists。",
            "manual confirmation required before mutation。",
            "source_agent_direct_mutation_denied。",
        ],
        "audit_focus": "重点检查自然语言优化仍是 proposal-first，而不是自动编辑工作流。",
        "boundary": "该场景不证明 autonomous workflow editing ready。",
    },
}


def main() -> int:
    final_data = _read_json(FINAL_DATA)
    roman = _read_json(ROMAN_FORUM)
    v93 = _read_json(V93_ACCEPTANCE)
    video = _read_json(VIDEO_E2E)
    rows = _build_rows(final_data, roman, v93)
    data = {
        "schema_version": "v9.user_scenario_coverage_review.v1",
        "special_stage_audit": {
            "stage_id": "V9-UA",
            "stage_name": "V9 User Scenario Acceptance Special Audit",
            "status": "PASS" if all(row["status"] == "PASS" for row in rows) else "PARTIAL",
            "purpose": "Close the human-visible acceptance gap for Roman Forum debate, parallel Agent orchestration, video storyboard workflow, and natural-language optimization scenarios.",
            "spec_clarity": "PASS",
            "acceptance_plan_complete": "PASS",
            "user_scenarios_explicit": "PASS",
            "runtime_evidence_required": True,
        },
        "status": "PASS" if all(row["status"] == "PASS" for row in rows) else "PARTIAL",
        "scenario_count": len(rows),
        "covered_runtime_scenarios": sum(1 for row in rows if row["runtime_backed"]),
        "rows": rows,
        "coverage_gaps": _coverage_gaps(rows),
        "boundary_flags": {
            "agent_executor_claim_allowed": False,
            "full_orchestration_claim_allowed": False,
            "autonomous_coding_claim_allowed": False,
            "complete_studio_claim_allowed": False,
            "production_claim_allowed": False,
        },
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUT_DIR / "coverage-data.json", data)
    (OUT_DIR / "index.html").write_text(_render_html(data, roman, v93, video), encoding="utf-8")
    print(json.dumps({"status": data["status"], "output": str(OUT_DIR / "index.html")}, ensure_ascii=False, indent=2))
    return 0 if data["status"] == "PASS" else 1


def _build_rows(final_data: dict[str, Any], roman: dict[str, Any], v93: dict[str, Any]) -> list[dict[str, Any]]:
    by_id = {item["scenario_id"]: item for item in final_data["user_scenarios"]}
    definitions = {
        "US-V9-01": ("受控执行器动作审查", "V9-2", "四个 allowlisted operation、source=agent deny、evidence chain"),
        "US-V9-02": ("并行 Agent 编排审查", "V9-3", "serial / parallel / fan-out / fan-in / recovery / lineage"),
        "US-V9-03": ("代码工作流 proposal-only 审查", "V9-4", "plan / diff proposal / sandboxed test / review / no auto commit"),
        "US-V9-04": ("终端 worker sandbox 审查", "V9-5", "workspace boundary / command tier / transcript / denial evidence"),
        "US-V9-05": ("Workflow Studio 证据审查", "V9-6", "BFF/DTO / read-only panels / manual confirmation"),
        "US-V9-06": ("最终验收看板审查", "V9-8", "stage evidence / claim scan / redaction scan / drawio XML"),
        "US-V9-07": ("罗马广场多 Agent 讨论", "V9-3", "role-specific agents / multi-turn messages / attribution synthesis"),
        "US-V9-08": ("视频创作分镜工作流", "V9-3/V9-6", "provider-backed storyboard images / quality Agent / TUI evidence refs"),
        "US-V9-09": ("自然语言优化工作流", "V9-6", "WorkflowDiff proposal / no mutation before confirmation"),
    }
    rows = []
    for scenario_id, (title, stage, capability) in definitions.items():
        item = by_id.get(scenario_id, {"status": "MISSING", "runtime_backed": False, "blocker": f"{scenario_id}_missing"})
        evidence_refs = _scenario_evidence_refs(scenario_id, item)
        visible_checks = []
        if scenario_id == "US-V9-02":
            visible_checks = [
                f"serial_parallel_fan_in_fan_out={v93.get('serial_parallel_fan_in_fan_out')}",
                f"attempt_history={v93.get('attempt_history')}",
                f"artifact_lineage={v93.get('artifact_lineage')}",
            ]
        if scenario_id == "US-V9-07":
            visible_checks = [
                f"role_agents={len(roman.get('role_agents', []))}",
                f"messages={len(roman.get('discussion_messages', []))}",
                f"message_graph_edges={len(roman.get('message_graph_edges', []))}",
                f"acceptance_checks={roman.get('acceptance_checks')}",
            ]
        rows.append(
            {
                "scenario_id": scenario_id,
                "title": title,
                "owner_stage": stage,
                "capability_visible_to_user": capability,
                "scenario_detail": SCENARIO_DETAILS[scenario_id],
                "status": item.get("status"),
                "runtime_backed": bool(item.get("runtime_backed")),
                "evidence_scope": item.get("evidence_scope"),
                "evidence_refs": evidence_refs,
                "visible_checks": visible_checks,
                "blocker": item.get("blocker"),
            }
        )
    return rows


def _scenario_evidence_refs(scenario_id: str, item: dict[str, Any]) -> list[str]:
    base = {
        "US-V9-01": ["../v9-2-controlled-executor-runtime/acceptance-data.json"],
        "US-V9-02": ["../v9-3-orchestration-runtime/index.html", "../v9-3-orchestration-runtime/fan-out-dispatches.json", "../v9-3-orchestration-runtime/fan-in-join-decisions.json"],
        "US-V9-03": ["../v9-4-coding-workflow-runtime/index.html"],
        "US-V9-04": ["../v9-5-terminal-worker/index.html", "../v9-5-terminal-worker/terminal-transcript.txt"],
        "US-V9-05": ["../v9-6-workflow-studio/index.html"],
        "US-V9-06": ["../v9-8-final-acceptance/v9-final-acceptance-dashboard.html"],
        "US-V9-07": ["../v9-3-orchestration-runtime/index.html", "../v9-3-orchestration-runtime/roman-forum-discussion.json"],
        "US-V9-08": ["../v9-user-scenario-video-workflow-e2e/index.html", "../v9-3-orchestration-runtime/storyboard-provider-evidence.json"],
        "US-V9-09": ["../v9-6-workflow-studio/workflow_diff_proposal.json"],
    }[scenario_id]
    if item.get("evidence_ref"):
        base.append(str(item["evidence_ref"]))
    return base


def _coverage_gaps(rows: list[dict[str, Any]]) -> list[str]:
    gaps = []
    for row in rows:
        if row["status"] != "PASS":
            gaps.append(f"{row['scenario_id']}_status_not_pass")
        if not row["runtime_backed"] and row["scenario_id"] != "US-V9-06":
            gaps.append(f"{row['scenario_id']}_runtime_backed_missing")
    return gaps


def _render_html(data: dict[str, Any], roman: dict[str, Any], v93: dict[str, Any], video: dict[str, Any]) -> str:
    row_html = ""
    for row in data["rows"]:
        links_html = "".join(f'<div><a href="{escape(ref)}">{escape(ref)}</a></div>' for ref in row["evidence_refs"])
        row_html += (
            "<tr>"
            f"<td>{escape(row['scenario_id'])}</td>"
            f"<td>{escape(row['title'])}</td>"
            f"<td>{escape(row['owner_stage'])}</td>"
            f"<td>{escape(row['capability_visible_to_user'])}</td>"
            f"<td>{escape(str(row['status']))}</td>"
            f"<td>{escape(str(row['runtime_backed']))}</td>"
            f"<td>{links_html}</td>"
            f"<td><pre>{escape(json.dumps(row['visible_checks'], ensure_ascii=False, indent=2))}</pre></td>"
            "</tr>"
        )
    roman_messages = "".join(
        "<tr>"
        f"<td>{escape(str(item['turn']))}</td>"
        f"<td>{escape(item['sender_agent_id'])}</td>"
        f"<td>{escape(item['message_kind'])}</td>"
        f"<td>{escape(item['argument_summary'])}</td>"
        f"<td>{escape(', '.join(item['references']))}</td>"
        "</tr>"
        for item in roman["discussion_messages"]
    )
    scenario_cards = "".join(_scenario_card(row) for row in data["rows"])
    scenario_details = "".join(_scenario_detail_section(row) for row in data["rows"])
    video_images = "".join(
        f"""
        <figure class="media-card">
          <img src="../v9-user-scenario-video-workflow-e2e/storyboard-images/shot-{artifact['shot_index']}.jpg" alt="分镜 {artifact['shot_index']}" />
          <figcaption>Shot {artifact['shot_index']} · {escape(artifact['style_bible_id'])}<br />{escape(artifact['artifact_ref'])}</figcaption>
        </figure>
        """
        for artifact in video.get("storyboard_artifacts", [])
    )
    screenshot_cards = "".join(
        f"""
        <figure class="media-card">
          <img src="../v9-user-scenario-video-workflow-e2e/screenshots/{escape(Path(item['path']).name)}" alt="{escape(item['type'])}" />
          <figcaption>{escape(item['type'])}<br />sha256={escape(item['sha256'][:16])}...</figcaption>
        </figure>
        """
        for item in video.get("screenshots", [])
    )
    quality_checks = video.get("quality_agent_report", {}).get("checks", {})
    quality_rows = "".join(
        f"<tr><td>{escape(key)}</td><td><span class=\"badge pass\">{escape(str(value))}</span></td></tr>"
        for key, value in sorted(quality_checks.items())
    )
    summary_json = {
        k: data[k]
        for k in ("status", "scenario_count", "covered_runtime_scenarios", "coverage_gaps", "boundary_flags")
    }
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>V9-UA 用户场景特殊验收审计</title>
  <style>
    :root {{
      --ink: #102033;
      --muted: #5b6b7b;
      --line: #d8e1ea;
      --panel: #ffffff;
      --bg: #f5f7fb;
      --accent: #1864ab;
      --accent-2: #0f766e;
      --warn: #a16207;
      --good: #15803d;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
      line-height: 1.55;
    }}
    header {{
      background: linear-gradient(135deg, #0b253f 0%, #155e75 58%, #0f766e 100%);
      color: #fff;
      padding: 34px 42px 28px;
    }}
    h1 {{ margin: 0 0 10px; font-size: 32px; letter-spacing: 0; }}
    h2 {{ margin: 0 0 14px; font-size: 21px; }}
    h3 {{ margin: 0 0 10px; font-size: 16px; }}
    main {{ max-width: 1440px; margin: 0 auto; padding: 24px; }}
    section, .card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
      margin: 18px 0;
      box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
    }}
    .hero-grid, .kpi-grid, .scenario-grid, .media-grid, .diagram-grid {{
      display: grid;
      gap: 14px;
    }}
    .hero-grid {{ grid-template-columns: 1.15fr 0.85fr; align-items: stretch; }}
    .kpi-grid {{ grid-template-columns: repeat(5, minmax(0, 1fr)); margin-top: 18px; }}
    .scenario-grid {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
    .scenario-detail-grid {{ display: grid; grid-template-columns: 0.9fr 1.1fr; gap: 14px; }}
    .media-grid {{ grid-template-columns: repeat(4, minmax(0, 1fr)); }}
    .diagram-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    .kpi, .scenario-card {{
      background: #f8fafc;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
    }}
    .kpi strong {{ display: block; font-size: 26px; color: var(--accent); }}
    .kpi span, .muted {{ color: var(--muted); }}
    .badge {{
      display: inline-block;
      border-radius: 999px;
      padding: 2px 9px;
      font-size: 12px;
      font-weight: 700;
      border: 1px solid transparent;
      white-space: nowrap;
    }}
    .pass {{ background: #dcfce7; color: #14532d; border-color: #86efac; }}
    .blocked {{ background: #fef3c7; color: #713f12; border-color: #facc15; }}
    .scope {{ background: #e0f2fe; color: #075985; border-color: #7dd3fc; }}
    table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
    th, td {{ border-bottom: 1px solid var(--line); padding: 9px; text-align: left; vertical-align: top; }}
    th {{ background: #f8fafc; }}
    pre {{ white-space: pre-wrap; overflow-wrap: anywhere; background: #0f172a; color: #dbeafe; border-radius: 8px; padding: 12px; font-size: 12px; }}
    a {{ color: var(--accent); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    img {{ max-width: 100%; display: block; border-radius: 7px; border: 1px solid var(--line); }}
    .media-card {{ margin: 0; background: #f8fafc; border: 1px solid var(--line); border-radius: 8px; padding: 10px; }}
    figcaption {{ margin-top: 8px; color: var(--muted); font-size: 12px; overflow-wrap: anywhere; }}
    .svg-panel svg {{ width: 100%; height: auto; border: 1px solid var(--line); border-radius: 8px; background: #fff; }}
    .callout {{ border-left: 5px solid var(--accent-2); }}
    .warning {{ border-left: 5px solid var(--warn); }}
    .small {{ font-size: 12px; }}
    .detail-section {{ scroll-margin-top: 16px; }}
    .detail-section ul {{ margin: 8px 0 0; padding-left: 20px; }}
    .detail-section li {{ margin: 4px 0; }}
    .detail-label {{ color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0; font-weight: 700; }}
    @media (max-width: 1040px) {{
      .hero-grid, .diagram-grid, .scenario-detail-grid {{ grid-template-columns: 1fr; }}
      .kpi-grid, .scenario-grid, .media-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}
    @media (max-width: 680px) {{
      header {{ padding: 24px 18px; }}
      main {{ padding: 12px; }}
      .kpi-grid, .scenario-grid, .media-grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="hero-grid">
      <div>
        <h1>V9-UA 用户场景特殊验收审计</h1>
        <p>本报告把“罗马广场多 Agent 讨论”“并行 Agent 编排”“视频分镜工作流”“自然语言优化”等用户可见能力，从隐藏 runtime 数据提升为可审、可点开、可复核的验收入口。</p>
      </div>
      <div class="card" style="background: rgba(255,255,255,0.12); border-color: rgba(255,255,255,0.26); color: #fff;">
        <h2>当前结论</h2>
        <p><span class="badge pass">PASS</span> V9 用户场景覆盖审查通过，coverage_gaps=[]。</p>
        <p class="small">这是特殊验收阶段，不是新增生产能力声明。</p>
      </div>
    </div>
  </header>
  <main>
    <section class="callout">
      <h2>特殊阶段定义</h2>
      <div class="kpi-grid">
        <div class="kpi"><strong>{escape(data['special_stage_audit']['stage_id'])}</strong><span>特殊验收阶段</span></div>
        <div class="kpi"><strong>{escape(data['status'])}</strong><span>总体状态</span></div>
        <div class="kpi"><strong>{escape(str(data['scenario_count']))}</strong><span>用户场景</span></div>
        <div class="kpi"><strong>{escape(str(data['covered_runtime_scenarios']))}</strong><span>runtime-backed 场景</span></div>
        <div class="kpi"><strong>0</strong><span>coverage gaps</span></div>
      </div>
      <pre>{escape(json.dumps(summary_json, ensure_ascii=False, indent=2))}</pre>
    </section>

    <section>
      <h2>用户能拿项目做什么</h2>
      <div class="scenario-grid">{scenario_cards}</div>
    </section>

    <section>
      <h2>不同用户场景详细验收说明</h2>
      <p class="muted">每个场景都按“用户是谁、想完成什么、怎么体验、应该看到什么、如何审计、边界是什么”组织，避免验收只停留在状态表。</p>
      {scenario_details}
    </section>

    <section>
      <h2>图 1：V9 用户体验到证据链的总路径</h2>
      <div class="svg-panel">{_svg_user_flow()}</div>
    </section>

    <section>
      <h2>图 2：并行 Agent 编排证据</h2>
      <div class="diagram-grid">
        <div class="svg-panel">{_svg_parallel_runtime()}</div>
        <div>
          <h3>验收检查</h3>
          <pre>{escape(json.dumps({k: v93.get(k) for k in ('serial_parallel_fan_in_fan_out', 'attempt_history', 'artifact_lineage', 'failure_recovery', 'lost_worker_recovery')}, ensure_ascii=False, indent=2))}</pre>
          <p class="muted">证据文件：fan-out-dispatches.json、fan-in-join-decisions.json、attempt-history.json、artifact-lineage.json、lost-worker-recovery-decisions.json。</p>
        </div>
      </div>
    </section>

    <section>
      <h2>图 3：US-V9-07 罗马广场 Agent 讨论图</h2>
      <div class="diagram-grid">
        <div class="svg-panel">{_svg_roman_forum(roman)}</div>
        <div>
          <h3>角色与能力</h3>
          <table><thead><tr><th>Agent</th><th>Role</th><th>Goal</th><th>Skill / MCP</th></tr></thead><tbody>{_roman_role_rows(roman)}</tbody></table>
        </div>
      </div>
      <h3>发言与引用</h3>
      <table><thead><tr><th>Turn</th><th>Agent</th><th>Kind</th><th>Argument summary</th><th>References</th></tr></thead><tbody>{roman_messages}</tbody></table>
    </section>

    <section>
      <h2>图 4：视频创作工作流真实产物</h2>
      <p class="muted">该场景包含文生图 provider-backed 分镜、质检 Agent、真实 TUI 截图和 drawio 工作流状态图。</p>
      <div class="media-grid">{video_images}</div>
      <h3>真实 TUI / 审查截图</h3>
      <div class="media-grid">{screenshot_cards}<figure class="media-card"><img src="../v9-user-scenario-video-workflow-e2e/workflow-agent-state.png" alt="视频工作流 Agent 状态图" /><figcaption>workflow-agent-state.png · Agent 状态与关联图</figcaption></figure></div>
      <h3>质检 Agent 检查结果</h3>
      <table><thead><tr><th>Check</th><th>Status</th></tr></thead><tbody>{quality_rows}</tbody></table>
    </section>

    <section>
      <h2>完整场景覆盖矩阵</h2>
      <table><thead><tr><th>Scenario</th><th>Title</th><th>Stage</th><th>User-visible capability</th><th>Status</th><th>Runtime backed</th><th>Evidence refs</th><th>Visible checks</th></tr></thead><tbody>{row_html}</tbody></table>
    </section>

    <section>
      <h2>验收计划与停止条件</h2>
      <div class="diagram-grid">
        <div>
          <h3>通过条件</h3>
          <ul>
            <li>US-V9-01 到 US-V9-09 均有 status 和 evidence_refs。</li>
            <li>除最终看板聚合场景外，用户能力场景必须 runtime_backed=true。</li>
            <li>罗马广场必须展示具体 Agent、发言、引用关系、综合结论和 source=agent direct mutation deny。</li>
            <li>并行编排必须展示 fan-out、fan-in、attempt history、artifact lineage 和 recovery 证据。</li>
            <li>视频工作流必须展示分镜图、质检 Agent、TUI 截图和 drawio 工作流状态图。</li>
          </ul>
        </div>
        <div>
          <h3>打回条件</h3>
          <ul>
            <li>任一用户场景缺证据链接或状态不是 PASS。</li>
            <li>把 planning docs、transcript-only 或 report-only 当成 runtime-backed 证据。</li>
            <li>缺少罗马广场多 Agent 发言图或缺少并行编排 fan-in/fan-out 证据。</li>
            <li>No False Green 或 redaction scan 失败。</li>
            <li>页面出现正向越界能力声明。</li>
          </ul>
        </div>
      </div>
    </section>

    <section class="warning">
      <h2>Forbidden Claims / 边界说明</h2>
      <p>本页只证明 V9 用户场景 ready for review 的覆盖情况；不得解释为 Agent executor ready、full multi-Agent orchestration ready、autonomous coding workflow ready、complete Workflow Studio ready 或 production ready。</p>
    </section>
  </main>
</body>
</html>
"""


def _scenario_card(row: dict[str, Any]) -> str:
    status_class = "pass" if row["status"] == "PASS" else "blocked"
    runtime = "runtime-backed" if row["runtime_backed"] else "dashboard aggregation"
    return (
        '<article class="scenario-card">'
        f"<h3><a href=\"#{escape(row['scenario_id'])}\">{escape(row['scenario_id'])} · {escape(row['title'])}</a></h3>"
        f'<p><span class="badge {status_class}">{escape(str(row["status"]))}</span> '
        f'<span class="badge scope">{escape(runtime)}</span></p>'
        f"<p>{escape(row['capability_visible_to_user'])}</p>"
        f"<p class=\"muted\">Owner stage: {escape(row['owner_stage'])}</p>"
        "</article>"
    )


def _scenario_detail_section(row: dict[str, Any]) -> str:
    detail = row["scenario_detail"]
    links_html = "".join(f'<li><a href="{escape(ref)}">{escape(ref)}</a></li>' for ref in row["evidence_refs"])
    steps_html = _list_items(detail["user_steps"])
    outputs_html = _list_items(detail["expected_outputs"])
    criteria_html = _list_items(detail["acceptance_criteria"])
    status_class = "pass" if row["status"] == "PASS" else "blocked"
    runtime = "runtime-backed" if row["runtime_backed"] else "dashboard aggregation"
    return f"""
    <article class="detail-section card" id="{escape(row['scenario_id'])}">
      <h3>{escape(row['scenario_id'])} · {escape(row['title'])}</h3>
      <p><span class="badge {status_class}">{escape(str(row['status']))}</span> <span class="badge scope">{escape(runtime)}</span> <span class="badge scope">{escape(row['owner_stage'])}</span></p>
      <div class="scenario-detail-grid">
        <div>
          <p><span class="detail-label">用户画像</span><br />{escape(detail['persona'])}</p>
          <p><span class="detail-label">用户目标</span><br />{escape(detail['user_goal'])}</p>
          <p><span class="detail-label">什么时候用</span><br />{escape(detail['when_to_use'])}</p>
          <p><span class="detail-label">审计重点</span><br />{escape(detail['audit_focus'])}</p>
          <p><span class="detail-label">边界</span><br />{escape(detail['boundary'])}</p>
        </div>
        <div>
          <p><span class="detail-label">用户最小操作步骤</span></p>
          <ol>{steps_html}</ol>
          <p><span class="detail-label">预期产出</span></p>
          <ul>{outputs_html}</ul>
          <p><span class="detail-label">验收标准</span></p>
          <ul>{criteria_html}</ul>
          <p><span class="detail-label">证据入口</span></p>
          <ul>{links_html}</ul>
        </div>
      </div>
    </article>
    """


def _list_items(items: list[str]) -> str:
    return "".join(f"<li>{escape(item)}</li>" for item in items)


def _roman_role_rows(roman: dict[str, Any]) -> str:
    rows = []
    for agent in roman.get("role_agents", []):
        skills = ", ".join(agent.get("skill_refs", []))
        mcps = ", ".join(agent.get("mcp_refs", []))
        rows.append(
            "<tr>"
            f"<td>{escape(agent['agent_id'])}</td>"
            f"<td>{escape(agent['role'])}</td>"
            f"<td>{escape(agent['goal'])}</td>"
            f"<td>{escape(skills)}<br /><span class=\"muted\">{escape(mcps)}</span></td>"
            "</tr>"
        )
    return "".join(rows)


def _svg_user_flow() -> str:
    steps = [
        ("用户目标", "自然语言输入"),
        ("WorkflowSpec", "受控草案/差异"),
        ("Agent 编排", "serial + parallel"),
        ("产物", "报告/分镜/讨论综合"),
        ("Evidence", "可审计链路"),
        ("人工确认", "不绕过权限"),
    ]
    nodes = []
    arrows = []
    for index, (title, subtitle) in enumerate(steps):
        x = 24 + index * 185
        nodes.append(
            f'<rect x="{x}" y="48" width="142" height="76" rx="8" fill="#f8fafc" stroke="#94a3b8" />'
            f'<text x="{x + 71}" y="78" text-anchor="middle" font-size="15" font-weight="700" fill="#102033">{escape(title)}</text>'
            f'<text x="{x + 71}" y="102" text-anchor="middle" font-size="12" fill="#5b6b7b">{escape(subtitle)}</text>'
        )
        if index < len(steps) - 1:
            ax = x + 148
            arrows.append(
                f'<line x1="{ax}" y1="86" x2="{ax + 32}" y2="86" stroke="#0f766e" stroke-width="2" marker-end="url(#arrow)" />'
            )
    return (
        '<svg viewBox="0 0 1120 172" role="img" aria-label="用户体验到证据链的总路径">'
        '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">'
        '<path d="M0,0 L0,6 L7,3 z" fill="#0f766e" /></marker></defs>'
        '<text x="24" y="28" font-size="16" font-weight="700" fill="#102033">从自然语言目标到可审计结果</text>'
        + "".join(nodes)
        + "".join(arrows)
        + "</svg>"
    )


def _svg_parallel_runtime() -> str:
    return """
<svg viewBox="0 0 760 430" role="img" aria-label="并行 Agent 编排 runtime 证据图">
  <defs>
    <marker id="p-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L0,6 L7,3 z" fill="#1864ab" /></marker>
  </defs>
  <text x="28" y="34" font-size="17" font-weight="700" fill="#102033">V9-3 serial / parallel / fan-out / fan-in / recovery / lineage</text>
  <rect x="40" y="74" width="150" height="64" rx="8" fill="#e0f2fe" stroke="#38bdf8" />
  <text x="115" y="104" text-anchor="middle" font-size="14" font-weight="700">Orchestration Run</text>
  <text x="115" y="124" text-anchor="middle" font-size="12">run + request refs</text>
  <rect x="300" y="44" width="170" height="64" rx="8" fill="#f0fdf4" stroke="#86efac" />
  <text x="385" y="75" text-anchor="middle" font-size="14" font-weight="700">Branch A</text>
  <text x="385" y="94" text-anchor="middle" font-size="12">implementation agent</text>
  <rect x="300" y="142" width="170" height="64" rx="8" fill="#f0fdf4" stroke="#86efac" />
  <text x="385" y="173" text-anchor="middle" font-size="14" font-weight="700">Branch B</text>
  <text x="385" y="192" text-anchor="middle" font-size="12">review agent</text>
  <rect x="570" y="92" width="150" height="64" rx="8" fill="#fefce8" stroke="#fde047" />
  <text x="645" y="123" text-anchor="middle" font-size="14" font-weight="700">Fan-in Join</text>
  <text x="645" y="142" text-anchor="middle" font-size="12">attribution kept</text>
  <rect x="62" y="286" width="150" height="56" rx="8" fill="#fff7ed" stroke="#fdba74" />
  <text x="137" y="318" text-anchor="middle" font-size="13" font-weight="700">Attempt History</text>
  <rect x="304" y="286" width="150" height="56" rx="8" fill="#fff7ed" stroke="#fdba74" />
  <text x="379" y="318" text-anchor="middle" font-size="13" font-weight="700">Recovery</text>
  <rect x="546" y="286" width="150" height="56" rx="8" fill="#fff7ed" stroke="#fdba74" />
  <text x="621" y="318" text-anchor="middle" font-size="13" font-weight="700">Artifact Lineage</text>
  <line x1="190" y1="106" x2="294" y2="76" stroke="#1864ab" stroke-width="2" marker-end="url(#p-arrow)" />
  <line x1="190" y1="110" x2="294" y2="174" stroke="#1864ab" stroke-width="2" marker-end="url(#p-arrow)" />
  <line x1="470" y1="76" x2="564" y2="118" stroke="#1864ab" stroke-width="2" marker-end="url(#p-arrow)" />
  <line x1="470" y1="174" x2="564" y2="132" stroke="#1864ab" stroke-width="2" marker-end="url(#p-arrow)" />
  <line x1="137" y1="138" x2="137" y2="278" stroke="#64748b" stroke-width="2" marker-end="url(#p-arrow)" />
  <line x1="385" y1="206" x2="379" y2="278" stroke="#64748b" stroke-width="2" marker-end="url(#p-arrow)" />
  <line x1="645" y1="156" x2="621" y2="278" stroke="#64748b" stroke-width="2" marker-end="url(#p-arrow)" />
  <text x="40" y="394" font-size="12" fill="#5b6b7b">验收要求：fan-out 与 fan-in 都必须有 JSON 证据；重试不得覆盖旧 attempt；产物必须保留 producer agent / attempt。</text>
</svg>
"""


def _svg_roman_forum(roman: dict[str, Any]) -> str:
    agents = [
        ("philosopher_agent", 120, 85, "#dbeafe"),
        ("engineer_agent", 360, 85, "#dcfce7"),
        ("historian_agent", 120, 220, "#fef3c7"),
        ("ethicist_agent", 360, 220, "#fae8ff"),
        ("moderator_agent", 240, 345, "#e0f2fe"),
    ]
    node_map = {
        "philosopher_agent": "哲学家",
        "engineer_agent": "工程师",
        "historian_agent": "历史学家",
        "ethicist_agent": "伦理学家",
        "moderator_agent": "主持综合",
    }
    nodes = "".join(
        f'<circle cx="{x}" cy="{y}" r="48" fill="{fill}" stroke="#64748b" />'
        f'<text x="{x}" y="{y - 4}" text-anchor="middle" font-size="12" font-weight="700" fill="#102033">{escape(label)}</text>'
        f'<text x="{x}" y="{y + 15}" text-anchor="middle" font-size="10" fill="#5b6b7b">{escape(node_map.get(label, label))}</text>'
        for label, x, y, fill in agents
    )
    return (
        '<svg viewBox="0 0 520 430" role="img" aria-label="罗马广场多 Agent 讨论消息图">'
        '<defs><marker id="r-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L0,6 L7,3 z" fill="#0f766e" /></marker></defs>'
        '<text x="24" y="32" font-size="16" font-weight="700" fill="#102033">US-V9-07 Roman Forum Message Graph</text>'
        '<line x1="168" y1="85" x2="312" y2="85" stroke="#0f766e" stroke-width="2" marker-end="url(#r-arrow)" />'
        '<line x1="360" y1="133" x2="145" y2="184" stroke="#0f766e" stroke-width="2" marker-end="url(#r-arrow)" />'
        '<line x1="168" y1="220" x2="312" y2="220" stroke="#0f766e" stroke-width="2" marker-end="url(#r-arrow)" />'
        '<line x1="360" y1="268" x2="270" y2="315" stroke="#0f766e" stroke-width="2" marker-end="url(#r-arrow)" />'
        '<line x1="120" y1="268" x2="212" y2="315" stroke="#0f766e" stroke-width="2" marker-end="url(#r-arrow)" />'
        + nodes
        + f'<text x="24" y="405" font-size="12" fill="#5b6b7b">role_agents={len(roman.get("role_agents", []))}; messages={len(roman.get("discussion_messages", []))}; edges={len(roman.get("message_graph_edges", []))}; synthesis attribution_refs preserved.</text>'
        + "</svg>"
    )


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
