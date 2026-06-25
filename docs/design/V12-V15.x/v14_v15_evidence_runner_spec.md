# V14-V15 Evidence Runner Spec

## Purpose

This spec defines the acceptance runner behavior required before V14 or V15
implementation can claim PASS. It is a development contract for future tools,
not evidence by itself.

## V14 Runner Contract

Expected command:

```bash
python3 tools/v14/run_v14_extension_ecosystem_acceptance.py
```

Required behavior:

- Start or connect to local BFF and browser preview.
- Exercise approved package inspection.
- Validate plugin, skill, tool and MCP manifests.
- Exercise compatibility approval and denial paths.
- Exercise scoped activation for a selected Agent/Station.
- Exercise unsafe package denial with visible reason.
- Capture browser screenshot, browser network log and BFF route log.
- Write `acceptance-data.json` and `artifact-manifest.json`.
- Validate both JSON files against V14 schemas.
- Run No False Green and redaction scans.
- Exit non-zero on missing artifacts, schema failure, route boundary failure,
  raw secret leakage or overclaim.

Required evidence directory:

```text
docs/design/V12-V15.x/evidence/v14-extension-ecosystem/
```

## V15 Runner Contract

Expected command:

```bash
python3 tools/v15/run_v15_observability_deployment_acceptance.py
```

Required behavior:

- Verify V12, V13 and V14 evidence packages exist and PASS.
- Exercise read-only observability dashboard.
- Validate trace, metrics, audit and incident DTOs.
- Run deployment profile validation and health checks.
- Capture deployment smoke command output.
- Execute final scenario matrix or explicitly mark accepted bounded PARTIAL
  with audit closure.
- Capture browser screenshots, browser network log and BFF route log.
- Write `acceptance-data.json` and `artifact-manifest.json`.
- Validate both JSON files against V15 schemas.
- Run No False Green and redaction scans.
- Exit non-zero on missing V14 evidence, smoke without command output, route
  boundary failure, raw secret leakage or overclaim.

Required evidence directory:

```text
docs/design/V12-V15.x/evidence/v15-observability-deployment/
```

## Shared Runner Rules

- A screenshot alone is never enough for PASS.
- Planning docs and Xpert references are never implementation evidence.
- Any required artifact marked `MISSING` blocks aggregate PASS.
- Forbidden positive claims must fail the run outside safe claim-scan context.
- Redaction scan failure blocks PASS.
- Browser network logs must not show direct internal runtime/store access.
- Every user-visible scenario result must include at least one evidence ref.

## Audit Opinion

The runner contract is specific enough to guide future implementation of V14
and V15 automated acceptance tools. Until those tools exist and pass, V14/V15
implementation evidence remains unavailable.
