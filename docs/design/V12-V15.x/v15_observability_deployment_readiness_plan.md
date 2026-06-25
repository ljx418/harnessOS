# V15 Observability Deployment And Final Interaction Readiness Plan

## Current Decision

V15 final acceptance was blocked until V12, V13 and V14 evidence packages
existed and passed. Those dependencies now exist and pass, and the bounded V15
observability, deployment and final interaction baseline evidence package also
passes. This document is retained as the readiness contract that authorized the
V15 implementation path.

Allowed after dependency PASS:

- Observability dashboard planning.
- Deployment smoke and health check planning.
- Final frontend interaction scenario planning.
- Final evidence aggregation and No False Green planning.

Completed bounded evidence after dependency PASS:

- Observability dashboard browser evidence.
- Deployment health and bounded smoke evidence.
- Final V12-V15 scenario matrix evidence.
- Aggregate V15 acceptance data and artifact manifest.

Blocked:

- Final V15 acceptance before V12-V14 evidence exists.
- Production ready or full production GA claim.
- Xpert parity complete claim.
- Observability dashboard constructing runtime truth.

## V15 Objective

V15 gives users and operators a browser-visible way to review traces, metrics,
audit exports, incidents, deployment health and final product interaction
evidence. It proves an Xpert-level frontend interaction baseline ready for
review, not full Xpert parity or production GA.

## Required Schemas And DTOs

- `TraceTimeline`
- `TraceEvent`
- `MetricsSnapshot`
- `AuditExportPackage`
- `IncidentTimeline`
- `IncidentTimelineEvent`
- `DeploymentProfile`
- `HealthCheckResult`
- `FrontendApiConfigCheck`
- `DeploymentSmokeResult`
- `FinalScenarioMatrix`
- `V15FinalAcceptanceData`

Common required fields:

- `schema_version`
- `workspace_id`
- `project_id`
- `app_id`
- `run_ref`
- `request_id`
- `correlation_id`
- `audit_ref`
- `created_at`
- `evidence_scope`

## Observability Boundary

Observability panels may display:

- trace timeline
- run status
- metrics snapshot
- audit export ref
- incident timeline
- redaction status
- claim scan status
- deployment health

They must not:

- mutate workflow/runtime truth
- hide failed or blocked states
- rewrite evidence scope
- expose raw prompt, raw provider payload, raw token or raw artifact content

## Deployment Smoke Boundary

V15 deployment smoke must include actual command output and health checks:

- environment file validation
- frontend/API base URL check
- storage/queue/provider config check
- API health
- browser product shell load
- one workflow smoke or bounded fixture-backed smoke with explicit scope
- rollback notes

Documentation-only deployment instructions cannot satisfy deployment smoke.

## Implementation Slices

### V15-1 Observability Dashboard

Exit evidence:

- trace timeline visible
- metrics snapshot visible
- audit export ref visible
- incident timeline visible
- dashboard is read-only for runtime truth

### V15-2 Deployment Profile And Health Diagnostics

Exit evidence:

- deployment profile exists
- health check results exist
- browser/API config consistency PASS
- environment mismatch is visible if present

### V15-3 Final Scenario Matrix

Exit evidence:

- product onboarding PASS
- workbench to Studio handoff PASS
- visual workflow authoring PASS
- Agent setup PASS
- plugin install/deny PASS
- workflow run/inspect PASS
- observability review PASS
- self-host smoke PASS or accepted bounded PARTIAL with reason

### V15-4 Final Acceptance Aggregation

Exit evidence:

- V12/V13/V14/V15 packages exist
- no FAIL or unaccepted BLOCKED
- No False Green PASS
- redaction PASS
- drawio XML PASS
- final allowed claim only

## User Scenarios

### US-V15-01 Operator Observability Review

User opens operations dashboard and sees trace, metrics, audit and incident
refs for a workflow run.

PASS:

- trace timeline exists
- metrics snapshot exists
- audit export ref exists
- incident refs visible if failures exist
- dashboard does not mutate runtime truth

### US-V15-02 Self-Host Smoke

User follows local deployment profile and reaches product shell with API health
visible.

PASS:

- command output exists
- health check JSON exists
- browser screenshot exists
- frontend/API mismatch absent or marked blocking

### US-V15-03 Final Xpert-Inspired Interaction Review

Reviewer compares HarnessOS product flow against the Xpert reference checklist.

PASS:

- product shell
- workbench
- Studio
- Agent setup
- plugin lifecycle
- execution review
- observability
- deployment smoke
- all backed by HarnessOS evidence, not Xpert screenshots

## V15 Evidence Package

```text
docs/design/V12-V15.x/evidence/v15-observability-deployment/
```

Required:

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
- `redaction-scan.json`
- `no-false-green-scan.json`
- `prd-spec-review.md`

## V15 Stop Conditions

- V12/V13/V14 evidence missing.
- Deployment smoke lacks actual command output.
- Browser/API mismatch is unresolved while final claims PASS.
- Observability dashboard constructs runtime truth.
- Xpert reference screenshot is counted as HarnessOS implementation evidence.
- Any forbidden positive claim appears outside safe context.
- Redaction scan fails.
