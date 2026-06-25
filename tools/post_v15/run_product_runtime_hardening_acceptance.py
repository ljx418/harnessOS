from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import jsonschema


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EVIDENCE_DIR = ROOT / "docs/design/V12-V15.x/evidence/post-v15-product-runtime-hardening"
REPORT_PATH = ROOT / "docs/design/V12-V15.x/reports/post_v15_product_runtime_hardening_acceptance_report.json"
SCHEMA_ROOT = ROOT / "docs/design/V12-V15.x/schemas"

REQUIRED_FILES = [
    "acceptance-data.json",
    "artifact-manifest.json",
    "entity-crud-report.json",
    "runtime-run-inspect-report.json",
    "deployment-smoke-output.txt",
    "deployment-health-report.json",
    "ux-hardening-report.json",
    "claim-to-evidence-matrix.json",
    "product-journey-screenshot.png",
    "runtime-inspect-screenshot.png",
    "browser-network-log.json",
    "bff-route-log.json",
    "prd-spec-review.md",
    "target-architecture-review.md",
    "audit-closure.md",
    "no-false-green-scan.txt",
    "redaction-scan.txt",
]

REQUIRED_STAGE_IDS = ["PV16-S1", "PV16-S2", "PV16-S3", "PV16-S4", "PV16-SA"]

FORBIDDEN_ROUTES = [
    "/v1/rpc",
    "/internal/runtime",
    "/runtime/store",
    "/api/runtime",
    "/debug/runtime",
]

FORBIDDEN_CLAIMS = [
    "production ready",
    "Xpert parity complete",
    "product-grade frontend complete",
    "complete Workflow Studio ready",
    "Agent executor ready",
]

