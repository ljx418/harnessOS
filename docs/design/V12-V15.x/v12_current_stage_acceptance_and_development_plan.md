# V12 Current Stage Acceptance And Development Plan

Status: `AUDIT_GATE_CLOSED_FOR_V12_READONLY_WORKBENCH`

Last updated: `2026-06-23`

## Scope

This plan governs the remaining V12 stage work before any broader V13 editable
Workflow Studio work can start.

Current stage:

- V12-0P design review closure.
- V12 implementation-readiness audit.
- V12 read-only browser workbench foundation revalidation.

This plan does not authorize V13 editable graph implementation, V14 extension
runtime implementation, V15 final acceptance, production readiness claims,
Agent executor readiness claims, complete Workflow Studio claims, or Xpert
parity claims.

## Current Evidence Baseline

Existing evidence:

- `evidence/v12-0p-high-fidelity-prototype/`
- `evidence/v12-gemini-generated-light-studio-review/`
- `evidence/v12-readiness/`
- `apps/workflow-console/src/ui/v12/V12ReadOnlyWorkbench.tsx`
- `apps/workflow-console/e2e/workflow-v12-readonly-canvas-foundation.spec.ts`

The Gemini-generated prototype has been imported, normalized to `V12-0P`,
converted away from the Tailwind CDN, locally rendered with Chrome, and scanned
for version drift, external dependency drift, required state terms, forbidden
positive claims and redaction terms.

## Blocking Interpretation

The existing `evidence/v12-readiness/v12-acceptance-data.json` says `PASS`, but
this plan does not treat that file as sufficient final acceptance for the new
human request because the request now requires real-data validation and
end-to-end acceptance after each substage.

For this plan, existing V12 readiness evidence is treated as legacy baseline
evidence requiring revalidation, not as final stage completion.

## Development Substages

### S0 Audit Gate And Evidence Reclassification

Goal:

- Prevent false green by separating design-only, fixture-backed and real-data
  evidence.

Required outputs:

- `v12_current_stage_prd_spec_review.md`
- `v12_current_stage_audit_opinion.md`
- `v12_current_stage_audit_closure.md`

Acceptance:

- No fatal or major audit item remains open.
- Any existing `PASS` that depends on fixture-only data is explicitly marked as
  requiring revalidation before final V12 acceptance.

### S1 V12-0P Design Review Closure

Goal:

- Decide whether the optimized Gemini prototype can serve as V12-0P
  high-fidelity design review input.

Required evidence:

- `evidence/v12-gemini-generated-light-studio-review/index.html`
- `styles.generated.css`
- `index.local-render.png`
- `validation-report.json`
- Updated `audit-notes.md`

Acceptance:

- Version drift scan PASS.
- External dependency scan PASS.
- Required state terms PASS.
- No False Green scan PASS.
- Redaction scan PASS.
- Local browser render PASS.
- PRD spec review confirms this remains design-only evidence.

### S2 Implementation-Readiness Contract Closure

Goal:

- Convert V12 readiness from planning to executable acceptance contracts.

Required checks:

- Product entity schema parse and negative fixture rejection.
- Canvas read model schema parse and negative fixture rejection.
- Browser network log schema parse.
- BFF route allowlist and denylist acceptance criteria.
- PRD review mapping from V12 target PRD to executable tests.

Acceptance:

- All schemas parse.
- Negative fixtures fail for the expected reason.
- BFF and browser boundary checks have executable tests or explicit blockers.
- No claim uses design prototype evidence as browser/BFF/runtime evidence.

### S3 Read-Only Workbench Real-Data E2E

Goal:

- Revalidate V12 read-only browser workbench using real project-local data and
  a BFF-shaped route boundary, not just static fixture claims.

Required scenario:

- Product shell opens.
- Workspace/project/app are loaded from a real local data source or a BFF smoke
  server that returns schema-valid DTOs.
- Canvas uses `CanvasReadModel`.
- Node selection shows `CanvasInspectorProjection`.
- Disabled actions show visible reasons.
- Network log proves browser does not call denied internal routes.

Acceptance:

- Browser screenshot PASS.
- Network log PASS.
- DTO snapshots PASS schema validation.
- Denylist attempts PASS.
- PRD spec review PASS.
- No False Green and redaction scans PASS.

Result:

- PASS in `evidence/v12-current-stage-real-data/`.
- BFF-shaped route log captured all required `/bff/v12/*` reads.
- Wrong workspace denial returned `404`.
- Schema validation passed for browser network log, product entity projection
  and canvas read model.
- Local Chrome headless screenshot exists.

### S4 Substage End-To-End Acceptance And Retrospective

Goal:

- Close each substage with real evidence before advancing.

Acceptance:

- Substage acceptance report exists.
- PRD spec review exists.
- Audit opinion says no fatal or major unclosed items.
- If acceptance fails, return to the plan/audit step before further
  implementation.

## Required Real-Data Standard

For this plan, "real data" means data produced by one of the following:

- A running local BFF/API route returning DTOs from repository code.
- A committed BFF smoke server used by Playwright and producing schema-valid
  route logs.
- A repository-local data file generated during the E2E run from route
  responses, not hand-authored as final proof.

The following are not sufficient by themselves:

- Static HTML prototypes.
- Xpert references.
- Gemini output.
- Hand-authored acceptance JSON.
- Browser screenshots without DTO or route evidence.

## Stop Conditions

Stop and request human confirmation if any of the following occur:

- Existing evidence cannot be downgraded or superseded without contradicting a
  previously accepted project decision.
- Real-data validation would require external credentials, provider secrets or
  production resources.
- Browser implementation work would need to bypass BFF/DTO boundaries.
- Any forbidden positive claim appears outside safe audit/boundary contexts.
- A substage fails twice for the same architectural reason.

## Allowed Claim After This Plan Passes

Only:

`V12 current-stage read-only workbench foundation real-data gate passed for review.`

Not allowed:

- Browser implementation complete.
- BFF/runtime evidence complete.
- Xpert parity complete.
- Product-grade frontend complete.
- Complete Workflow Studio ready.
- Production ready.
- Agent executor ready.
