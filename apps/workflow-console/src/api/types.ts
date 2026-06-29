export interface WorkflowSummary {
  workflow_template_id: string;
  name: string;
  latest_version_id?: string;
}

export interface WorkflowVersionSummary {
  workflow_version_id: string;
  workflow_template_id: string;
  version: string;
}

export interface WorkflowInstanceSummary {
  workflow_instance_id: string;
  workflow_template_id: string;
  workflow_version_id: string;
  status: string;
}

export interface PV19AuditRef {
  audit_ref_id?: string;
  operation?: string;
  entity_id?: string;
  created_at?: string;
  redaction_status?: "redacted";
}

export interface PV19WorkflowDraftSummary {
  workflow_draft_id: string;
  revision: number;
  status: string;
}

export interface PV19GraphNode {
  station_id: string;
  name?: string;
  role?: string;
  skill_refs?: string[];
  input_contracts?: unknown[];
  output_contracts?: unknown[];
  approval_required?: boolean;
  metadata?: Record<string, unknown>;
}

export interface PV19GraphEdge {
  edge_id: string;
  from_station_id: string;
  to_station_id: string;
  order?: number;
}

export interface PV19WorkbenchStateDTO {
  schema_version: "pv19.runtime_workflow_platform.v1";
  scope: Record<string, string | null>;
  entry: { route: string; root_empty_allowed: boolean; status: string };
  workspace: { workspace_id: string; display_name: string };
  project: { project_id: string; display_name: string };
  workflow: WorkflowSummary;
  draft: PV19WorkflowDraftSummary;
  active_version?: WorkflowVersionSummary | null;
  active_run?: WorkflowInstanceSummary | null;
  health: Record<string, unknown>;
  audit_refs: PV19AuditRef[];
  evidence_refs: unknown[];
  redaction_status: "redacted";
}

export interface PV19WorkflowGraphDTO {
  schema_version: "pv19.runtime_workflow_platform.v1";
  scope: Record<string, string | null>;
  workflow: WorkflowSummary;
  draft: PV19WorkflowDraftSummary;
  graph: {
    nodes: PV19GraphNode[];
    edges: PV19GraphEdge[];
    human_gate_nodes: string[];
    redaction_status: "redacted";
  };
  platform_contract: {
    business_pack_mode: string;
    core_customization_allowed: boolean;
    runtime_backed: boolean;
  };
  audit_refs: PV19AuditRef[];
  redaction_status: "redacted";
}

export interface PV19GraphValidationDTO {
  schema_version: "pv19.runtime_workflow_platform.v1";
  scope: Record<string, string | null>;
  workflow_id: string;
  status: "valid" | "invalid";
  errors: Array<Record<string, unknown>>;
  warnings: Array<Record<string, unknown>>;
  runtime_readiness: { can_publish: boolean; can_run_after_publish: boolean; human_gate_nodes: string[] };
  audit_refs: PV19AuditRef[];
  redaction_status: "redacted";
}

export interface PV19WorkflowDiffDTO {
  schema_version: "pv19.runtime_workflow_platform.v1";
  scope: Record<string, string | null>;
  workflow_id: string;
  draft_revision: number;
  workflow_diff: {
    workflow_patch_id: string;
    before_graph_ref: string;
    after_graph_ref: string;
    change_summary?: unknown[];
    confirmation_boundary: string;
  };
  workflow: WorkflowSummary;
  audit_refs: PV19AuditRef[];
  evidence_refs: string[];
  redaction_status: "redacted";
}

export interface PV19PublishResultDTO {
  schema_version: "pv19.runtime_workflow_platform.v1";
  scope: Record<string, string | null>;
  status: string;
  workflow_version_id: string;
  published_from_diff?: string | null;
  published_by: string;
  published_at: string;
  version: WorkflowVersionSummary & { workflow_draft_id?: string; draft_revision?: number; draft_status?: string };
  audit_refs: PV19AuditRef[];
  evidence_refs: string[];
  redaction_status: "redacted";
}

export interface PV19HumanGateRef {
  approval_id?: string;
  status?: string;
  station_id?: string;
  station_run_id?: string;
  audit_refs?: PV19AuditRef[];
}

export interface PV19RuntimeRef {
  event_ref?: string;
  event_type?: string;
  workflow_instance_id?: string;
  station_run_id?: string;
}

export interface PV19RunDTO {
  schema_version: "pv19.runtime_workflow_platform.v1";
  scope: Record<string, string | null>;
  workflow_instance: WorkflowInstanceSummary;
  status?: WorkflowStatus;
  station_runs: Array<Record<string, unknown>>;
  runtime_event_refs: PV19RuntimeRef[];
  trace_refs: Array<Record<string, unknown>>;
  artifact_refs?: Array<Record<string, unknown>>;
  quality_refs?: Array<Record<string, unknown>>;
  pending_human_gates: PV19HumanGateRef[];
  human_gate_refs?: PV19HumanGateRef[];
  audit_refs: PV19AuditRef[];
  redaction_status: "redacted";
}

