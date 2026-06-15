from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SHELL_DIR = ROOT / "docs/design/V10.x/evidence/v10-1-mission-tui-shell"
FINAL_DIR = ROOT / "docs/design/V10.x/evidence/v10-7-final-acceptance"
AGENT_BACKED_DIR = ROOT / "docs/design/V10.x/evidence/v10-8-agent-backed-tui"
V10_FINAL_DIR = ROOT / "docs/design/V10.x/evidence/v10-9-final-acceptance"


def test_v10_mission_tui_package_tests_and_acceptance() -> None:
    test_result = subprocess.run(
        ["npm", "--prefix", "apps/mission-tui", "test"],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    assert test_result.returncode == 0, test_result.stdout + test_result.stderr

    acceptance_result = subprocess.run(
        ["npm", "--prefix", "apps/mission-tui", "run", "acceptance"],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    assert acceptance_result.returncode == 0, acceptance_result.stdout + acceptance_result.stderr

    agent_backed_result = subprocess.run(
        ["npm", "--prefix", "apps/mission-tui", "run", "acceptance:v10-8"],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    assert agent_backed_result.returncode == 0, agent_backed_result.stdout + agent_backed_result.stderr

    final_result = subprocess.run(
        ["npm", "--prefix", "apps/mission-tui", "run", "acceptance:v10-final"],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    assert final_result.returncode == 0, final_result.stdout + final_result.stderr

    shell_data = json.loads((SHELL_DIR / "acceptance-data.json").read_text(encoding="utf-8"))
    final_data = json.loads((FINAL_DIR / "v10-final-acceptance-data.json").read_text(encoding="utf-8"))
    agent_backed_data = json.loads((AGENT_BACKED_DIR / "acceptance-data.json").read_text(encoding="utf-8"))
    v10_final_data = json.loads((V10_FINAL_DIR / "v10-final-acceptance-data.json").read_text(encoding="utf-8"))
    screen_80 = (SHELL_DIR / "real-tui-80x24.txt").read_text(encoding="utf-8")
    screen_120 = (SHELL_DIR / "real-tui-120x40.txt").read_text(encoding="utf-8")
    agent_backed_screen = (AGENT_BACKED_DIR / "agent-backed-terminal-180x55.txt").read_text(encoding="utf-8")

    assert shell_data["status"] == "PASS"
    assert shell_data["evidence_scope"] == "real_tui_render_fixture"
    assert shell_data["openharness_primary_copy_present"] is False
    assert shell_data["concept_images_are_runtime_evidence"] is False
    assert "HarnessOS" in screen_80
    assert "› 输入消息或 /command" in screen_80
    assert "WorkflowDiff" in screen_80
    assert "OpenHarness" not in screen_80
    assert "Document Scanner Agent" in screen_120
    assert "Stoic Persona Agent" in screen_120
    assert "Storyboard Agent" in screen_120
    assert "Coding Proposal Agent" in screen_120
    assert final_data["status"] == "PASS"
    assert final_data["read_model_baseline_claim_allowed"] is True
    assert final_data["final_claim_allowed"] is False
    assert final_data["final_v10_completion_blocked_until_v10_8"] is True
    assert len(final_data["stage_evidence"]) == 6
    assert final_data["claim_scan"] == "PASS"
    assert final_data["redaction_scan"] == "PASS"
    assert len(final_data["user_scenarios"]) == 5
    assert agent_backed_data["status"] == "PASS"
    assert agent_backed_data["evidence_scope"] == "agent_backed_gateway_turn"
    assert agent_backed_data["runtime_backed"] is True
    assert agent_backed_data["fixture_only"] is False
    assert agent_backed_data["local_parser_only"] is False
    assert agent_backed_data["gateway_session_started"] is True
    assert agent_backed_data["gateway_turn_started"] is True
    assert agent_backed_data["assistant_output_from_gateway"] is True
    assert agent_backed_data["provider_mode"] in {"provider-backed", "local-runtime", "demo-fallback"}
    assert "mode:agent-backed" in agent_backed_screen
    assert "Gateway 事件" in agent_backed_screen
    assert "turn.started" in agent_backed_screen
    assert "turn.completed" in agent_backed_screen or "turn.failed" in agent_backed_screen
    assert "local-interactive-no-provider" not in agent_backed_screen
    assert v10_final_data["status"] == "PASS"
    assert v10_final_data["final_claim_allowed"] is True
    assert v10_final_data["v10_8_agent_backed_bridge"]["runtime_backed"] is True
    assert v10_final_data["bounded_interpretation"]["production_ready"] is False
    assert v10_final_data["bounded_interpretation"]["agent_executor_ready"] is False
    assert v10_final_data["provider_backed_claim_allowed"] is (
        agent_backed_data["provider_backed"] is True
    )


def test_v10_mission_tui_cli_rejects_negative_fixture() -> None:
    result = subprocess.run(
        [
            "node",
            "apps/mission-tui/src/cli.js",
            "--fixture",
            "apps/mission-tui/fixtures/workflowdiff_auto_apply_action.json",
            "--validate",
        ],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 2
    assert "auto_apply_workflowdiff" in result.stderr
