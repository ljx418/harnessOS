# V11 Development And Acceptance Plan

## Stage Order

| Stage | Name | Status | Exit Claim |
| --- | --- | --- | --- |
| V11-0 | Planning, Architecture Contract And Boundary Freeze | complete / ready for review | V11-0 complete: real-time Mission TUI architecture planning gate ready for review. |
| V11-1 | Real-Time TUI Event Stream | complete / ready for review | V11-1 complete: real-time TUI event stream slice ready for review. |
| V11-2 | Composer, Slash Commands And Keyboard UX | complete / ready for review | V11-2 complete: Mission TUI command interaction slice ready for review. |
| V11-3 | Workflow State Timeline | complete / ready for review | V11-3 complete: workflow state timeline slice ready for review. |
| V11-4 | Station/Agent Inspector | complete / ready for review | V11-4 complete: station and Agent explainability inspector ready for review. |
| V11-5 | Tool Execution And Permission Blocks | complete / ready for review | V11-5 complete: transparent tool and permission block slice ready for review. |
| V11-6 | Output, Quality And Evidence Preview | complete / ready for review | V11-6 complete: output quality and evidence preview slice ready for review. |
| V11-7 | HTML Explainer From Live Session | complete / ready for review | V11-7 complete: live-session explainer export ready for review. |
| V11-8 | User Scenario End-To-End Validation | complete / ready for review | V11-8 complete: V11 user scenario validation package ready for review. |
| V11-9 | Final Acceptance | complete / ready for review | V11 complete: real-time explainable Mission TUI interaction baseline ready for review. |

## Stage Acceptance

Detailed implementation inputs, outputs, fixtures and stop conditions are
defined in `v11_stage_implementation_specs.md`.

| Stage | Development Focus | Required Evidence |
| --- | --- | --- |
| V11-0 | Freeze architecture planes, roles, entities, event/data flow and runtime boundary | `v11_architecture_contract.md`, updated drawio, document audit, XML validation |
| V11-1 | Stream Gateway/tool/workflow events into TUI without silent waits | CLI transcript showing live phase changes and event blocks; failed turn is visible and cannot pass as completed |
| V11-2 | Slash commands, input history, command help, visible shortcuts | `/help`, `/status`, `/stations`, `/evidence`, `/diff`, `/trace` evidence; invalid command error visible |
| V11-3 | Workflow state timeline | Timeline shows goal/spec/diff/confirmation/run/evidence states; no durable mutation before confirmation |
| V11-4 | Station/Agent inspector | Agent role, goal, memory summary, tools, skills, MCP refs, attempt and evidence visible |
| V11-5 | Tool and permission lifecycle | tool started/completed/failed, risk, sandbox, permission prompt and forbidden reason visible |
| V11-6 | Output/quality/evidence preview | artifact refs, quality refs, evidence links visible; raw content not leaked |
| V11-7 | HTML explainer export | HTML generated from live-session data and marked supporting, not runtime truth |
| V11-8 | User scenarios | Multi-Agent discussion, video storyboard, coding proposal, local docs, revision and failure recovery scenarios PASS or bounded PARTIAL with reasons |
| V11-9 | Final acceptance | V11-1 through V11-8 evidence exists, No False Green PASS, redaction PASS, drawio XML valid |

## Required Commands

```bash
npm --prefix apps/mission-tui test
npm --prefix apps/mission-tui run start -- --agent-backed --model deepseek-chat
npm --prefix apps/mission-tui run acceptance:v11
npm --prefix apps/mission-tui run acceptance:v11-2
npm --prefix apps/mission-tui run acceptance:v11-3
npm --prefix apps/mission-tui run acceptance:v11-4
npm --prefix apps/mission-tui run acceptance:v11-5
npm --prefix apps/mission-tui run acceptance:v11-6
npm --prefix apps/mission-tui run acceptance:v11-7
npm --prefix apps/mission-tui run acceptance:v11-8
npm --prefix apps/mission-tui run acceptance:v11-final
./.venv/bin/python -m pytest tests/test_v11_*.py -q
xmllint --noout docs/design/V11.x/v11_current_gap_analysis.drawio
```

`acceptance:v11` covers V11-1. `acceptance:v11-2` covers V11-2.
`acceptance:v11-3` through `acceptance:v11-8` cover V11-3 through V11-8.
`acceptance:v11-final` covers V11-9 final acceptance.

## Architecture Pre-Implementation Checklist

V11-1 implementation should not start unless V11-0 has:

- architecture planes and owners frozen,
- core entity model frozen,
- Gateway/TUI/runtime truth boundary frozen,
- TUI event taxonomy frozen,
- evidence package requirements frozen,
- drawio XML valid,
- No False Green guard aligned with the architecture contract.

## Stop Conditions

- Architecture docs do not identify owner plane or mutation boundary for a core
  entity.
- TUI silently ignores user input.
- Running state is not visible while a turn or tool is active.
- `turn.failed` is counted as a completed turn.
- WorkflowDiff auto applies before user confirmation.
- source=agent performs direct durable mutation.
- Tool/permission block hides risk, sandbox or forbidden reason.
- Evidence preview leaks raw key, token, raw provider payload, raw artifact
  content or raw file content.
- HTML explainer is treated as runtime truth.
- V11 claims production ready, Agent executor ready, complete Workflow Studio or
  Codex/Claude Code parity.