export interface PV19HumanActionDTO {
  schema_version: "pv19.runtime_workflow_platform.v1";
  scope: Record<string, string | null>;
  action_type: "approve" | "reject";
  actor: string;
  approval_id: string;
  before_state: Record<string, unknown>;
  after_state: Record<string, unknown>;
  workflow_side_effect?: Record<string, unknown>;
  audit_refs: PV19AuditRef[];
  evidence_refs: string[];
  redaction_status: "redacted";
}

export interface PV19EvidenceSummaryDTO {
  schema_version: "pv19.runtime_workflow_platform.v1";
  scope: Record<string, string | null>;
  claims: Array<{ claim: string; evidence_refs: unknown[]; status: string }>;
  route_boundary: { allowed_prefix: string; browser_denylist: string[]; status: string };
  platform_generality: { status: string; primary_sample: string; reuse_check: string; core_customization_allowed: boolean };
  redaction: { status: string; secret_allowed: boolean; provider_payload_allowed: boolean; artifact_content_allowed: boolean };
  artifact_lineage: { artifact_refs: unknown[] };
  trace_timeline: { trace_refs: unknown[] };
  human_gate_lineage: { human_gate_refs: PV19HumanGateRef[] };
  missing_evidence: string[];
  allowed_claim: string;
  audit_refs: PV19AuditRef[];
  redaction_status: "redacted";
}

export interface PV20AgentExecutorStateDTO {
  schema_version: "pv20.agent_executor_contract.v1";
  stage: string;
  status: string;
  entry: { route: string; implementation_status: string };
  workflow_instance: WorkflowInstanceSummary;
  station_run: Record<string, unknown>;
  agent_execution_contract: PV20AgentExecutionContractDTO["agent_execution_contract"];
  agent_execution_result: PV20AgentExecutionContractDTO["agent_execution_result"];
  allowed_claim: string;
  audit_refs: PV19AuditRef[];
  redaction_status: "redacted";
}

export interface PV20AgentExecutionContractDTO {
  schema_version: "pv20.agent_executor_contract.v1";
  stage: string;
  workflow_instance: WorkflowInstanceSummary;
  station_run: Record<string, unknown>;
  agent_execution_contract: {
    execution_envelope_id: string;
    workflow_instance_id: string;
    station_run_id: string;
    station_id: string;
    agent_id: string;
    operation: string;
    allowed_operation_refs: string[];
    forbidden_operation_refs: string[];
    execution_authority: Record<string, unknown>;
    redaction_status: "redacted";
  };
  agent_execution_result: {
    execution_result_id: string;
    execution_status: string;
    status: string;
    skill_call_refs: string[];
    tool_call_refs: string[];
    mcp_call_refs: string[];
    approval_refs?: string[];
    artifact_refs?: unknown[];
    policy_decision?: Record<string, unknown>;
    redaction_status: "redacted";
  };
  audit_refs: PV19AuditRef[];
  redaction_status: "redacted";
}

export interface PV20AgentExecutionEvidenceDTO {
  schema_version: "pv20.agent_executor_contract.v1";
  stage: string;
  status: string;
  route_boundary: { allowed_prefix: string; forbidden_direct_routes: string[]; status: string };
  claim_matrix: Array<{ claim: string; evidence_refs: unknown[]; status: string }>;
  missing_evidence: string[];
  allowed_claim: string;
  not_claimed: string[];
  audit_refs: PV19AuditRef[];
  redaction_status: "redacted";
}

export interface PV20AgentExecutionActionDTO {
  schema_version: "pv20.agent_executor_contract.v1";
  stage: string;
  execution: {
    status: string;
    skill_call_refs?: string[];
    tool_call_refs?: string[];
    mcp_call_refs?: string[];
    approval_refs?: string[];
    artifact_refs?: unknown[];
    redaction_status: "redacted";
  };
  redaction_status: "redacted";
}

export interface PV21ScopeDTO {
  app_id?: string | null;
  project_id?: string | null;
  workspace_id?: string | null;
  workflow_id?: string | null;
}

export interface PV21NodeDTO {
  node_id: string;
  station_id: string;
  type: string;
  label: string;
  role?: string;
  inputs: unknown[];
  outputs: unknown[];
  policy?: Record<string, unknown>;
  executor_binding?: string | null;
  params?: Record<string, unknown>;
  metadata?: Record<string, unknown>;
}

export interface PV21EdgeDTO {
  edge_id: string;
  source: string;
  target: string;
  from_station_id: string;
  to_station_id: string;
  order?: number;
  metadata?: Record<string, unknown>;
}

export interface PV21WorkflowGraphDTO {
  schema_version: "pv21.complete_workflow_studio.v1";
  scope: PV21ScopeDTO;
  workflow_id: string;
  draft_revision: number;
  nodes: PV21NodeDTO[];
  edges: PV21EdgeDTO[];
  layout: Record<string, unknown>;
  validation_status: string;
  audit_refs?: PV19AuditRef[];
  redaction_status: "redacted";
}

