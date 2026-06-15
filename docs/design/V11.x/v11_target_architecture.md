# V11 Target Architecture

## Architecture Intent

V11 is the real-time, explainable Mission TUI architecture stage. It upgrades
the V10 terminal renderer into a live workflow front end while preserving the
existing Gateway/runtime/evidence boundaries.

V11 is not a new runtime authority. It is a user interaction, event projection
and evidence inspection layer over the governed HarnessOS runtime.

## Baseline

V10 currently provides:

- CLI-native string rendering and a readline interaction loop.
- Gateway `session.start` / `turn.start` bridge.
- Provider-backed one-turn evidence.
- Read-model blocks for workflow, station, output, diff and evidence.
- Supporting HTML review pages.

Known architectural gaps:

- The TUI does not yet behave like a live state machine from the user's point
  of view.
- The user cannot reliably see whether the system is planning, waiting,
  running, blocked, failed or complete.
- Agent/Station roles, tool decisions and evidence are shown as blocks, but
  not as a coherent architecture of interactive runtime projections.
- Current diagrams do not sufficiently describe planes, entities, ownership or
  boundaries.

## Target Architecture Summary

```text
User
  -> Mission TUI Interaction Plane
  -> Conversation And Command Plane
  -> Gateway Session/Turn Plane
  -> Event Stream And State Projection Plane
  -> Workflow/Station/Agent Projection Plane
  -> Tool, Permission And Policy Visibility Plane
  -> Artifact, Quality And Evidence Review Plane
  -> HTML Explainer And Audit Export Plane
```

Runtime truth remains below the TUI:

```text
GatewayService / Agent Runtime / Controlled Executor / Workflow Store /
Artifact Store / Evidence Package
```

The TUI can display, propose, ask for confirmation and export evidence. It must
not directly mutate runtime truth.

## Change Classification

V11 uses the same change classification as
`v11_current_gap_analysis.drawio`.

| Color | Meaning | Architecture Items |
| --- | --- | --- |
| Gray | Inherit, do not rebuild | V4 Headless Workflow Core; V5-V7 tenant, credential, audit and productization baseline; V8-V9 Station Agent, controlled executor, orchestration, coding workflow, terminal worker and Studio evidence; GatewayService runtime boundary. |
| Yellow | Modify or strengthen | Mission TUI Shell, Conversation Controller, Gateway Session/Turn Adapter, Projection Adapters, Station/Agent Inspector, Tool/Permission Blocks, Output/Quality/Evidence Preview. |
| Orange-red | Add in V11 | Real-Time Event Stream Reducer, visible state machine, live repaint/heartbeat contract, V11 acceptance data contract. |

This classification is a hard planning rule. V11 must not reimplement gray
runtime/evidence/governance planes. V11 work should either strengthen yellow
projection/interaction components or add orange-red real-time interaction
components.

## Architectural Roles

| Role | Responsibility | Not Responsible For |
| --- | --- | --- |
| Human User | Enters goals, asks follow-up questions, reviews proposals, confirms or rejects handoffs. | Runtime execution authority before confirmation. |
| Mission TUI Shell | Owns terminal layout, composer, status rail, message stream and keyboard focus. | WorkflowStore or Artifact writes. |
| Conversation Controller | Normalizes user text, slash commands, input history, retries and revise requests. | Agent reasoning or provider invocation. |
| Gateway Session Client | Opens/resumes Gateway sessions and submits turns. | Bypassing GatewayService or creating executor routes. |
| Event Stream Reducer | Converts Gateway/local workflow events into visible UI state changes. | Runtime truth, persistence or policy decisions. |
| TUI State Store | Holds display truth: transcript, active phase, selected station, evidence refs and available actions. | Durable runtime truth. |
| Workflow Projection Adapter | Reads WorkflowSpec, WorkflowDiff, RuntimeReport and EvidenceChain projections. | Applying WorkflowDiff or publishing workflow versions. |
| Station/Agent Inspector | Explains station role, Agent goal, memory summary, tools, skills, MCP refs, attempt state and quality refs. | Claiming each station is a fully autonomous production Agent. |
| Tool/Permission Presenter | Shows tool lifecycle, sandbox, risk, policy decision, approval requirement and forbidden reason. | Executing unrestricted tools or granting approvals. |
| Evidence Previewer | Shows artifact refs, quality refs, redacted summaries and evidence links. | Storing raw secrets, raw provider payloads or raw artifact content. |
| HTML Explainer Generator | Produces a readable supporting review page from live-session evidence. | Replacing runtime evidence or terminal screenshots. |
| No False Green Guard | Prevents overclaiming and validates allowed wording. | Product capability expansion. |

