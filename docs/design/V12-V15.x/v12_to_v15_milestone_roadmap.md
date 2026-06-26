# V12-V15 Milestone Roadmap

| Milestone | Stage | User-Visible Outcome | Evidence Scope | Exit Gate |
| --- | --- | --- | --- | --- |
| V12-GA | V12 | User opens onboarding/product shell and sees frontend/API health | browser + health evidence | Product entry PASS |
| V12-G0A | V12 | User reviews top bar, navigation, canvas, node card, inspector and Chat Workbench as component sketches before full Figma | component sketches + HTML report + human decisions | Component prototype review PASS |
| V12-GP | V12 | User reviews the intended browser shell, read-only canvas, inspector, Chat Workbench and evidence drawer in Figma before implementation | Figma URL + prototype review evidence | Figma prototype review PASS |
| V12-G0P | V12 | User reviews the Gemini-generated V12-0P Light Studio prototype with local CSS and V12 naming preserved | optimized prototype + static render + validation report | Design-only prototype review PASS for bounded review |
| V12-GR | V12 | User opens the HarnessOS V12 read-only workbench and sees BFF-shaped real data for workspace, project, app, station agents, canvas and inspector | BFF route log + browser network log + schema validation + screenshot | Current read-only real-data gate PASS for bounded review |
| V12-GB | V12 | User sees real workspaces, projects and station-agent profiles | entity + BFF evidence | Product entity foundation PASS |
| V12-GC | V12 | User opens a read-only browser canvas shell with entity sidebar and selected-node inspector | canvas DTO + browser screenshot + BFF network evidence | Canvas foundation PASS |
| V12-SD | V12 | User discusses a goal in Chat Workbench and sees proposal timeline | transcript + proposal evidence | Workbench foundation PASS |
| V12-SQ | V12 | User sees a product shell that has coherent hierarchy, readable node cards, shared components and responsive behavior | screenshots + component inventory + human UX review | Product polish hardening PASS |
| V12-SI | V12 | User clicks/selects/tries disabled canvas actions and receives visible feedback or reasons | Playwright action log + DTO snapshots + disabled reason screenshot | Interaction depth foundation PASS |
| V12-SA | V12 | User and reviewer see V12 evidence reconciled into one bounded exit decision | aggregate manifest + validator report + claim scan | V12 bounded baseline PASS |
| V13-R0 | V13 | Reviewer sees V13 readiness audit closed before implementation | readiness audit + document support evidence | V13 implementation entry PASS |
| V13-S1 | V13 | User loads WorkflowSpecGraph and sees graph validation pass/fail evidence | graph DTO + validation + BFF route log | Graph schema/BFF PASS |
| V13-S2 | V13 | User adds, moves, connects and configures nodes in the browser Studio pilot | browser action log + screenshots + inspector evidence | Editable canvas pilot PASS |
| V13-S3 | V13 | User reviews WorkflowDiff and confirms handoff without publish/run | WorkflowDiff + confirmation transcript | WorkflowDiff handoff PASS |
| V13-SA | V13 | Reviewer sees V13 evidence reconciled into one bounded exit decision | acceptance data + artifact manifest + claim scan | V13 bounded pilot PASS |
| V14-R0 | V14 | Reviewer sees V14 manifest, compatibility, scope and unsafe-denial plan accepted | readiness audit + PRD/architecture review | V14 implementation entry PASS |
| V14-S1 | V14 | User inspects plugin/skill/tool/MCP manifests and compatibility decisions | schema evidence + DTO samples + negative fixtures | Manifest and compatibility PASS |
| V14-S2 | V14 | User scopes approved capability to selected workspace/Agent/Station | browser screenshot + BFF route log + scoped activation refs | Scoped activation PASS |
| V14-S3 | V14 | User sees unsafe package denied with visible reason and audit ref | denial fixture + audit log + redaction scan | Unsafe denial PASS |
| V14-SA | V14 | Reviewer accepts governed extension ecosystem pilot | acceptance data + artifact manifest + claim scan | Extension ecosystem pilot PASS |
| V15-R0 | V15 | Reviewer sees observability/deployment schemas, smoke contract and final matrix accepted | readiness audit + PRD/architecture review | V15 implementation entry PASS |
| V15-S1 | V15 | Operator reviews trace, metrics, audit and incident evidence in browser | dashboard screenshot + DTOs + route log | Operations evidence dashboard PASS |
| V15-S2 | V15 | Operator self-hosts locally and sees health/smoke output | command output + health checks + smoke result | Deployment smoke PASS |
| V15-S3 | V15 | Reviewer completes product console, Studio, extension, observability and deployment scenarios | Playwright logs + screenshots + human UX review | Final scenario matrix PASS |
| V15-SA | V15 | Reviewer accepts final V12-V15 interaction baseline without overclaiming | evidence map + claim-to-evidence matrix + scans | Frontend interaction baseline ready for review |
| PV16-R0 | PV16 | Reviewer selects product-runtime hardening scope and sees readiness risks before implementation | post-V15 plan + PRD/architecture audit + schema/runner plan | PV16 implementation entry PASS |
| PV16-S1 | PV16 | User creates or updates product entities through BFF-only routes and sees audit refs | entity CRUD report + route/network logs + negative policy fixtures | Durable entity hardening PASS |
| PV16-S2 | PV16 | User confirms a WorkflowSpec run and inspects runtime-backed progress, outputs and evidence refs | runtime event log + trace/artifact/quality refs + screenshots | Runtime run/inspect pilot PASS |
| PV16-S3 | PV16 | Operator starts a documented local/self-host profile and completes smoke with command output | smoke output + health report + redaction scan | Self-host hardening smoke PASS |
| PV16-S4 | PV16 | Reviewer follows setup, Studio, run review and operations as one coherent product journey | UX matrix + screenshots + accessibility notes + human review | Product-runtime journey PASS |
| PV16-SA | PV16 | Reviewer accepts product-runtime hardening pilot without production or Xpert overclaims | acceptance data + artifact manifest + claim scan + redaction scan | Product-runtime hardening pilot ready for review |
| PV17-R0 | PV17 | Reviewer sees product closed loop PRD, target architecture, development plan, milestone roadmap, acceptance gate and drawio before implementation | PV17 docs + drawio + claim scan | PV17 documentation gate retained as audit trace |
| PV17-E0 | PV17 | Developer restores local Python validation before implementation | API/CLI/pack smoke output | Local validation entry PASS |
| PV17-S1..SA | PV17 | User follows one mainline setup -> Product Console -> Mission Studio -> confirm run -> inspect -> evidence path | browser E2E + BFF route log + DTO snapshots + runtime inspect + evidence package | PV17 bounded product closed loop review PASS |

