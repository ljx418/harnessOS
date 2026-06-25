from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACK_DIR = ROOT / "docs/design/V12-V15.x/gemini_frontend_review_pack"
DEFAULT_OUTPUT_DIR = ROOT / "docs/design/V12-V15.x/evidence/v12-gemini-generated-light-studio-review"

EXPECTED_PACK_FILES = [
    "00_README.md",
    "01_GEMINI_GENERATION_PROMPT.md",
    "02_PRODUCT_AND_BOUNDARIES.md",
    "03_FROZEN_UX_DECISIONS.md",
    "04_USER_SCENARIOS_AND_ACCEPTANCE.md",
    "05_STARTER_PROTOTYPE_LIGHT_STUDIO.html",
    "06_REFERENCE_RENDER.png",
    "07_REVIEW_CHECKLIST.json",
    "08_MANIFEST.json",
]

EXPECTED_OUTPUT_FILES = [
    "index.html",
    "README.md",
    "audit-notes.md",
]

REQUIRED_STATE_TERMS = [
    "api_online",
    "api_offline",
    "api_rate_limited",
    "api_unconfigured",
    "run_idle",
    "run_in_progress",
    "run_blocked",
    "run_failed",
    "awaiting_confirmation",
    "evidence_ready",
    "evidence_missing",
    "design_only_evidence",
    "node_hover",
    "node_selected",
    "blocked",
    "invalid_edge",
]

FORBIDDEN_POSITIVE_CLAIMS = [
    "Xpert parity complete",
    "Xpert-level UX complete",
    "product-grade frontend complete",
    "complete Workflow Studio ready",
    "production ready",
    "Agent executor ready",
    "已完全追平 Xpert",
    "产品级前端已完成",
    "完整工作流工作台已完成",
    "生产可用",
    "Agent 执行器已完成",
]

RAW_CONTENT_TERMS = [
    "raw secret",
    "raw token",
    "raw provider payload",
    "raw artifact content",
    "Bearer ",
    "API key",
    "signed URL",
    "credential raw secret",
]

SAFE_CONTEXT_TERMS = [
    "forbidden",
    "blocked",
    "禁止",
    "不得",
    "不能",
    "must_not",
    "claim_",
    "false green",
    "False Green",
]


def _read_json(path: Path) -> tuple[bool, str]:
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - validation report should preserve parser detail.
        return False, str(exc)
    return True, "ok"


def _scan_text_files(root: Path, terms: list[str]) -> list[dict[str, object]]:
    hits: list[dict[str, object]] = []
    for path in sorted(root.rglob("*")):
        if path.name == "validation-report.json":
            continue
        if not path.is_file() or path.suffix.lower() not in {".html", ".md", ".json", ".txt", ".css", ".js"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        file_safe_context = path.name == "artifact-manifest.json" and "blocked_claims" in text
        for line_number, line in enumerate(text.splitlines(), start=1):
            for term in terms:
                if term in line:
                    safe_context = file_safe_context or any(marker in line for marker in SAFE_CONTEXT_TERMS)
                    hits.append(
                        {
                            "path": str(path.relative_to(ROOT)),
                            "line": line_number,
                            "term": term,
                            "safe_context": safe_context,
                        }
                    )
    return hits


def validate_pack() -> dict[str, object]:
    actual = sorted(path.name for path in PACK_DIR.iterdir() if path.is_file())
    expected = sorted(EXPECTED_PACK_FILES)
    manifest_path = PACK_DIR / "08_MANIFEST.json"
    checklist_path = PACK_DIR / "07_REVIEW_CHECKLIST.json"
    manifest_ok, manifest_error = _read_json(manifest_path)
    checklist_ok, checklist_error = _read_json(checklist_path)

    return {
        "pack_dir": str(PACK_DIR.relative_to(ROOT)),
        "actual_count": len(actual),
        "expected_count": len(expected),
        "missing": sorted(set(expected) - set(actual)),
        "extra": sorted(set(actual) - set(expected)),
        "matches_expected_files": actual == expected,
        "manifest_json": "PASS" if manifest_ok else "FAIL",
        "manifest_error": manifest_error if not manifest_ok else None,
        "review_checklist_json": "PASS" if checklist_ok else "FAIL",
        "review_checklist_error": checklist_error if not checklist_ok else None,
    }


def validate_output(output_dir: Path) -> dict[str, object]:
    exists = output_dir.exists()
    actual = sorted(path.name for path in output_dir.iterdir() if path.is_file()) if exists else []
    missing = sorted(set(EXPECTED_OUTPUT_FILES) - set(actual))
    pending_output = "index.html" not in actual
    forbidden_hits = _scan_text_files(output_dir, FORBIDDEN_POSITIVE_CLAIMS) if exists else []
    unsafe_forbidden_hits = [hit for hit in forbidden_hits if not hit["safe_context"]]
    raw_hits = _scan_text_files(output_dir, RAW_CONTENT_TERMS) if exists else []
    index_path = output_dir / "index.html"
    index_text = index_path.read_text(encoding="utf-8", errors="ignore") if index_path.exists() else ""
    missing_state_terms = [term for term in REQUIRED_STATE_TERMS if term not in index_text]
    version_drift_terms = [term for term in ["V13", "v13", "V13-0P", "V13-OP"] if term in index_text]
    external_dependency_terms = [
        term
        for term in ["https://cdn.tailwindcss.com", "tailwind.config"]
        if term in index_text
    ]

    return {
        "output_dir": str(output_dir.relative_to(ROOT)),
        "exists": exists,
        "actual_files": actual,
        "required_files": EXPECTED_OUTPUT_FILES,
        "missing_required_files": missing,
        "pending_gemini_output": pending_output,
        "supports_review": (
            exists
            and not pending_output
            and not missing
            and not unsafe_forbidden_hits
            and not raw_hits
            and not missing_state_terms
            and not version_drift_terms
            and not external_dependency_terms
        ),
        "evidence_scope": "design_only",
        "browser_implementation_backed": False,
        "bff_backed": False,
        "dto_backed": False,
        "runtime_backed": False,
        "forbidden_positive_claim_scan": "PASS" if not unsafe_forbidden_hits else "FAIL",
        "forbidden_positive_claim_hits": forbidden_hits,
        "redaction_scan": "PASS" if not raw_hits else "FAIL",
        "redaction_hits": raw_hits,
        "required_state_terms": "PASS" if not missing_state_terms else "FAIL",
        "missing_state_terms": missing_state_terms,
        "version_drift_scan": "PASS" if not version_drift_terms else "FAIL",
        "version_drift_terms": version_drift_terms,
        "external_dependency_scan": "PASS" if not external_dependency_terms else "FAIL",
        "external_dependency_terms": external_dependency_terms,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the V12 Gemini frontend review pack and output folder.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args()

    report = {
        "schema_version": "v12.gemini_frontend_review_validation.v1",
        "status": "PASS",
        "pack": validate_pack(),
        "output": validate_output(args.output_dir.resolve()),
    }

    if not report["pack"]["matches_expected_files"]:
        report["status"] = "FAIL"
    if report["pack"]["manifest_json"] != "PASS" or report["pack"]["review_checklist_json"] != "PASS":
        report["status"] = "FAIL"
    if args.output_dir.exists() and not report["output"]["pending_gemini_output"] and not report["output"]["supports_review"]:
        report["status"] = "FAIL"

    if args.write_report:
        report_path = args.output_dir / "validation-report.json"
        args.output_dir.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
