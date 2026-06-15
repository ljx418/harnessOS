# V12-V15 Xpert Reference Audit

## Purpose

This document records the Xpert reference baseline used by HarnessOS V12-V15.
The goal is to make Xpert a concrete product-experience benchmark, not a vague
parity slogan.

## Reference Repository

- Repository: `https://github.com/xpert-ai/xpert`
- Local checkout: `/Users/Zhuanz/Desktop/workspace/xpert`
- Checked commit: `0377cd9`
- Deployment mode reviewed: Docker Compose, China mirror compose file.
- Verified frontend URL: `http://127.0.0.1:18080/onboarding`
- Verified API health URL: `http://127.0.0.1:18080/api/health`
- Screenshot evidence:
  `docs/design/V12-V15.x/evidence/xpert-reference/xpert-onboarding-ready.png`
- Focused canvas evidence:
  `docs/design/V12-V15.x/evidence/xpert-reference/canvas-survey/index.html`

## Deployment Review

Xpert was deployed locally with Docker Compose. The following services were
observed:

- `docker-db-1`: PostgreSQL with pgvector, healthy.
- `docker-redis-1`: Redis stack, healthy.
- `docker-api-1`: Xpert API, healthy after default plugin initialization.
- `docker-webapp-1`: Xpert webapp, serving static frontend and proxying API.

The webapp required local API base URL alignment before the onboarding page
could load system status. This matters for HarnessOS because V15 self-hosting
acceptance must test browser-visible API configuration, not only backend
health.

## Source Areas Reviewed

| Area | Xpert Source | Relevant HarnessOS Gap |
| --- | --- | --- |
| Web product shell | `apps/cloud/src/app/features/*` | Product navigation, project workspace, settings and admin surfaces. |
| Chat workbench | `apps/cloud/src/app/@shared/chat/*` | Composer, attachments, tool-call chunks, execution panels and preview. |
| Xpert Studio | `apps/cloud/src/app/features/xpert/studio/*` | Visual Agent/workflow authoring and node inspectors. |
| Agent model | `packages/contracts/src/ai/xpert-agent.model.ts` | Durable Agent profile with prompt, memory, tools, model, retry and fallback settings. |
| Workflow model | `packages/contracts/src/ai/xpert-workflow.model.ts` | Rich workflow DSL node catalog and graph runtime semantics. |
| Runtime context | `packages/contracts/src/agent/graph.ts` | Workspace, checkpoint, tenant/org/user/project/xpert/agent/tool/model refs. |
| Execution observability | `apps/cloud/src/app/@shared/xpert/execution/*` | Status, log, provider/model, token and sub-execution review. |
| Tool/plugin system | `packages/plugin-sdk`, `packages/plugins/*`, `docs/zh-hans/guides/plugin.mdx` | Plugin package lifecycle, config schema and compatibility boundary. |
| File understanding | `docs/zh-hans/guides/file-understanding-architecture.mdx` | File assets, chunks, citations and workspace tools rather than raw full-file prompts. |

## Product Experience Lessons

HarnessOS should not clone Xpert mechanically. HarnessOS should use Xpert as a
reference for product completeness:

1. A user starts from a workspace/project product shell, not a raw command.
2. Chat, workflow Studio, execution review and artifact preview are connected.
3. Agents are durable product entities with role, model, memory, tool and
   permission configuration.
4. Workflow authoring is visual and schema-backed.
5. Tool, skill, plugin and MCP capabilities are managed as scoped product
   assets.
6. Execution evidence is visible as status, logs, traces, tokens, artifacts and
   sub-executions.
7. Self-hosting requires browser-visible configuration checks, not only server
   health checks.

## Focused Canvas Survey Findings

The focused Xpert Studio canvas survey confirms that the reference experience
is not a simple graph widget. It is a full workbench composed of:

- left global navigation and Xpert entity sidebar;
- central infinite dotted canvas;
- selectable nodes with input/output ports;
- right-side node inspector for model, prompt, memory, attachments, tools,
  knowledge, retry, fallback and output structure;
- top action bar for auto-save, Agent settings, preview, features and publish;
- bottom canvas toolbar for zoom, undo, redo, history, add and auto-layout;
- context/add menus for Agent, external expert, knowledgebase, toolset,
  middleware and workflow entities.

HarnessOS must therefore avoid treating "Xpert-level frontend interaction" as
only a TUI or report problem. V12 must establish the browser workbench and
canvas shell. V13 must implement editable canvas semantics.

Evidence boundary: the local Xpert canvas was entered with a benchmark fixture
and placeholder model. The survey is reference evidence only and cannot count
as HarnessOS implementation or runtime evidence.

## HarnessOS Differentiators To Preserve

V12-V15 must preserve HarnessOS boundaries:

- No False Green claim guard.
- Redaction and evidence scope discipline.
- Browser/BFF/runtime truth separation.
- WorkflowDiff confirmation before publish/run.
- Controlled executor and high-risk human decision rules.
- Evidence packages that distinguish runtime evidence from planning docs,
  screenshots and concept images.

## Implications For V12-V15

| Stage | Xpert-Inspired Target | HarnessOS-Specific Guard |
| --- | --- | --- |
| V12 | Product entity foundation plus browser workbench shell and read-only canvas foundation. | Entity writes must go through BFF/DTO and include audit refs; canvas shell is not runtime truth. |
| V13 | Editable Workflow Studio, visual DSL, node inspector, graph diff and versioning. | Studio cannot directly write runtime truth or auto publish/run. |
| V14 | Plugin/skill/tool/MCP management. | Install and activation require compatibility, scope and policy decisions. |
| V15 | Observability, deployment and final interaction review. | Deployment smoke must include browser-visible frontend/API health and runtime evidence. |

## Non-Goals

- Do not claim Xpert parity complete.
- Do not claim production ready.
- Do not claim complete Workflow Studio ready.
- Do not claim unrestricted plugin ecosystem ready.
- Do not claim Agent executor ready.