## Architectural Planes

### 1. Mission TUI Interaction Plane

Purpose: provide the user's primary operating surface.

Change classification: yellow. V10 already has a CLI-native shell; V11
strengthens it into a real-time interaction surface.

Owned components:

- terminal shell layout,
- status line,
- transcript block renderer,
- composer,
- keyboard focus model,
- scroll and selection model.

Required entities:

- `MissionTuiViewport`
- `ComposerState`
- `FocusedBlockRef`
- `KeyboardBinding`
- `ScreenLayoutMode`

Acceptance focus:

- user input appears immediately,
- the running phase is visible before provider/runtime output returns,
- failed and blocked states are visible,
- narrow terminal rendering remains readable.

### 2. Conversation And Command Plane

Purpose: turn natural-language input and slash commands into bounded user
intents.

Change classification: yellow. Existing input handling is extended with
first-class command routing, retry/revise behavior and visible errors.

Owned components:

- natural-language submit path,
- slash command router,
- input history,
- command help,
- revise/retry command handling,
- invalid command error rendering.

Required entities:

- `MissionInputEvent`
- `SlashCommandInvocation`
- `CommandResultBlock`
- `AvailableAction`
- `ForbiddenActionReason`

Boundaries:

- a slash command can inspect or request a proposal;
- a slash command cannot directly apply/publish/run workflow changes;
- `/retry` cannot hide the previous failed attempt.

### 3. Gateway Session/Turn Plane

Purpose: connect the TUI to the HarnessOS Gateway boundary.

Change classification: yellow over gray. GatewayService is inherited and must
not be rebuilt; the V11 adapter strengthens event consumption and visible
provider/session/turn state.

Owned components:

- Gateway stdio/HTTP client adapter,
- session start/resume,
- turn start,
- event subscription or polling adapter,
- provider mode visibility,
- trace/session/turn refs.

Required entities:

- `GatewaySessionRef`
- `GatewayTurnRef`
- `ProviderMode`
- `TraceRef`
- `GatewayErrorBlock`

Boundaries:

- V11 must use GatewayService as the runtime boundary;
- V11 must not create a new executor route;
- V11 must not call provider APIs directly from UI code;
- provider-backed and fallback/demo modes must be visibly separated.

### 4. Event Stream And State Projection Plane

Purpose: make runtime and workflow progress observable in real time.

Change classification: orange-red. This is the primary V11 addition.

Owned components:

- event normalizer,
- reducer,
- state transition validator,
- heartbeat/elapsed-time tracker,
- event log buffer,
- UI repaint scheduler.

Required event families:

- `input.received`
- `gateway.session.started`
- `turn.started`
- `assistant.delta`
- `tool.started`
- `tool.completed`
- `tool.failed`
- `permission.requested`
- `workflow.state.changed`
- `station.started`
- `station.completed`
- `quality.completed`
- `evidence.recorded`
- `turn.completed`
- `turn.failed`

Required state line:

```text
Idle -> InputReceived -> SessionReady -> TurnStarted -> AgentRunning ->
Streaming -> ToolRunning -> AwaitingConfirmation -> ProposalReady ->
RunningWorkflow -> RuntimeReportReady -> EvidenceRecorded -> Completed
```

Failure states:

```text
ProviderFailed
ToolFailed
PolicyDenied
PermissionRequired
ValidationFailed
Timeout
Cancelled
```

Boundaries:

- event projection is display truth, not runtime truth;
- `turn.failed` cannot satisfy completion;
- hidden waits are stop conditions.

### 5. Workflow/Station/Agent Projection Plane

Purpose: explain what the workflow is, which station is active and which Agent
role is responsible for each output.

