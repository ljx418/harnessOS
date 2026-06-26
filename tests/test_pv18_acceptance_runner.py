"""PV18 Knowledge OPC acceptance runner tests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_pv18_acceptance_runner_passes_complete_temp_package(tmp_path) -> None:
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    _write_complete_package(evidence)
    report = tmp_path / "report.json"

    result = subprocess.run(
        [
            sys.executable,
            "tools/pv18/run_knowledge_opc_acceptance.py",
            "--evidence-dir",
            str(evidence),
            "--report-path",
            str(report),
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    assert result.returncode == 0, result.stdout
    payload = json.loads(report.read_text(encoding="utf-8"))
    assert payload["status"] == "PASS"
    assert payload["route_boundary"]["status"] == "PASS"
    assert payload["platform_generality"]["status"] == "PASS"


def test_pv18_acceptance_runner_fails_missing_package(tmp_path) -> None:
    evidence = tmp_path / "missing"
    report = tmp_path / "report.json"

    result = subprocess.run(
        [
            sys.executable,
            "tools/pv18/run_knowledge_opc_acceptance.py",
            "--evidence-dir",
            str(evidence),
            "--report-path",
            str(report),
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    assert result.returncode == 1
    payload = json.loads(report.read_text(encoding="utf-8"))
    assert payload["status"] == "FAIL"
    assert "acceptance-data.json" in payload["missing_artifacts"]


def _write_complete_package(evidence: Path) -> None:
    allowed_claim = "PV18 complete: Knowledge OPC productization implementation ready for bounded review."
    write_json(
        evidence / "acceptance-data.json",
        {
            "schema_version": "pv18.knowledge_opc_acceptance_data.v1",
            "stage_id": "PV18-SA",
            "status": "PASS",
            "allowed_claim": allowed_claim,
            "scenario_results": [
                {
                    "case_id": case_id,
                    "status": "PASS",
                    "user_visible_result": f"{case_id} visible",
                    "evidence_refs": [f"{case_id}.json"],
                    "blocking_failure": False,
                }
                for case_id in [
                    "knowledge_console_state_visible",
                    "source_import_registers_standard_artifacts",
                    "build_failed_is_visible",
                    "query_returns_citation_bundle",
                    "missing_citation_blocks_verified_answer",
                    "quality_feedback_requires_review_when_risky",
                    "correction_plan_does_not_auto_publish",
                    "evidence_summary_maps_claims_to_artifacts",
                    "browser_network_denylist_passes",
                    "platform_generality_review_passes",
                    "no_false_green_and_redaction_pass",
                ]
            ],
            "artifact_refs": ["source-artifact"],
            "real_data_service": {
                "status": "PASS",
                "connector_id": "data_service_mcp",
                "execution_mode": "mcp_stdio",
                "workspace_id": "knowledge-test-workspace",
            },
            "route_boundary": {"status": "PASS", "allowed_prefixes": ["/bff/pv18/knowledge"], "forbidden_matches": []},
            "platform_generality_review": {
                "status": "PASS",
                "knowledge_only_platform_changes": [],
                "generic_reuse_checks": ["BFF domain facade only"],
            },
            "claim_scan": {"status": "PASS", "matches": []},
            "redaction_scan": {"status": "PASS", "matches": []},
            "blocking_failures": [],
        },
    )
    write_json(evidence / "artifact-manifest.json", {"status": "PASS", "artifacts": []})
    write_json(
        evidence / "dto-snapshots.json",
        {
            "snapshots": [
                {"route": route, "method": "GET", "dto": {"schema_version": "pv18.knowledge_opc.v1"}}
                for route in [
                    "/bff/pv18/knowledge/state",
                    "/bff/pv18/knowledge/sources/import",
                    "/bff/pv18/knowledge/query",
                    "/bff/pv18/knowledge/evidence/summary",
                ]
            ]
        },
    )
    write_json(evidence / "knowledge-console-report.json", {"status": "PASS"})
    write_json(evidence / "source-ingest-report.json", {"status": "PASS"})
    write_json(
        evidence / "knowledge-query-report.json",
        {
            "status": "PASS",
            "citation_coverage": {"status": "pass"},
            "source_refs": [{"source_id": "src"}],
            "verified": False,
        },
    )
    write_json(
        evidence / "quality-correction-report.json",
        {"status": "PASS", "requires_human_review": True, "auto_publish_allowed": False},
    )
    write_json(evidence / "artifact-lineage-report.json", {"status": "PASS"})
    write_json(evidence / "evidence-review-report.json", {"status": "PASS"})
    write_json(evidence / "browser-network-log.json", {"routes": ["/bff/pv18/knowledge/state"]})
    write_json(evidence / "bff-route-log.json", {"routes": ["/bff/pv18/knowledge/state"]})
    write_json(
        evidence / "claim-to-evidence-matrix.json",
        {"claims": [{"claim_id": "pv18-bff", "status": "PASS", "evidence_refs": ["/bff/pv18/knowledge/state"]}]},
    )
    for name in [
        "no-false-green-scan.txt",
        "redaction-scan.txt",
        "prd-spec-review.md",
        "target-architecture-review.md",
        "platform-generality-review.md",
        "audit-closure.md",
    ]:
        (evidence / name).write_text("PASS\n", encoding="utf-8")
    (evidence / "no-false-green-scan.txt").write_text(
        "PASS\n禁止正向声明：production ready / Xpert parity complete / Agent executor ready\n",
        encoding="utf-8",
    )
    (evidence / "audit-closure.md").write_text(
        "PASS\n本阶段不声明 production ready，不声明 complete Workflow Studio ready。\n",
        encoding="utf-8",
    )
    png = bytes.fromhex(
        "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4890000000a49444154789c6360000002000154a24f5d0000000049454e44ae426082"
    )
    for name in [
        "knowledge-console-screenshot.png",
        "query-and-citation-screenshot.png",
        "evidence-review-screenshot.png",
    ]:
        (evidence / name).write_bytes(png)


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
