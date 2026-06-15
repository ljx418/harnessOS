import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
V12 = ROOT / "docs/design/V12-V15.x"


def _load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def test_v12_canonical_readiness_files_exist():
    for relative in [
        "00_README.md",
        "v12_to_v15_no_false_green_claim_guard.md",
        "v12_implementation_readiness_plan.md",
        "v12_product_entity_and_workbench_contracts.md",
        "v12_bff_route_and_browser_boundary.md",
        "v12_evidence_and_user_acceptance_plan.md",
        "v12_to_v15_automated_ux_test_matrix.md",
        "v12_to_v15_current_gap_analysis.drawio",
    ]:
        assert (V12 / relative).exists(), relative


def test_v12_schema_and_fixture_json_parse():
    for relative in [
        "schemas/v12_product_entity_projection.schema.json",
        "schemas/v12_canvas_read_model.schema.json",
        "schemas/v12_browser_network_log.schema.json",
        "schemas/v12_acceptance_data.schema.json",
        "fixtures/v12/product_entity_projection.sample.json",
        "fixtures/v12/canvas_read_model.sample.json",
        "fixtures/v12/browser_network_log.sample.json",
        "fixtures/v12/v12_acceptance_data.sample.json",
        "fixtures/v12/forbidden_direct_runtime_call.negative.json",
    ]:
        assert _load_json(V12 / relative), relative


def test_v12_acceptance_fixture_contains_required_evidence_refs():
    data = _load_json(V12 / "fixtures/v12/v12_acceptance_data.sample.json")
    assert data["stage_id"] == "V12"
    assert data["status"] == "PASS"
    assert data["evidence_scope"] == "browser_e2e"
    assert data["schema_parse_result"] == "PASS"
    assert data["browser_network_result"] == "PASS"
    assert data["claim_scan"] == "PASS"
    assert data["redaction_scan"] == "PASS"
    assert {item["check_id"] for item in data["ux_checks"]} >= {
        "ux_v12_product_entry_visible",
        "ux_v12_canvas_shell_visible",
        "ux_v12_disabled_canvas_action_has_reason",
        "ux_v12_workflowdiff_handoff_visible",
        "ux_v12_agent_profile_visible",
    }


def test_v12_negative_fixture_blocks_direct_runtime_route():
    data = _load_json(V12 / "fixtures/v12/forbidden_direct_runtime_call.negative.json")
    assert data["forbidden_route_scan"]["status"] == "FAIL"
    assert "/v1/internal/runtime" in data["forbidden_route_scan"]["forbidden_matches"]


def test_v12_canvas_read_model_is_read_only():
    data = _load_json(V12 / "fixtures/v12/canvas_read_model.sample.json")
    assert data["read_only"] is True
    assert data["nodes"]
    assert data["evidence_refs"]
