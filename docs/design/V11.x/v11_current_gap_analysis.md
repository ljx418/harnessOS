# V11 Current Gap Analysis

## Baseline

V10 complete: CLI-native Agent-backed TUI experience and explainability baseline
ready for review.

This means HarnessOS has a bounded TUI baseline with provider-backed Gateway
turn evidence, not a finished Codex/Claude Code quality workbench.

## Gap Table

| Area | Current V10 | V11 Target | Gap Severity |
| --- | --- | --- | --- |
| Architecture clarity | Goal surface exists, but roles/planes/entities are under-specified | Multi-plane architecture contract with owners, entities, boundaries and evidence requirements | P0 |
| Input feedback | User input recorded, but experience can feel delayed | Immediate user message plus running state | P0 |
| Streaming | Completed turn rendered after result | Live assistant/tool/workflow events | P0 |
| State machine | Single phase line | Full workflow timeline | P0 |
| Commands | `/session` and `/trace` plus local commands | Discoverable slash command system | P1 |
| Tool visibility | Tool blocks exist as render shape | Live tool lifecycle with risk/sandbox/result | P0 |
| Permission UX | Permission block render exists | Real allow/deny/revise interaction path | P1 |
| Station explainability | Agent role/goal/tools/evidence visible | Inspector with memory/context/attempt/quality | P1 |
| Output preview | Artifact and quality refs visible | Preview navigation and quality detail | P1 |
| HTML report | Supporting reports exist | Export from live session data | P2 |
| Evidence trust | Improved after V10 full validation | Every scenario classified by evidence scope | P0 |

## Current Risks

- A static report may be mistaken for runtime UX.
- Provider-backed single-turn evidence may be overread as full workflow runtime.
- Fixture-backed station views may be overread as live Agent execution.
- Terminal screenshots can be polluted if not window-scoped or Playwright-rendered.

## Required Remediation

- Freeze `v11_architecture_contract.md` before treating V11 as implementation
  ready.
- Keep plane ownership and runtime truth boundary visible in docs and drawio.
- Build V11 event stream before expanding claims.
- Keep evidence scope visible in every report.
- Use Playwright screenshots of generated reports and controlled terminal renders,
  not arbitrary desktop screenshots.
- Treat HTML as supporting audit surface.

## Architecture Gap Closure Criteria

- Drawio includes architecture planes, current-vs-target gap, entity model,
  event/data flow, milestones and exit gates.
- PRD, architecture, development plan and acceptance gate all reference the
  same runtime boundary: TUI display truth only.
- Core entities have owner plane, fields and evidence requirements.
- Tool/permission/evidence ownership is explicit enough for implementation and
  external audit.
