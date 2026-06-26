"""PV17 product closed loop acceptance runner tests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_pv17_acceptance_runner_passes_complete_temp_package(tmp_path) -> None:
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    _write_complete_package(evidence)
    report = tmp_path / "report.json"

    result = subprocess.run(
        [
            sys.executable,
            "tools/pv17/run_product_closed_loop_acceptance.py",
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
    assert payload["browser_boundary"]["status"] == "PASS"
    assert payload["runtime_evidence"]["status"] == "PASS"


def test_pv17_acceptance_runner_fails_missing_package(tmp_path) -> None:
    evidence = tmp_path / "missing"
    report = tmp_path / "report.json"

    result = subprocess.run(
        [
            sys.executable,
            "tools/pv17/run_product_closed_loop_acceptance.py",
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
    allowed_claim = "PV17 complete: product closed loop implementation ready for bounded review."
    write_json(
        evidence / "acceptance-data.json",
        {
            "status": "PASS",
            "allowed_claim": allowed_claim,
            "stage_results": [
                {
                    "stage_id": stage_id,
                    "status": "PASS",
                    "user_visible_result": f"{stage_id} visible",
                    "evidence_refs": [f"{stage_id}.json"],
                    "blocking_failures": [],
                }
                for stage_id in [
                    "PV17-S1-product-console",
                    "PV17-S2-entity-mutation",
                    "PV17-S3-studio-versioning",
                    "PV17-S4-runtime-inspect",
                    "PV17-S5-evidence-review",
                    "PV17-SA-aggregate",
                ]
            ],
        },
    )
    write_json(evidence / "artifact-manifest.json", {"status": "PASS", "artifacts": []})
    write_json(evidence / "product-console-report.json", {"status": "PASS"})
    write_json(
        evidence / "entity-mutation-report.json",
        {
            "mutations": [
                {
                    "entity_ref": {"entity_id": "station_agent:reviewer"},
                    "user_confirmed": True,
                    "audit_ref": {"audit_ref_id": "audit"},
                    "policy_decision_ref": "policy",
                }
            ],
            "negative_fixtures": [{"status": "denied"}],
        },
    )
    write_json(
        evidence / "studio-workflow-version-report.json",
        {
            "workflow_diff": {"before": [], "after": []},
            "expected_revision": 1,
            "confirmation_transcript": "confirmed by user",
            "workflow_version_id": "wfv_1",
            "source": "mission_studio",
            "published": True,
        },
    )
    write_json(
        evidence / "runtime-run-inspect-report.json",
        {
            "runtime_backed": True,
            "runtime_event_refs": ["event"],
            "trace_refs": ["trace"],
            "artifact_refs": ["artifact"],
            "quality_refs": ["quality"],
        },
    )
    write_json(evidence / "evidence-review-report.json", {"status": "PASS"})
    write_json(evidence / "browser-network-log.json", {"routes": ["/bff/pv17/product-console/state"]})
    write_json(evidence / "bff-route-log.json", {"routes": ["/bff/pv17/product-console/state"]})
    write_json(
        evidence / "dto-snapshots.json",
        {
            "snapshots": {
                stage: {"schema_version": "pv17.product_closed_loop.v1"}
                for stage in ["S1", "S2", "S3", "S4", "S5"]
            }
        },
    )
    write_json(
        evidence / "claim-to-evidence-matrix.json",
        {"claims": [{"claim_id": "pv17-closed-loop", "status": "PASS", "evidence_refs": ["runtime-run-inspect-report.json"]}]},
    )
    for name in ["product-console-screenshot.png", "studio-run-inspect-screenshot.png", "evidence-review-screenshot.png"]:
        (evidence / name).write_bytes(b"png")
    for name in ["prd-spec-review.md", "target-architecture-review.md", "audit-closure.md", "no-false-green-scan.txt", "redaction-scan.txt"]:
        (evidence / name).write_text("PASS\n", encoding="utf-8")


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