REDACTION_PATTERNS = [
    "raw_secret",
    "Bearer ",
    "signed URL",
    "sk-",
    "AKIA",
    "raw provider payload",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate post-V15 PV16 evidence package.")
    parser.add_argument("--evidence-dir", type=Path, default=DEFAULT_EVIDENCE_DIR)
    args = parser.parse_args()
    evidence_dir = args.evidence_dir.resolve()

    missing = [name for name in REQUIRED_FILES if not (evidence_dir / name).exists()]
    schema_results = validate_schemas(evidence_dir) if not missing_schema_inputs(evidence_dir) else blocked_schema_results()
    claim_matches = scan_for_forbidden_positive_claims(evidence_dir, FORBIDDEN_CLAIMS)
    redaction_matches = scan_text(evidence_dir, REDACTION_PATTERNS)
    browser_boundary = validate_browser_boundary(evidence_dir)
    runtime_evidence = validate_runtime_evidence(evidence_dir)
    deployment_smoke = validate_deployment_smoke(evidence_dir)
    stage_results = validate_stage_results(evidence_dir)
    claim_evidence = validate_claim_to_evidence(evidence_dir)

    acceptance = read_json(evidence_dir / "acceptance-data.json") if (evidence_dir / "acceptance-data.json").exists() else {}
    manifest = read_json(evidence_dir / "artifact-manifest.json") if (evidence_dir / "artifact-manifest.json").exists() else {}

    status = (
        "PASS"
        if not missing
        and all(result["status"] == "PASS" for result in schema_results)
        and acceptance.get("status") == "PASS"
        and manifest.get("status") == "PASS"
        and browser_boundary["status"] == "PASS"
        and runtime_evidence["status"] == "PASS"
        and deployment_smoke["status"] == "PASS"
        and stage_results["status"] == "PASS"
        and claim_evidence["status"] == "PASS"
        and not claim_matches
        and not redaction_matches
        else "FAIL"
    )

    report = {
        "schema_version": "post_v15.product_runtime_hardening_acceptance_report.v1",
        "status": status,
        "stage_id": acceptance.get("stage_id", "PV16-SA"),
        "evidence_dir": str(evidence_dir.relative_to(ROOT)) if evidence_dir.is_relative_to(ROOT) else str(evidence_dir),
        "missing_artifacts": missing,
        "schema_results": schema_results,
        "browser_boundary": browser_boundary,
        "runtime_evidence": runtime_evidence,
        "deployment_smoke": deployment_smoke,
        "stage_results": stage_results,
        "claim_to_evidence": claim_evidence,
        "claim_scan": {"status": "PASS" if not claim_matches else "FAIL", "matches": claim_matches},
        "redaction_scan": {"status": "PASS" if not redaction_matches else "FAIL", "matches": redaction_matches},
        "allowed_claim": "PV16 complete: product-runtime hardening pilot ready for review.",
        "forbidden_positive_claims": FORBIDDEN_CLAIMS,
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(f"{json.dumps(report, indent=2, ensure_ascii=False)}\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if status == "PASS" else 1


def missing_schema_inputs(evidence_dir: Path) -> bool:
    return not (evidence_dir / "acceptance-data.json").exists() or not (evidence_dir / "artifact-manifest.json").exists()


def blocked_schema_results() -> list[dict[str, str]]:
    return [
        {
            "status": "BLOCKED",
            "reason": "acceptance-data.json and artifact-manifest.json are required before schema validation.",
        }
    ]


def validate_schemas(evidence_dir: Path) -> list[dict[str, str]]:
    checks = [
        (
            evidence_dir / "acceptance-data.json",
            SCHEMA_ROOT / "post_v15_product_runtime_hardening_acceptance_data.schema.json",
        ),
        (
            evidence_dir / "artifact-manifest.json",
            SCHEMA_ROOT / "post_v15_product_runtime_hardening_artifact_manifest.schema.json",
        ),
    ]
    results: list[dict[str, str]] = []
    for data_path, schema_path in checks:
        try:
            jsonschema.validate(read_json(data_path), read_json(schema_path))
            status = "PASS"
            reason = ""
        except Exception as exc:  # noqa: BLE001 - report validation failure without hiding context.
            status = "FAIL"
            reason = str(exc)
        results.append(
            {
                "status": status,
                "data": str(data_path.relative_to(ROOT)),
                "schema": str(schema_path.relative_to(ROOT)),
                "reason": reason,
            }
        )
    return results


def validate_browser_boundary(evidence_dir: Path) -> dict[str, Any]:
    path = evidence_dir / "browser-network-log.json"
    if not path.exists():
        return {"status": "FAIL", "reason": "browser-network-log.json is missing", "forbidden_matches": []}
    text = path.read_text(encoding="utf-8")
    matches = [route for route in FORBIDDEN_ROUTES if route in text]
    return {"status": "PASS" if not matches else "FAIL", "forbidden_matches": matches}


def validate_runtime_evidence(evidence_dir: Path) -> dict[str, Any]:
    path = evidence_dir / "runtime-run-inspect-report.json"
    if not path.exists():
        return {"status": "FAIL", "reason": "runtime-run-inspect-report.json is missing"}
    data = read_json(path)
    required = ["runtime_event_refs", "trace_refs", "artifact_refs", "quality_refs"]
    missing = [key for key in required if not data.get(key)]
    runtime_backed = data.get("runtime_backed") is True
    return {
        "status": "PASS" if not missing and runtime_backed else "FAIL",
        "missing_fields": missing,
        "runtime_backed": runtime_backed,
    }


def validate_deployment_smoke(evidence_dir: Path) -> dict[str, Any]:
    path = evidence_dir / "deployment-smoke-output.txt"
    if not path.exists():
        return {"status": "FAIL", "reason": "deployment-smoke-output.txt is missing"}
    text = path.read_text(encoding="utf-8")
    has_command = "$ " in text or "COMMAND:" in text
    has_health = "health" in text.lower() and ("200" in text or "PASS" in text)
    return {"status": "PASS" if has_command and has_health else "FAIL", "has_command": has_command, "has_health": has_health}


def validate_stage_results(evidence_dir: Path) -> dict[str, Any]:
    path = evidence_dir / "acceptance-data.json"
    if not path.exists():
        return {"status": "FAIL", "reason": "acceptance-data.json is missing", "missing_stage_ids": REQUIRED_STAGE_IDS}
    data = read_json(path)
    stages = {item.get("scenario_id"): item for item in data.get("scenario_results", [])}
    missing = [stage_id for stage_id in REQUIRED_STAGE_IDS if stage_id not in stages]
    failing = [
        stage_id
        for stage_id in REQUIRED_STAGE_IDS
        if stage_id in stages and stages[stage_id].get("status") != "PASS"
    ]
    missing_evidence = [
        stage_id
        for stage_id in REQUIRED_STAGE_IDS
        if stage_id in stages and not stages[stage_id].get("evidence_refs")
    ]
    return {
        "status": "PASS" if not missing and not failing and not missing_evidence else "FAIL",
        "missing_stage_ids": missing,
        "failing_stage_ids": failing,
        "missing_evidence_stage_ids": missing_evidence,
    }


def validate_claim_to_evidence(evidence_dir: Path) -> dict[str, Any]:
    path = evidence_dir / "claim-to-evidence-matrix.json"
    if not path.exists():
        return {"status": "FAIL", "reason": "claim-to-evidence-matrix.json is missing"}
    data = read_json(path)
    claims = data.get("claims", [])
    missing = [item.get("claim_id", "<unknown>") for item in claims if not item.get("evidence_refs")]
    statuses = [item.get("status") for item in claims]
    return {
        "status": "PASS" if claims and not missing and all(status == "PASS" for status in statuses) else "FAIL",
        "claim_count": len(claims),
        "missing_evidence_claim_ids": missing,
    }


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
                matches.append({"path": str(path.relative_to(ROOT)), "pattern": pattern})
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
                for token in [
                    "forbidden",
                    "must not",
                    "does not",
                    "not mean",
                    "blocked",
                    "negative",
                    "禁止",
                    "不得",
                    "不能",
                    "不等于",
                    "不是",
                    "不可",
                ]
            )
            if safe_negative_context:
                continue
            for pattern in patterns:
                if pattern in line:
                    matches.append({"path": str(path.relative_to(ROOT)), "line": str(line_number), "pattern": pattern})
    return matches


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
