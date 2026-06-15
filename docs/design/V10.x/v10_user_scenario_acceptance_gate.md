# V10 User Scenario Acceptance Gate

## Purpose

V10 is user-experience driven. This gate defines what a real user must be able
to experience after the stage is implemented, and what evidence proves it.

## Global Scenario Rules

- Real TUI scenarios require real terminal screenshots or terminal recording
  evidence. Concept images do not count.
- HTML explainers are supporting audit artifacts only.
- Each scenario must show available actions, forbidden reasons and evidence
  refs when relevant.
- Workflow modification must remain proposal-first until user confirmation.
- source=agent must not directly perform durable mutation.
- Agent-backed scenario PASS requires Gateway session/turn evidence; local
  parser or fixture-only response can only be PARTIAL/BLOCKED for that scenario.

## US-V10-01 Local Markdown Workflow

### User Story

用户在终端输入：“总结这个本地技术文档目录，并告诉我关键风险。” 系统应展示从目标捕获、计划、文档读取、summary 生成到质量检查的完整过程。

### Required TUI Experience

- Bottom composer accepts the natural-language goal.
- Plan block appears before durable action.
- Station blocks show document scanner, summarizer and quality reviewer.
- Output preview shows folder summary refs and quality refs.
- Evidence links are visible and openable.

### Acceptance Evidence

- 80x24 screenshot.
- 120x40 screenshot.
- Fixture or runtime evidence with `scanner_actual_read_count > 0`.
- Redaction scan PASS.

## US-V10-02 Roman Forum Discussion

### User Story

用户输入一个哲学问题，系统用多个 persona Agent 并行讨论，并给出综合总结。用户需要能看见每个 Agent 的身份、观点、输出和最终综合证据。

### Required TUI Experience

- Multiple station/Agent blocks are visible in the transcript.
- Each persona block shows role, goal, status and evidence refs.
- Final synthesis block links to the contributing Agent outputs.
- Parallel/fan-in behavior is visible as read-model state, not claimed as full
  multi-Agent orchestration readiness.

### Acceptance Evidence

- Real TUI screenshot showing at least three persona Agent blocks.
- Synthesis evidence refs.
- No claim of full multi-Agent orchestration ready.

## US-V10-03 Video Storyboard Workflow

### User Story

用户输入一个视频点子，系统展示视频创作工作流：脚本、分镜、图像产物、质检 Agent 和修改建议。用户要能预览关键分镜和质量结果。

### Required TUI Experience

- Storyboard station output appears as preview block.
- Image/artifact refs are listed without raw provider payload.
- Quality Agent block shows pass/fail and evidence refs.
- User can request revision and see WorkflowDiff proposal.

### Acceptance Evidence

- TUI screenshot with storyboard output and quality status.
- HTML explainer may show richer storyboard media as supporting evidence.
- Provider-backed image artifacts must remain evidence refs, not raw payloads.

## US-V10-04 Coding Proposal Workflow

### User Story

用户要求修改项目代码，系统展示计划、diff proposal、sandboxed test、review summary 和 human handoff。用户必须清楚看到系统没有自动 commit / push / deploy。

### Required TUI Experience

- Coding proposal station block shows plan and diff refs.
- Sandboxed test block shows result and evidence refs.
- Review handoff block offers confirm/revise/reject, not auto-apply.
- Forbidden reasons show why commit/push/deploy are unavailable.

### Acceptance Evidence

- Real TUI screenshot showing diff proposal and test result.
- Negative evidence for no auto commit / push / deploy.
- No autonomous coding workflow ready claim.

## US-V10-05 Natural-Language Workflow Revision

### User Story

用户看完结果后说：“把质检工位提前，并增加一个审稿 Agent。” 系统应生成 WorkflowDiff proposal，让用户确认、修改或拒绝。

### Required TUI Experience

- User revision appears in transcript.
- WorkflowDiff block shows affected stations and proposed changes.
- Confirm/revise/reject controls are visible.
- TUI does not apply/publish/run without explicit confirmation.

### Acceptance Evidence

- WorkflowDiff fixture or runtime evidence.
- Negative fixture where auto-apply action fails.
- Evidence refs for proposed changes.

## US-V10-06 Agent-Backed Chatbot Turn

### User Story

用户在 TUI composer 中输入：“我想做一个多 Agent 的工作流，围绕同一个话题进行三四轮讨论，最后由一个 Agent 总结。” 用户需要看到系统真的把输入提交给后端 Agent/Gateway，而不是只在本地生成一个静态 proposal。

### Required TUI Experience

- User message appears immediately after pressing Enter.
- Status line transitions through visible phases such as `submitting`,
  `agent_running`, `streaming`, `completed` or `failed`.
- TUI shows Gateway `session_id`, `turn_id` and provider/fallback mode.
- Assistant response is derived from Gateway runtime output, not local template
  text.
- `/trace` shows ordered Gateway events.
- If provider key is missing, UI clearly marks demo/fallback runtime.
- If the turn fails, an error block appears with retry/recovery guidance.

### Acceptance Evidence

- Real terminal screenshot before submit.
- Real terminal screenshot after submit showing Agent-backed state.
- Raw Gateway event transcript containing `turn.started` and `turn.completed`
  or `turn.failed`.
- JSON acceptance data with:
  - `gateway_session_started=true`
  - `gateway_turn_started=true`
  - `gateway_turn_completed=true` or explicit failure state
  - `assistant_output_from_gateway=true`
  - `fixture_only=false`
- Negative evidence that local-parser/fixture mode cannot satisfy this scenario.

## Final Scenario Gate

V10 final acceptance cannot pass unless:

- US-V10-01 through US-V10-05 evidence exists.
- US-V10-06 evidence exists before final V10 completion may be claimed.
- At least V10-1 real TUI screenshots exist at 80x24 and 120x40.
- User-facing Simplified Chinese copy is present.
- No OpenHarness primary product branding remains in V10 TUI copy.
- No False Green PASS.
- Redaction PASS.
