# V10 Target PRD: CLI-Native TUI Experience And Explainability

## Product Goal

V10 turns HarnessOS from a mostly evidence-rich backend/workflow system into a
user-facing terminal workbench that a real user can learn quickly. The primary
experience is a CLI-native chatbot TUI inspired by the interaction quality of
Codex CLI and Claude Code: single-column conversation stream, bottom composer,
clear tool blocks, visible permission prompts, compact state lines and live
Agent/Gateway turn state.

V10 must help users:

- create a workflow from natural language,
- chat with an Agent-backed front end instead of only browsing fixture/read
  models,
- observe workflow state and Agent/station progress,
- inspect station outputs and quality signals,
- understand why an action is available or forbidden,
- review evidence, runtime report, blueprint and diff links,
- propose workflow changes in natural language,
- confirm controlled handoffs without source=agent direct durable mutation.

## Target Users

- First-time local users who want to create and run a workflow from a terminal
  without reading the full architecture docs first.
- Workflow reviewers who need to inspect station output, quality checks and
  evidence quickly.
- Power users who prefer keyboard-first CLI interaction over browser dashboards.
- Developers validating HarnessOS workflows locally with real evidence packages.

## Target Experience

The V10 Mission TUI should feel like a practical CLI-native agent workbench:

- top status line: workspace, model/provider mode, permission mode, sandbox,
  evidence status and live phase,
- main stream: user messages, assistant output, plan/todo blocks, tool calls,
  station/Agent output blocks and errors,
- bottom composer: natural-language goals, slash commands and shortcut hints,
- inline expandable blocks: Agent role, goal, tools, skills, MCP refs, output
  preview, quality checks, evidence links and forbidden reasons,
- optional side rail only on wide terminals; it must not become the primary
  experience.
- Agent-backed bridge: user input is submitted to the existing Gateway
  `session.start` / `turn.start` path, and runtime events are rendered as TUI
  blocks.

User-facing copy is Simplified Chinese. Code identifiers and comments remain
English.

## End-State User Experience

At the end of V10, a user should be able to:

1. Start the Mission TUI and immediately see workspace, model, permission mode,
   sandbox and evidence status.
2. Type a natural-language goal such as "帮我把这个视频点子做成分镜工作流".
3. See the TUI move from `idle` to `submitting`, `agent_running`,
   `streaming` and `completed` or `failed`.
4. See a real Gateway/Agent response appear in the transcript, including
   session id, turn id and trace/evidence refs.
5. See a plan block and WorkflowSpec draft before any durable action happens.
6. Inspect station/Agent blocks as the workflow progresses.
7. Expand station output previews, quality results, artifact refs and evidence
   refs without leaving the terminal.
8. Ask for a workflow change in natural language and receive a WorkflowDiff
   proposal with confirm/revise/reject controls.
9. Export or open an HTML explainer only when richer media or audit review is
   needed.

## V10-0R Scope

V10-0R corrects the earlier cockpit-first concept direction. It produces:

- PRD and target architecture,
- stage plan and acceptance gates,
- current gap analysis and drawio,
- no false green guard,
- CLI-native concept prompts and concept SVGs,
- an HTML report comparing implementation options,
- explicit acceptance rules for real TUI screenshots in later stages.

V10-0R does not implement the runtime TUI.

## V10 Functional Slices

1. V10-0R CLI-Native TUI Planning Correction Gate
2. V10-1 React/Ink CLI-Native Mission Shell
3. V10-2 Tool / Permission / Plan Blocks
4. V10-3 Workflow Explainability Inline Blocks
5. V10-4 Station Output And Quality Preview
6. V10-5 Natural Language WorkflowDiff Preview
7. V10-6 Evidence HTML Explainer Generator
8. V10-7 User Onboarding And Read-Model UX Acceptance
9. V10-8 Agent-Backed Chatbot TUI Bridge

## User Scenario Acceptance

V10 must support these scenario families:

- First-run workflow creation: user enters a goal in the bottom composer and
  sees a plan block plus WorkflowSpec draft before any durable action.
- Workflow observation: the message stream shows current station, Agent role,
  status, tool activity and evidence links.
- Output review: expandable station blocks show output preview, quality status,
  artifact refs and quality evidence.
- Workflow modification: user asks for a change and receives a WorkflowDiff
  proposal, not an automatic mutation.
- Scenario replay: user can open an HTML explainer for Roman Forum, video
  storyboard, local markdown summary and coding proposal workflows, but the
  HTML page is supporting evidence rather than the primary TUI.

## Scenario-Specific Gates

| Scenario | Minimum User Flow | V10 Acceptance Gate |
| --- | --- | --- |
| Local Markdown Summary | User enters a folder-summary goal | TUI shows plan, document-read status, summaries, quality and evidence refs |
| Roman Forum Discussion | User asks multiple persona Agents to discuss a topic | TUI shows parallel station/Agent blocks and final synthesis evidence |
| Video Storyboard | User gives a creative idea | TUI shows storyboard station output, image/artifact refs and quality Agent checks |
| Coding Proposal | User asks for a code change | TUI shows diff proposal, sandboxed test result and no auto commit/push/deploy boundary |
| Workflow Revision | User asks to optimize a workflow | TUI shows WorkflowDiff proposal before any apply/publish/run action |
| Agent-Backed Chat | User sends a natural-language message | TUI shows Gateway session/turn state, assistant response, trace and runtime completion/failure |

## Boundaries

V10 does not prove:

- production ready,
- complete Workflow Studio,
- Agent executor ready,
- full multi-Agent orchestration ready,
- unrestricted terminal worker ready,
- autonomous workflow editing ready.

V10 also must not treat concept images or HTML reports as real TUI screenshots.
V10 must not treat fixture-only or local-parser proposal evidence as
Agent-backed runtime evidence.
