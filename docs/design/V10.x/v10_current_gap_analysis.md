# V10 Current Gap Analysis

## Current State

Current local TUI and evidence pages still carry OpenHarness-style interaction
and naming. V7/V8/V9 proved strong workflow evidence, station Agent evidence,
terminal worker evidence and user scenario acceptance, but the primary TUI does
not yet feel like a HarnessOS-native CLI product. The first V10 planning package
also drifted toward a cockpit/dashboard concept; V10-0R corrects the target
toward Codex CLI / Claude Code style terminal-native basics.

After V10-8, Mission TUI can render fixture/read-model state, accept local
keyboard input and run an Agent-backed Gateway session/turn through the stdio
bridge. The current provider mode is `demo-fallback` in the local environment,
so V10 proves Gateway-backed chatbot wiring and visible live state, not
provider-backed LLM quality.

## Gaps

| Area | Current | V10 Target | Stage |
| --- | --- | --- | --- |
| TUI style | OpenHarness-compatible Textual/React launcher | HarnessOS React/Ink CLI-native Mission TUI | V10-1 |
| Layout | Cockpit/dashboard concept drift | Single-column transcript, bottom composer, compact status line | V10-1 |
| Tool UX | Logs and modal prompts | Terminal tool blocks with risk, sandbox, allow/deny and evidence refs | V10-2 |
| Workflow orientation | Evidence pages and transcripts | Inline workflow/station blocks in the command stream | V10-3 |
| Explainability | HTML evidence packages | Expandable Agent role, tools, skills, MCP, quality and forbidden reason blocks | V10-3 |
| Output preview | Separate evidence links | Station-level terminal preview and quality status | V10-4 |
| Modification | WorkflowDiff exists | Natural-language diff preview in TUI | V10-5 |
| Rich explanation | Static reports | Generated scenario explainer HTML as supporting evidence | V10-6 |
| Onboarding | Docs and scattered examples | First-run guide and scenario presets | V10-7 |
| Agent-backed Chat | Gateway stdio bridge implemented with demo-fallback provider mode | Provider-backed LLM quality evidence remains future/additional | V10-8 complete for review |
| Final UX Acceptance | V10-1..V10-8 evidence aggregation complete | Future phases may improve provider quality and React/Ink dependency migration | V10-9 complete for review |
| Implementation Detail | High-level stage plan | Stage-by-stage implementation specs, scenario gate and final acceptance framework | V10-1..V10-9 |

## Architecture Gap Summary

| Layer | Current | Target | Risk |
| --- | --- | --- | --- |
| User Entry | OpenHarness-compatible TUI and evidence HTML | HarnessOS CLI-native Mission TUI | High UX mismatch if OpenHarness copy remains |
| Chat Runtime | Local parser or fixture renderer | Agent-backed Gateway session/turn bridge | High false-green risk if fixture is called real Agent |
| Runtime State | V9 evidence packages and projections | Read-model adapter feeding terminal blocks | Medium if TUI constructs runtime truth |
| Review Surface | HTML reports and scattered JSON | Inline station, quality, evidence and diff blocks | Medium if evidence refs are missing |
| Rich Media | Evidence pages | Optional HTML explainer export | Low if clearly secondary |

## Required Scenario Coverage

- Local Markdown summary workflow.
- Roman Forum parallel Agent discussion.
- Video storyboard workflow.
- Coding proposal workflow.
- Natural-language workflow revision.
- Agent-backed chatbot turn with live Gateway state.

## Key Risk

The largest risk is false green: a polished TUI can make bounded pilot evidence
look like a complete product. V10 must keep ready-for-review language and
visible boundaries. Concept images and HTML explainers must not be presented as
real TUI screenshots.

The second largest risk is calling a local parser or fixture proposal
"Agent-backed". V10-8 requires Gateway session/turn evidence before it can PASS;
local-parser evidence remains negative/supporting evidence only.

## Current Documentation Adequacy

After the Agent-backed bridge implementation, the V10 documentation supports
V10 completion for review with bounded interpretation. V10-1 through V10-7
evidence remains a bounded read-model UX baseline. V10-8 evidence proves
Gateway-backed chatbot wiring with visible live state and `demo-fallback`
provider mode. It does not prove provider-backed LLM quality, production
readiness, Agent executor readiness or complete Workflow Studio readiness.
