# V9-UA User Scenario Special Acceptance Audit

Current status: PASS-ready for review after regenerated evidence.

This document defines a special acceptance stage for the V9 user-visible
scenario gap found after final acceptance review. It does not add runtime
authority. It packages existing V9 runtime evidence into a human-auditable
acceptance report and tightens the visible scenario gates.

## Stage Scope

Stage id: V9-UA

Stage name: V9 User Scenario Acceptance Special Audit

Purpose:

- Make Roman Forum multi-Agent discussion evidence explicit and inspectable.
- Make parallel Agent orchestration evidence visible to humans.
- Make video storyboard workflow outputs, quality Agent checks, TUI screenshots,
  and workflow-state diagram available from one review page.
- Make natural-language optimization evidence linkable from the scenario matrix.
- Preserve V9 No False Green boundaries.

Allowed claim:

V9-UA complete: V9 user scenario acceptance package ready for review.

## Forbidden Claims / Boundary Interpretations

- Agent executor ready
- full multi-Agent orchestration ready
- autonomous coding workflow ready
- complete Workflow Studio ready
- production ready

## Target User Experience

After this stage, a reviewer can open one HTML page and answer:

- What can the project currently demonstrate for each V9 user scenario?
- Which scenarios are runtime-backed and which are aggregation-only?
- Where is the evidence for Roman Forum role-specific Agent discussion?
- Where is the evidence for parallel fan-out/fan-in Agent orchestration?
- Where are the video storyboard images, quality Agent report, TUI screenshots,
  and drawio workflow-state diagram?
- Which claims are still explicitly forbidden?

## User Scenario Gates

### US-V9-02 Parallel Agent Orchestration

Required evidence:

- `fan-out-dispatches.json`
- `fan-in-join-decisions.json`
- `attempt-history.json`
- `artifact-lineage.json`
- `lost-worker-recovery-decisions.json`
- HTML section named `并行 Agent 工作流证据`

Pass criteria:

- serial / parallel / fan-out / fan-in = PASS
- attempt history = PASS
- artifact lineage = PASS
- failure recovery = PASS
- lost worker recovery = PASS

### US-V9-07 Roman Forum Multi-Agent Discussion

Required evidence:

- `roman-forum-discussion.json`
- V9-3 runtime HTML section named `US-V9-07 罗马广场多 Agent 讨论`
- user-scenario coverage report section named `US-V9-07 罗马广场发言明细`

Pass criteria:

- At least five role-specific Agents are visible.
- At least two discussion turns are present.
- Message references between Agents are present.
- Moderator synthesis preserves attribution refs.
- source=agent direct durable mutation remains denied.

### US-V9-08 Video Storyboard Workflow

Required evidence:

- `v9-user-scenario-video-workflow-e2e/index.html`
- four storyboard image files
- `quality-agent-report.json`
- real TUI screenshot refs
- `workflow-agent-state.drawio`
- `workflow-agent-state.png`

Pass criteria:

- storyboard shot count is four.
- style_bible_id is consistent.
- character_bible_id is consistent.
- quality Agent report = PASS.
- provider raw payload is not stored.
- TUI screenshots are linked.

### US-V9-09 Natural-Language Optimization

Required evidence:

- `workflow_diff_proposal.json`

Pass criteria:

- WorkflowDiff proposal exists.
- No durable mutation before manual confirmation.
- source=agent direct durable mutation remains denied.

## Overall Acceptance Plan

Pass conditions:

- US-V9-01 to US-V9-09 are listed in the coverage matrix.
- Every listed scenario has status and evidence refs.
- User capability scenarios are runtime-backed, except the V9-8 final dashboard
  aggregation scenario.
- coverage_gaps is empty.
- No False Green scan = PASS.
- Redaction scan = PASS.
- V9 final acceptance generation = PASS.
- V9 current gap drawio XML = valid.

Stop conditions:

- Any scenario is missing from the coverage matrix.
- Roman Forum evidence lacks role Agents, messages, references, or synthesis.
- Parallel orchestration evidence lacks fan-out/fan-in or lineage.
- Video workflow evidence lacks images, quality Agent report, TUI screenshot, or
  drawio workflow-state diagram.
- Planning docs, transcript-only output, or report-only output is counted as
  runtime-backed evidence.
- Any forbidden completion claim appears outside a boundary or No False Green
  context.

## Evidence Entrypoints

- `docs/design/V9.x/evidence/v9-user-scenario-coverage-review/index.html`
- `docs/design/V9.x/evidence/v9-user-scenario-coverage-review/coverage-data.json`
- `docs/design/V9.x/evidence/v9-3-orchestration-runtime/index.html`
- `docs/design/V9.x/evidence/v9-3-orchestration-runtime/roman-forum-discussion.json`
- `docs/design/V9.x/evidence/v9-user-scenario-video-workflow-e2e/index.html`
- `docs/design/V9.x/evidence/v9-user-scenario-video-workflow-e2e/workflow-agent-state.drawio`
- `docs/design/V9.x/evidence/v9-user-scenario-video-workflow-e2e/workflow-agent-state.png`
- `docs/design/V9.x/evidence/v9-8-final-acceptance/v9-final-acceptance-dashboard.html`

## Audit Opinion

The previous V9 final acceptance package had the correct machine-readable
evidence, but the Roman Forum and parallel Agent workflow proof was not
sufficiently visible for human review. V9-UA closes that presentation and
traceability gap by adding a dedicated review page and stronger scenario
evidence references.

Residual risk remains bounded: V9-UA still does not prove a general Agent
executor, unrestricted orchestration, complete Studio, or production readiness.
