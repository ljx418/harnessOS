from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EVIDENCE_DIR = ROOT / "docs/design/V12-V15.x/evidence/pv17-product-closed-loop"
REPORT_PATH = ROOT / "docs/design/V12-V15.x/reports/pv17_product_closed_loop_acceptance_report.json"

REQUIRED_FILES = [
    "acceptance-data.json",
    "artifact-manifest.json",
    "product-console-report.json",
    "entity-mutation-report.json",
    "studio-workflow-version-report.json",
    "runtime-run-inspect-report.json",
    "evidence-review-report.json",
    "browser-network-log.json",
    "bff-route-log.json",
    "dto-snapshots.json",
    "claim-to-evidence-matrix.json",
    "product-console-screenshot.png",
    "studio-run-inspect-screenshot.png",
    "evidence-review-screenshot.png",
    "prd-spec-review.md",
    "target-architecture-review.md",
    "audit-closure.md",
    "no-false-green-scan.txt",
    "redaction-scan.txt",
]

REQUIRED_STAGE_IDS = [
    "PV17-S1-product-console",
    "PV17-S2-entity-mutation",
    "PV17-S3-studio-versioning",
    "PV17-S4-runtime-inspect",
    "PV17-S5-evidence-review",
    "PV17-SA-aggregate",
]

REQUIRED_DTO_STAGES = ["S1", "S2", "S3", "S4", "S5"]

FORBIDDEN_BROWSER_ROUTES = [
    "/v1/rpc",
    "/internal/runtime",
    "/runtime/store",
    "/api/runtime",
    "/debug/runtime",
]

FORBIDDEN_CLAIMS = [
    "production ready",  # forbidden positive claim
    "HarnessOS is production ready",  # forbidden positive claim
    "Xpert parity complete",  # forbidden positive claim
    "product-grade frontend complete",  # forbidden positive claim
    "complete Workflow Studio ready",  # forbidden positive claim
    "Agent executor ready",  # forbidden positive claim
]

REDACTION_PATTERNS = [
    "raw_secret",
    "Bearer ",
    "signed URL",
    "sk-",
    "AKIA",
    "raw provider payload",
    "raw_artifact_content",
    "raw_provider_payload",
]