export interface PV21GraphValidationDTO {
  schema_version: "pv21.complete_workflow_studio.v1";
  scope: PV21ScopeDTO;
  workflow_id: string;
  status: "valid" | "invalid";
  errors: Array<Record<string, unknown>>;
  warnings: Array<Record<string, unknown>>;
  affected_nodes: unknown[];
  affected_edges: unknown[];
  publish_blocked: boolean;
  runtime_readiness?: Record<string, unknown>;
  audit_refs: PV19AuditRef[];
  redaction_status: "redacted";
}

export interface PV21WorkflowVersionDTO {
  version_id: string;
  workflow_version_id: string;
  workflow_template_id: string;
  version: string;
  status: string;
  created_at?: string;
  published_by?: string;
  graph_hash?: string;
  rollback_allowed: boolean;
}

export interface PV21StudioStateDTO {
  schema_version: "pv21.complete_workflow_studio.v1";
  scope: PV21ScopeDTO;
  entry: { route: string; root_empty_allowed: boolean; status: string };
  workspace: { workspace_id: string; display_name: string };
  project: { project_id: string; display_name: string };
  app: { app_id: string; display_name: string };
  workflow: WorkflowSummary;
  platform_contract: {
    workflow_core_customization_allowed: boolean;
    gateway_core_customization_allowed: boolean;
    app_shell_customization_allowed: boolean;
    business_pack_allowed: boolean;
    boundary: string;
    status: string;
  };
  node_library: Array<Record<string, unknown>>;
  draft_graph: PV21WorkflowGraphDTO;
  published_version: PV21WorkflowVersionDTO | null;
  version_history: PV21WorkflowVersionDTO[];
  run_history: WorkflowInstanceSummary[];
  evidence_health: { status: string; missing_refs: string[] };
  route_claims: string[];
  audit_refs: PV19AuditRef[];
  redaction_status: "redacted";
}

export interface PV21WorkflowDiffDTO {
  schema_version: "pv21.complete_workflow_studio.v1";
  diff_id: string;
  base_version_id?: string;
  draft_revision: number;
  added_nodes: string[];
  removed_nodes: string[];
  changed_nodes: string[];
  changed_edges: string[];
  risk_summary: string[];
  publish_blocked: boolean;
  user_confirmation_required: boolean;
  audit_refs: PV19AuditRef[];
  redaction_status: "redacted";
}

export interface PV21VersionsDTO {
  schema_version: "pv21.complete_workflow_studio.v1";
  versions: PV21WorkflowVersionDTO[];
  published_version_id?: string | null;
  rollback_candidates: string[];
  audit_refs: PV19AuditRef[];
  redaction_status: "redacted";
}

export interface PV21RunDTO {
  schema_version: "pv21.complete_workflow_studio.v1";
  run_id: string;
  version_id: string;
  state: string;
  workflow_instance: WorkflowInstanceSummary;
  station_runs: Array<Record<string, unknown>>;
  current_human_gate?: Record<string, unknown> | null;
  pending_human_gates: Array<Record<string, unknown>>;
  trace_refs: unknown[];
  artifact_refs: unknown[];
  quality_refs: unknown[];
  approval_refs: unknown[];
  audit_refs: PV19AuditRef[];
  redaction_status: "redacted";
}

export interface PV21HumanActionDTO {
  schema_version: "pv21.complete_workflow_studio.v1";
  action_id: string;
  run_id: string;
  station_id?: string;
  decision: string;
  before_state: Record<string, unknown>;
  after_state: Record<string, unknown>;
  resulting_run_state: string;
  resulting_station_state?: string | null;
  audit_refs: PV19AuditRef[];
  redaction_status: "redacted";
}

export interface PV21EvidenceSummaryDTO {
  schema_version: "pv21.complete_workflow_studio.v1";
  artifact_refs: unknown[];
  trace_refs: unknown[];
  quality_refs: unknown[];
  approval_refs: unknown[];
  claim_refs: Array<Record<string, unknown>>;
  redaction_refs: Array<Record<string, unknown>>;
  missing_refs: string[];
  no_false_green_status: "pass" | "fail" | "not_run";
  route_boundary: { allowed_prefix: string; browser_denylist: string[]; status: string };
  platform_generality: Record<string, unknown>;
  allowed_claim: string;
  not_claimed: string[];
  audit_refs: PV19AuditRef[];
  redaction_status: "redacted";
}

export interface WorkflowStatus {
  workflow_instance_id: string;
  status: string;
  current_station_ids: string[];
  station_counts?: Record<string, number>;
  job_counts?: Record<string, number>;
  artifact_count?: number;
  quality_count?: number;
}

export interface ArtifactSummary {
  artifact_id: string;
  kind?: string;
  name?: string;
  metadata?: Record<string, unknown>;
  parent_ids?: string[];
}

export interface JobSummary {
  job_id: string;
  status: string;
  progress?: number;
}

export interface ApprovalSummary {
  approval_id: string;
  status: string;
  reason?: string;
  request_summary?: string;
  active?: boolean;
  inactive_reason?: string;
  station_run_id?: string;
  station_id?: string;
}