Change classification: yellow over gray. V4-V9 runtime/evidence objects are
inherited; V11 adds projection adapters and user-facing explanations.

Owned components:

- WorkflowSpec projection,
- WorkflowDiff projection,
- station list,
- station status map,
- Agent descriptor projection,
- round/attempt state projection,
- dependency and fan-in/fan-out visibility.

Required entities:

- `WorkflowSpecProjection`
- `WorkflowDiffProjection`
- `WorkflowStateTimeline`
- `StationProjection`
- `StationAttemptRef`
- `AgentRoleDescriptor`
- `AgentMemorySummary`
- `AgentToolSkillMcpProfile`

Boundaries:

- station/Agent projection may show V9 runtime evidence;
- projection must keep evidence scope visible;
- projection must not claim a production Agent executor;
- source=agent direct durable mutation remains denied.

### 6. Tool, Permission And Policy Visibility Plane

Purpose: make every action understandable and auditable before, during and
after it happens.

Change classification: yellow over gray. V6-V9 policy, executor and governance
evidence is inherited; V11 renders it as transparent user-facing blocks.

Owned components:

- tool block renderer,
- permission prompt renderer,
- risk badge,
- sandbox badge,
- policy/capability decision summary,
- approval/handoff refs,
- retry/failure hint.

Required entities:

- `ToolLifecycleBlock`
- `PermissionRequestBlock`
- `PolicyDecisionSummary`
- `CapabilityDecisionSummary`
- `ApprovalRequirement`
- `SandboxDescriptor`
- `RiskLevel`

Boundaries:

- V11 can display and request confirmation;
- V11 cannot grant approval by rendering a button alone;
- high-risk actions require existing governed paths;
- no unrestricted `connector.call`, `external_llm.call`, `git.commit`,
  `git.push` or `production.deploy`.

### 7. Artifact, Quality And Evidence Review Plane

Purpose: let users inspect outputs and quality without leaking raw content.

Change classification: yellow over gray. V4 Evidence Chain and V9 evidence
packages are inherited; V11 improves preview and evidence-scope visibility.

Owned components:

- artifact ref preview,
- quality result preview,
- evidence link list,
- redaction status,
- source/evidence scope badge,
- acceptance status badge.

Required entities:

- `ArtifactPreviewRef`
- `QualityReportRef`
- `EvidenceChainRef`
- `RuntimeReportRef`
- `RedactionStatus`
- `EvidenceScope`

Boundaries:

- raw prompt, raw file content, raw provider payload, raw connector payload,
  raw secret, token and raw artifact content are forbidden in preview/evidence;
- HTML reports are supporting surfaces only;
- planning docs and concept images cannot satisfy runtime acceptance.

### 8. Governance, Acceptance And Claim Guard Plane

Purpose: ensure V11 stays scoped to explainable TUI capability.

Change classification: gray plus orange-red. Existing No False Green and
redaction patterns are inherited; V11 adds its own acceptance data contract for
real-time TUI evidence.

Owned components:

- No False Green claim scanner,
- redaction scanner,
- evidence classifier,
- final acceptance aggregator,
- drawio XML validation,
- manual review checklist.

Required entities:

- `V11AcceptanceData`
- `ScenarioEvidenceMatrix`
- `ClaimScanResult`
- `RedactionScanResult`
- `DrawioValidationResult`
- `ManualReviewQuestion`

Boundaries:

- V11 final claim is only: `V11 complete: real-time explainable Mission TUI
  interaction baseline ready for review.`
- V11 must not be summarized as production ready, Agent executor ready,
  complete Workflow Studio, full multi-Agent orchestration, unrestricted
  terminal worker, production terminal automation or Codex/Claude Code parity.

## Core Entity Model

