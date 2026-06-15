# V12-0A imag2 Target Experience Generation Procedure

## Scope

This package records the host-native `gpt-image-2` generation procedure for the
V12 Light Studio target experience. The generated images are concept evidence
only. They are paired with local SVG factual mirrors so reviewers can verify
layout, component names, state labels and boundary claims without relying on
image model text fidelity.

## Mode Detection

Command:

```bash
node /Users/Zhuanz/.agents/skills/gpt-image-2/scripts/check-mode.js --json
```

Result:

```json
{
  "mode": "B-or-C",
  "recommendation": "host-or-advisor",
  "garden_mode_enabled": false,
  "has_api_key": false,
  "summary": "MODE B / C: use host-native image tool when available"
}
```

Execution choice: Mode B host-native image generation.

## Generated Concept Set

1. Overall workbench concept:
   `prompts/01-overall-workbench.md`
   - Host-generated PNG:
     `assets/01-overall-workbench-imag2.png`
2. Six-component design sheet:
   `prompts/02-component-sheet.md`
   - Host-generated PNG:
     `assets/02-component-sheet-imag2.png`
3. User interaction flow:
   `prompts/03-interaction-flow.md`
   - Host-generated PNG:
     `assets/03-interaction-flow-imag2.png`

## Consistency Constraints

- Same product name: HarnessOS V12 Light Studio.
- Same theme: light SaaS workbench, warm white background, slate text, blue
  primary accent, subtle borders, 8px radius.
- Same six component groups:
  global top bar, left product navigation, canvas workbench,
  Agent/Station node card, right inspector, Chat Workbench.
- Same visible states:
  API online/offline, running/failed/blocked, evidence ready/missing,
  awaiting confirmation.
- Same safe boundary:
  design-only; not browser, BFF, runtime, Xpert parity or production evidence.

## Local Factual Mirrors

Because host-native generated images are stored by the host image tool, this
repository also stores exact local SVG mirrors:

- `assets/01-overall-workbench.svg`
- `assets/02-component-sheet.svg`
- `assets/03-interaction-flow.svg`

These mirrors are not substitutes for the host images. They are audit anchors
that freeze names, layout slots, state labels and boundary language.