export interface QualitySummary {
  evaluation_id: string;
  status: string;
  score?: number;
  issues?: unknown[];
  suggestions?: unknown[];
  rubric_id?: string;
  station_run_id?: string;
  artifact_id?: string;
}

export interface TraceSummary {
  trace_id?: string;
  summary?: string;
  events?: unknown[];
  [key: string]: unknown;
}

export interface StationRunSummary {
  station_run_id: string;
  station_id: string;
  status: string;
  job?: JobSummary;
  input_artifacts?: ArtifactSummary[];
  output_artifacts?: ArtifactSummary[];
  approvals?: ApprovalSummary[];
  quality?: QualitySummary[];
  trace_summary?: TraceSummary;
}

export interface StationBoardSummary {
  station: {
    station_id: string;
    name?: string;
    role?: string;
  };
  runs: StationRunSummary[];
  status: string;
  input_artifacts?: ArtifactSummary[];
  output_artifacts?: ArtifactSummary[];
  approvals?: ApprovalSummary[];
  quality?: QualitySummary[];
  trace_summary?: TraceSummary;
}

export interface WorkflowBoard {
  workflow_instance: WorkflowInstanceSummary;
  stations: StationBoardSummary[];
  current_station_ids: string[];
  jobs?: JobSummary[];
  artifacts?: ArtifactSummary[];
  approvals?: ApprovalSummary[];
  quality_evaluations?: QualitySummary[];
  trace_summary?: TraceSummary;
}

export interface WorkflowEvent {
  id?: string;
  type: string;
  source?: "live" | "demo" | "trace_only";
  timestamp?: string;
  data?: Record<string, unknown>;
}

export type PatchStatus = "proposed" | "selected" | "applied" | "rejected" | "stale" | "blocked" | "conflicted";

export interface WorkflowPatchProposal {
  workflow_patch_id: string;
  patch_id?: string;
  workflow_template_id: string;
  workflow_draft_id: string;
  base_revision?: number;
  current_draft_revision?: number;
  operation: string;
  status: PatchStatus;
  proposed_by?: string;
  source?: "canvas" | "inspector" | "agent" | "workflow_console";
  intent_type?: "node_add" | "edge_add" | "inspector_update";
  requires_approval?: boolean;
  risk_flags?: string[];
  selected?: boolean;
  stale_reason?: string | null;
  conflict_reason?: string | null;
  created_at?: string;
  updated_at?: string;
}

export type PatchQueueDTO = WorkflowPatchProposal;

export interface NodeTemplateDescriptor {
  node_template_id: string;
  station_kind: string;
  schema_version: string;
  allowed_skill_refs: string[];
  allowed_connector_refs: string[];
  allowed_artifact_kinds: string[];
  allowed_quality_rules: string[];
  allowed_approval_policies: string[];
}

export interface StationDescriptorMapping extends NodeTemplateDescriptor {
  catalog_id: string;
  catalog_version: string;
}

export interface NodeCatalogItem extends StationDescriptorMapping {
  id: string;
  label: string;
}

export interface CanvasDraftProjection {
  projection_id: string;
  workflow_instance_id: string;
  workflow_template_id: string;
  workflow_draft_id: string;
  draft_revision: number;
  generated_at: string;
  board_status_timestamp?: string;
  status_updated_at?: string;
  patch_queue_revision?: string;
  freshness_state?: "fresh" | "stale_draft" | "stale_board" | "stale_patch" | "unknown";
  stale_reasons?: string[];
  source_refs: Record<string, unknown>;
  nodes: Array<{
    station_id: string;
    name?: string;
    role?: string;
    station_kind?: string;
    skill_refs: string[];
    connector_refs: string[];
    status?: string;
    run_count: number;
  }>;
  edges: Array<{
    edge_id: string;
    from_station_id: string;
    to_station_id: string;
    order?: number;
  }>;
  runtime_summary: Record<string, unknown>;
  patch_queue?: PatchQueueDTO[];
  pending_patch?: PatchQueueDTO | null;
  redaction_status: "redacted";
}

export interface FolderSummaryAuthorization {
  authorization_id: string;
  requested_path: string;
  resolved_path_label: string;
  allowed_root: string;
  status: string;
  created_at: string;
  expires_at: string;
  redaction_status: "redacted";
}

export interface FolderSummaryScanResult {
  folder_tree: Array<{ path: string; kind: "file" | "folder" }>;
  total_file_count: number;
  markdown_file_count: number;
  child_folder_count: number;
  unsupported_file_count: number;
  unsupported_files: string[];
  empty_folders: string[];
  redaction_status: "redacted";
}

export interface FolderSummaryProposal {
  proposal_id: string;
  workflow_template_id: string;
  workflow_draft_id: string;
  workflow_instance_id?: string | null;
  draft_revision: number;
  status: "proposed" | "applied" | "published" | "completed" | "failed";
  requested_path: string;
  nodes: Array<{ station_id: string; name: string; status: string }>;
  edges: Array<{ edge_id: string; from_station_id: string; to_station_id: string }>;
  risk_flags: string[];
  requires_user_confirmation: boolean;
  created_at: string;
  updated_at: string;
  redaction_status: "redacted";
}

