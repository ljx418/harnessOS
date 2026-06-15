# V10 Milestone Roadmap

## Purpose

This roadmap maps V10 implementation milestones to user-facing capability,
evidence scope, allowed claims and exit gates.

## Milestones

| Milestone | Stage | Capability | Evidence Scope | Allowed Claim |
| --- | --- | --- | --- | --- |
| M0 | V10-0R | CLI-native planning correction | planning + concept evidence | V10-0R complete: CLI-native TUI experience planning correction ready for review. |
| M1 | V10-1 | Terminal shell and composer | real TUI screenshot + component tests | V10-1 complete: CLI-native Mission TUI shell ready for review. |
| M2 | V10-2 | Tool, permission and plan blocks | fixture render + negative permission tests | V10-2 complete: terminal tool, permission and plan blocks ready for review. |
| M3 | V10-3 | Workflow/station explainability blocks | V9 scenario fixture render | V10-3 complete: workflow explainability inline blocks ready for review. |
| M4 | V10-4 | Output, quality and artifact preview | station output and quality evidence refs | V10-4 complete: station output preview and quality view ready for review. |
| M5 | V10-5 | WorkflowDiff modification preview | proposal-first evidence | V10-5 complete: workflow modification proposal preview ready for review. |
| M6 | V10-6 | HTML explainer export | generated HTML audit package | V10-6 complete: evidence explainer generator ready for review. |
| M7 | V10-7 | Read-model UX acceptance | scenario matrix + screenshots + scans + local-parser boundary | V10-1..V10-7 complete: CLI-native read-model TUI experience baseline ready for review. |
| M8 | V10-8 | Agent-backed chatbot bridge | Gateway session/turn evidence + terminal screenshots + trace | V10-8 complete: Agent-backed Mission TUI chatbot bridge ready for review. |
| M9 | V10-9 | Final V10 UX acceptance | V10-1..V10-8 evidence aggregation | V10 complete: CLI-native Agent-backed TUI experience and explainability baseline ready for review. |

## Exit Gates

- M1 cannot pass without real TUI screenshots; concept images do not count.
- M2 cannot pass if forbidden reasons are hidden.
- M3 cannot pass if station/Agent blocks lack evidence refs.
- M4 cannot pass if quality status is report-only without linked evidence.
- M5 cannot pass if WorkflowDiff is auto-applied.
- M6 cannot pass if HTML explainer is described as the primary TUI.
- M7 cannot be used as final V10 completion without V10-8 Agent-backed
  evidence.
- M8 cannot pass from fixture-only/local-parser evidence; it requires Gateway
  `turn.started` plus `turn.completed` or explicit failure evidence.
- M9 cannot pass with forbidden claims, redaction failures or missing user
  scenario evidence.

## Forbidden Final Interpretations

- production ready
- full production GA
- complete Workflow Studio ready
- Agent executor ready
- Agent-backed chatbot ready without Gateway turn evidence
- full multi-Agent orchestration ready
- unrestricted terminal worker ready
- autonomous workflow editing ready
