# Document Cleanup Report - 2026-06-08

## Summary

This cleanup moves clearly inactive, superseded, or non-canonical documentation
artifacts out of active `docs/design` and `docs/architecture` paths into
`docs/history`.

No current V6/V7/V8/V9/V10 canonical baseline, runtime evidence package, test
fixture, schema bundle, or active acceptance dashboard was moved.

## Archived By Stage / Category

### V2.0 Historical Design

Moved from `docs/design/V2.0/` to `docs/history/design/V2.0/`:

- `harnessos_architecture_master_spec_v2.md`
- `harnessos_baseline_v2.md`

Reason: V2 is no longer an active stage directory. It remains useful for
historical architecture traceability.

### V10.x Superseded Concept

Moved from active V10 evidence to
`docs/history/design/V10.x/superseded/v10-0-cockpit-first/`:

- `host-generated-cockpit.png`

Reason: V10-0R superseded the cockpit/dashboard-first direction with a
CLI-native TUI baseline. The image remains useful as historical visual context
but must not be treated as current target direction or runtime evidence.

### Drawio Backup Files

Moved drawio temporary backup files to:

- `docs/history/cleanup/drawio-backups/`

Reason: `.$*.drawio.bkp` files are editor-generated backup artifacts and are not
active canonical diagrams.

### System Artifacts

Moved `.DS_Store` files to:

- `docs/history/cleanup/system-artifacts/`

Reason: `.DS_Store` files are macOS filesystem metadata, not design documents.
They were moved out of active documentation paths without deleting data.

## Deferred From Cleanup

The following stage directories remain in active `docs/design` because they are
still referenced by startup instructions, tests, scripts, or current evidence
chains:

- `docs/design/V3.0` is referenced by `AGENTS.md` and `TASKS.md`.
- `docs/design/V3.6` is referenced by V4.0 contract-alignment tests.
- `docs/design/V4.0` is referenced by V4.0 contract, claim guard, and frontend
  tests.
- `docs/design/V4.2` through `docs/design/V4.6` are referenced by V4 reality
  check scripts and acceptance tests.
- `docs/design/V4.x` remains a canonical V4 closure and evidence baseline.
- `docs/design/V5.x` through `docs/design/V9.x` remain historical baselines and
  active evidence dependencies for later-stage verification.
- `docs/design/V10.x` is the current active planning and UX direction.

Moving any deferred directory would require updating tests, scripts, and
cross-stage evidence references in a separate migration.

## Verification

- Active docs no longer contain `.DS_Store` or `.$*.drawio.bkp` files.
- `docs/design/V2.0` has been removed from active design docs and archived.
- V10 report generation now references the superseded cockpit image in
  `docs/history`.
- V10 planning tests and drawio XML validation were run after the cleanup.
