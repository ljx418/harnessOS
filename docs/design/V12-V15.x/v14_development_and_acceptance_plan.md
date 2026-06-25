# V14 Development And Acceptance Plan

## Purpose

This document is the executable development contract for the V14 governed
extension ecosystem pilot. It translates the V12-V15 PRD and target
architecture into concrete BFF routes, DTOs, frontend states, fixture data,
evidence artifacts and acceptance commands.

V14 remains a bounded pilot. It proves governed extension inspection, scoped
activation and unsafe denial for review. It does not prove an unrestricted
marketplace, production plugin runtime or Agent executor readiness.

## Entry Baseline

| Dependency | Required Result | Evidence |
| --- | --- | --- |
| V12 bounded baseline | PASS | `evidence/v12-sa-aggregate/` |
| V13 editable Studio pilot | PASS | `evidence/v13-workflow-studio-pilot/` |
| V14 readiness audit | GO | `v14_implementation_readiness_audit.md` |
| V14 PRD/architecture coverage | Covered | `v14_prd_architecture_coverage_audit.md` |
| V14 schemas | Present | `schemas/v14_extension_ecosystem_*.schema.json` |
| V14 runner spec | Present | `v14_v15_evidence_runner_spec.md` |

## V14 User-Visible Target

A reviewer can open a V14 extension registry in the browser, inspect approved
and unsafe packages, see compatibility decisions, activate an approved
capability for a selected Agent/Station scope, and see unsafe packages denied
with visible reasons and audit refs.

## Implementation Slices

### V14-S1 Manifest And Compatibility

Development output:

- Add test-only V14 BFF DTO fixtures for:
  - `PluginPackageManifest`
  - `SkillPackageManifest`
  - `ToolCapabilityManifest`
  - `McpConnectorManifest`
  - `ExtensionCompatibilityDecision`
- Add BFF routes:
  - `GET /bff/v14/system/health`
  - `GET /bff/v14/extensions/packages`
  - `GET /bff/v14/extensions/packages/{package_id}`
  - `POST /bff/v14/extensions/packages/{package_id}/compatibility-check`
- Add schema/fixture validation with positive and negative package cases.

User-visible result:

- The browser shows package name, type, trust level, requested permissions,
  required credential refs, compatibility status and audit ref.
- Incompatible or unknown permission cases show visible denial reasons.

Required evidence:

- `plugin-manifest.json`
- `skill-manifest.json`
- `tool-capability-manifest.json`
- `mcp-connector-manifest.json`
- `compatibility-decision.json`
- `negative-compatibility-fixtures.json`
- browser screenshot and BFF route log.

Stop conditions:

- Raw secret or raw connector payload appears in manifest evidence.
- Unknown permission is approved.
- Browser bypasses `/bff/v14/*`.

### V14-S2 Scoped Activation And Agent Binding

Development output:

- Add BFF routes:
  - `POST /bff/v14/extensions/packages/{package_id}/install-decision`
  - `POST /bff/v14/extensions/packages/{package_id}/activate`
  - `GET /bff/v14/agents/{agent_id}/capability-bindings`
  - `POST /bff/v14/agents/{agent_id}/capability-bindings`
- Add browser route or Studio state for V14 extension registry:
  - expected query route: `?studio=v14-extension-ecosystem`
- Add frontend panels:
  - package registry list
  - package detail and compatibility card
  - scoped activation selector
  - Agent/Station capability binding panel
  - visible audit/ref area

User-visible result:

- The user activates an approved package only for a selected workspace,
  project, app and Agent/Station scope.
- The Agent/Station panel shows only scoped capabilities.

Required evidence:

- `install-decision.json`
- `activation-decision.json`
- `scoped-capability-binding.json`
- `agent-binding-screenshot.png`
- `browser-action-log.json`
- `browser-network-log.json`
- `bff-route-log.json`

Stop conditions:

- Activated capability appears globally.
- Activation lacks workspace/project/app/Agent/Station refs.
- UI implies capability can run workflow/runtime actions.

### V14-S3 Unsafe Denial And Audit Trail

Development output:

- Add unsafe package fixture with one or more blocked properties:
  - unknown executable payload
  - unreviewed permission
  - raw secret-like config
  - scope escalation request
- Add BFF routes:
  - `POST /bff/v14/extensions/packages/{package_id}/unsafe-denial`
  - `GET /bff/v14/extensions/audit/{audit_ref}`