export interface FolderSummaryArtifact {
  artifact_id: string;
  name: string;
  kind: string;
  content: string;
  metadata?: Record<string, unknown>;
  redaction_status: "redacted";
}

export interface FolderSummaryQualityReport {
  status: string;
  summary_coverage: { expected_folder_count: number; generated_summary_count: number };
  unsupported_files: string[];
  empty_folders: string[];
  markdown_file_count: number;
  child_folder_count: number;
  redaction_status: "redacted";
}

export interface FolderSummaryNodeAttempt {
  attempt_id: string;
  attempt: number;
  status: string;
  created_at: string;
  error?: string | null;
}

export interface FolderSummaryRun {
  workflow_instance_id: string;
  proposal_id: string;
  authorization_id: string;
  status: string;
  nodes: Array<{ station_id: string; name: string; status: string; updated_at: string; error?: string | null; attempts?: FolderSummaryNodeAttempt[] }>;
  artifacts: FolderSummaryArtifact[];
  quality_report: FolderSummaryQualityReport;
  operation_evidence?: OperationEvidenceRecord[];
  governance_review?: GovernanceReviewSummary;
  created_at: string;
  updated_at: string;
  redaction_status: "redacted";
}

export interface ControlledRuntimeEvidenceRecord extends OperationEvidenceRecord {
  operation_type?: string;
  capability_decision?: string;
  timeout_baseline?: { enabled: boolean; timeout_seconds?: number; status: string };
  kill_switch_baseline?: { enabled: boolean; scope?: string; status: string };
}

export interface ControlledRuntimeResult {
  workflow_instance_id: string;
  workflow_template_id: string;
  status: string;
  backed_by: "generic_controlled_runtime";
  user_confirmed_required: true;
  agent_mutation_allowed: false;
  nodes: FolderSummaryRun["nodes"];
  artifacts: FolderSummaryArtifact[];
  quality_report: FolderSummaryQualityReport;
  attempt_history: {
    workflow_instance_id: string;
    stations: Array<{ station_id: string; status: string; attempts: FolderSummaryNodeAttempt[] }>;
    redaction_status: "redacted";
  };
  downstream_stale: Array<{ station_id: string; reason: string; requires_user_confirmed_continue: true }>;
  operation_evidence: ControlledRuntimeEvidenceRecord[];
  timeout_baseline: { enabled: boolean; timeout_seconds?: number; status: string };
  kill_switch_baseline: { enabled: boolean; scope?: string; status: string };
  redaction_status: "redacted";
}

export interface NodeAddIntent {
  source: "canvas";
  intent_type: "node_add";
  operation: "add_station";
  workflow_instance_id?: string;
  payload: {
    station: {
      station_id: string;
      name: string;
      role?: string;
      skill_refs?: string[];
      connector_refs?: string[];
      metadata: {
        node_catalog_id: string;
        node_label: string;
        catalog_id: string;
        catalog_version: string;
        node_template_id: string;
        station_kind: string;
        schema_version: string;
        allowed_skill_refs: string[];
        allowed_connector_refs: string[];
        allowed_artifact_kinds: string[];
        allowed_quality_rules: string[];
        allowed_approval_policies: string[];
      };
    };
  };
}

export interface EdgeAddIntent {
  source: "canvas";
  intent_type: "edge_add";
  operation: "update_edge";
  workflow_instance_id?: string;
  payload: {
    edge_id: string;
    edge_patch: {
      action: "add";
      from_station_id: string;
      to_station_id: string;
      condition?: Record<string, unknown>;
      order?: number;
      metadata?: Record<string, unknown>;
    };
  };
}

export interface InspectorUpdateIntent {
  source: "inspector" | "agent";
  intent_type: "inspector_update";
  operation:
    | "update_station_prompt"
    | "update_connector"
    | "update_artifact_contract"
    | "update_quality_rule"
    | "update_approval_point";
  workflow_instance_id?: string;
  payload: Record<string, unknown>;
}

export type CanvasPatchIntent = NodeAddIntent | EdgeAddIntent | InspectorUpdateIntent;

export type AgentActionName =
  | "explain_workflow"
  | "summarize_events"
  | "summarize_quality"
  | "summarize_context"
  | "suggest_patch"
  | "show_patch_diff"
  | "show_approval_notice"
  | "show_context_summary"
  | "navigate_to_editing_panel"
  | "open_editing_panel"
  | "open_approval_panel"
  | "open_context_panel"
  | "open_quality_panel"
  | "open_artifact_panel"
  | "propose_patch"
  | "propose_context_update"
  | "propose_approval_decision"
  | "propose_station_rerun";

export interface AgentActionIntent {
  action: AgentActionName;
  executable: false;
}

export interface AgentTalkMessage {
  message_id: string;
  agent_session_id: string;
  workflow_instance_id: string;
  workflow_template_id: string;
  role: "user" | "assistant" | "system" | "event";
  source: "user" | "assistant" | "system" | "event";
  content: string;
  resource_refs?: Record<string, unknown>;
  created_at?: string;
  redaction_status: "redacted";
}

