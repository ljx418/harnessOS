# V15 Development And Acceptance Plan

## Purpose

This document is the executable development contract for the V15
observability, deployment and final interaction baseline prototype. It converts
the V12-V15 PRD and target architecture into concrete BFF routes, DTOs,
frontend states, fixture-backed local smoke evidence and acceptance commands.

V15 remains bounded. It proves a frontend interaction baseline ready for
review. It does not prove production GA, Xpert parity, product-grade frontend
completion, complete Workflow Studio readiness or Agent executor readiness.

## Entry Baseline

| Dependency | Required Result | Evidence |
| --- | --- | --- |
| V12 bounded baseline | PASS | `evidence/v12-sa-aggregate/` |
| V13 editable Studio pilot | PASS | `evidence/v13-workflow-studio-pilot/` |
| V14 governed extension ecosystem pilot | PASS | `evidence/v14-extension-ecosystem/` |
| V15 readiness audit | GO after V14 PASS | `v15_implementation_readiness_audit.md` |
| V15 PRD/architecture coverage | Covered | `v15_prd_architecture_coverage_audit.md` |
| V15 schemas | Present | `schemas/v15_observability_deployment_*.schema.json` |
| V15 runner spec | Present | `v14_v15_evidence_runner_spec.md` |

## V15 User-Visible Target

A reviewer can open a V15 operations and deployment review page in the browser,
inspect read-only trace, metrics, audit and incident evidence, run bounded local
deployment health/smoke checks, and review the final V12-V15 scenario matrix
without seeing production or Xpert parity claims.

## Implementation Slices

### V15-S1 Observability Dashboard

Development output:

- Add test-only V15 BFF DTO fixtures for:
  - `TraceTimeline`
  - `MetricsSnapshot`
  - `AuditExportPackage`
  - `IncidentTimeline`
- Add BFF routes:
  - `GET /bff/v15/system/health`
  - `GET /bff/v15/observability/trace-timeline`
  - `GET /bff/v15/observability/metrics-snapshot`
  - `GET /bff/v15/observability/audit-export`
  - `GET /bff/v15/observability/incidents`

User-visible result:

- The browser shows trace events, metrics, audit export refs, incident status
  and redaction/claim scan state.
- The dashboard is read-only and never constructs runtime truth.

Required evidence:

- `trace-timeline.json`
- `metrics-snapshot.json`
- `audit-export-package.json`
- `incident-timeline.json`
- `observability-dashboard-screenshot.png`
- BFF route log and browser network log.

Stop conditions:

- Dashboard mutates runtime state.
- Dashboard hides failed or blocked states.
- Raw prompt, provider payload, raw token or raw artifact content appears.

### V15-S2 Deployment Profile And Health Diagnostics

Development output:

- Add BFF routes:
  - `GET /bff/v15/deployment/profile`
  - `POST /bff/v15/deployment/health-check`
  - `POST /bff/v15/deployment/smoke`
- Add browser controls for local health check and bounded smoke review.

User-visible result:

- The user sees environment/profile checks, frontend/API consistency, health
  status, smoke command output and rollback notes.

Required evidence:

- `deployment-profile.json`
- `health-check-result.json`
- `deployment-smoke-output.txt`
- `product-shell-screenshot.png`

Stop conditions:

- Deployment smoke lacks actual command or HTTP output.
- Browser/API mismatch is hidden while smoke claims PASS.
- Smoke is represented as production readiness.

### V15-S3 Final Scenario Matrix

Development output:

- Add BFF route:
  - `GET /bff/v15/final-scenario-matrix`
- Add browser matrix for V12, V13, V14 and V15 scenario review.

User-visible result:

- The reviewer sees each major product experience mapped to HarnessOS evidence
  refs and bounded claim language.

Required evidence:

- `final-scenario-matrix.json`
- product shell and observability screenshots
- PRD review and target architecture review.

Stop conditions:

- Xpert screenshots or planning docs are counted as HarnessOS implementation
  evidence.
- Matrix marks a missing dependency as PASS.

### V15-SA Aggregate Acceptance

Development output:

- Add acceptance runner:
  - `tools/v15/run_v15_observability_deployment_acceptance.py`
- Runner must:
  - verify V12, V13 and V14 evidence packages exist and PASS
  - build or serve the workflow console
  - start local test-only BFF
  - exercise V15-S1/S2/S3 scenarios in a CDP-backed browser
  - write all required artifacts
  - validate `acceptance-data.json` against
    `schemas/v15_observability_deployment_acceptance_data.schema.json`
  - validate `artifact-manifest.json` against
    `schemas/v15_observability_deployment_artifact_manifest.schema.json`
  - scan for forbidden claims and redaction failures
  - exit non-zero on missing artifact, failed schema, route boundary failure,
    documentation-only smoke or overclaim.

Required evidence directory:

```text
docs/design/V12-V15.x/evidence/v15-observability-deployment/
```

Required aggregate artifacts:

- `acceptance-data.json`
- `artifact-manifest.json`
- `trace-timeline.json`
- `metrics-snapshot.json`
- `audit-export-package.json`
- `incident-timeline.json`
- `deployment-profile.json`
- `health-check-result.json`
- `deployment-smoke-output.txt`
- `final-scenario-matrix.json`
- `product-shell-screenshot.png`
- `observability-dashboard-screenshot.png`
- `browser-network-log.json`
- `bff-route-log.json`
- `prd-spec-review.md`
- `target-architecture-review.md`
- `audit-opinion.md`
- `audit-closure.md`
- `no-false-green-scan.json`
- `redaction-scan.json`

## Real Data Requirement

V15 acceptance must use V12/V13/V14 PASS evidence refs, BFF-shaped DTOs and
actual browser/CDP plus local HTTP health/smoke output. Static documents,
drawio pages, Xpert references or screenshots alone cannot satisfy V15
implementation evidence.

## Required Verification Commands

```bash
python3 -m py_compile apps/workflow-console/e2e/bff_smoke_server.py tools/v15/run_v15_observability_deployment_acceptance.py
cd apps/workflow-console && node node_modules/typescript/bin/tsc -p tsconfig.test.json
cd apps/workflow-console && node node_modules/vite/bin/vite.js build
python3 tools/v15/run_v15_observability_deployment_acceptance.py
```

If browser automation depends on local Chrome CDP, the runner must mark missing
browser automation as BLOCKED, not PASS.

## PRD Review Checklist

- User can inspect trace, metrics, audit and incident evidence without raw
  provider payloads.
- User can run local health and bounded deployment smoke checks.
- Final scenario matrix maps V12, V13, V14 and V15 evidence to user-visible
  experience.
- No copy implies production GA, Xpert parity, product-grade frontend
  completion or Agent executor readiness.

## Target Architecture Review Checklist

- Browser only uses V15 BFF routes.
- Observability DTOs are read-only evidence projections.
- Deployment smoke includes concrete command/HTTP output.
- V15 consumes prior stage evidence; it does not invent runtime truth.
- Evidence package separates implementation evidence from planning/reference
  material.

## Audit Opinion

With V14-SA evidence now PASS, this plan is complete enough to guide V15
observability, deployment and final interaction baseline implementation and
acceptance.