## Execution Naming Migration

The project no longer uses `M12-*`, `M13-*`, `M14` or `M15-*` as executable
milestone names because that format is easy to confuse with the V12-V15
version/stage labels. Historical mentions map to the current names as follows:

| Former Name | Current Name | Meaning |
| --- | --- | --- |
| M12-A | V12-GA | Product entry gate. |
| M12-0A | V12-G0A | Component prototype gate. |
| M12-P | V12-GP | Figma or high-fidelity prototype gate. |
| M12-0P-G | V12-G0P | Gemini optimized V12-0P prototype gate. |
| M12-C1 | V12-GR | Read-only real-data workbench gate. |
| M12-B | V12-GB | Product entity foundation gate. |
| M12-C | V12-GC | Canvas foundation gate. |
| M12-D | V12-SD | Chat to WorkflowDiff development substage. |
| M12-I | V12-SI | Interaction depth development substage. |
| M12-Q | V12-SQ | Product polish development substage. |
| M12-AGG | V12-SA | V12-SA aggregate evidence reconciliation. |
| M13-A | V13-R0/V13-S1 | V13 readiness and graph schema/BFF entry. |
| M13-B | V13-S2 | V13 editable canvas pilot. |
| M13-C | V13-S3/V13-SA | V13 WorkflowDiff handoff and aggregate acceptance. |
| M14 | V14-R0/V14-S1/V14-S2/V14-S3/V14-SA | V14 governed extension ecosystem pilot. |
| M15-A | V15-R0/V15-S1 | V15 readiness and operations evidence dashboard. |
| M15-B | V15-S2 | V15 deployment smoke. |
| M15-C | V15-S3 | V15 final scenario matrix. |
| M15-D | V15-SA | V15 final interaction baseline acceptance. |

## Dependency Rules

- V13 cannot start implementation until V12 entity schemas and BFF routes pass.
- V12 Figma prototype freeze cannot start until V12-0A component prototype
  review passes.
- V12 browser UI implementation evidence cannot be accepted until the V12 Figma
  prototype review has passed.
- V13 cannot start implementation until V12 read-only canvas foundation passes.
- V12-GR can support bounded review of the current workbench foundation, but it
  does not by itself satisfy the V12 bounded exit claim until V12-SD, V12-SI,
  V12-SQ and V12-SA evidence are reconciled.
- V13 editable canvas interaction work cannot claim PASS until V12-SQ product
  polish and V12-SI interaction depth evidence exist or are explicitly accepted
  as bounded non-blocking.
- V13 cannot claim Studio readiness until a WorkflowSpecGraph round-trip and
  browser denylist evidence exist.
- V14 plugin runtime work cannot start until V12 scopes and policies exist.
- V15 final review cannot run until V12, V13 and V14 evidence packages exist;
  this dependency is now satisfied for bounded V15-SA evidence.
- V15 deployment smoke cannot pass unless browser-visible frontend/API health
  and bounded local smoke output pass.
- V15 final interaction baseline cannot pass unless automated UX checks and
  human UX review both pass or have accepted bounded PARTIAL.
- V15 final interaction baseline cannot pass from the current engineering
  prototype alone; it needs product polish, interaction trace and scenario
  evidence.
- PV16 bounded pilot review is complete because post-V15 PRD/architecture
  audit, schemas, runner, route-boundary contracts and real PV16 evidence exist
  with no open fatal or major findings, and the post-V15 acceptance runner
  passes.
- PV16 cannot claim production readiness, complete Workflow Studio readiness,
  Agent executor readiness, Xpert parity or product-grade frontend completion.
- PV17 bounded review is complete because formal `/bff/pv17/*` routes, DTOs,
  browser E2E evidence, runtime inspect DTOs, evidence package and acceptance
  report exist for the bounded product closed loop scenario.
- PV17 cannot claim production readiness, complete Workflow Studio readiness,
  Agent executor readiness, Xpert parity or product-grade frontend completion.
- No stage may claim Xpert parity complete.
- No stage may count Figma prototype screens as runtime evidence.
- No stage may count component sketches or HTML prototype reports as runtime
  evidence.
