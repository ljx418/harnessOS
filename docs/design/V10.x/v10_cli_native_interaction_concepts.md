# V10 CLI-Native Interaction Concepts

## Purpose

This document defines the concrete interaction concepts for the V10 Mission TUI.
It supersedes cockpit/dashboard-first visual direction and keeps the experience
close to practical terminal agents such as Codex CLI and Claude Code.

## Interaction Principles

- One primary transcript stream. Panels are secondary and optional.
- The bottom composer is always visible unless a modal permission prompt owns
  focus.
- Every tool call, permission request, station output and WorkflowDiff proposal
  is rendered as a bounded terminal block.
- Slash commands teach the product without forcing users to read docs first.
- HTML explainers are export/audit artifacts; they are not the primary TUI.
- Concept images are planning evidence only. V10-1 and later require real TUI
  screenshots.

## Core Screens

| Screen | User Intent | Required Blocks | Acceptance |
| --- | --- | --- | --- |
| Message Stream | Enter a goal and watch the assistant respond | status line, user message, assistant stream, plan/todo, composer | 80x24 readable; composer visible |
| Command Palette | Learn what can be done | slash command list, short descriptions, keyboard hints | `/new`, `/plan`, `/stations`, `/evidence`, `/diff`, `/help` visible |
| Tool Permission | Decide whether a tool can run | tool preview, risk, sandbox, evidence ref, allow/deny | forbidden reason visible; deny does not mutate |
| Station Preview | Review a station result | Agent role, goal, output preview, quality, artifact/evidence refs | station output cannot lack evidence refs |
| WorkflowDiff Review | Modify workflow safely | natural language request, affected stations, diff summary, policy decision, confirm/revise/reject | proposal-first; no auto apply |

## Minimum Keyboard Model

| Key | Behavior |
| --- | --- |
| `enter` | submit composer or expand selected block |
| `esc` | close palette/details/modal |
| `ctrl+p` | open plan/todo block |
| `ctrl+e` | open evidence refs for selected block |
| `ctrl+d` | quit session |
| `/` | open slash command palette when composer is empty |
| `c` | confirm a selected proposal only when confirmation is available |
| `r` | revise a selected proposal |
| `x` | reject a selected proposal |

## Safety Boundaries

- The TUI reads projections; it does not own runtime truth.
- The TUI may request confirmation or create proposal objects.
- The TUI must not directly write WorkflowDraft / WorkflowVersion /
  WorkflowInstance / StationRun / Artifact.
- source=agent must not directly perform durable mutation.
- Confirmation UI must show risk, policy decision, affected targets and
  evidence refs before accepting.

## Concept Evidence

The V10-0R report must include these planning artifacts:

- `concept-terminal-message-stream.svg`
- `concept-command-palette-onboarding.svg`
- `concept-tool-permission-blocks.svg`
- `concept-station-output-preview.svg`
- `concept-workflowdiff-review.svg`
- `prompt-terminal_message_stream.md`
- `prompt-command_palette_onboarding.md`
- `prompt-tool_permission_blocks.md`
- `prompt-station_output_preview.md`
- `prompt-workflowdiff_review.md`
