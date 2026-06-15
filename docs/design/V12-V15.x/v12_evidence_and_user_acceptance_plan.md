# V12 Evidence And User Acceptance Plan

## Evidence Directory

V12 evidence must be collected under:

```text
docs/design/V12-V15.x/evidence/v12-readiness/
```

Required files:

- `v12-acceptance-data.json`
- `product-shell-screenshot.png`
- `canvas-workbench-screenshot.png`
- `canvas-node-inspector-screenshot.png`
- `workbench-screenshot.png`
- `browser-network-log.json`
- `bff-route-log.json`
- `canvas-read-model.json`
- `product-entity-projection.json`
- `schema-validation-report.json`
- `negative-fixture-report.json`
- `redaction-scan.txt`
- `no-false-green-scan.txt`
- `prd-spec-review.md`
- `../v12-component-prototype/index.html`
- `component-prototype-review.md`
- `component-prototype-review-data.json`
- `../v12-component-prototype/artifact-manifest.json`
- `../v12-component-prototype/prd-spec-review.md`
- `../v12-component-prototype/v12-0a-acceptance-audit.md`
- `../v12-component-prototype/no-false-green-scan.txt`
- `../v12-component-prototype/redaction-scan.txt`
- `../v12-component-prototype/assets/`
- `../v12-component-prototype/wireframes/`
- `component-prototype-schema-validation-report.json`
- `component-foundation-build.log`
- `component-inventory-review.md`
- `figma-prototype-url.txt`
- `figma-prototype-screenshot.png`
- `figma-prototype-review.md`
- `figma-prototype-review-data.json`
- `../v12-0p-high-fidelity-prototype/index.html`
- `../v12-0p-high-fidelity-prototype/prototype-review-data.json`
- `../v12-0p-high-fidelity-prototype/artifact-manifest.json`
- `../v12-0p-high-fidelity-prototype/prd-spec-review.md`
- `../v12-0p-high-fidelity-prototype/static-render-report.json`

## Acceptance Data Shape

Required fields:

- `stage_id`
- `status`
- `evidence_scope`
- `runtime_backed`
- `browser_backed`
- `bff_backed`
- `canvas_foundation_backed`
- `xpert_reference_used_as_runtime_evidence`
- `scenario_results`
- `component_prototype_review`
- `figma_prototype_review`
- `component_foundation`
- `schema_validation`
- `browser_boundary`
- `redaction_scan`
- `claim_scan`
- `created_at`

V12 PASS requires:

- `status=PASS`
- `browser_backed=true`
- `bff_backed=true`
- `canvas_foundation_backed=true`
- `xpert_reference_used_as_runtime_evidence=false`
- all required user scenarios PASS or accepted bounded PARTIAL
- component prototype review PASS before full Figma prototype freeze or
  browser UI implementation evidence is accepted
- Figma prototype review PASS before browser UI implementation evidence is
  accepted
- V12-0P high-fidelity prototype review PASS or explicitly superseded by a
  reviewed Figma prototype before browser UI implementation evidence is
  accepted
- component foundation build PASS
- redaction PASS
- claim scan PASS

## Figma Prototype Acceptance

V12 must include a Figma prototype review before browser implementation is
accepted. The Figma prototype is UX planning and review evidence only.

PASS:

- Prototype URL is recorded.
- Prototype includes product shell, browser canvas workbench, selected-node
  inspector, Chat Workbench proposal timeline and evidence/quality drawer.
- Major elements are editable Figma layers, not a single flattened image.
- Prototype marks V12 canvas as read-only foundation and proposal-only handoff.
- Prototype does not claim Xpert parity complete, complete Workflow Studio,
  production ready or Agent executor ready.

The prototype cannot replace HarnessOS browser screenshots, BFF network logs,
DTO snapshots or runtime evidence.

## Component Prototype Acceptance

V12 must include a component-level prototype review before full Figma prototype
freeze or browser implementation evidence is accepted. The component prototype
is design planning evidence only.

PASS:

- First-batch components are present: global top bar, left product navigation,
  canvas workbench, Agent / Station node card, right inspector and Chat
  Workbench + proposal timeline.
- Component prototype follows
  `v12_component_prototype_execution_plan.md`.
- Each component includes user goal, visible data, primary actions,
  disabled/denied actions, boundary notes and acceptance checks.
- At least one concept image or wireframe exists for each first-batch
  component.
- If a text-only fallback is accepted for a component, the reviewer records a
  non-empty `visual_artifact_exception_reason`.
- HTML prototype sketch report exists.
- `component-prototype-review-data.json` validates against
  `schemas/v12_component_prototype_review.schema.json`.
- `artifact-manifest.json` validates against
  `schemas/v12_component_prototype_artifact_manifest.schema.json` and is not
  left in `PLANNED_NOT_EVIDENCE` status for a V12-0A PASS.
- Reviewer marks each first-batch component accepted or accepted with bounded
  revisions.
