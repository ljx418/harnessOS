# V14-V15 Remaining Stage Development And Acceptance Plan

## Purpose

This document defines the remaining post-V13 plan for V14 and V15. It turns
the accepted V12 and V13 evidence into a concrete development and acceptance
path for governed extensions, observability, deployment and final interaction
baseline review.

## Current Entry Baseline

| Baseline | Status | Evidence |
| --- | --- | --- |
| V12 product entity, browser workbench and read-only canvas foundation | PASS | `evidence/v12-sa-aggregate/` |
| V13 editable Workflow Studio pilot slice | PASS | `evidence/v13-workflow-studio-pilot/` |
| V14 governed extension ecosystem | PASS | `evidence/v14-extension-ecosystem/` and `reports/v14_extension_ecosystem_acceptance_report.json` |
| V15 observability/deployment/final interaction baseline | Current target | Requires V12-V14 PASS evidence and V15 readiness audit. |

## V14 Stage Goal

V14 should let a reviewer use the browser to inspect, approve and bind scoped
Plugin, Skill, Tool and MCP capabilities into Agent/Station configuration. The
target user experience is a governed extension ecosystem pilot, not an
unrestricted marketplace or production plugin runtime.

## V14 Development Slices

| Slice | Development Output | User-Visible Result | Required Evidence |
| --- | --- | --- | --- |
| V14-R0 readiness audit | Manifest, compatibility, scope and unsafe-denial plan | Reviewer sees accepted V14 scope and stop conditions | readiness audit, PRD review, architecture review |
| V14-S1 manifest and compatibility model | `PluginPackageManifest`, `SkillPackageManifest`, `ToolCapabilityManifest`, `McpConnectorManifest` DTOs | Reviewer can inspect package metadata and compatibility result | schema validation, DTO samples, negative fixtures |
| V14-S2 scoped activation UI | Browser extension registry and Agent binding panel | User enables approved capability for selected workspace/Agent scope | browser screenshot, BFF route log, scoped activation refs |
| V14-S3 unsafe denial and audit trail | Deny-by-default policy, visible reason and audit ref | Unsafe or incompatible package is denied with clear reason | denial fixture, audit log, redaction scan |
| V14-SA aggregate acceptance | Evidence reconciliation and claim scan | Reviewer accepts governed extension ecosystem pilot | acceptance data, artifact manifest, No False Green scan |

## V14 Acceptance Criteria

- V14 readiness audit has no open fatal or major findings.
- Manifest schemas reject unknown fields and missing permissions.
- Approved plugin/skill/tool/MCP capability can be scoped to workspace/project
  and selected Agent/Station only.
- Unsafe package is denied before execution with a visible reason and audit ref.
- Raw secrets are represented only as redacted refs.
- Browser routes use `/bff/v14/*` or an accepted BFF namespace.
- Capability binding cannot run workflow/runtime actions without later
  confirmation.
- Evidence package includes acceptance data, artifact manifest, screenshots,
  route logs, manifest samples, compatibility decisions, denial fixtures,
  PRD review, architecture review, audit opinion, audit closure, claim scan and
  redaction scan.

## V14 Stop Conditions

- Plugin install executes unreviewed code.
- Package config leaks raw secrets or provider payload.
- Browser bypasses compatibility resolver or BFF scope checks.
- Tool/MCP capability appears globally before scoped activation.
- UI claims unrestricted plugin ecosystem or production marketplace readiness.

## V15 Stage Goal

V15 should let a reviewer inspect product operations evidence from the browser
and complete the final V12-V15 scenario matrix with trace, metrics, audit,
deployment smoke and interaction baseline evidence. The target is a frontend
interaction baseline ready for review, not production GA.

## V15 Development Slices

| Slice | Development Output | User-Visible Result | Required Evidence |
| --- | --- | --- | --- |
| V15-R0 readiness audit | Observability/deployment schemas, smoke contract, final matrix | Reviewer sees accepted V15 scope and evidence requirements | readiness audit, PRD review, architecture review |
| V15-S1 operations evidence dashboard | Trace timeline, metrics snapshot, audit export and incident refs | Operator can inspect read-only operations evidence | dashboard screenshot, DTOs, route log |
| V15-S2 deployment smoke | Compose/env profile, health checks, browser/API diagnostics | Operator can start local stack and see health/smoke output | command output, health logs, smoke result |
| V15-S3 final scenario matrix | Product console, Studio, extension, observability and deployment scenarios | Reviewer can follow the end-to-end target experience | Playwright logs, screenshots, human UX review |
| V15-SA final aggregate acceptance | Evidence map, claim-to-evidence matrix and scans | Reviewer accepts V12-V15 interaction baseline for review | aggregate manifest, No False Green scan, redaction scan |

## V15 Acceptance Criteria

- V12, V13 and V14 evidence packages exist and PASS before V15 final acceptance.
- Trace, metrics, audit and incident panels are read-only and do not construct
  runtime truth.
- Deployment smoke includes command output, health checks, browser/API
  diagnostics and rollback notes.
- Final scenario matrix covers product console, Studio authoring, Agent setup,
  extension binding, run/inspect evidence, observability and self-host smoke.
- Browser-visible failures have clear feedback and do not silently pass.
- No forbidden completion or production claims appear outside safe claim-scan
  context.

## V15 Stop Conditions

- Final acceptance runs while V14 evidence is missing.
- Deployment smoke is documentation-only.
- Observability dashboard mutates runtime truth or hides failed health checks.
- Browser shows API/environment mismatch while smoke claims PASS.
- UI or docs claim production GA, Xpert parity, product-grade frontend
  completion, complete Studio readiness or Agent executor readiness.

## Required Machine-Readable Artifacts To Add

| Stage | Artifact |
| --- | --- |
| V14 | `schemas/v14_extension_ecosystem_acceptance_data.schema.json` |
| V14 | `schemas/v14_extension_ecosystem_artifact_manifest.schema.json` |
| V14 | `reports/v14_extension_ecosystem_acceptance_report.json` |
| V14 | `evidence/v14-extension-ecosystem/acceptance-data.json` |
| V14 | `evidence/v14-extension-ecosystem/artifact-manifest.json` |
| V15 | `schemas/v15_observability_deployment_acceptance_data.schema.json` |
| V15 | `schemas/v15_observability_deployment_artifact_manifest.schema.json` |
| V15 | `reports/v15_document_support_audit_report.json` |
| V15 | `evidence/v15-observability-deployment/acceptance-data.json` |
| V15 | `evidence/v15-observability-deployment/artifact-manifest.json` |

## Audit Opinion

The current document set supports review of completed V12, V13 and V14 bounded
stages. With V14-SA PASS, V15 may proceed as the current implementation target
under the bounded observability, deployment and final interaction baseline
contract.
