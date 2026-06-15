# V11 Milestone Roadmap

| Milestone | Stage | User-Visible Outcome | Evidence Scope | Exit Gate |
| --- | --- | --- | --- | --- |
| M0 | V11-0 | Architecture contract and planning package frozen | docs/drawio | External audit may review V11 scope and plane boundaries |
| M1 | V11-1 | User sees live progress instead of silent wait | real CLI/provider-backed turn | Event stream PASS |
| M2 | V11-2 | User can navigate with commands and shortcuts | CLI transcript | Slash command PASS |
| M3 | V11-3 | User sees workflow lifecycle state | TUI state fixture + runtime event fixture | Timeline PASS |
| M4 | V11-4 | User can inspect station/Agent details | V9/V11 evidence-backed fixture | Inspector PASS |
| M5 | V11-5 | Tool execution and permission risk are visible | tool/permission runtime fixture | Tool transparency PASS |
| M6 | V11-6 | Outputs, quality and evidence can be previewed | artifact/evidence refs | Preview PASS |
| M7 | V11-7 | User can export a readable audit page | generated HTML + Playwright screenshot | Supporting explainer PASS |
| M8 | V11-8 | Key user scenarios are validated end to end | scenario evidence package | Scenario matrix PASS |
| M9 | V11-9 | V11 baseline ready for review | final acceptance package | Final claim allowed |

## Current Milestone Status

- M0 / V11-0: PASS, ready for review.
- M1 / V11-1: PASS, ready for review.
- M2 / V11-2: PASS, ready for review.
- M3 / V11-3: PASS, ready for review.
- M4 / V11-4: PASS, ready for review.
- M5 / V11-5: PASS, ready for review.
- M6 / V11-6: PASS, ready for review.
- M7 / V11-7: PASS, ready for review.
- M8 / V11-8: PASS, ready for review.
- M9 / V11-9: PASS, ready for review.

## Milestone Dependencies

- M1 must pass before M3/M5 can claim live runtime visibility.
- M2 must pass before manual acceptance can rely on slash-command workflows.
- M4/M6 must pass before V11 can claim improved explainability.
- M8 cannot pass from planning docs or concept images.
- M9 cannot run unless M1 through M8 evidence packages exist.
- M1 cannot start if M0 does not freeze architecture planes, entity ownership
  and runtime truth boundary.