ALLOWED_CLAIM = "PV17 complete: product closed loop implementation ready for bounded review."


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate PV17 product closed loop evidence package.")
    parser.add_argument("--evidence-dir", type=Path, default=DEFAULT_EVIDENCE_DIR)
    parser.add_argument("--report-path", type=Path, default=REPORT_PATH)
    args = parser.parse_args()

    evidence_dir = args.evidence_dir.resolve()
    report_path = args.report_path.resolve()
    missing = [name for name in REQUIRED_FILES if not (evidence_dir / name).exists()]
    stage_results = validate_stage_results(evidence_dir)
    browser_boundary = validate_browser_boundary(evidence_dir)
    bff_boundary = validate_bff_boundary(evidence_dir)
    dto_coverage = validate_dto_coverage(evidence_dir)
    entity_mutation = validate_entity_mutation(evidence_dir)
    studio_versioning = validate_studio_versioning(evidence_dir)
    runtime_evidence = validate_runtime_evidence(evidence_dir)
    claim_to_evidence = validate_claim_to_evidence(evidence_dir)
    claim_matches = scan_for_forbidden_positive_claims(evidence_dir, FORBIDDEN_CLAIMS)
    redaction_matches = scan_text(evidence_dir, REDACTION_PATTERNS)
    allowed_claim = validate_allowed_claim(evidence_dir)
    manifest = read_json(evidence_dir / "artifact-manifest.json") if (evidence_dir / "artifact-manifest.json").exists() else {}

    checks = [
        stage_results,
        browser_boundary,
        bff_boundary,
        dto_coverage,
        entity_mutation,
        studio_versioning,
        runtime_evidence,
        claim_to_evidence,
        allowed_claim,
    ]
    status = (
        "PASS"
        if not missing
        and all(check.get("status") == "PASS" for check in checks)
        and manifest.get("status") == "PASS"
        and not claim_matches
        and not redaction_matches
        else "FAIL"
    )

    report = {
        "schema_version": "pv17.product_closed_loop_acceptance_report.v1",
        "status": status,
        "stage_id": "PV17-SA",
        "evidence_dir": relative(evidence_dir),
        "missing_artifacts": missing,
        "schema_results": [{"status": "PASS" if not missing else "BLOCKED", "reason": "" if not missing else "required evidence files are missing"}],
        "stage_results": stage_results,
        "browser_boundary": browser_boundary,
        "bff_boundary": bff_boundary,
        "dto_coverage": dto_coverage,
        "entity_mutation": entity_mutation,
        "studio_versioning": studio_versioning,
        "runtime_evidence": runtime_evidence,
        "claim_to_evidence": claim_to_evidence,
        "claim_scan": {"status": "PASS" if not claim_matches else "FAIL", "matches": claim_matches},
        "redaction_scan": {"status": "PASS" if not redaction_matches else "FAIL", "matches": redaction_matches},
        "allowed_claim": ALLOWED_CLAIM,
        "allowed_claim_check": allowed_claim,
        "forbidden_positive_claims": FORBIDDEN_CLAIMS,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(f"{json.dumps(report, indent=2, ensure_ascii=False)}\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if status == "PASS" else 1


def validate_stage_results(evidence_dir: Path) -> dict[str, Any]:
    path = evidence_dir / "acceptance-data.json"
    if not path.exists():
        return {"status": "FAIL", "reason": "acceptance-data.json is missing", "missing_stage_ids": REQUIRED_STAGE_IDS}
    data = read_json(path)
    raw = data.get("stage_results", data.get("scenario_results", []))
    stages = {item.get("stage_id") or item.get("scenario_id"): item for item in raw if isinstance(item, dict)}
    missing = [stage_id for stage_id in REQUIRED_STAGE_IDS if stage_id not in stages]
    failing = [stage_id for stage_id in REQUIRED_STAGE_IDS if stage_id in stages and stages[stage_id].get("status") != "PASS"]
    missing_evidence = [stage_id for stage_id in REQUIRED_STAGE_IDS if stage_id in stages and not stages[stage_id].get("evidence_refs")]
    missing_visible = [stage_id for stage_id in REQUIRED_STAGE_IDS if stage_id in stages and not stages[stage_id].get("user_visible_result")]
    blocking = [stage_id for stage_id in REQUIRED_STAGE_IDS if stage_id in stages and stages[stage_id].get("blocking_failures")]
    return {
        "status": "PASS" if not missing and not failing and not missing_evidence and not missing_visible and not blocking else "FAIL",
        "missing_stage_ids": missing,
        "failing_stage_ids": failing,
        "missing_evidence_stage_ids": missing_evidence,
        "missing_user_visible_result_stage_ids": missing_visible,
        "blocking_failure_stage_ids": blocking,
    }


def validate_browser_boundary(evidence_dir: Path) -> dict[str, Any]:
    path = evidence_dir / "browser-network-log.json"
    if not path.exists():
        return {"status": "FAIL", "reason": "browser-network-log.json is missing", "forbidden_matches": []}
    text = path.read_text(encoding="utf-8")
    matches = [route for route in FORBIDDEN_BROWSER_ROUTES if route in text]
    return {"status": "PASS" if not matches else "FAIL", "forbidden_matches": matches}


def validate_bff_boundary(evidence_dir: Path) -> dict[str, Any]:
    path = evidence_dir / "bff-route-log.json"
    if not path.exists():
        return {"status": "FAIL", "reason": "bff-route-log.json is missing"}
    text = path.read_text(encoding="utf-8")
    uses_pv17 = "/bff/pv17/" in text
    uses_pv16_positive = "/bff/pv16/" in text
    return {
        "status": "PASS" if uses_pv17 and not uses_pv16_positive else "FAIL",
        "uses_pv17": uses_pv17,
        "uses_pv16_positive_path": uses_pv16_positive,
    }


def validate_dto_coverage(evidence_dir: Path) -> dict[str, Any]:
    path = evidence_dir / "dto-snapshots.json"
    if not path.exists():
        return {"status": "FAIL", "reason": "dto-snapshots.json is missing", "missing_stages": REQUIRED_DTO_STAGES}
    data = read_json(path)
    snapshots = data.get("snapshots", data if isinstance(data, dict) else {})
    missing = [stage for stage in REQUIRED_DTO_STAGES if stage not in snapshots]
    missing_schema = [stage for stage in REQUIRED_DTO_STAGES if stage in snapshots and not snapshots[stage].get("schema_version")]
    return {"status": "PASS" if not missing and not missing_schema else "FAIL", "missing_stages": missing, "missing_schema_version": missing_schema}


def validate_entity_mutation(evidence_dir: Path) -> dict[str, Any]:
    path = evidence_dir / "entity-mutation-report.json"
    if not path.exists():
        return {"status": "FAIL", "reason": "entity-mutation-report.json is missing"}
    data = read_json(path)
    mutations = data.get("mutations", [])
    negative = data.get("negative_fixtures", [])
    missing = [
        item.get("entity_ref", {}).get("entity_id", "<unknown>")
        for item in mutations
        if item.get("user_confirmed") is not True or not item.get("audit_ref") or not item.get("policy_decision_ref")
    ]
    return {"status": "PASS" if mutations and negative and not missing else "FAIL", "missing_required_fields": missing, "negative_fixture_count": len(negative)}


def validate_studio_versioning(evidence_dir: Path) -> dict[str, Any]:
    path = evidence_dir / "studio-workflow-version-report.json"
    if not path.exists():
        return {"status": "FAIL", "reason": "studio-workflow-version-report.json is missing"}
    data = read_json(path)
    required = ["workflow_diff", "expected_revision", "confirmation_transcript", "workflow_version_id"]
    missing = [key for key in required if not data.get(key)]
    agent_silent = data.get("source") == "agent" and data.get("published") is True
    return {"status": "PASS" if not missing and not agent_silent else "FAIL", "missing_fields": missing, "agent_silent_publish": agent_silent}


def validate_runtime_evidence(evidence_dir: Path) -> dict[str, Any]:
    path = evidence_dir / "runtime-run-inspect-report.json"
    if not path.exists():
        return {"status": "FAIL", "reason": "runtime-run-inspect-report.json is missing"}
    data = read_json(path)
    required = ["runtime_event_refs", "trace_refs", "artifact_refs", "quality_refs"]
    missing = [key for key in required if not data.get(key)]
    fixture_only = data.get("runtime_backed") is False or data.get("fixture_only") is True
    return {"status": "PASS" if not missing and not fixture_only else "FAIL", "missing_fields": missing, "fixture_only": fixture_only}


def validate_claim_to_evidence(evidence_dir: Path) -> dict[str, Any]:
    path = evidence_dir / "claim-to-evidence-matrix.json"
    if not path.exists():
        return {"status": "FAIL", "reason": "claim-to-evidence-matrix.json is missing"}
    data = read_json(path)
    claims = data.get("claims", [])
    missing = [item.get("claim_id", "<unknown>") for item in claims if not item.get("evidence_refs")]
    failing = [item.get("claim_id", "<unknown>") for item in claims if item.get("status") not in {"PASS", "SUPPORTED"}]
    return {"status": "PASS" if claims and not missing and not failing else "FAIL", "claim_count": len(claims), "missing_evidence_claim_ids": missing, "failing_claim_ids": failing}


def validate_allowed_claim(evidence_dir: Path) -> dict[str, Any]:
    path = evidence_dir / "acceptance-data.json"
    if not path.exists():
        return {"status": "FAIL", "reason": "acceptance-data.json is missing"}
    data = read_json(path)
    claim = data.get("allowed_claim")
    return {"status": "PASS" if claim == ALLOWED_CLAIM else "FAIL", "actual": claim, "expected": ALLOWED_CLAIM}


def scan_text(root: Path, patterns: list[str]) -> list[dict[str, str]]:
    if not root.exists():
        return []
    matches: list[dict[str, str]] = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in patterns:
            if pattern in text:
                matches.append({"path": relative(path), "pattern": pattern})
    return matches


def scan_for_forbidden_positive_claims(root: Path, patterns: list[str]) -> list[dict[str, str]]:
    if not root.exists():
        return []
    matches: list[dict[str, str]] = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp"}:
            continue
        if path.name in {"artifact-manifest.json", "no-false-green-scan.txt", "no-false-green-scan.json"}:
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(lines, start=1):
            lowered = line.lower()
            safe_negative_context = any(
                token in lowered
                for token in ["forbidden", "must not", "does not", "not mean", "blocked", "negative", "禁止", "不得", "不能", "不等于", "不是", "不可"]
            )
            if safe_negative_context:
                continue
            for pattern in patterns:
                if pattern in line:
                    matches.append({"path": relative(path), "line": str(line_number), "pattern": pattern})
    return matches


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def relative(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else str(resolved)


if __name__ == "__main__":
    raise SystemExit(main())
