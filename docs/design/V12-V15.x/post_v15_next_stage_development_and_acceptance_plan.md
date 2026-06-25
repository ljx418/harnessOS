# Post-V15 Next Stage Development And Acceptance Plan

## Purpose

This document defines the first development plan after the bounded V15 result.
It does not extend the V15 claim. V15 remains limited to:

```text
V15 complete: frontend interaction baseline ready for review.
```

The next stage exists because the target PRD still describes product outcomes
that are not proven by the bounded V12-V15 evidence: durable product mutation,
runtime-backed workflow run and inspection, production-like self-hosting
hardening, and broader product interaction quality.

## Scope Decision

The recommended next stage is:

```text
PV16: product-runtime hardening readiness and pilot evidence.
```

PV16 is a post-V15 stage name. It is intentionally separate from V12-V15 so the
project does not backfill unproven runtime or production claims into the V15
evidence package.

## Current Evidence Baseline

PV16 may reuse these accepted bounded inputs:

- V12 product entity, browser workbench and read-only canvas foundation
  evidence.
- V13 editable Workflow Studio pilot evidence.
- V14 governed extension ecosystem pilot evidence.
- V15 observability, deployment smoke and final interaction baseline evidence.
- V12-V15 No False Green, redaction, route-boundary and drawio validation
  artifacts.

PV16 must not reuse those inputs as proof of production readiness, complete
Workflow Studio readiness, runtime executor readiness, Xpert parity,
product-grade frontend completion or unrestricted plugin marketplace readiness.

## PV16 Stage Outline

| Stage | User-Visible Outcome | Development Work | Acceptance Evidence |
| --- | --- | --- | --- |
| PV16-R0 | Reviewer sees the selected post-V15 scope, PRD coverage and risk gates before implementation. | Freeze PV16 scope, route ownership, DTO contracts, evidence schemas, runner behavior and stop conditions. | Readiness audit, document-support audit, schema draft, route allowlist, claim scan. |
| PV16-R0.1 | Implementer sees substage-specific evidence rules before code is counted. | Lock scenario ids, required files, runner checks and claim-to-evidence mapping for PV16-S1/S2/S3/S4/SA. | Updated runner spec, schemas, acceptance runner and document-support audit. |
| PV16-S1 | User creates or updates workspace, project, app and Station Agent records with visible audit refs. | Add durable entity mutation through BFF-only routes; enforce ownership, policy and validation; show failed/denied states in UI. | Entity CRUD report, BFF route log, browser network log, audit refs, negative ownership/policy fixtures. |
| PV16-S2 | User confirms a WorkflowSpec run and inspects real runtime-backed progress, output, trace and evidence refs. | Connect confirmed WorkflowDiff/WorkflowSpec to controlled runtime gateway; stream run status; surface artifacts, quality refs and trace refs. | Runtime run report, event log, trace refs, artifact refs, quality refs, screenshot/video, no direct browser runtime calls. |
| PV16-S3 | Operator starts a documented local/self-host profile and completes one smoke path with command output. | Harden compose/env/profile checks, frontend/API/runtime health diagnostics, storage/queue/provider placeholders and rollback notes. | Deployment smoke output, health report, config redaction scan, failure-mode screenshot, runbook review. |
| PV16-S4 | Reviewer verifies a coherent product journey across setup, Studio, run review and operations. | Harden navigation, responsive layout, keyboard/focus, empty/loading/denied/failure states and scenario continuity. | Automated UX matrix, desktop/constrained screenshots, accessibility notes, human UX review. |
| PV16-SA | Reviewer sees one aggregate decision with every positive claim mapped to evidence. | Reconcile PV16-S1/S2/S3/S4 evidence and scan for false claims, secrets and missing runtime proof. | Acceptance data, artifact manifest, claim-to-evidence matrix, No False Green scan, redaction scan. |

## Required Evidence Package

PV16 evidence must be written under:

```text
docs/design/V12-V15.x/evidence/post-v15-product-runtime-hardening/
```

Minimum files:

- `acceptance-data.json`
- `artifact-manifest.json`
- `entity-crud-report.json`
- `runtime-run-inspect-report.json`
- `deployment-smoke-output.txt`
- `deployment-health-report.json`
- `ux-hardening-report.json`
- `claim-to-evidence-matrix.json`
- `product-journey-screenshot.png`
- `runtime-inspect-screenshot.png`
- `prd-spec-review.md`
- `target-architecture-review.md`
- `audit-closure.md`
- `no-false-green-scan.txt`
- `redaction-scan.txt`

## Required Schemas And Runner

Implementation evidence cannot be accepted unless these contracts are used:

- `schemas/post_v15_product_runtime_hardening_acceptance_data.schema.json`
- `schemas/post_v15_product_runtime_hardening_artifact_manifest.schema.json`
- `tools/post_v15/run_product_runtime_hardening_acceptance.py`
- `tools/post_v15/run_product_runtime_hardening_e2e.py`

These contracts now exist. The runner must fail when:

- required evidence files are missing;
- schemas fail validation;
- any PV16-S1, PV16-S2, PV16-S3, PV16-S4 or PV16-SA scenario result is missing
  or not PASS;
- the claim-to-evidence matrix is missing or contains a positive claim without
  evidence refs;
- a browser log shows direct internal runtime or store calls;
- runtime evidence is represented only by static fixtures;
- deployment smoke lacks actual command output;
- any forbidden completion claim appears outside a safe negative context;
- raw secrets, raw provider payloads or raw artifact contents are exposed.

The runner behavior is specified in `post_v15_acceptance_runner_spec.md`.
Implementation entry is audited in `post_v15_implementation_readiness_audit.md`.
The E2E helper starts the test BFF, workflow-console preview and headless
Chrome CDP, generates the PV16 evidence package and then invokes the acceptance
runner. The acceptance runner remains the source of truth for PASS/FAIL.

## PRD Review Loop

Before each PV16 implementation substage starts:

1. Re-read `v12_to_v15_target_prd.md`.
2. Identify which target scenarios the substage owns.
3. Write expected user-visible outcomes and evidence files.
4. Record fatal, major and minor audit findings.
5. Close all fatal and major findings before implementation.

After each substage completes:

1. Run the substage acceptance runner.
2. Record PRD scenario coverage.
3. Record target architecture plane coverage.
4. Scan claims and secrets.
5. If acceptance fails, return to planning and update this document or the
   substage plan before retrying implementation.

## Target Architecture Review Loop

Each PV16 substage must explicitly review these architecture boundaries:

- browser routes go through BFF DTOs only;
- product entities do not own runtime execution state;
- WorkflowSpec / WorkflowVersion changes are audited;
- runtime gateway controls execution and emits trace/evidence refs;
- observability reads runtime evidence and does not construct runtime truth;
- deployment smoke proves command output and health checks, not production GA.

## Stop Conditions

Stop and request human confirmation if any of the following appears:

- PV16 scope requires external provider credentials or irreversible runtime
  actions.
- The browser must call internal runtime/store routes directly to proceed.
- A test cannot distinguish fixture evidence from real runtime evidence.
- Deployment smoke requires destructive local environment changes.
- The user-facing claim would imply production ready, Xpert parity, complete
  Workflow Studio ready or Agent executor ready.
- A fatal or major PRD/architecture audit finding cannot be closed by document
  or implementation changes in the current substage.

## Allowed PV16 Claim

If PV16-SA passes, the only allowed claim is:

```text
PV16 complete: product-runtime hardening pilot ready for review.
```

This claim does not mean production ready, complete Workflow Studio ready,
Agent executor ready, Xpert parity or product-grade frontend complete.