- Component sketches do not claim Xpert parity, product-grade frontend
  complete, complete Workflow Studio, production ready or Agent executor ready.

The component prototype cannot replace Figma, HarnessOS browser screenshots,
BFF network logs, DTO snapshots or runtime evidence.

## User Scenario Acceptance

### US-V12-01 Product Onboarding

User goal:

Open HarnessOS in browser and understand whether the local product shell and
API are usable.

PASS:

- Product shell or onboarding page opens.
- API health is visible.
- Environment/API mismatch is either absent or explicitly shown as a blocking
  state.
- Screenshot and network log exist.

### US-V12-02 Create Small Studio Project

User goal:

Create or inspect a workspace/project/app and understand the project inventory.

PASS:

- Workspace/project/app appear in product shell.
- Entity audit refs exist.
- Wrong workspace/project negative case is denied.
- No raw credential or provider payload appears.

### US-V12-03 Configure Station Agent

User goal:

Configure a station Agent with role, goal, memory policy, model profile,
tool/skill/MCP refs and policy refs.

PASS:

- StationAgentProfile is visible.
- StationAgentBinding has policy and capability refs.
- Raw credential material is not visible.
- UI copy does not claim Agent executor ready.

### US-V12-04 Chat Workbench Goal To WorkflowDiff Handoff

User goal:

Describe a workflow idea in natural language and receive a proposal timeline
with a WorkflowDiff handoff.

PASS:

- Workbench conversation exists.
- Proposal timeline reaches `awaiting_user_confirmation` or `handoff_ready`.
- WorkflowDiff proposal ref exists.
- Transcript is marked as proposal evidence, not runtime evidence.
- Confirm handoff does not publish or run.

### US-V12-05 Browser Canvas Workbench Foundation

User goal:

Open a browser workbench that feels like the first step toward Xpert-level
canvas UX: entity sidebar, canvas nodes, node selection and inspector
foundation.

PASS:

- HarnessOS browser canvas/workbench shell opens.
- Canvas uses BFF-provided `CanvasReadModel`.
- Entity sidebar and at least one station-agent node are visible.
- Selecting one node shows `CanvasInspectorProjection`.
- Canvas toolbar actions are either implemented as read-only UI-local actions
  or disabled with visible reason.
- Browser network log shows no direct internal runtime/store route calls.
- Screenshot evidence is from HarnessOS UI, not Xpert reference screenshots.
- Evidence scope explicitly says read-only canvas foundation, not editable
  Workflow Studio.

### US-V12-06 Browser Boundary Review

User goal:

Verify the browser product shell cannot bypass BFF boundaries.

PASS:

- Browser denylist tests pass.
- Internal runtime/store/credential routes are not called.
- Denied attempts are visible in evidence.

### US-V12-07 Mature Component Foundation

User goal:

Review a browser workbench that feels like a coherent product surface instead
of a bespoke mock screen.

PASS:

- Product shell, toolbar, tabs, badges, cards, tooltips, scroll areas and
  inspector fields use the shared shadcn-style component layer.
- Canvas graph uses XyFlow, not static screenshots or manually positioned
  boxes.
- Disabled controls expose visible reason through tooltip/title/copy.
- The UI remains dense and operational, not card-heavy marketing layout.
- Browser screenshot exists and can be compared against the Figma component
  inventory.

### US-V12-08 Component Prototype Review

User goal:

Review the target workbench component-by-component before full Figma or real
browser development.

PASS:

- First-batch component sketches exist.
- HTML prototype sketch report exists.
- Reviewer can approve, reject or request revision for every component.
- The report explains the user flow assembled from components.
- Component evidence is marked design-only and cannot count as runtime
  implementation evidence.

## PRD Specification Review

V12 PRD review must confirm:

- V12 is product foundation, not complete Studio.
- Figma prototype has been reviewed as a browser experience contract.
- Component-level prototype review has been completed before Figma freeze.
- V12 includes a read-only browser canvas foundation; editable graph semantics
  remain V13.
- Xpert reference is benchmark input, not runtime evidence.
- Workbench can propose and hand off but cannot silently publish/run.
- Browser/BFF boundaries preserve V4-V11 runtime truth boundaries.
- V13/V14/V15 remain blocked until V12 evidence exists.

## V12 Final Stop Conditions

- Any required scenario FAIL.
- Component prototype review missing before Figma freeze or browser UI
  implementation evidence is accepted.
- Figma prototype review missing or used as runtime evidence.
- Xpert reference screenshot used as HarnessOS runtime evidence.
- Browser direct internal runtime/store/credential call appears.
- Raw secret, raw token, raw provider payload or raw artifact content appears.
- Workbench transcript is marked as runtime-backed execution.
- Canvas foundation evidence is static/drawio/Xpert-reference only.
- Browser UI is composed from one-off screen-specific controls where shared
  V12 component primitives are required.
- Canvas read model is treated as `WorkflowSpecGraph` or runtime truth.
- Positive claim says Xpert parity complete, complete Workflow Studio ready,
  production ready or Agent executor ready.
