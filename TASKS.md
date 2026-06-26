# Tasks - harnessOS

本文是当前开发主线入口。旧 Phase 0-5 清单已经与 V3.0、V12-V15/PV16、V3.5 后续文档发生口径漂移；从现在起，任务判断优先以本文和下列 source of truth 为准。

## Source Of Truth

| 用途 | 文档 |
| --- | --- |
| 当前主线选项与事实核查 | `docs/design/current-mainline-development-options.md` |
| V3.0 Core / Pack / Connector closeout | `docs/design/V3.0/CURRENT-STATUS_v3.md` |
| V3.0 gap / V3.x+ backlog | `docs/design/V3.0/v3_current_gap_analysis.md` |
| V3.0 development plan | `docs/design/V3.0/v3_development_plan_multi_app_core.md` |
| V12-V15/PV16 product evidence boundary | `docs/design/V12-V15.x/v12_to_v15_current_gap_analysis.md` |
| PV17 selected product closed loop stage | `docs/design/V12-V15.x/pv17_product_closed_loop_development_and_acceptance_plan.md` |
| ChatGPT / human project intro | `docs/present/harnessos-project-introduction/00_CHATGPT_CONTEXT_INDEX.md` |

## Current Status

### Frozen Baseline

- [x] Gateway protocol control plane: `/v1/runs`, `/v1/runs/stream`, `/v1/rpc`, session list/read/transcript/events, stdio JSONL and headless CLI baseline exist.
- [x] V3.0 Multi-App Core: `AppProfile`、`ScopeContext`、scope-aware Gateway/Core service paths and namespace isolation are frozen as baseline.
- [x] V3.0 Pack / Connector: Pack manifest loading, PackAssemblyResult, ConnectorRegistry, connector health/capabilities and connector execution runtime are baseline.
- [x] V3.0 Job / Artifact / Governance: job lifecycle, connector jobs, artifact metadata/lineage, large-file read blocking and trace/approval scope guards are baseline.
- [x] Meeting reference pack: `packs/meeting` validates platform boundaries with FunASR / Meeting MCP integration, legacy facade equivalence and strict/resilience real-audio evidence.
- [x] Knowledge reference pack: `packs/knowledge` validates data_service MCP lifecycle, artifact set, data boundary and connector replacement.
- [x] V12-V15/PV16 bounded product evidence: browser workbench foundation, editable Studio pilot, governed extension ecosystem pilot, observability/deployment baseline and product-runtime hardening pilot have bounded review evidence.
- [x] PV17 Product Closed Loop bounded review: formal `/bff/pv17/*` routes, Product Console / Mission Studio / confirm run / inspect / evidence browser path and acceptance runner evidence passed.

### Bounded / Limited Completion

- [ ] Full product experience is not complete. V12-V15/PV16 evidence proves bounded review slices only.
- [ ] Complete Workflow Studio is not complete. V13 proves editable Studio pilot only.
- [ ] Complete Agent executor is not complete. PV16 proves runtime-backed run/inspect pilot only.
- [ ] Production deployment is not complete. V15/PV16 prove smoke / hardening evidence only.
- [ ] PV17 is bounded review evidence only; it does not prove production readiness, complete Workflow Studio or Agent executor readiness.
- [ ] Meeting and Knowledge are reference packs / validation samples, not final productized business apps.
- [ ] Video Studio currently generates planning and lineage artifacts; it does not prove real rendering execution.
- [ ] Interview and Investment remain stub / planned packs.
- [x] Local Python environment restored for current smoke: `.venv` was rebuilt with Python 3.12, `pydantic_settings` and `pytest` import successfully, and the current lightweight smoke suite passed.

## Current Backlog

### P0 - Mainline Synchronization And Validation

- [x] Replace stale `TASKS.md` with current source-of-truth structure.
- [x] Add `docs/design/current-mainline-development-options.md` with fact check, open gaps and technical path options.
- [x] Restore or document a working local Python environment.
- [x] Re-run lightweight smoke after environment restore:
  - `tests/test_api_runs.py`
  - `tests/test_cli_headless.py`
  - `tests/test_pack_registry.py`
  - Meeting / Knowledge pack assembly tests
- [ ] Reconcile outdated V3.0 TODO wording that still appears in old archived sections or downstream docs.

### P1 - Selected Product / Platform Stage

The selected current stage is Path A, documented as PV17 Product Closed Loop.

- [x] Path A: Product closed loop.
  Built a bounded user-facing Product Console / Studio / run-inspect-evidence loop with browser evidence, BFF-only DTOs and runtime-backed inspection.
- [ ] Path B: Platform external app contract.
  Consolidate SDK, BFF templates, reference app, auth / capability token and method/event/error registry into a current mainline stage.
- [ ] Path C: Business pack productization.
  Promote one reference or stub domain into a productized app flow, with clear evidence boundaries and no Core/Gateway business bypass.
- [ ] Path D: Production governance hardening.
  Focus on tenant isolation, credential lifecycle, audit retention, deployment runbooks, smoke automation and operational recovery.

### P2 - Long-Range Backlog

- [ ] Complete Workflow Studio versioning, publish/run/rollback and audit loop.
- [ ] Complete Agent executor with governed execution contracts and evidence.
- [ ] Productize Meeting / Knowledge / Interview / Investment / Video Studio as real business apps.
- [ ] External plugin / skill / tool / MCP ecosystem examples and compatibility policy.
- [ ] Open-source / commercial readiness: contributor docs, release pipeline, license/CLA, deployment docs and billing / rate-limit strategy.

## Archived Legacy Plan Mapping

旧 Phase 计划保留为历史语境，不再作为当前实施顺序。若重新启用其中任务，必须在新的 stage plan 中承接。

| Legacy area | Current mapping |
| --- | --- |
| Phase 0 foundation | Mostly covered by Gateway protocol, API server, CLI and V3.0 Core baseline. Remaining item: verify local dependency environment and CI smoke. |
| Phase 1 Meeting / Interview / Knowledge MVP | Meeting / Knowledge are reference packs; Interview remains planned/stub. Treat as business pack productization backlog, not Core blocker. |
| Phase 2 production and governance | Partially covered by V3.0 governance and V12-V15/PV16 bounded evidence. Full tenant, credential, audit retention, deployment and SLA work remains backlog. |
| Phase 3 multi-agent automation | Several later V4-V11 slices exist as bounded evidence, but complete Agent executor and production multi-agent automation remain backlog. |
| Phase 4 local video workflow | Video Studio planning artifacts exist; real media execution, render polling, retry and batch production remain backlog. |
| Phase 5-C / 5-D MCP integration | V3.0 closeout says FunASR / data_service / Meeting-to-Knowledge validation passed. Keep as regression, not active unfinished mainline. |
| Phase 5 open-source / commercial readiness | Still backlog; should be re-planned as a separate stage with concrete release and documentation gates. |

## No-Go

- Do not claim HarnessOS is production ready.
- Do not claim Xpert parity complete.
- Do not claim product-grade frontend complete.
- Do not claim complete Workflow Studio ready.
- Do not claim Agent executor ready.
- Do not treat docs, screenshots, content images or presentation pages as runtime / BFF / DTO / browser E2E / production evidence.

## Current Default Next Step

PV17 Product Closed Loop has passed bounded review acceptance. The next implementation must be selected as a new stage before code work starts. Current backlog options are Path B Platform External App Contract, Path C Business Pack Productization and Path D Production Governance Hardening. Do not mix them into the completed PV17 scope without a new PRD, architecture plan, acceptance gate and audit closure.
