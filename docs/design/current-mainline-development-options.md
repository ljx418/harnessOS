# harnessOS Current Mainline Development Options

文档状态：当前主线事实核查与下一阶段开发选项。
日期：2026-06-25。
用途：把当前业务实际实现、未完成内容和可选技术路径放到同一入口，避免旧 `TASKS.md`、V3.0 closeout、V12-V15/PV16 pilot 证据互相混淆。
边界：本文是开发计划和事实核查文档，不是运行证据、生产证据或产品完成声明。

## 1. Fact Check

### 当前已能作为实现事实讨论

| Area | Current fact | Evidence entry |
| --- | --- | --- |
| API / Gateway | FastAPI app includes health, BFF routes, `/v1/runs`, `/v1/runs/stream`, `/v1/rpc`, sessions and events. | `main.py`, `apps/api/__init__.py`, `apps/api/routers/runs.py` |
| RPC registry | Gateway registers session, turn, trace, approval, artifact, job, connector, workflow, pack and agent methods. | `apps/gateway/service.py` |
| Multi-app scope | Built-in app profiles exist for meeting, knowledge, interview, investment and video_studio. | `core/apps/profiles.py` |
| Pack registry | Pack manifest loading, duplicate rejection, PackAssemblyResult and assembly status exist. | `core/packs/registry.py` |
| Connector registry/runtime | Built-in connector definitions, health, security descriptors, submit/poll/cancel/collect and MCP stdio execution exist. | `apps/gateway/connectors.py`, `apps/gateway/connector_execution.py` |
| Meeting reference pack | Active pack with `meeting.workflow`, FunASR / Meeting MCP contracts and artifact lineage. | `packs/meeting/manifest.json`, `packs/meeting/workflow.py` |
| Knowledge reference pack | Active pack with data_service MCP workflow, artifacts and boundary checks. | `packs/knowledge/manifest.json`, `packs/knowledge/workflow.py` |
| Video Studio planning | Active pack creates planning and lineage artifacts. | `packs/video_studio/manifest.json`, `packs/video_studio/workflow.py` |
| SDK / templates | Python SDK, TypeScript SDK, BFF templates and reference app assets exist. | `sdk/`, `templates/`, `examples/reference_app/` |

### 当前不能作为完成声明

| Claim | Reality |
| --- | --- |
| Production readiness | Not proven. V15/PV16 only provide bounded smoke / hardening evidence. |
| Complete Workflow Studio | Not proven. V13 proves editable Studio pilot only. |
| Complete Agent executor | Not proven. PV16 proves runtime-backed run/inspect pilot only. |
| Product-grade frontend complete | Not proven. V12-V15 are bounded review slices. |
| Full Meeting / Knowledge productization | Not proven. They are reference packs / validation samples. |
| Interview / Investment productization | Not implemented. Their packs are stub / planned. |
| Real Video Studio rendering | Not proven. Current workflow produces planning and render manifest artifacts. |

### Environment finding

The local environment has been restored for the current PV17 implementation pass:

```text
pydantic_settings 2.14.2
pytest 9.1.1
30 passed, 6 warnings
```

The restored smoke covered API runs, CLI headless, pack registry, Meeting pack assembly, Knowledge pack assembly, PV17 BFF routes and the PV17 acceptance runner tests. Remaining warnings are existing dependency / Pydantic deprecation warnings, not current PV17 failures.

## 2. Current Gap

The main project gap is no longer V3.0 Core completion. V3.0 is documented as final closeout, with Meeting / Knowledge reference pack validation passed.

The active gap has now been resolved for this stage: **Path A - Product Closed Loop** was selected, implemented and accepted as PV17 bounded review evidence. PV17 turns the V12-V15/PV16 bounded review slices into one mainline product path without overclaiming production, Xpert parity or Agent executor readiness.

The alternative paths remain backlog options:

- external app / SDK contract;
- business pack productization;
- production governance hardening.

`TASKS.md` has been rewritten to make this distinction explicit.

## 3. Technical Paths

### Path A - Product Closed Loop

Status: selected and implemented as PV17 bounded review evidence. Canonical docs:

- `docs/design/V12-V15.x/pv17_product_closed_loop_prd.md`
- `docs/design/V12-V15.x/pv17_product_closed_loop_target_architecture.md`
- `docs/design/V12-V15.x/pv17_product_closed_loop_bff_dto_contract.md`
- `docs/design/V12-V15.x/pv17_product_closed_loop_implementation_task_matrix.md`
- `docs/design/V12-V15.x/pv17_product_closed_loop_development_and_acceptance_plan.md`
- `docs/design/V12-V15.x/pv17_product_closed_loop_acceptance_runner_spec.md`
- `docs/design/V12-V15.x/pv17_product_closed_loop_milestone_roadmap.md`
- `docs/design/V12-V15.x/pv17_product_closed_loop_acceptance_gate.md`
- `docs/design/V12-V15.x/pv17_product_closed_loop_current_gap_analysis.md`
- `docs/design/V12-V15.x/pv17_product_closed_loop_implementation_readiness_audit.md`
- `docs/design/V12-V15.x/pv17_product_closed_loop_gap_analysis.drawio`

