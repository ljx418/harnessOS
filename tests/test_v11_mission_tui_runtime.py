from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
V11_DIR = ROOT / "docs/design/V11.x"
V11_0_DIR = V11_DIR / "evidence/v11-0-architecture-contract"
V11_1_DIR = V11_DIR / "evidence/v11-1-real-time-event-stream"
V11_2_DIR = V11_DIR / "evidence/v11-2-command-ux"


def test_v11_0_architecture_contract_evidence_is_frozen() -> None:
    data = json.loads((V11_0_DIR / "architecture-contract-acceptance.json").read_text(encoding="utf-8"))
    drawio_validation = (V11_0_DIR / "drawio-validation.txt").read_text(encoding="utf-8")
    document_audit = (V11_0_DIR / "document-audit.md").read_text(encoding="utf-8")

    assert data["stage_id"] == "V11-0"
    assert data["status"] == "PASS"
    assert data["runtime_backed"] is False
    assert data["drawio_xml"] == "PASS"
    assert data["architecture_contract"] == "PASS"
    assert data["document_audit"] == "PASS"
    assert data["bounded_interpretation"]["production_ready"] is False
    assert data["bounded_interpretation"]["agent_executor_ready"] is False
    assert data["bounded_interpretation"]["complete_workflow_studio_ready"] is False
    assert data["stop_conditions_triggered"] == []
    assert data["claim_scan"] == "PASS"
    assert data["redaction_scan"] == "PASS"
    assert "result: PASS" in drawio_validation
    assert "V11 inherits V4-V10 runtime" in document_audit


def test_v11_1_real_time_event_stream_evidence_is_runtime_backed() -> None:
    data = json.loads((V11_1_DIR / "acceptance-data.json").read_text(encoding="utf-8"))
    events = [
        json.loads(line)
        for line in (V11_1_DIR / "events.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    snapshots = json.loads((V11_1_DIR / "tui-state-snapshots.json").read_text(encoding="utf-8"))
    transcript = (V11_1_DIR / "cli-transcript.txt").read_text(encoding="utf-8")

    assert data["stage_id"] == "V11-1"
    assert data["status"] == "PASS"
    assert data["runtime_backed"] is True
    assert data["provider_backed"] is True
    assert data["provider_mode"] == "provider-backed"
    assert data["runtime_backend"] in {"simple", "openharness"}
    assert data["provider_evidence_mode"] in {
        "provider-backed",
        "simple_runtime_openai_compatible_llm_call",
    }
    assert data["dotenv_loaded_count"] >= 1
    assert data["evidence_scope"] == "provider_backed_cli_turn_or_gateway_runtime"
    assert data["input_received_visible"] is True
    assert data["agent_running_visible"] is True
    assert data["gateway_turn_started"] is True
    assert data["gateway_turn_completed"] is True
    assert data["gateway_turn_failed"] is False
    assert data["failed_turn_can_satisfy_completion"] is False
    assert data["event_ordering_errors"] == []
    assert data["claim_scan"] == "PASS"
    assert data["redaction_scan"] == "PASS"
    assert data["runtime_truth_boundary"] == "tui_read_model_not_runtime_truth"

    event_types = [event["event_type"] for event in events]
    assert "gateway.session.started" in event_types
    assert "input.received" in event_types
    assert "agent.running" in event_types
    assert "turn.started" in event_types
    assert "assistant.delta" in event_types
    assert "turn.completed" in event_types
    assert "turn.failed" not in event_types
    assert event_types.index("input.received") < event_types.index("turn.started")
    assert event_types.index("turn.started") < event_types.index("turn.completed")

    phases = [snapshot.get("phase") for snapshot in snapshots]
    assert "input_received" in phases
    assert "agent_running" in phases
    assert "completed" in phases
    assert "Gateway 事件" in transcript
    assert "turn.started" in transcript
    assert "turn.completed" in transcript


def test_v11_2_slash_command_evidence_is_non_mutating() -> None:
    data = json.loads((V11_2_DIR / "acceptance-data.json").read_text(encoding="utf-8"))
    transcript = (V11_2_DIR / "slash-command-transcript.txt").read_text(encoding="utf-8")
    invalid_transcript = (V11_2_DIR / "invalid-command-transcript.txt").read_text(encoding="utf-8")
    terminal = (V11_2_DIR / "terminal-render.txt").read_text(encoding="utf-8")

    assert data["stage_id"] == "V11-2"
    assert data["status"] == "PASS"
    assert data["evidence_scope"] == "tui_command_transcript"
    assert data["runtime_backed"] is False
    assert data["durable_mutation_performed"] is False
    assert data["invalid_command_feedback_visible"] is True
    assert data["slash_commands_cannot_apply_publish_run"] is True
    assert "/help" in data["commands_covered"]
    assert "/station station-storyboard" in data["commands_covered"]
    assert data["errors"] == []
    assert data["claim_scan"] == "PASS"
    assert data["redaction_scan"] == "PASS"
    assert "WorkflowDiff" in transcript
    assert "确认前不会 apply/publish/run" in transcript
    assert "未知命令" in invalid_transcript
    assert "›" in terminal


def test_v11_documents_freeze_evidence_and_stage_gate_rules() -> None:
    acceptance_gate = (V11_DIR / "v11_acceptance_gate.md").read_text(encoding="utf-8")
    stage_specs = (V11_DIR / "v11_stage_implementation_specs.md").read_text(encoding="utf-8")
    claim_guard = (V11_DIR / "v11_no_false_green_claim_guard.md").read_text(encoding="utf-8")

    assert "docs/design/V11.x/evidence/" in acceptance_gate
    assert "Final Aggregator Rules" in acceptance_gate
    assert "Provider-Backed And Fixture-Backed Evidence Priority" in acceptance_gate
    assert "V11-1 Event Ordering Assertions" in acceptance_gate
    assert "input.received must be recorded before" in acceptance_gate
    assert "turn.failed cannot be followed by turn.completed" in acceptance_gate

    assert "Global Stage Evidence Rules" in stage_specs
    assert "events.jsonl" in stage_specs
    assert "tui-state-snapshots.json" in stage_specs
    assert "HTML explainer is always supporting-only" in stage_specs

    assert "Stage Claim Order Rule" in claim_guard
    assert "V11-N complete cannot be claimed" in claim_guard


def test_v11_drawio_xml_is_valid() -> None:
    result = subprocess.run(
        ["xmllint", "--noout", "docs/design/V11.x/v11_current_gap_analysis.drawio"],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
