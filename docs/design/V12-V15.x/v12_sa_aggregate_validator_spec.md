# V12-SA Aggregate Validator Spec

## Purpose

This spec defines the validation rules for V12-SA evidence reconciliation. It
is a validator contract, not a PASS report.

## Required Inputs

V12-SA cannot pass unless these evidence groups exist or are explicitly marked
as accepted bounded partial:

- V12-GB product entity foundation evidence.
- V12-GC canvas foundation evidence.
- V12-GR read-only real-data workbench evidence.
- V12-SD Chat Workbench to WorkflowDiff handoff evidence.
- V12-SI interaction depth evidence.
- V12-SQ product polish evidence.

## Validation Rules

| Rule ID | Rule | Failure Status |
| --- | --- | --- |
| `v12_sa_missing_required_group` | Any required evidence group is missing and not explicitly accepted as bounded partial. | `BLOCKED` |
| `v12_sa_missing_required_artifact` | A required substage artifact listed in `artifact-manifest.json` is missing while the substage claims PASS. | `FAIL` |
| `v12_sa_design_only_as_browser_evidence` | Design-only evidence is counted as browser-backed evidence. | `FAIL` |
| `v12_sa_design_only_as_runtime_evidence` | Design-only evidence is counted as runtime-backed evidence. | `FAIL` |
| `v12_sa_xpert_reference_as_harnessos_evidence` | Xpert reference material is counted as HarnessOS implementation or runtime evidence. | `FAIL` |
| `v12_sa_browser_without_bff_log` | Browser-backed claim lacks browser network log or BFF route log. | `FAIL` |
| `v12_sa_dto_without_schema_validation` | DTO-backed claim lacks schema validation. | `FAIL` |
| `v12_sa_claim_without_evidence` | Any positive V12 claim lacks a linked evidence ref. | `FAIL` |
| `v12_sa_forbidden_completion_claim` | Forbidden completion claim appears outside a safe guard or stop-condition context. | `FAIL` |
| `v12_sa_v13_unblocked_by_v12_gr_only` | V13 is unblocked using V12-GR alone instead of reconciled V12 evidence. | `FAIL` |

## Allowed Aggregate Claim

V12-SA may only allow this bounded claim after PASS:

```text
V12 complete: product entity, browser workbench and read-only canvas foundation ready for review.
```

This claim remains bounded. It does not mean editable Studio, runtime
execution, product-grade frontend completion, Xpert-level UX completion,
production readiness or Agent executor readiness.

## Required Outputs

V12-SA validator output must include:

- `acceptance-data.json`
- `v12-evidence-map.json`
- `claim-to-evidence-matrix.json`
- `schema-validation-report.json`
- `prd-spec-review.md`
- `target-architecture-review.md`
- `audit-opinion.md`
- `audit-closure.md`
- `no-false-green-scan.txt`
- `redaction-scan.txt`