Goal: make one coherent browser path usable for review: setup -> Studio -> run -> inspect -> evidence.

Implementation outline:

- Add or harden BFF-only routes for workspace/project/app/Station Agent mutation.
- Connect WorkflowSpec versioning to a runtime-backed run/inspect path.
- Ensure Studio and operations views read DTOs, route logs and evidence refs rather than runtime truth directly.
- Add browser E2E and screenshots for create/edit/confirm/run/inspect.
- Keep all copy clear that this is not production readiness or complete Studio unless later evidence proves it.

Acceptance:

- Browser scenario PASS with screenshots.
- BFF route log and DTO schema validation.
- Runtime-backed run/inspect report.
- Browser denylist proving no direct Core/runtime store access.
- No False Green and redaction scans.

Evidence entry:

- `docs/design/V12-V15.x/evidence/pv17-product-closed-loop/`
- `docs/design/V12-V15.x/reports/pv17_product_closed_loop_acceptance_report.json`
- `docs/design/V12-V15.x/reports/pv17_stage_execution_plan.md`
- `docs/design/V12-V15.x/reports/pv17_prd_architecture_audit_closure.md`

Best when:

- The priority is a visible product experience or OPC demo.

### Path B - Platform External App Contract

Goal: turn existing SDK / BFF / template / reference app assets into a coherent external app integration stage.

Implementation outline:

- Freeze a protocol version and method/event/error registry subset for external apps.
- Validate Python and TypeScript SDK clients against real Gateway RPC.
- Harden capability token / scope binding / auth denial behavior.
- Make BFF templates and reference app run through documented smoke tests.
- Document compatibility and migration guarantees.

Acceptance:

- Python SDK smoke PASS.
- TypeScript SDK build/test PASS.
- Minimal and full BFF template smoke PASS.
- Reference app E2E PASS.
- Auth/scope negative fixtures PASS.
- Redaction and No False Green scans.

Best when:

- The priority is adoption by other apps, developers or partners.

### Path C - Business Pack Productization

Goal: choose one business domain and move it from reference/stub/planning status toward a productized workflow.

Recommended order:

1. Knowledge, because it already has data_service MCP and citation artifacts.
2. Meeting, because it already has real-audio reference validation but depends on adjacent services.
3. Video Studio, if the next goal is creative workflow planning before real rendering.
4. Interview, if the target is lower-risk OPC service packaging.
5. Investment only after stronger risk, citation, compliance and human-review boundaries.

Implementation outline:

- Define one user-facing workflow with inputs, outputs, quality gates and handoff.
- Keep domain code inside Pack / Connector / RuntimeAdapter boundaries.
- Add E2E sample data, artifact lineage, trace, audit and failure recovery.
- Add business quality evaluation only after platform evidence is stable.

Acceptance:

- Domain E2E PASS with deterministic fixtures.
- Artifact lineage and trace coverage.
- Policy / approval negative cases.
- Human-readable report and failure explanation.
- No Core/Gateway business special-case added.

Best when:

- The priority is OPC commercialization or one vertical product.

### Path D - Production Governance Hardening

Goal: close the platform gaps needed before any production-readiness discussion.

Implementation outline:

- Tenant isolation and auth policy hardening.
- Credential lifecycle, secret redaction and revocation.
- Audit retention, export and incident timelines.
- Deployment runbooks, health checks, rollback and smoke automation.
- CI matrix for default regression and explicit integration tests.

Acceptance:

- Tenant isolation denial fixtures.
- Credential rotation/revocation evidence.
- Audit export and incident timeline evidence.
- Deployment smoke with rollback notes.
- CI default suite and explicit integration suite documented.

Best when:

- The priority is enterprise, self-hosting or compliance-heavy deployment.

## 4. Recommended Sequence

1. Restore local validation environment.
2. Run lightweight smoke for API, CLI, Pack Registry, Meeting assembly and Knowledge assembly.
3. Treat PV17 as complete for bounded review only.
4. Select the next stage from Path B, Path C or Path D with a new PRD / architecture / acceptance plan.
5. Keep unrelated backlogs out of the selected next stage unless explicitly replanned.

## 5. No-Go

- Do not claim HarnessOS is production ready.
- Do not claim Xpert parity complete.
- Do not claim product-grade frontend complete.
- Do not claim complete Workflow Studio ready.
- Do not claim Agent executor ready.
- Do not treat docs, screenshots, content images or presentation pages as runtime / BFF / DTO / browser E2E / production evidence.
