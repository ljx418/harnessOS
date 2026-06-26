from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EVIDENCE_DIR = ROOT / "docs/design/V12-V15.x/evidence/pv18-knowledge-opc-productization"
REPORT_PATH = ROOT / "docs/design/V12-V15.x/reports/pv18_knowledge_opc_productization_acceptance_report.json"

REQUIRED_FILES = [
    "acceptance-data.json",
    "artifact-manifest.json",
    "dto-snapshots.json",
    "knowledge-console-report.json",
    "source-ingest-report.json",
    "knowledge-query-report.json",
    "quality-correction-report.json",
    "artifact-lineage-report.json",
    "evidence-review-report.json",
    "browser-network-log.json",
    "bff-route-log.json",
    "claim-to-evidence-matrix.json",
    "no-false-green-scan.txt",
    "redaction-scan.txt",
    "prd-spec-review.md",
    "target-architecture-review.md",
    "platform-generality-review.md",
    "audit-closure.md",
    "knowledge-console-screenshot.png",
    "query-and-citation-screenshot.png",
    "evidence-review-screenshot.png",
]

REQUIRED_CASES = [
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

FORBIDDEN_BROWSER_ROUTES = [
    "/v1/rpc",
    "/internal/runtime",
    "/runtime/store",
    "/api/runtime",
    "/debug/runtime",
    "data_service_mcp/internal",
]

FORBIDDEN_CLAIMS = [
    "production ready",
    "HarnessOS is production ready",
    "Xpert parity complete",
    "product-grade frontend complete",
    "complete Workflow Studio ready",
    "Agent executor ready",
    "Knowledge productization complete",
    "production data service ready",
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
    "raw_connector_payload",
]

ALLOWED_CLAIM = "PV18 complete: Knowledge OPC productization implementation ready for bounded review."


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate PV18 Knowledge OPC evidence package.")
    parser.add_argument("--evidence-dir", type=Path, default=DEFAULT_EVIDENCE_DIR)
    parser.add_argument("--report-path", type=Path, default=REPORT_PATH)
    args = parser.parse_args()

    evidence_dir = args.evidence_dir.resolve()
    report_path = args.report_path.resolve()
    missing = [name for name in REQUIRED_FILES if not (evidence_dir / name).exists()]
    scenario_results = validate_scenarios(evidence_dir)
    route_boundary = validate_route_boundary(evidence_dir)
    dto_coverage = validate_dto_coverage(evidence_dir)
    citation = validate_citation(evidence_dir)
    correction = validate_correction(evidence_dir)
    real_data_service = validate_real_data_service(evidence_dir)
    platform_generality = validate_platform_generality(evidence_dir)
    claim_to_evidence = validate_claim_to_evidence(evidence_dir)
    allowed_claim = validate_allowed_claim(evidence_dir)
    claim_matches = scan_text(evidence_dir, FORBIDDEN_CLAIMS)
    redaction_matches = scan_text(evidence_dir, REDACTION_PATTERNS)
    manifest = read_json(evidence_dir / "artifact-manifest.json") if (evidence_dir / "artifact-manifest.json").exists() else {}

    checks = [
        scenario_results,
        route_boundary,
        dto_coverage,
        citation,
        correction,
        real_data_service,
        platform_generality,
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
        "schema_version": "pv18.knowledge_opc_acceptance_report.v1",
        "status": status,
        "stage_id": "PV18-SA",
        "evidence_dir": relative(evidence_dir),
        "missing_artifacts": missing,
        "schema_results": [{"status": "PASS" if not missing else "BLOCKED", "reason": "" if not missing else "required evidence files are missing"}],
        "scenario_results": scenario_results,
        "route_boundary": route_boundary,
        "dto_coverage": dto_coverage,
        "citation": citation,
        "correction": correction,
        "real_data_service": real_data_service,
        "platform_generality": platform_generality,
        "claim_to_evidence": claim_to_evidence,
        "claim_scan": {"status": "PASS" if not claim_matches else "FAIL", "matches": claim_matches},
        "redaction_scan": {"status": "PASS" if not redaction_matches else "FAIL", "matches": redaction_matches},
        "allowed_claim": ALLOWED_CLAIM,
        "allowed_claim_check": allowed_claim,
        "forbidden_positive_claims": FORBIDDEN_CLAIMS,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if status == "PASS" else 1


def validate_scenarios(evidence_dir: Path) -> dict[str, Any]:
    path = evidence_dir / "acceptance-data.json"
    if not path.exists():
        return {"status": "FAIL", "reason": "acceptance-data.json is missing", "missing_case_ids": REQUIRED_CASES}
    data = read_json(path)
    raw = data.get("scenario_results", [])
    cases = {item.get("case_id"): item for item in raw if isinstance(item, dict)}
    missing = [case_id for case_id in REQUIRED_CASES if case_id not in cases]
    failing = [case_id for case_id in REQUIRED_CASES if case_id in cases and cases[case_id].get("status") != "PASS"]
    missing_visible = [case_id for case_id in REQUIRED_CASES if case_id in cases and not cases[case_id].get("user_visible_result")]
    return {"status": "PASS" if not missing and not failing and not missing_visible else "FAIL", "missing_case_ids": missing, "failing_case_ids": failing, "missing_user_visible_result_case_ids": missing_visible}


def validate_route_boundary(evidence_dir: Path) -> dict[str, Any]:
    browser_log = evidence_dir / "browser-network-log.json"
    bff_log = evidence_dir / "bff-route-log.json"
    if not browser_log.exists() or not bff_log.exists():
        return {"status": "FAIL", "reason": "browser-network-log.json or bff-route-log.json is missing"}
    browser_text = browser_log.read_text(encoding="utf-8")
    bff_text = bff_log.read_text(encoding="utf-8")
    forbidden = [route for route in FORBIDDEN_BROWSER_ROUTES if route in browser_text]
    uses_pv18 = "/bff/pv18/knowledge" in browser_text and "/bff/pv18/knowledge" in bff_text
    return {"status": "PASS" if uses_pv18 and not forbidden else "FAIL", "uses_pv18": uses_pv18, "forbidden_matches": forbidden}


def validate_dto_coverage(evidence_dir: Path) -> dict[str, Any]:
    path = evidence_dir / "dto-snapshots.json"
    if not path.exists():
        return {"status": "FAIL", "reason": "dto-snapshots.json is missing"}
    data = read_json(path)
    snapshots = data.get("snapshots") if isinstance(data.get("snapshots"), list) else []
    required_routes = {
        "/bff/pv18/knowledge/state",
        "/bff/pv18/knowledge/sources/import",
        "/bff/pv18/knowledge/query",
        "/bff/pv18/knowledge/evidence/summary",
    }
    actual = {str(item.get("route") or "") for item in snapshots if isinstance(item, dict)}
    missing = sorted(required_routes - actual)
    missing_schema = [item.get("route") for item in snapshots if isinstance(item, dict) and not item.get("dto", {}).get("schema_version")]
    return {"status": "PASS" if not missing and not missing_schema else "FAIL", "missing_routes": missing, "missing_schema_version_routes": missing_schema}


def validate_citation(evidence_dir: Path) -> dict[str, Any]:
    path = evidence_dir / "knowledge-query-report.json"
    if not path.exists():
        return {"status": "FAIL", "reason": "knowledge-query-report.json is missing"}
    data = read_json(path)
    coverage = data.get("citation_coverage") if isinstance(data.get("citation_coverage"), dict) else {}
    source_refs = data.get("source_refs") if isinstance(data.get("source_refs"), list) else []
    verified_without_citation = data.get("verified") is True and not source_refs
    return {"status": "PASS" if coverage.get("status") == "pass" and source_refs and not verified_without_citation else "FAIL", "source_ref_count": len(source_refs), "verified_without_citation": verified_without_citation}


def validate_correction(evidence_dir: Path) -> dict[str, Any]:
    path = evidence_dir / "quality-correction-report.json"
    if not path.exists():
        return {"status": "FAIL", "reason": "quality-correction-report.json is missing"}
    data = read_json(path)
    return {
        "status": "PASS" if data.get("requires_human_review") is True and data.get("auto_publish_allowed") is False else "FAIL",
        "requires_human_review": data.get("requires_human_review"),
        "auto_publish_allowed": data.get("auto_publish_allowed"),
    }


def validate_real_data_service(evidence_dir: Path) -> dict[str, Any]:
    path = evidence_dir / "acceptance-data.json"
    if not path.exists():
        return {"status": "FAIL", "reason": "acceptance-data.json is missing"}
    data = read_json(path)
    service = data.get("real_data_service") if isinstance(data.get("real_data_service"), dict) else {}
    return {
        "status": "PASS" if service.get("status") == "PASS" and service.get("execution_mode") == "mcp_stdio" else "FAIL",
        "execution_mode": service.get("execution_mode"),
        "connector_id": service.get("connector_id"),
        "workspace_id": service.get("workspace_id"),
    }


def validate_platform_generality(evidence_dir: Path) -> dict[str, Any]:
    data = read_json(evidence_dir / "acceptance-data.json") if (evidence_dir / "acceptance-data.json").exists() else {}
    review = data.get("platform_generality_review") if isinstance(data.get("platform_generality_review"), dict) else {}
    doc = evidence_dir / "platform-generality-review.md"
    platform_changes = review.get("knowledge_only_platform_changes") if isinstance(review.get("knowledge_only_platform_changes"), list) else []
    reuse_checks = review.get("generic_reuse_checks") if isinstance(review.get("generic_reuse_checks"), list) else []
    return {
        "status": "PASS" if review.get("status") == "PASS" and not platform_changes and reuse_checks and doc.exists() else "FAIL",
        "knowledge_only_platform_changes": platform_changes,
        "generic_reuse_check_count": len(reuse_checks),
        "review_doc_exists": doc.exists(),
    }


def validate_claim_to_evidence(evidence_dir: Path) -> dict[str, Any]:
    path = evidence_dir / "claim-to-evidence-matrix.json"
    if not path.exists():
        return {"status": "FAIL", "reason": "claim-to-evidence-matrix.json is missing"}
    data = read_json(path)
    claims = data.get("claims") if isinstance(data.get("claims"), list) else []
    missing = [item.get("claim_id", "<unknown>") for item in claims if isinstance(item, dict) and not item.get("evidence_refs")]
    failing = [item.get("claim_id", "<unknown>") for item in claims if isinstance(item, dict) and item.get("status") not in {"PASS", "SUPPORTED"}]
    return {"status": "PASS" if claims and not missing and not failing else "FAIL", "claim_count": len(claims), "missing_evidence_claim_ids": missing, "failing_claim_ids": failing}


def validate_allowed_claim(evidence_dir: Path) -> dict[str, Any]:
    path = evidence_dir / "acceptance-data.json"
    if not path.exists():
        return {"status": "FAIL", "reason": "acceptance-data.json is missing"}
    claim = read_json(path).get("allowed_claim")
    return {"status": "PASS" if claim == ALLOWED_CLAIM else "FAIL", "actual": claim, "expected": ALLOWED_CLAIM}


def scan_text(root: Path, patterns: list[str]) -> list[dict[str, str]]:
    if not root.exists():
        return []
    matches: list[dict[str, str]] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            for pattern in patterns:
                if pattern in line and not is_guarded_claim_context(path, line):
                    matches.append({"path": relative(path), "line": str(line_no), "pattern": pattern})
    return matches


def is_guarded_claim_context(path: Path, line: str) -> bool:
    guard_files = {
        "artifact-manifest.json",
        "no-false-green-scan.txt",
        "acceptance-data.json",
    }
    if path.name in guard_files:
        return True
    normalized = line.lower()
    guard_markers = [
        "forbidden",
        "must not",
        "do not claim",
        "does not claim",
        "not claim",
        "no false green",
        "no-go",
        "denylist",
        "不声明",
        "不得",
        "禁止",
        "不能",
        "边界",
        "误报",
    ]
    return any(marker in normalized for marker in guard_markers)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
