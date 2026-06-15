# V11 Acceptance Gate

## Final Allowed Claim

V11 complete: real-time explainable Mission TUI interaction baseline ready for review.

## Required Final Evidence

- V11-0 architecture contract and drawio are accepted.
- V11-1 through V11-8 acceptance data exists.
- Real provider-backed CLI turn evidence exists.
- Failed provider turn is visibly failed and cannot satisfy completion.
- Slash command transcript exists.
- Workflow state timeline transcript exists.
- Station/Agent inspector evidence exists.
- Tool/permission lifecycle evidence exists.
- Output/quality/evidence preview evidence exists.
- HTML explainer export exists and is marked supporting.
- User scenario matrix covers:
  - multi-Agent discussion,
  - video storyboard,
  - coding proposal,
  - local document summary,
  - workflow revision,
  - failure recovery.
- No False Green scan PASS.
- Redaction scan PASS.
- Drawio XML valid.

## Architecture Gate

V11 cannot pass final acceptance unless the evidence package proves:

- Mission TUI Interaction Plane owns only display state.
- Conversation And Command Plane cannot apply/publish/run durable changes.
- Gateway Session/Turn Plane remains the only provider/runtime entry boundary.
- Event Stream And State Projection Plane visibly preserves failed/blocked
  states.
- Workflow/Station/Agent Projection Plane keeps Agent readiness claims bounded.
- Tool/Permission Plane shows risk, sandbox, decision and forbidden reason.
- Artifact/Quality/Evidence Plane does not leak raw content.
- Governance Plane blocks forbidden completion claims.

## Provider-Backed And Fixture-Backed Evidence Priority

| Evidence Type | Can Satisfy V11 Runtime UX? | Notes |
| --- | --- | --- |
| Provider-backed CLI transcript | yes | Must include session, turn, trace and completed turn. At least one is required for final V11. |
| Runtime fixture | yes, bounded | Must keep `evidence_scope=real_runtime_fixture`. |
| TUI read-model fixture | partial | Can verify UI rendering, not runtime execution. |
| HTML explainer | supporting only | Cannot be runtime truth. |
| Concept image | no | Planning illustration only. |
| Planning docs | no | Cannot satisfy runtime acceptance. |

## Evidence Package Layout

V11 evidence packages must use this layout:

```text
docs/design/V11.x/evidence/
  v11-0-architecture-contract/
    architecture-contract-acceptance.json
    drawio-validation.txt
    document-audit.md
  v11-1-real-time-event-stream/
    acceptance-data.json
    cli-transcript.txt
    events.jsonl
    tui-state-snapshots.json
    failed-turn-transcript.txt
  v11-2-command-ux/
    acceptance-data.json
    slash-command-transcript.txt
    invalid-command-transcript.txt
  v11-3-workflow-timeline/
  v11-4-station-agent-inspector/
  v11-5-tool-permission-blocks/
  v11-6-output-quality-evidence-preview/
  v11-7-live-session-html-explainer/
  v11-8-user-scenarios/
  v11-9-final-acceptance/
```

## Final Aggregator Rules

`acceptance:v11` must fail if:

- any required V11-1 through V11-8 evidence package is missing,
- any required stage has `status=FAIL`,
- any `BLOCKED` stage lacks an accepted bounded reason,
- a forbidden claim appears outside safe context,
- redaction scan is not PASS,
- drawio XML validation is not PASS,
- scenario evidence is planning-only while claiming runtime UX PASS.

## V11-1 Event Ordering Assertions

V11-1 event ordering must satisfy:

- input.received must be recorded before the related turn.started.
- `gateway.session.started` may precede user input when the session is
  preconnected.
- `turn.started` must precede `assistant.delta`, `tool.started`,
  `turn.completed` or `turn.failed` for the same turn.
- turn.failed cannot be followed by turn.completed or a completed acceptance
  result for the same turn.

## Manual Review Questions

- Can a first-time user tell whether the system is waiting, running, failed or done?
- Can the user see which Agent/station is responsible for each output?
- Can the user inspect evidence without reading architecture docs?
- Can the user revise a workflow before any durable mutation?
- Are forbidden actions and risk reasons visible?
- Is the UI closer to Codex/Claude Code in interaction behavior, not just
  visual style?
- Can a reviewer identify which architecture plane owns each visible block?
- Does every proposed mutation have a visible governed boundary?
