# Codex Handoff - 2026-06-22

## Purpose

This document is the migration handoff for continuing HarnessOS development on another computer and in a new Codex terminal session.

It captures repository state, current product stage, important document paths, recovery steps, and the prompt to give the next Codex session.

Do not store API keys or local `.env` values in this document.

## Repository

```text
git remote: git@github.com:ljx418/harnessOS.git
project root: /Users/Zhuanz/Desktop/workspace/harnessOS
```

## Current Development Line

The active workstream is V12 / V12-V15 frontend product experience planning.

Current focus:

- V12-0P high-fidelity frontend prototype review.
- Gemini generation pack for producing a new reviewable frontend webpage prototype.
- Browser implementation has not been accepted as complete.
- Current artifacts are `design_only`; they are not BFF, DTO, browser implementation, or runtime evidence.

Important false-green boundaries:

- Do not claim `Xpert parity complete`.
- Do not claim `product-grade frontend complete`.
- Do not claim `complete Workflow Studio ready`.
- Do not claim `production ready`.
- Do not claim `Agent executor ready`.
- Do not treat Gemini output, HTML prototypes, screenshots, or Xpert references as HarnessOS runtime evidence.

## Key Paths

### Startup Context

```text
TASKS.md
CLAUDE.md
AGENTS.md
```

### Active V12-V15 Planning

```text
docs/design/V12-V15.x/00_README.md
docs/design/V12-V15.x/v12_to_v15_target_prd.md
docs/design/V12-V15.x/v12_to_v15_target_architecture.md
docs/design/V12-V15.x/v12_0p_high_fidelity_prototype_plan.md
docs/design/V12-V15.x/v12_figma_prototype_review_plan.md
docs/design/V12-V15.x/v12_0p_component_design_decision_record.md
```

### Current V12-0P Review Evidence

```text
docs/design/V12-V15.x/evidence/v12-0p-high-fidelity-prototype/index.html
docs/design/V12-V15.x/evidence/v12-0p-high-fidelity-prototype/imag2-vs-html-comparison.html
docs/design/V12-V15.x/evidence/v12-0p-high-fidelity-prototype/component-deep-design-v4.html
docs/design/V12-V15.x/evidence/v12-0p-high-fidelity-prototype/gemini-derived-light-studio-v1.html
docs/design/V12-V15.x/evidence/v12-0p-high-fidelity-prototype/v12-0p-acceptance-audit.md
docs/design/V12-V15.x/evidence/v12-0p-high-fidelity-prototype/prototype-review-data.json
```

### Gemini Generation Pack

Give the next Gemini session this folder:

```text
docs/design/V12-V15.x/gemini_frontend_review_pack/
```

Important file:

```text
docs/design/V12-V15.x/gemini_frontend_review_pack/01_GEMINI_GENERATION_PROMPT.md
```

The pack is intentionally limited to 9 files and is designed for Gemini to generate a new frontend prototype, not to review the old incorrect Gemini draft.

### Project Introduction Poster Pack

```text
docs/design/V12-V15.x/evidence/project-introduction-poster-pack/index.html
```

## Minimal Recovery Steps On Another Computer

1. Clone the repository.

```bash
git clone git@github.com:ljx418/harnessOS.git
cd harnessOS
```

2. Read the required startup context.

```bash
sed -n '1,220p' TASKS.md
sed -n '1,260p' CLAUDE.md
sed -n '1,220p' AGENTS.md
```

3. Check repository state.

```bash
git status --short
git remote -v
```

4. Open the current frontend review page.

```bash
open docs/design/V12-V15.x/evidence/v12-0p-high-fidelity-prototype/index.html
```

5. Open the Gemini package prompt.

```bash
open docs/design/V12-V15.x/gemini_frontend_review_pack/01_GEMINI_GENERATION_PROMPT.md
```

6. Validate the Gemini package JSON files.

```bash
./.venv/bin/python -m json.tool docs/design/V12-V15.x/gemini_frontend_review_pack/07_REVIEW_CHECKLIST.json
./.venv/bin/python -m json.tool docs/design/V12-V15.x/gemini_frontend_review_pack/08_MANIFEST.json
```

If `.venv` is unavailable on the new machine, use:

```bash
python3 -m json.tool docs/design/V12-V15.x/gemini_frontend_review_pack/07_REVIEW_CHECKLIST.json
python3 -m json.tool docs/design/V12-V15.x/gemini_frontend_review_pack/08_MANIFEST.json
```

## Prompt For The Next Codex Terminal

Copy this prompt into the new Codex terminal after cloning the repository:

```text
You are continuing HarnessOS development after migration from another computer.

Before doing any work:
1. Read TASKS.md.
2. Read CLAUDE.md.
3. Read AGENTS.md.
4. Read docs/development/codex_handoff_2026-06-22.md.

Current active workstream:
- V12 / V12-V15 frontend product experience planning.
- V12-0P high-fidelity frontend prototype review.
- Gemini generation pack for producing a new reviewable frontend webpage prototype.

Important paths:
- docs/design/V12-V15.x/00_README.md
- docs/design/V12-V15.x/v12_to_v15_target_prd.md
- docs/design/V12-V15.x/v12_to_v15_target_architecture.md
- docs/design/V12-V15.x/v12_0p_high_fidelity_prototype_plan.md
- docs/design/V12-V15.x/v12_0p_component_design_decision_record.md
- docs/design/V12-V15.x/evidence/v12-0p-high-fidelity-prototype/index.html
- docs/design/V12-V15.x/gemini_frontend_review_pack/01_GEMINI_GENERATION_PROMPT.md

Current boundary:
- V12 artifacts are design_only unless explicitly proven otherwise.
- Do not claim browser implementation complete.
- Do not claim BFF or runtime evidence.
- Do not claim Xpert parity complete.
- Do not claim product-grade frontend complete.
- Do not claim complete Workflow Studio ready.
- Do not claim production ready.
- Do not claim Agent executor ready.

Your first task:
1. Inspect git status.
2. Validate the Gemini generation pack has exactly the expected files.
3. Read the V12-0P review page and current Gemini prompt.
4. Report current state and propose the next concrete step.

Use concise Chinese for user-facing communication. Keep code comments, variable names, and commit messages in English.
```

## Current Human Intent

The user is moving to another computer and wants the repository plus relevant Codex terminal context available from GitHub.

The desired recovery outcome:

- clone repository;
- open the active review artifacts;
- continue V12 frontend design/prototype workflow without losing context;
- keep all false-green boundaries intact.

## Notes For Future Work

- If Gemini returns a new prototype, do not treat it as runtime or browser implementation evidence.
- Save Gemini output into a new evidence folder or a clearly named subfolder under `docs/design/V12-V15.x/evidence/`.
- Run local validation before asking the user to review.
- For browser implementation work, require a separate readiness acceptance after the design prototype is accepted.
