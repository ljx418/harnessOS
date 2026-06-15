from __future__ import annotations

import json
import subprocess
from pathlib import Path


OUT_DIR = Path("docs/design/V10.x/evidence/v10-0-tui-experience-planning")


def test_v10_0_report_generator_outputs_readable_concept_package() -> None:
    result = subprocess.run(
        ["./.venv/bin/python", "-m", "tools.v10.generate_v10_tui_experience_report"],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    data = json.loads((OUT_DIR / "acceptance-data.json").read_text(encoding="utf-8"))
    html = (OUT_DIR / "index.html").read_text(encoding="utf-8")
    assert data["status"] == "PASS"
    assert data["stage_id"] == "V10-0R"
    assert data["selected_route"] == "React/Ink CLI-native Mission TUI"
    assert data["visual_direction"] == "Codex/ClaudeCode-like terminal-native baseline"
    assert data["runtime_implementation_started"] is False
    assert data["host_generated_image_ref"] is None
    assert data["terminal_native_acceptance"]["bottom_composer_required"] is True
    assert "M7 final UX acceptance" in data["milestone_roadmap"]
    assert "US-V10-03 video storyboard workflow" in data["user_scenario_matrix"]
    assert "React/Ink 终端原生 TUI" in html
    assert "V10-0R CLI-native TUI 体验修订" in html
    assert "交互概念设计" in html
    assert "concept-cli-native-interaction-board.png" in html
    assert "旧的 cockpit 图保留为历史证据" in html
    assert (OUT_DIR / "concept-cli-native-interaction-board.html").exists()
    assert (OUT_DIR / "concept-cli-native-interaction-board.png").exists()
    assert "底部 composer" in (OUT_DIR / "concept-terminal-message-stream.svg").read_text(encoding="utf-8")
    assert "Slash Command Onboarding" in (OUT_DIR / "concept-command-palette-onboarding.svg").read_text(encoding="utf-8")
    assert "permission" in (OUT_DIR / "concept-tool-permission-blocks.svg").read_text(encoding="utf-8")
    assert "WorkflowDiff proposal" in (OUT_DIR / "concept-station-output-preview.svg").read_text(encoding="utf-8")
    assert "source=agent durable mutation denied" in (OUT_DIR / "concept-workflowdiff-review.svg").read_text(encoding="utf-8")


def test_v10_docs_preserve_false_green_boundaries() -> None:
    guard = Path("docs/design/V10.x/v10_no_false_green_claim_guard.md").read_text(encoding="utf-8")
    readme = Path("docs/design/V10.x/00_README.md").read_text(encoding="utf-8")

    assert "Forbidden Claims" in guard
    assert "Do not shorten \"ready for review\" to \"ready\"" in guard
    assert "Do not keep cockpit/dashboard images as the current V10 target direction." in guard
    assert "V10-1..V10-7 complete: CLI-native read-model TUI experience baseline ready for review." in readme
    assert "V10-8 complete: Agent-backed Mission TUI chatbot bridge ready for review." in readme
    assert "V10 complete: CLI-native Agent-backed TUI experience and explainability baseline ready for review." in readme


def test_v10_docs_define_cli_native_acceptance() -> None:
    plan = Path("docs/design/V10.x/v10_development_and_acceptance_plan.md").read_text(encoding="utf-8")
    prd = Path("docs/design/V10.x/v10_target_prd.md").read_text(encoding="utf-8")
    drawio = Path("docs/design/V10.x/v10_current_gap_analysis.drawio").read_text(encoding="utf-8")
    concepts = Path("docs/design/V10.x/v10_cli_native_interaction_concepts.md").read_text(encoding="utf-8")
    roadmap = Path("docs/design/V10.x/v10_milestone_roadmap.md").read_text(encoding="utf-8")
    readme = Path("docs/design/V10.x/00_README.md").read_text(encoding="utf-8")
    state_contract = Path("docs/design/V10.x/v10_tui_state_contract.md").read_text(encoding="utf-8")
    bridge_contract = Path("docs/design/V10.x/v10_runtime_bridge_contract.md").read_text(encoding="utf-8")
    fixture_matrix = Path("docs/design/V10.x/v10_test_fixture_matrix.md").read_text(encoding="utf-8")
    schema_package = Path("docs/design/V10.x/v10_schema_and_fixture_package.md").read_text(encoding="utf-8")
    readiness = Path("docs/design/V10.x/v10_implementation_readiness_audit.md").read_text(encoding="utf-8")
    stage_specs = Path("docs/design/V10.x/v10_stage_implementation_specs.md").read_text(encoding="utf-8")
    scenario_gate = Path("docs/design/V10.x/v10_user_scenario_acceptance_gate.md").read_text(encoding="utf-8")
    final_framework = Path("docs/design/V10.x/v10_final_acceptance_framework.md").read_text(encoding="utf-8")

    assert "80x24 terminal snapshot remains readable without a side rail." in plan
    assert "Concept images and HTML reports are not accepted as real TUI screenshots." in plan
    assert "Agent-backed TUI bridge through Gateway session/turn" in plan
    assert "US-V10-03 video storyboard workflow" in plan
    assert "single-column conversation stream, bottom composer" in prd
    assert "Agent-backed bridge" in prd
    assert "Video Storyboard" in prd
    assert "M0：V10-0R planning correction PASS" in drawio
    assert "V10-8 Agent-backed" in drawio
    assert "JSONL RPC" in drawio
    assert "US-V10-03 视频分镜" in drawio
    assert "Canonical Docs" in drawio
    assert "Implementation Gates" in drawio
    assert "Tool Permission" in concepts
    assert "WorkflowDiff Review" in concepts
    assert "M7" in roadmap
    assert "MissionTuiState" in state_contract
    assert "source=agent must not directly perform durable mutation" in state_contract
    assert "Event Mapping" in bridge_contract
    assert "station_without_evidence_ref.json" in fixture_matrix
    assert "mission_tui_state.schema.json" in schema_package
    assert "source_agent_direct_mutation_action.json" in schema_package
    assert "V10-1 implementation readiness review" in readiness
    assert "Schema And Fixture Package" in readiness
    assert "supports_v10_stage_by_stage_development=true" in readiness
    assert "V10-5 Natural-Language WorkflowDiff Preview" in stage_specs
    assert "US-V10-02 Roman Forum Discussion" in scenario_gate
    assert "Fixture/local-parser evidence is used as Agent-backed proof" in final_framework
    assert "v10_milestone_roadmap.md" in readme
    assert "v10_runtime_bridge_contract.md" in readme
    assert "v10_schema_and_fixture_package.md" in readme
    assert "v10_user_scenario_acceptance_gate.md" in readme
    assert "cockpit/dashboard concept" not in prd