export interface AgentTalkSuggestion {
  suggestion_id: string;
  workflow_instance_id: string;
  workflow_template_id: string;
  workflow_patch_id?: string;
  type: "explain" | "summarize" | "propose_patch" | "show_diff" | "approval_notice" | "show_context_summary";
  title: string;
  summary: string;
  status: "active" | "dismissed";
  action_intent: AgentActionIntent;
  patch_intent?: CanvasPatchIntent | null;
  risk_flags?: string[];
  requires_approval?: boolean;
  created_at?: string;
  redaction_status: "redacted";
}

export interface AgentTalkSession {
  agent_session_id: string;
  workflow_instance_id: string;
  workflow_template_id: string;
  scope?: Record<string, unknown>;
  created_by?: string;
  created_at?: string;
  updated_at?: string;
  redaction_status: "redacted";
  messages: AgentTalkMessage[];
  suggestions: AgentTalkSuggestion[];
}

export interface AgentTalkInteractionState {
  workflow_instance_id: string;
  workflow_template_id: string;
  agent_session_id: string;
  selected_suggestion_id?: string | null;
  selected_proposal_id?: string | null;
  selected_handoff_id?: string | null;
  selected_patch_id?: string | null;
  selected_evidence_id?: string | null;
  stale_reasons: string[];
  refresh_generation: string;
  source_refs?: Record<string, unknown>;
  generated_at?: string;
  redaction_status: "redacted";
}

export type AgentActionPolicyClass = "display_only" | "navigation" | "proposal_only" | "forbidden";
export type AgentActionLifecycle = "proposed" | "reviewed" | "dismissed" | "converted_to_patch" | "converted_to_navigation" | "expired" | "blocked";

export interface AgentActionProposal {
  proposal_id: string;
  agent_session_id: string;
  workflow_instance_id: string;
  workflow_template_id: string;
  intent_type: AgentActionName;
  policy_class: AgentActionPolicyClass;
  lifecycle: AgentActionLifecycle;
  status: AgentActionLifecycle;
  title: string;
  summary: string;
  target_panel?: "editing" | "approval" | "context" | "quality" | "artifact" | "events" | null;
  workflow_patch_id?: string | null;
  risk_level: "low" | "medium" | "high";
  risk_flags: string[];
  requires_approval: boolean;
  policy_decision: string;
  payload_summary?: Record<string, unknown>;
  resource_refs?: Record<string, unknown>;
  created_by?: string;
  created_at?: string;
  updated_at?: string;
  redaction_status: "redacted";
}

export type AgentHandoffTargetPanel = "editing_panel" | "approval_panel" | "context_panel" | "quality_panel" | "artifact_panel";
export type AgentHandoffStatus = "active" | "opened" | "used_for_user_confirmed_action" | "dismissed" | "expired" | "stale" | "blocked";

export interface AgentActionHandoff {
  handoff_id: string;
  proposal_id: string;
  workflow_instance_id: string;
  workflow_template_id: string;
  target_panel: AgentHandoffTargetPanel;
  target_resource: Record<string, unknown>;
  suggested_form_prefill: Record<string, unknown>;
  expires_at: string;
  status: AgentHandoffStatus;
  inactive_reason?: string;
  updated_at?: string;
  created_at: string;
  created_by?: string;
  redaction_status: "redacted";
}

export interface AgentHandoffAuditRecord {
  audit_id: string;
  handoff_id: string;
  event_type: string;
  summary: string;
  data?: Record<string, unknown>;
  created_at: string;
  redaction_status: "redacted";
}

export interface WorkflowPatchDiff {
  workflow_patch_id: string;
  workflow_draft_id: string;
  base_revision: number;
  operation: string;
  target?: Record<string, unknown>;
  before_summary: string;
  after_summary: string;
  risk_flags: string[];
  requires_approval: boolean;
  redacted: boolean;
}

export interface PatchActionResult {
  workflow_patch_id: string;
  workflow_template_id?: string;
  workflow_draft_id?: string;
  status: PatchStatus;
  operation?: string;
  base_revision?: number;
  applied_revision?: number;
  resulting_draft_revision?: number;
  requires_approval?: boolean;
  risk_flags?: string[];
  blocked_reason?: string;
}

export interface PublishVersionResult {
  workflow_template_id: string;
  workflow_draft_id?: string;
  draft_status?: string;
  draft_revision?: number;
  workflow_version_id: string;
  version: string;
}

export interface WorkflowContextSummary {
  workflow_instance_id: string;
  revision: number;
  business: Record<string, unknown>;
  updated_at?: string;
  trace_id?: string;
}

export interface OperationResult<T = unknown> {
  operation: string;
  status: string;
  resource: T;
  idempotent?: boolean;
  trace_id?: string;
  evidence?: OperationEvidenceRecord;
}

export type OperationEvidenceStatus =
  | "succeeded"
  | "failed"
  | "idempotent_replayed"
  | "blocked"
  | "stale_rejected"
  | "expired_rejected";

