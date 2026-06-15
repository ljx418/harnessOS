# V10 Final Acceptance Framework

## Purpose

This framework defines how V10 final acceptance is executed. It prevents
planning documents, concept images or supporting HTML pages from being counted
as runtime TUI evidence.

## Allowed Final Claim

```text
V10 complete: CLI-native Agent-backed TUI experience and explainability baseline ready for review.
```

## Forbidden Final Interpretations

- production ready
- full production GA
- complete Workflow Studio ready
- Agent executor ready
- full multi-Agent orchestration ready
- unrestricted terminal worker ready
- production terminal automation ready
- autonomous workflow editing ready
- Codex/Claude 体验已追平

## Required Stage Evidence

| Stage | Required Evidence |
| --- | --- |
| V10-1 | real TUI screenshots at 80x24 and 120x40, component tests, package boundary |
| V10-2 | tool/permission/plan block fixtures and negative permission tests |
| V10-3 | workflow/station/Agent explainability fixture with evidence refs |
| V10-4 | output preview and quality preview evidence |
| V10-5 | WorkflowDiff proposal-first evidence and no auto-apply negative test |
| V10-6 | HTML explainer generated from read-model/evidence state and marked supporting |
| V10-7 | read-model user scenario matrix, onboarding evidence, claim/redaction/drawio PASS and explicit local-parser boundary |
| V10-8 | Gateway session/turn evidence, live state screenshots, trace evidence and negative local-parser-only evidence |
| V10-9 | final aggregation of V10-1 through V10-8 evidence |

## Required Checks

- `apps/mission-tui` tests PASS when implementation exists.
- `tests/test_v10_*.py` PASS.
- Drawio XML validates with `xmllint`.
- No False Green scan PASS.
- Redaction scan PASS.
- Real screenshot evidence is distinct from concept images.
- Supporting HTML is not primary runtime truth.
- Current V10 baseline may use text terminal render captures as real terminal
  evidence; GUI PNG screenshots are optional future evidence.
- Agent-backed final acceptance requires Gateway `turn.started` and
  `turn.completed` or explicit failure evidence.
- Local parser / fixture output cannot satisfy Agent-backed final acceptance.

## Final Acceptance Data Shape

```json
{
  "stage_id": "V10-9",
  "status": "PASS|PARTIAL|FAIL|BLOCKED",
  "allowed_claim": "V10 complete: CLI-native Agent-backed TUI experience and explainability baseline ready for review.",
  "stage_evidence": [],
  "user_scenarios": [],
  "real_tui_screenshots": [],
  "claim_scan": "PASS|FAIL",
  "redaction_scan": "PASS|FAIL",
  "drawio_xml": "PASS|FAIL",
  "forbidden_claim_violations": [],
  "runtime_truth_boundary": "tui_read_model_not_runtime_truth",
  "agent_backed_gateway_turn": {
    "session_started": true,
    "turn_started": true,
    "turn_completed_or_failed": true,
    "assistant_output_from_gateway": true,
    "fixture_only": false
  }
}
```

## Stop Conditions

- Any V10-1 through V10-8 required evidence package is missing.
- Any required user scenario is missing.
- Concept image is used as real TUI screenshot.
- HTML explainer is used as runtime truth.
- source=agent can directly perform durable mutation.
- V10-8 Gateway turn evidence is missing.
- Fixture/local-parser evidence is used as Agent-backed proof.
- No False Green or redaction scan fails.
- Drawio XML is invalid.
