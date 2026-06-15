from __future__ import annotations

import json
import subprocess
from pathlib import Path

from tools.v9.generate_v9_8_final_acceptance import build_final_acceptance


OUT_DIR = Path("docs/design/V9.x/evidence/v9-8-final-acceptance")
SCENARIO_REVIEW_DIR = Path("docs/design/V9.x/evidence/v9-user-scenario-coverage-review")


def test_v9_8_allows_final_claim_when_storyboard_provider_evidence_passes() -> None:
    data = build_final_acceptance()

    assert data["status"] == "PASS"
    assert data["final_claim"] == "V9 complete: high-risk Agent execution and workflow productization baseline ready for review."
    assert data["blockers"] == []
    assert data["production_ready"] is False
    assert data["agent_executor_ready"] is False
    assert data["complete_workflow_studio_ready"] is False
    scenarios = {item["scenario_id"]: item for item in data["user_scenarios"]}
    assert scenarios["US-V9-08"]["evidence_scope"] == "real_provider_backed_runtime_fixture"
    assert scenarios["US-V9-08"]["storyboard_image_count"] == 4
    assert scenarios["US-V9-07"]["runtime_backed"] is True
    assert scenarios["US-V9-07"]["message_graph_ref"] == "roman-forum-discussion.json"
    assert len(scenarios["US-V9-07"]["role_specific_agents"]) >= 5
    assert len(scenarios["US-V9-07"]["message_refs"]) >= 5


def test_v9_8_generates_pass_dashboard_without_forbidden_capability_claims() -> None:
    result = subprocess.run(["./.venv/bin/python", "-m", "tools.v9.generate_v9_8_final_acceptance"], check=False, text=True, capture_output=True)

    assert result.returncode == 0
    assert (OUT_DIR / "v9-final-acceptance-dashboard.html").exists()
    assert (OUT_DIR / "v9-final-acceptance-data.json").exists()
    data = json.loads((OUT_DIR / "v9-final-acceptance-data.json").read_text(encoding="utf-8"))
    assert data["status"] == "PASS"
    assert data["final_claim"]
    assert data["planning_docs_counted_as_runtime_evidence"] is False
    assert data["agent_executor_ready"] is False
    assert data["full_multi_agent_orchestration_ready"] is False


def test_v9_8_global_gates_pass_with_provider_backed_storyboard_evidence() -> None:
    data = build_final_acceptance()

    assert data["claim_scan"] == "PASS"
    assert data["redaction_scan"] == "PASS"
    assert data["drawio_xml"] == "PASS"
    assert all(item["status"] == "PASS" for item in data["stage_results"])


def test_v9_user_scenario_special_acceptance_report_is_human_readable() -> None:
    result = subprocess.run(["./.venv/bin/python", "-m", "tools.v9.generate_v9_user_scenario_coverage_review"], check=False, text=True, capture_output=True)

    assert result.returncode == 0
    html = (SCENARIO_REVIEW_DIR / "index.html").read_text(encoding="utf-8")
    data = json.loads((SCENARIO_REVIEW_DIR / "coverage-data.json").read_text(encoding="utf-8"))
    assert data["special_stage_audit"]["stage_id"] == "V9-UA"
    assert data["special_stage_audit"]["spec_clarity"] == "PASS"
    assert data["coverage_gaps"] == []
    assert data["rows"][6]["scenario_detail"]["persona"] == "想用多 Agent 做观点讨论、研究辩论或创意评审的用户"
    assert data["rows"][7]["scenario_detail"]["user_goal"].startswith("输入一个短视频点子")
    assert "图 2：并行 Agent 编排证据" in html
    assert "图 3：US-V9-07 罗马广场 Agent 讨论图" in html
    assert "图 4：视频创作工作流真实产物" in html
    assert "不同用户场景详细验收说明" in html
    assert "用户最小操作步骤" in html
    assert "想用多 Agent 做观点讨论、研究辩论或创意评审的用户" in html
    assert "短视频创作者或小工作室制片人" in html
    assert "通过 Product Console / Thin Web Console 查看 runtime report" in html
    assert "workflow-agent-state.png" in html
    assert "storyboard-images/shot-1.jpg" in html
    assert "real-openharness-textual-tui-window.png" in html
    assert "发言与引用" in html
