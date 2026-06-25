# Post-V15 Acceptance Runner Spec

## Runner

```text
tools/post_v15/run_product_runtime_hardening_acceptance.py
```

## Evidence Generation Helper

```text
tools/post_v15/run_product_runtime_hardening_e2e.py
```

The helper may be used to generate browser and BFF evidence before invoking
the runner. It is not a substitute for the runner PASS result.

## Inputs

- Evidence directory:
  `docs/design/V12-V15.x/evidence/post-v15-product-runtime-hardening/`
- Schemas:
  - `schemas/post_v15_product_runtime_hardening_acceptance_data.schema.json`
  - `schemas/post_v15_product_runtime_hardening_artifact_manifest.schema.json`

## Required Checks

The runner must fail unless all checks pass:

1. Required files exist.
2. `acceptance-data.json` validates against the acceptance schema.
3. `artifact-manifest.json` validates against the artifact manifest schema.
4. `acceptance-data.json.status == PASS`.
5. `artifact-manifest.json.status == PASS`.
6. `runtime_backed == true` for PV16-S2 or PV16-SA.
7. PV16-S1, PV16-S2, PV16-S3, PV16-S4 and PV16-SA scenario results are all
   present and PASS.
8. `claim-to-evidence-matrix.json` contains evidence refs for every positive
   PV16 claim.
9. Browser network logs contain no direct internal runtime/store calls.
10. Runtime run/inspect report contains event, trace, artifact and quality refs.
11. Deployment smoke output contains actual command output and health result.
12. No forbidden positive claim is present outside a safe negative context.
13. Redaction scan finds no raw secrets, raw provider payloads or raw artifact
    content.

## Forbidden Browser Routes

- `/v1/rpc`
- `/internal/runtime`
- `/runtime/store`
- `/api/runtime`
- `/debug/runtime`

## Forbidden Positive Claims

- `production ready`
- `Xpert parity complete`
- `product-grade frontend complete`
- `complete Workflow Studio ready`
- `Agent executor ready`

## Output

The runner writes:

```text
docs/design/V12-V15.x/reports/post_v15_product_runtime_hardening_acceptance_report.json
```

The report must contain:

- overall `status`;
- missing artifact list;
- schema validation results;
- browser boundary result;
- runtime evidence result;
- deployment smoke result;
- per-stage result;
- claim-to-evidence result;
- claim scan result;
- redaction scan result;
- allowed claim.