export interface OperationRuntimeResultRef {
  type: string;
  resource_id?: string;
  workflow_instance_id?: string;
  workflow_template_id?: string;
  operation: string;
  status: string;
  trace_id?: string;
}

export interface OperationEvidenceRecord {
  evidence_id: string;
  workflow_instance_id: string;
  workflow_template_id?: string;
  operation: string;
  status: OperationEvidenceStatus;
  correlation_id: string;
  operation_id: string;
  idempotency_key: string;
  handoff_id?: string | null;
  proposal_id?: string | null;
  handoff_status_at_execution?: string | null;
  proposal_status_at_execution?: string | null;
  user_confirmed: boolean;
  source?: string;
  risk_flags: string[];
  policy_decision?: string;
  runtime_result_ref: OperationRuntimeResultRef;
  audit_refs?: Array<Record<string, unknown>>;
  created_at?: string;
  created_by?: string;
  redaction_status: "redacted";
}

export interface GovernanceReviewSummary {
  workflow_instance_id: string;
  workflow_template_id?: string;
  summary: {
    evidence_count: number;
    handoff_count: number;
    status_counts: Record<string, number>;
    operation_counts: Record<string, number>;
  };
  operation_evidence: OperationEvidenceRecord[];
  handoff_summary: Array<Record<string, unknown>>;
  audit_timeline: Array<Record<string, unknown>>;
  redaction_status: "redacted";
}

export interface PV17AuditRef {
  audit_ref_id: string;
  operation: string;
  scope?: Record<string, unknown>;
  entity_id?: string | null;
  created_at?: string;
  redaction_status: "redacted";
}

export interface PV17SystemHealthDTO {
  schema_version: string;
  status: string;
  api_status: string;
  gateway_status: string;
  workflow_store_status: string;
  frontend_config_status: string;
  method_count?: number;
  scope?: Record<string, unknown>;
  created_at?: string;
  redaction_status: "redacted";
}

export interface PV17ProductEntityProjection {
  entity_kind: string;
  entity_id: string;
  display_name?: string;
  role?: string | null;
  goal?: string | null;
  connector_refs?: string[];
  memory_refs?: string[];
  model_refs?: string[];
  tool_refs?: string[];
  skill_refs?: string[];
  mcp_refs?: string[];
  source?: string;
  audit_refs?: PV17AuditRef[];
  redaction_status: "redacted";
}

export interface PV17ProductConsoleStateDTO {
  schema_version: string;
  workspace: PV17ProductEntityProjection;
  project: PV17ProductEntityProjection;
  app: PV17ProductEntityProjection & { domain?: string; default_pack?: string; metadata?: Record<string, unknown> };
  workflows: WorkflowSummary[];
  station_agents: PV17ProductEntityProjection[];
  active_run?: WorkflowInstanceSummary | null;
  evidence_summary: {
    status: string;
    workflow_instance_id?: string;
    runtime_event_ref_count?: number;
    artifact_ref_count?: number;
    quality_ref_count?: number;
    claims?: string[];
    missing_evidence?: string[];
    allowed_claim?: string;
    redaction_status: "redacted";
  };
  audit_refs: PV17AuditRef[];
  created_at?: string;
  redaction_status: "redacted";
}

export interface PV17EntityMutationResultDTO {
  schema_version: string;
  status: "accepted" | "denied";
  entity_ref: { entity_kind: string; entity_id: string; scope?: Record<string, unknown> };
  entity?: PV17ProductEntityProjection;
  audit_ref: PV17AuditRef;
  policy_decision_ref: string;
  denied_reason?: string | null;
  redaction_status: "redacted";
}

export interface PV17StudioWorkflowDTO {
  schema_version: string;
  workflow_template: WorkflowSummary;
  draft: { workflow_draft_id?: string; revision?: number; status?: string };
  versions: WorkflowVersionSummary[];
  graph: { nodes: Array<Record<string, unknown>>; edges: Array<Record<string, unknown>>; redaction_status: "redacted" };
  inspector: Record<string, unknown>;
  patch_queue: PatchQueueDTO[];
  audit_refs: PV17AuditRef[];
  redaction_status: "redacted";
}

export interface PV17WorkflowPatchResultDTO {
  schema_version: string;
  status: "proposed";
  workflow_patch: WorkflowPatchProposal;
  audit_refs: PV17AuditRef[];
  redaction_status: "redacted";
}

export interface PV17PublishResultDTO {
  schema_version: string;
  status: "published";
  publish: PublishVersionResult;
  audit_refs: PV17AuditRef[];
  redaction_status: "redacted";
}

export interface PV17RunConfirmResultDTO {
  schema_version: string;
  status: "started";
  workflow_instance: WorkflowInstanceSummary;
  station_runs: Array<Record<string, unknown>>;
  runtime_event_refs: Array<Record<string, unknown>>;
  trace_refs: Array<Record<string, unknown>>;
  audit_refs: PV17AuditRef[];
  redaction_status: "redacted";
}

