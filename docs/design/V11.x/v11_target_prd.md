# V11 Target PRD: Real-Time Explainable Mission TUI

## Product Goal

V11 turns the current V10 terminal renderer into a practical interactive
workflow front end. The experience should feel closer to Codex CLI and Claude
Code: immediate input feedback, live event streaming, visible tool execution,
clear permission prompts, inspectable context, workflow state timeline and
quality/evidence previews.

The user should understand what HarnessOS is doing while it is doing it, not
only after a report has been generated.

## Target Users

- Local users who want to create and observe workflows from a terminal.
- Reviewers who need to audit station output, quality checks and evidence.
- Power users who expect keyboard-first interaction and transparent tool use.
- Developers validating HarnessOS runtime behavior with real evidence.

## Target User Experience

At the end of V11, a user can:

1. Start the Mission TUI and see a compact status line with workspace, model,
   provider mode, sandbox, session, turn, evidence status and live phase.
2. Type a natural-language goal and see the message appear immediately.
3. Watch live events stream into the terminal: thinking/assistant output,
   tool start, tool result, permission request, station progress and errors.
4. See a workflow state timeline:
   `GoalCaptured -> IntentCaptured -> SpecDrafted -> DiffReady ->
   AwaitingConfirmation -> Running -> EvidenceRecorded`.
5. Inspect each station/Agent block for role, goal, memory summary, tools,
   skills, MCP refs, output preview, quality result and evidence refs.
6. Review a WorkflowDiff proposal with confirm/revise/reject actions before any
   durable mutation.
7. Use slash commands and keyboard shortcuts to inspect `/help`, `/status`,
   `/stations`, `/evidence`, `/diff`, `/trace`, `/quality`, `/artifacts` and
   `/explain`.
8. Open a generated HTML explainer for rich media and audit review, while the
   terminal remains the primary operating surface.

## Required Architectural Experience

V11 must make the architecture visible through the product experience. A user
should not need to read developer documentation to understand the current
workflow state.

| Experience Question | Required UI Answer |
| --- | --- |
| What is the system doing now? | Status line and timeline show current phase, session, turn and provider mode. |
| Which Agent or station owns this output? | Station/Agent inspector shows role, goal, tools, skills, MCP refs and evidence. |
| Why is an action blocked or waiting? | Permission block shows risk, sandbox, policy/capability decision and forbidden reason. |
| What evidence proves this result? | Evidence preview shows scoped refs, runtime report, quality report and redaction status. |
| Can this change mutate the workflow? | WorkflowDiff actions show confirm/revise/reject only; no auto apply/publish/run. |
| Is this real runtime or fixture evidence? | Every scenario and report shows evidence_scope and provider/runtime backing. |

## Required User Scenarios

| Scenario | Target Experience | Required V11 Evidence |
| --- | --- | --- |
| Multi-Agent discussion | User asks for multiple roles to discuss a topic for several rounds; TUI shows round progress, persona stations and synthesis Agent. | Real or fixture-backed orchestration evidence, visible round timeline, final synthesis refs. |
| Video storyboard workflow | User gives a creative idea; TUI shows storyboard planning, image artifact refs, quality Agent checks and evidence links. | Storyboard artifact refs, quality report refs, style/character consistency checks. |
| Coding proposal workflow | User asks for a code change; TUI shows plan, diff proposal, sandboxed tests and review handoff. | Diff preview, test result, no auto commit/push/deploy evidence. |
| Local document workflow | User asks to summarize local Markdown docs; TUI shows scan progress, summaries, quality and evidence refs. | Document read evidence and summaries; no raw file content leakage. |
| Workflow revision | User asks to optimize a workflow; TUI produces WorkflowDiff and waits for confirmation. | Confirm/revise/reject visible; no auto apply/publish/run. |
| Failure recovery | Provider or tool fails; TUI shows error, retry/revise options and trace. | Failure block, trace ref, no silent failure. |

## Boundaries

V11 must not claim:

- production readiness,
- Agent executor readiness,
- complete Workflow Studio,
- full multi-Agent orchestration readiness,
- unrestricted terminal worker,
- autonomous workflow editing,
- exact Codex/Claude Code parity.

V11 may use V9 runtime fixture evidence and V10 provider-backed Gateway turn
evidence, but every evidence item must keep its evidence scope visible.

## Architecture Acceptance Requirements

- V11 must implement a visible state model, not just a static transcript.
- V11 must keep the TUI as display/proposal/confirmation surface, not runtime
  truth.
- V11 must expose Agent/Station role, goal, context summary, tools, skills and
  evidence refs for user inspection.
- V11 must expose tool lifecycle, risk, sandbox, permission and failure state.
- V11 must separate terminal runtime UX evidence from supporting HTML reports
  and concept images.