| Entity | Plane | Key Fields | Evidence Requirement |
| --- | --- | --- | --- |
| `MissionTuiSession` | Interaction | session_id, workspace, model, provider_mode, sandbox, evidence_status | CLI transcript or acceptance JSON |
| `MissionInputEvent` | Conversation | input_id, text_redacted_ref, submitted_at, command_kind | raw prompt must not be stored in evidence |
| `SlashCommandInvocation` | Conversation | command, args, status, result_block_ref | invalid command negative test |
| `GatewayTurnRef` | Gateway | session_id, turn_id, trace_id, started_at, completed_at, status | provider-backed or fixture-backed scope |
| `TuiRuntimeEvent` | Event | event_id, event_type, source, timestamp, payload_ref | event ordering preserved |
| `WorkflowStateTimeline` | Projection | states, current_state, blockers, evidence_refs | no skipped required states |
| `StationProjection` | Projection | station_id, status, active_attempt, agent_ref, quality_ref | station evidence ref |
| `AgentRoleDescriptor` | Projection | agent_id, role, goal, memory_summary_ref, tools, skills, mcp_refs | explicit evidence scope |
| `ToolLifecycleBlock` | Permission | tool_call_id, risk_level, sandbox, status, elapsed_ms, evidence_ref | tool started/completed/failed visible |
| `PermissionRequestBlock` | Permission | request_id, action, risk, required_confirmation, forbidden_reason | no silent allow |
| `ArtifactPreviewRef` | Evidence | artifact_id, artifact_kind, preview_summary_ref, redaction_status | no raw artifact content |
| `QualityReportRef` | Evidence | quality_report_id, target_ref, status, findings_ref | quality Agent output visible |
| `EvidenceChainRef` | Evidence | evidence_id, scope, source_refs, created_at | scope must be visible |
| `V11AcceptanceData` | Governance | stage_id, status, evidence_refs, claim_scan, redaction_scan | final acceptance input |

## Data Flow

```text
1. User enters natural-language goal or slash command.
2. Conversation Controller records MissionInputEvent and immediately emits
   input.received.
3. Gateway Session Client creates/resumes session and starts turn.
4. Gateway events and local workflow projection events flow into the Event
   Stream Reducer.
5. Reducer updates MissionTuiState and emits repaint-ready block changes.
6. Workflow Projection Adapter binds WorkflowSpec, WorkflowDiff,
   RuntimeReport and EvidenceChain refs into display blocks.
7. Station/Agent Inspector binds station attempts, Agent roles and output refs.
8. Tool/Permission Presenter renders action lifecycle and human decision needs.
9. Evidence Previewer shows redacted artifact/quality/evidence previews.
10. HTML Explainer may export the same evidence as a supporting review page.
```

## Ownership Matrix

| Capability | Owner | Runtime Truth? | May Mutate? |
| --- | --- | --- | --- |
| Display transcript | Mission TUI Shell | no | no |
| Parse slash commands | Conversation Controller | no | no |
| Submit turn | Gateway Session Client | Gateway owns truth | no direct workflow mutation |
| Normalize events | Event Stream Reducer | no | no |
| Show WorkflowDiff | Workflow Projection Adapter | no | proposal only |
| Confirm proposal | Governed confirmation path | yes, after validation | only through existing runtime path |
| Show Agent role/tools | Station/Agent Inspector | no | no |
| Show tool permission | Tool/Permission Presenter | no | confirmation request only |
| Preview artifact | Evidence Previewer | no | no |
| Export HTML | HTML Explainer | no | no |

## Required Architecture Invariants

- TUI state is display truth only.
- Gateway remains the only turn/session boundary.
- Workflow mutations must flow through governed confirmation/handoff paths.
- `source=agent` cannot directly mutate durable runtime state.
- Tool execution risk, sandbox and forbidden reasons must be visible.
- Runtime failures must remain visible and cannot be counted as PASS.
- Evidence scope must be explicit on every scenario and report.
- HTML and concept images cannot replace runtime or provider-backed evidence.
- User-facing copy must stay clear enough that a first-time user can know what
  the system is doing.

## Architecture Acceptance Gates

| Gate | Required Proof |
| --- | --- |
| Plane clarity | Drawio and markdown list all planes, owners and boundaries. |
| Entity clarity | Core entities have owner plane, fields and evidence requirements. |
| Flow clarity | User input, Gateway turn, event stream, projection, preview and export flow are documented. |
| Runtime boundary | No direct WorkflowStore / StationRun / Artifact write from TUI. |
| Explainability | Station/Agent/tool/evidence blocks show why and how outputs were produced. |
| No False Green | Forbidden claims only appear in safe contexts. |
