# V12 Current Stage PRD Specification Review

Status: `PASS_FOR_V12_READONLY_WORKBENCH_REAL_DATA_GATE`

Last updated: `2026-06-23`

## Reviewed Sources

- `v12_to_v15_target_prd.md`
- `v12_to_v15_target_architecture.md`
- `v12_implementation_readiness_plan.md`
- `v12_product_entity_and_workbench_contracts.md`
- `v12_bff_route_and_browser_boundary.md`
- `v12_evidence_and_user_acceptance_plan.md`
- `v12_to_v15_acceptance_gate.md`
- `v12_to_v15_no_false_green_claim_guard.md`
- `evidence/v12-gemini-generated-light-studio-review/`
- `evidence/v12-readiness/`
- `apps/workflow-console/src/ui/v12/V12ReadOnlyWorkbench.tsx`

## PRD Alignment

| Requirement | Current Support | Review |
| --- | --- | --- |
| V12 is product foundation, not complete Studio | Strong | Existing docs and UI copy preserve read-only boundaries. |
| V12 includes product shell and read-only canvas foundation | Partial to strong | Existing React slice and evidence exist; must be revalidated with real-data route evidence. |
| Chat Workbench can propose, not publish/run | Partial | Current UI has proposal handoff copy; needs E2E proof that confirm handoff does not publish/run. |
| Browser must use BFF/DTO boundary | Partial | Boundary is documented; existing network evidence appears fixture/local and needs BFF-shaped real-data revalidation. |
| Station Agent profile is configuration only | Strong | Current UI copy avoids Agent executor readiness. |
| Evidence and raw content are redacted refs only | Partial | Scans pass, but DTO schema negative fixtures must be rerun in this stage. |
| Xpert reference is planning only | Strong | No current optimized Gemini artifact uses Xpert as implementation proof. |
| V13/V14/V15 remain blocked until V12 evidence passes | Strong | Stage documents preserve the order. |

## Specification Gaps

### Gap 1: Existing PASS Evidence Is Too Broad For New Real-Data Requirement

`evidence/v12-readiness/v12-acceptance-data.json` reports `PASS`, but the new
request requires real-data E2E after each substage. The current evidence must be
treated as baseline evidence requiring revalidation.

Severity: `MAJOR`

Required closure:

- Add a current-stage audit closure that supersedes fixture-only PASS as final
  acceptance.
- Re-run V12 read-only workbench acceptance against BFF-shaped route data.

### Gap 2: BFF Route Evidence Is Not Yet Strong Enough For Final V12 Acceptance

The route allowlist/denylist is documented, but acceptance needs executable
proof that the browser uses BFF-shaped DTO routes and does not call internal
runtime/store/credential routes.

Severity: `MAJOR`

Required closure:

- Implement or reuse a BFF smoke server for V12 DTOs.
- Capture browser network logs and DTO snapshots during Playwright E2E.

### Gap 3: Prototype Evidence Must Remain Design-Only

The optimized Gemini prototype is useful for V12-0P design review, but cannot
replace browser, BFF, DTO or runtime evidence.

Severity: `CONTROLLED`

Required closure:

- Keep prototype scans in design-only evidence.
- Ensure final V12 readiness report does not count it as implementation proof.

## PRD Review Decision

`PASS_FOR_V12_READONLY_WORKBENCH_REAL_DATA_GATE`

The major gaps identified for the current V12 read-only workbench gate have
been closed by `evidence/v12-current-stage-real-data/`.

This still does not permit V13 editable Workflow Studio, production readiness,
complete Workflow Studio, Xpert parity, or Agent executor readiness claims.