export interface PV17RuntimeInspectDTO {
  schema_version: string;
  workflow_instance: WorkflowInstanceSummary;
  status: WorkflowStatus;
  station_runs: Array<Record<string, unknown>>;
  runtime_event_refs: Array<Record<string, unknown>>;
  trace_refs: Array<Record<string, unknown>>;
  artifact_refs: Array<Record<string, unknown>>;
  quality_refs: Array<Record<string, unknown>>;
  approval_refs: Array<Record<string, unknown>>;
  audit_refs: PV17AuditRef[];
  redaction_status: "redacted";
}

export interface PV17EvidenceSummaryDTO {
  schema_version: string;
  claims: Array<{ claim: string; evidence_refs: unknown[]; status: string }>;
  route_boundary: { allowed_prefix: string; browser_denylist: string[]; status: string };
  redaction: { status: string; secret_allowed: boolean; provider_payload_allowed: boolean; artifact_content_allowed: boolean };
  artifact_lineage: { artifact_refs: Array<Record<string, unknown>> };
  trace_timeline: { trace_refs: Array<Record<string, unknown>> };
  missing_evidence: string[];
  allowed_claim: string;
  audit_refs: PV17AuditRef[];
  redaction_status: "redacted";
}

export type PV18AuditRef = PV17AuditRef;

export interface PV18KnowledgeWorkspaceDTO {
  workspace_id: string;
  display_name: string;
  owner?: string;
  scope: Record<string, unknown>;
  data_boundary?: string;
  audit_refs?: PV18AuditRef[];
  redaction_status: "redacted";
}

export interface PV18KnowledgeSourceDTO {
  source_id: string;
  source_reference: Record<string, unknown>;
  note: Record<string, unknown>;
  artifact_refs: Array<Record<string, unknown>>;
  lineage_refs: Array<Record<string, unknown>>;
  redaction_status: "redacted";
}

export interface PV18BuildStatusDTO {
  schema_version: string;
  build_id: string;
  workspace_id: string;
  status: string;
  stage: string;
  failure_reason?: string | null;
  trace_refs: Array<Record<string, unknown>>;
  next_actions: string[];
  audit_refs?: PV18AuditRef[];
  redaction_status: "redacted";
}

export interface PV18QueryResultDTO {
  schema_version: string;
  query_id: string;
  workspace_id: string;
  status: string;
  answer: string;
  brief: string;
  citation_bundle: { status: string; citations: Array<Record<string, unknown>> };
  citation_coverage: { status: string; source_ref_count: number };
  source_refs: Array<Record<string, unknown>>;
  artifact_refs: Array<Record<string, unknown>>;
  trace_refs: Array<Record<string, unknown>>;
  runner_warnings?: string[];
  audit_refs?: PV18AuditRef[];
  redaction_status: "redacted";
}

export interface PV18QualityFeedbackDTO {
  schema_version: string;
  quality_id: string;
  workspace_id: string;
  quality_status: string;
  issues: unknown[];
  low_signal_sources: unknown[];
  correction_required: boolean;
  trace_refs: Array<Record<string, unknown>>;
  audit_refs?: PV18AuditRef[];
  redaction_status: "redacted";
}

export interface PV18CorrectionPlanDTO {
  schema_version: string;
  plan_id: string;
  workspace_id: string;
  status: string;
  rules: unknown[];
  requires_human_review: boolean;
  auto_publish_allowed: boolean;
  audit_refs?: PV18AuditRef[];
  redaction_status: "redacted";
}

export interface PV18EvidenceSummaryDTO {
  schema_version?: string;
  status: string;
  claims: Array<{ claim_id?: string; claim: string; evidence_refs: unknown[]; status: string }>;
  route_boundary: { allowed_prefix: string; browser_denylist: string[]; status: string };
  artifact_lineage: { artifact_refs: Array<Record<string, unknown>>; source_count?: number };
  trace_timeline: { trace_refs: Array<Record<string, unknown>> };
  redaction: { status: string; secret_allowed: boolean; provider_payload_allowed: boolean; artifact_content_allowed: boolean };
  platform_generality?: { status: string; knowledge_only_platform_changes: string[]; generic_reuse_checks: string[] };
  quality_ref_count?: number;
  correction_ref_count?: number;
  missing_evidence: string[];
  allowed_claim: string;
  audit_refs?: PV18AuditRef[];
  redaction_status: "redacted";
}

export interface PV18KnowledgeStateDTO {
  schema_version: string;
  status: string;
  scope: Record<string, unknown>;
  workspace: PV18KnowledgeWorkspaceDTO;
  connector_health: {
    connector_id: string;
    status: string;
    execution_mode?: string;
    real_data_service?: boolean;
    capabilities?: Record<string, unknown>;
    redaction_status: "redacted";
  };
  sources: PV18KnowledgeSourceDTO[];
  builds: PV18BuildStatusDTO[];
  queries: PV18QueryResultDTO[];
  evidence_summary: PV18EvidenceSummaryDTO;
  audit_refs: PV18AuditRef[];
  created_at?: string;
  redaction_status: "redacted";
}
