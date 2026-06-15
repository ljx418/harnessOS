# HarnessOS V11.x Canonical Index

Current V11 baseline:

- V10 is accepted only as: CLI-native Agent-backed TUI experience and
  explainability baseline ready for review.
- V10 does not prove production ready, Agent executor ready, complete Workflow
  Studio ready, full multi-Agent orchestration ready, or Codex/Claude Code
  parity.
- V11 focuses on a real-time, CLI-first user experience that narrows the gap
  with Codex CLI and Claude Code while preserving HarnessOS governed runtime
  boundaries.

Allowed V11 planning claim:

V11 planning complete: real-time explainable Mission TUI development package ready for review.

Allowed future V11 final claim:

V11 complete: real-time explainable Mission TUI interaction baseline ready for review.

Forbidden interpretations:

- production ready
- full production GA
- Agent executor ready
- complete Workflow Studio ready
- full multi-Agent orchestration ready
- autonomous workflow editing ready
- unrestricted terminal worker ready
- production terminal automation ready
- Codex/Claude Code parity complete

## Canonical Documents

- `v11_target_prd.md`
- `v11_target_architecture.md`
- `v11_architecture_contract.md`
- `v11_stage_implementation_specs.md`
- `v11_development_and_acceptance_plan.md`
- `v11_milestone_roadmap.md`
- `v11_acceptance_gate.md`
- `v11_current_gap_analysis.md`
- `v11_current_gap_analysis.drawio`
- `v11_no_false_green_claim_guard.md`
- `v11_document_audit.md`

## Current Decision

V11 should improve the user-facing Mission TUI before expanding product claims.
V11-0 architecture contract evidence is PASS.
V11-1 Real-Time TUI Event Stream is ready for review with provider-backed CLI
turn evidence.
V11-2 Composer, Slash Commands And Keyboard UX is ready for review with
non-mutating TUI command transcript evidence.
V11-3 Workflow State Timeline is ready for review with bounded
`tui_read_model_fixture` timeline evidence.
V11-4 Station/Agent Inspector is ready for review with V9 evidence projection.
V11-5 Tool Execution And Permission Blocks is ready for review with visible
risk, sandbox, denial and forbidden-reason evidence.
V11-6 Output, Quality And Evidence Preview is ready for review with artifact,
quality and evidence refs and redaction PASS.
V11-7 HTML Explainer From Live Session is ready for review as supporting-only
HTML with Playwright screenshot evidence.
V11-8 User Scenario End-To-End Validation is ready for review with six scenario
PASS results.
V11-9 Final Acceptance is PASS.

Current allowed final claim:

V11 complete: real-time explainable Mission TUI interaction baseline ready for review.

## Architecture Review Focus

The V11 architecture must be reviewed as a multi-plane system, not as a simple
terminal skin:

- Mission TUI Interaction Plane
- Conversation And Command Plane
- Gateway Session/Turn Plane
- Event Stream And State Projection Plane
- Workflow/Station/Agent Projection Plane
- Tool, Permission And Policy Visibility Plane
- Artifact, Quality And Evidence Review Plane
- Governance, Acceptance And Claim Guard Plane

`v11_architecture_contract.md` is the implementation-facing architecture
contract. It defines required interfaces, entity ownership, runtime truth
boundary and evidence contract that V11 stages must preserve.
