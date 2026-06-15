# V12-V15 Milestone Roadmap

| Milestone | Stage | User-Visible Outcome | Evidence Scope | Exit Gate |
| --- | --- | --- | --- | --- |
| M12-A | V12 | User opens onboarding/product shell and sees frontend/API health | browser + health evidence | Product entry PASS |
| M12-0A | V12 | User reviews top bar, navigation, canvas, node card, inspector and Chat Workbench as component sketches before full Figma | component sketches + HTML report + human decisions | Component prototype review PASS |
| M12-P | V12 | User reviews the intended browser shell, read-only canvas, inspector, Chat Workbench and evidence drawer in Figma before implementation | Figma URL + prototype review evidence | Figma prototype review PASS |
| M12-B | V12 | User sees real workspaces, projects and station-agent profiles | entity + BFF evidence | Product entity foundation PASS |
| M12-C | V12 | User opens a read-only browser canvas shell with entity sidebar and selected-node inspector | canvas DTO + browser screenshot + BFF network evidence | Canvas foundation PASS |
| M12-D | V12 | User discusses a goal in Chat Workbench and sees proposal timeline | transcript + proposal evidence | Workbench foundation PASS |
| M12-Q | V12 | User sees a product shell that has coherent hierarchy, readable node cards, shared components and responsive behavior | screenshots + component inventory + human UX review | Product polish hardening PASS |
| M12-I | V12 | User clicks/selects/tries disabled canvas actions and receives visible feedback or reasons | Playwright action log + DTO snapshots + disabled reason screenshot | Interaction depth foundation PASS |
| M13-A | V13 | User builds workflow visually and reviews WorkflowDiff | browser E2E + schema evidence | Studio canvas PASS |
| M13-B | V13 | User inspects Agent/station/tool/evidence nodes from the graph | inspector + schema evidence | Visual DSL inspector PASS |
| M13-C | V13 | User adds, configures, moves, connects and auto-layouts graph nodes with validation feedback | graph action trace + round-trip + WorkflowDiff evidence | Canvas interaction loop PASS |
| M14 | V14 | User installs approved plugins/skills/tools and binds them to Agents | plugin lifecycle evidence | Extension ecosystem PASS |
| M15-A | V15 | User reviews traces/metrics/audit/incident evidence | ops + dashboard evidence | Observability dashboard PASS |
| M15-B | V15 | User self-hosts and completes one browser workflow smoke | compose + health + runtime evidence | Deployment smoke PASS |
| M15-C | V15 | User completes final Xpert-inspired scenario matrix | scenario matrix | Xpert-level frontend interaction baseline ready for review |
| M15-D | V15 | User and reviewer can audit interaction quality from automated UX checks plus human review checklist | Playwright + screenshot + network + human review evidence | Interaction experience PASS |
| M15-E | V15 | User completes Xpert-inspired experience review without overclaiming parity | scenario matrix + product polish review + claim scan | Xpert-inspired baseline review PASS |

## Dependency Rules

- V13 cannot start implementation until V12 entity schemas and BFF routes pass.
- V12 Figma prototype freeze cannot start until V12-0A component prototype
  review passes.
- V12 browser UI implementation evidence cannot be accepted until the V12 Figma
  prototype review has passed.
- V13 cannot start implementation until V12 read-only canvas foundation passes.
- V13 editable canvas interaction work cannot claim PASS until V12-Q product
  polish and V12-I interaction depth evidence exist or are explicitly accepted
  as bounded non-blocking.
- V13 cannot claim Studio readiness until a WorkflowSpecGraph round-trip and
  browser denylist evidence exist.
- V14 plugin runtime work cannot start until V12 scopes and policies exist.
- V15 final review cannot run until V12, V13 and V14 evidence packages exist.
- V15 deployment smoke cannot pass unless browser-visible frontend/API health
  and at least one confirmed workflow smoke pass.
- V15 final interaction baseline cannot pass unless automated UX checks and
  human UX review both pass or have accepted bounded PARTIAL.
- V15 final interaction baseline cannot pass from the current engineering
  prototype alone; it needs product polish, interaction trace and scenario
  evidence.
- No stage may claim Xpert parity complete.
- No stage may count Figma prototype screens as runtime evidence.
- No stage may count component sketches or HTML prototype reports as runtime
  evidence.