- Add visible denial state in the browser.

User-visible result:

- The user sees unsafe package denial status, denial reason, blocked fields and
  audit ref.
- The denied package never appears as active capability.

Required evidence:

- `unsafe-package-denial.json`
- `policy-audit-ref.json`
- `denied-package-screenshot.png`
- `redaction-scan.json`
- `no-false-green-scan.json`

Stop conditions:

- Unsafe package is installable or active.
- Denial reason is hidden.
- Audit ref is missing.
- Raw secrets appear in evidence.

### V14-SA Aggregate Acceptance

Development output:

- Add acceptance runner:
  - `tools/v14/run_v14_extension_ecosystem_acceptance.py`
- Runner must:
  - build or serve the workflow console
  - start local test-only BFF
  - exercise V14-S1/S2/S3 scenarios in browser or CDP-backed browser
  - write all required artifacts
  - validate `acceptance-data.json` against
    `schemas/v14_extension_ecosystem_acceptance_data.schema.json`
  - validate `artifact-manifest.json` against
    `schemas/v14_extension_ecosystem_artifact_manifest.schema.json`
  - scan for forbidden claims and redaction failures
  - exit non-zero on missing artifact, failed schema, route boundary failure or
    unsafe approval.

User-visible result:

- Reviewer sees one evidence package proving a governed extension ecosystem
  pilot ready for review.

Required evidence directory:

```text
docs/design/V12-V15.x/evidence/v14-extension-ecosystem/
```

Required aggregate artifacts:

- `acceptance-data.json`
- `artifact-manifest.json`
- `plugin-manifest.json`
- `skill-manifest.json`
- `tool-capability-manifest.json`
- `mcp-connector-manifest.json`
- `compatibility-decision.json`
- `install-decision.json`
- `activation-decision.json`
- `scoped-capability-binding.json`
- `unsafe-package-denial.json`
- `agent-binding-screenshot.png`
- `denied-package-screenshot.png`
- `browser-action-log.json`
- `browser-network-log.json`
- `bff-route-log.json`
- `prd-spec-review.md`
- `target-architecture-review.md`
- `audit-opinion.md`
- `audit-closure.md`
- `no-false-green-scan.json`
- `redaction-scan.json`

## Real Data Requirement

V14 acceptance must use real local fixture data served from the HarnessOS
test-only BFF. The fixtures must be shaped as product DTOs and must reference
the accepted V12/V13 workspace, project, app and Agent/Station identities where
possible:

- workspace: `ws-v12-technical-content-real`
- project: `proj-v12-local-knowledge-real`
- app: `app-v12-markdown-workflow-real`
- agent profile: `agent-v12-quality-reviewer-real`
- workflow: `wf-v13-markdown-summary-studio-pilot`

Static design files, screenshots, drawio pages or Xpert references cannot
satisfy V14 implementation evidence.

## Required Verification Commands

Minimum expected verification set after V14 implementation:

```bash
python3 -m py_compile apps/workflow-console/e2e/bff_smoke_server.py tools/v14/run_v14_extension_ecosystem_acceptance.py
cd apps/workflow-console && node node_modules/typescript/bin/tsc -p tsconfig.test.json
cd apps/workflow-console && node node_modules/vite/bin/vite.js build
python3 tools/v14/run_v14_extension_ecosystem_acceptance.py
```

If browser automation depends on local Chrome CDP, the runner must document the
same fallback strategy used by V13 and must mark missing browser automation as
BLOCKED, not PASS.

## PRD Review Checklist

- User can inspect package details without reading raw JSON.
- Compatibility status and denial reasons are visible.
- Scoped activation shows workspace/project/app/Agent/Station boundaries.
- Agent/Station panel shows only allowed capabilities.
- Unsafe package is denied and unavailable.
- No copy implies unrestricted plugin ecosystem or production marketplace.

## Target Architecture Review Checklist

- Browser only uses V14 BFF routes.
- DTOs include audit refs and redacted config refs.
- Compatibility resolver owns approval/denial.
- Activation decision owns scope.
- Runtime Gateway remains the only future execution authority.
- Evidence package separates implementation evidence from planning/reference
  material.

## Audit Opinion

With this plan in place, the V14 document set was complete enough to guide the
full V14 governed extension ecosystem pilot implementation and acceptance. V14
SA now passes, and V15 has proceeded under its own bounded implementation and
acceptance contract.
