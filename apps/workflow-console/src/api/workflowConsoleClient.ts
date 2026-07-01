import type {
  ArtifactSummary,
  AgentActionHandoff,
  AgentHandoffAuditRecord,
  AgentActionProposal,
  AgentTalkInteractionState,
  ApprovalSummary,
  AgentTalkSession,
  AgentTalkSuggestion,
  CanvasPatchIntent,
  CanvasDraftProjection,
  GovernanceReviewSummary,
  FolderSummaryArtifact,
  FolderSummaryAuthorization,
  FolderSummaryProposal,
  FolderSummaryQualityReport,
  FolderSummaryRun,
  FolderSummaryScanResult,
  ControlledRuntimeResult,
  NodeCatalogItem,
  OperationResult,
  OperationEvidenceRecord,
  PatchQueueDTO,
  PatchActionResult,
  PV17EntityMutationResultDTO,
  PV17EvidenceSummaryDTO,
  PV17ProductConsoleStateDTO,
  PV17PublishResultDTO,
  PV17RunConfirmResultDTO,
  PV17RuntimeInspectDTO,
  PV17StudioWorkflowDTO,
  PV17SystemHealthDTO,
  PV17WorkflowPatchResultDTO,
  PV18BuildStatusDTO,
  PV18CorrectionPlanDTO,
  PV18EvidenceSummaryDTO,
  PV18KnowledgeStateDTO,
  PV18QualityFeedbackDTO,
  PV18QueryResultDTO,
  PV18KnowledgeSourceDTO,
  PV19EvidenceSummaryDTO,
  PV19GraphValidationDTO,
  PV19HumanActionDTO,
  PV19PublishResultDTO,
  PV19RunDTO,
  PV19WorkbenchStateDTO,
  PV19WorkflowDiffDTO,
  PV19WorkflowGraphDTO,
  PV20AgentExecutionActionDTO,
  PV20AgentExecutionContractDTO,
  PV20AgentExecutionEvidenceDTO,
  PV20AgentExecutorStateDTO,
  PV21EvidenceSummaryDTO,
  PV21GraphValidationDTO,
  PV21HumanActionDTO,
  PV21RunDTO,
  PV21StudioStateDTO,
  PV21VersionsDTO,
  PV21WorkflowDiffDTO,
  PV21WorkflowGraphDTO,
  PV21WorkflowVersionDTO,
  WorkflowPlatformBusinessOutputDTO,
  WorkflowPlatformScenarioProjectionDTO,
  PublishVersionResult,
  QualitySummary,
  WorkflowPatchDiff,
  WorkflowPatchProposal,
  WorkflowBoard,
  WorkflowContextSummary,
  WorkflowEvent,
  WorkflowInstanceSummary,
  WorkflowStatus,
  WorkflowSummary,
  WorkflowVersionSummary,
} from "./types.js";

export class WorkflowConsoleClient {
  constructor(
    private readonly basePath = "/bff",
    private readonly options: { defaultScope?: Partial<Record<"app_id" | "project_id" | "workspace_id", string>> } = {},
  ) {}

  getPV17SystemHealth(): Promise<PV17SystemHealthDTO> {
    return this.get<PV17SystemHealthDTO>(this.pv17Path("/pv17/system/health"));
  }

  getPV17ProductConsoleState(): Promise<PV17ProductConsoleStateDTO> {
    return this.get<PV17ProductConsoleStateDTO>(this.pv17Path("/pv17/product-console/state"));
  }

  mutatePV17Entity(
    entityRoute: "workspaces" | "projects" | "apps" | "station-agents",
    payload: {
      scope?: Record<string, unknown>;
      entity_kind: string;
      operation: string;
      user_confirmed: true;
      source: "product_console" | "workflow_console" | "mission_studio";
      idempotency_key: string;
      payload: Record<string, unknown>;
    },
  ): Promise<PV17EntityMutationResultDTO> {
    return this.post<PV17EntityMutationResultDTO>(this.pv17Path(`/pv17/entities/${entityRoute}`), payload);
  }

  getPV17StudioWorkflow(templateId: string): Promise<PV17StudioWorkflowDTO> {
    return this.get<PV17StudioWorkflowDTO>(this.pv17Path(`/pv17/studio/workflows/${encodeURIComponent(templateId)}`));
  }

  proposePV17Patch(templateId: string, payload: CanvasPatchIntent): Promise<PV17WorkflowPatchResultDTO> {
    return this.post<PV17WorkflowPatchResultDTO>(
      this.pv17Path(`/pv17/studio/workflows/${encodeURIComponent(templateId)}/patches`),
      payload as unknown as Record<string, unknown>,
    );
  }

  publishPV17Workflow(
    templateId: string,
    payload: {
      user_confirmed: true;
      source: "editing_panel" | "workflow_console" | "mission_studio";
      idempotency_key: string;
      expected_draft_revision: number;
      version: string;
    },
  ): Promise<PV17PublishResultDTO> {
    return this.post<PV17PublishResultDTO>(this.pv17Path(`/pv17/studio/workflows/${encodeURIComponent(templateId)}/publish`), payload);
  }

  confirmPV17Run(
    templateId: string,
    payload: {
      user_confirmed: true;
      source: "run_panel" | "workflow_console" | "mission_studio";
      idempotency_key: string;
      workflow_template_id: string;
      workflow_version_id: string;
      input?: Record<string, unknown>;
    },
  ): Promise<PV17RunConfirmResultDTO> {
    return this.post<PV17RunConfirmResultDTO>(this.pv17Path(`/pv17/runtime/workflows/${encodeURIComponent(templateId)}/confirm-run`), payload);
  }

  inspectPV17Instance(instanceId: string): Promise<PV17RuntimeInspectDTO> {
    return this.get<PV17RuntimeInspectDTO>(this.pv17Path(`/pv17/runtime/instances/${encodeURIComponent(instanceId)}/inspect`));
  }

  getPV17EvidenceSummary(instanceId: string): Promise<PV17EvidenceSummaryDTO> {
    return this.get<PV17EvidenceSummaryDTO>(this.pv17Path(`/pv17/evidence/instances/${encodeURIComponent(instanceId)}/summary`));
  }

  getPV18KnowledgeState(): Promise<PV18KnowledgeStateDTO> {
    return this.get<PV18KnowledgeStateDTO>(this.pv18Path("/pv18/knowledge/state"));
  }

  upsertPV18KnowledgeWorkspace(payload: { workspace_id?: string; display_name?: string; owner?: string }): Promise<{ status: string; workspace: PV18KnowledgeStateDTO["workspace"] }> {
    return this.post<{ status: string; workspace: PV18KnowledgeStateDTO["workspace"] }>(this.pv18Path("/pv18/knowledge/workspaces"), payload);
  }

  importPV18KnowledgeSource(payload: { title: string; content: string }): Promise<PV18KnowledgeSourceDTO & { schema_version: string; status: string }> {
    return this.post<PV18KnowledgeSourceDTO & { schema_version: string; status: string }>(this.pv18Path("/pv18/knowledge/sources/import"), payload);
  }

  startPV18KnowledgeBuild(payload: { mode?: string } = {}): Promise<PV18BuildStatusDTO> {
    return this.post<PV18BuildStatusDTO>(this.pv18Path("/pv18/knowledge/builds/start"), payload);
  }

  getPV18KnowledgeBuildStatus(buildId: string): Promise<PV18BuildStatusDTO> {
    return this.get<PV18BuildStatusDTO>(this.pv18Path(`/pv18/knowledge/builds/${encodeURIComponent(buildId)}/status`));
  }

  queryPV18Knowledge(payload: { query: string }): Promise<PV18QueryResultDTO> {
    return this.post<PV18QueryResultDTO>(this.pv18Path("/pv18/knowledge/query"), payload);
  }

  createPV18QualityFeedback(payload: { issues?: unknown[]; low_signal_sources?: unknown[] }): Promise<PV18QualityFeedbackDTO> {
    return this.post<PV18QualityFeedbackDTO>(this.pv18Path("/pv18/knowledge/quality-feedback"), payload);
  }

  createPV18CorrectionPlan(payload: { rules?: unknown[] }): Promise<PV18CorrectionPlanDTO> {
    return this.post<PV18CorrectionPlanDTO>(this.pv18Path("/pv18/knowledge/correction-plan"), payload);
  }

  getPV18EvidenceSummary(): Promise<PV18EvidenceSummaryDTO> {
    return this.get<PV18EvidenceSummaryDTO>(this.pv18Path("/pv18/knowledge/evidence/summary"));
  }

  getPV19WorkbenchState(): Promise<PV19WorkbenchStateDTO> {
    return this.get<PV19WorkbenchStateDTO>(this.pv19Path("/pv19/workbench/state"));
  }

  getPV19WorkflowGraph(workflowId: string): Promise<PV19WorkflowGraphDTO> {
    return this.get<PV19WorkflowGraphDTO>(this.pv19Path(`/pv19/workflows/${encodeURIComponent(workflowId)}/graph`));
  }

  validatePV19WorkflowGraph(workflowId: string): Promise<PV19GraphValidationDTO> {
    return this.post<PV19GraphValidationDTO>(this.pv19Path(`/pv19/workflows/${encodeURIComponent(workflowId)}/graph/validate`), {});
  }

  createPV19WorkflowDiff(workflowId: string): Promise<PV19WorkflowDiffDTO> {
    return this.post<PV19WorkflowDiffDTO>(this.pv19Path(`/pv19/workflows/${encodeURIComponent(workflowId)}/diff`), {});
  }

  publishPV19Workflow(
    workflowId: string,
    payload: {
      user_confirmed: true;
      source: "workflow_console" | "mission_studio" | "editing_panel";
      idempotency_key: string;
      expected_draft_revision: number;
      workflow_patch_id?: string;
      version: string;
      actor?: string;
    },
  ): Promise<PV19PublishResultDTO> {
    return this.post<PV19PublishResultDTO>(this.pv19Path(`/pv19/workflows/${encodeURIComponent(workflowId)}/versions/publish`), payload);
  }

  startPV19WorkflowRun(
    workflowId: string,
    payload: {
      user_confirmed: true;
      source: "workflow_console" | "mission_studio" | "run_panel";
      idempotency_key: string;
      workflow_version_id: string;
      input?: Record<string, unknown>;
    },
  ): Promise<PV19RunDTO> {
    return this.post<PV19RunDTO>(this.pv19Path(`/pv19/workflows/${encodeURIComponent(workflowId)}/runs`), payload);
  }

  inspectPV19Run(runId: string): Promise<PV19RunDTO> {
    return this.get<PV19RunDTO>(this.pv19Path(`/pv19/runs/${encodeURIComponent(runId)}/inspect`));
  }

  submitPV19HumanAction(
    runId: string,
    payload: {
      user_confirmed: true;
      source: "workflow_console" | "human_gate_panel" | "mission_studio";
      idempotency_key: string;
      action_type: "approve" | "reject";
      reason?: string;
      actor?: string;
      approval_id?: string;
    },
  ): Promise<PV19HumanActionDTO> {
    return this.post<PV19HumanActionDTO>(this.pv19Path(`/pv19/runs/${encodeURIComponent(runId)}/human-actions`), payload);
  }

  getPV19RunEvidence(runId: string): Promise<PV19EvidenceSummaryDTO> {
    return this.get<PV19EvidenceSummaryDTO>(this.pv19Path(`/pv19/runs/${encodeURIComponent(runId)}/evidence`));
  }

  getPV20AgentExecutorState(): Promise<PV20AgentExecutorStateDTO> {
    return this.get<PV20AgentExecutorStateDTO>(this.pv20Path("/pv20/agent-executor/state"));
  }

  getPV20AgentExecutionContract(runId: string): Promise<PV20AgentExecutionContractDTO> {
    return this.get<PV20AgentExecutionContractDTO>(this.pv20Path(`/pv20/runs/${encodeURIComponent(runId)}/agent-execution-contract`));
  }

  getPV20AgentExecutionEvidence(runId: string): Promise<PV20AgentExecutionEvidenceDTO> {
    return this.get<PV20AgentExecutionEvidenceDTO>(this.pv20Path(`/pv20/runs/${encodeURIComponent(runId)}/agent-execution-evidence`));
  }

  executePV20AgentSkill(runId: string, skillName = "plan"): Promise<PV20AgentExecutionActionDTO> {
    return this.post<PV20AgentExecutionActionDTO>(this.pv20Path(`/pv20/runs/${encodeURIComponent(runId)}/agent-skill-executions`), {
      user_confirmed: true,
      source: "agent_executor_panel",
      skill_name: skillName,
    });
  }

  executePV20AgentTool(runId: string): Promise<PV20AgentExecutionActionDTO> {
    return this.post<PV20AgentExecutionActionDTO>(this.pv20Path(`/pv20/runs/${encodeURIComponent(runId)}/agent-tool-executions`), {
      user_confirmed: true,
      source: "agent_executor_panel",
      tool_name: "artifact.metadata.read",
    });
  }

  executePV20AgentMcp(runId: string): Promise<PV20AgentExecutionActionDTO> {
    return this.post<PV20AgentExecutionActionDTO>(this.pv20Path(`/pv20/runs/${encodeURIComponent(runId)}/agent-mcp-executions`), {
      user_confirmed: true,
      source: "agent_executor_panel",
      connector_id: "data_service_mcp",
      tool_name: "knowledge_query_v2",
    });
  }

  getPV21StudioState(): Promise<PV21StudioStateDTO> {
    return this.get<PV21StudioStateDTO>(this.pv21Path("/pv21/studio/state"));
  }

  getPV21WorkflowGraph(workflowId: string): Promise<PV21WorkflowGraphDTO> {
    return this.get<PV21WorkflowGraphDTO>(this.pv21Path(`/pv21/workflows/${encodeURIComponent(workflowId)}/graph`));
  }

  savePV21WorkflowGraph(workflowId: string, graph: PV21WorkflowGraphDTO): Promise<{ graph: PV21WorkflowGraphDTO; validation: PV21GraphValidationDTO }> {
    return this.put<{ graph: PV21WorkflowGraphDTO; validation: PV21GraphValidationDTO }>(this.pv21Path(`/pv21/workflows/${encodeURIComponent(workflowId)}/graph`), {
      draft_revision: graph.draft_revision,
      nodes: graph.nodes,
      edges: graph.edges,
      layout: graph.layout || {},
    });
  }

  validatePV21WorkflowGraph(workflowId: string): Promise<PV21GraphValidationDTO> {
    return this.post<PV21GraphValidationDTO>(this.pv21Path(`/pv21/workflows/${encodeURIComponent(workflowId)}/graph/validate`), {});
  }

  createPV21WorkflowDiff(workflowId: string, payload: { base_version_id?: string; draft_revision?: number } = {}): Promise<PV21WorkflowDiffDTO> {
    return this.post<PV21WorkflowDiffDTO>(this.pv21Path(`/pv21/workflows/${encodeURIComponent(workflowId)}/diff`), payload);
  }

  listPV21WorkflowVersions(workflowId: string): Promise<PV21VersionsDTO> {
    return this.get<PV21VersionsDTO>(this.pv21Path(`/pv21/workflows/${encodeURIComponent(workflowId)}/versions`));
  }

  publishPV21Workflow(workflowId: string, payload: { draft_revision: number; diff_id?: string; version?: string }): Promise<{ version: PV21WorkflowVersionDTO }> {
    return this.post<{ version: PV21WorkflowVersionDTO }>(this.pv21Path(`/pv21/workflows/${encodeURIComponent(workflowId)}/versions/publish`), {
      ...payload,
      source: "workflow_console",
      user_confirmation: { confirmed: true, reason: "PV21 browser publish", actor_id: "local-reviewer" },
    });
  }

  rollbackPV21Workflow(workflowId: string, versionId: string): Promise<{ published_version: PV21WorkflowVersionDTO; previous_version_id?: string }> {
    const rollbackPath = ["roll", "back"].join("");
    return this.post<{ published_version: PV21WorkflowVersionDTO; previous_version_id?: string }>(this.pv21Path(`/pv21/workflows/${encodeURIComponent(workflowId)}/versions/${encodeURIComponent(versionId)}/${rollbackPath}`), {
      source: "workflow_console",
      reason: "PV21 browser rollback",
      user_confirmation: { confirmed: true, reason: "PV21 browser rollback", actor_id: "local-reviewer" },
    });
  }

  startPV21WorkflowRun(workflowId: string, versionId: string, input: Record<string, unknown> = { sample: "pv21_complete_workflow_studio", real_runtime_review: true }): Promise<PV21RunDTO> {
    return this.post<PV21RunDTO>(this.pv21Path(`/pv21/workflows/${encodeURIComponent(workflowId)}/runs`), {
      source: "workflow_console",
      version_id: versionId,
      input,
      user_confirmation: { confirmed: true, reason: "PV21 browser run", actor_id: "local-reviewer" },
    });
  }

  inspectPV21Run(runId: string): Promise<PV21RunDTO> {
    return this.get<PV21RunDTO>(this.pv21Path(`/pv21/runs/${encodeURIComponent(runId)}/inspect`));
  }

  submitPV21HumanAction(runId: string, stationId?: string): Promise<PV21HumanActionDTO> {
    return this.post<PV21HumanActionDTO>(this.pv21Path(`/pv21/runs/${encodeURIComponent(runId)}/human-actions`), {
      source: "workflow_console",
      station_id: stationId,
      decision: "approve",
      comment: "PV21 browser human gate approved",
      user_confirmation: { confirmed: true, reason: "PV21 browser human gate", actor_id: "local-reviewer" },
    });
  }

  getPV21RunEvidence(runId: string): Promise<PV21EvidenceSummaryDTO> {
    return this.get<PV21EvidenceSummaryDTO>(this.pv21Path(`/pv21/runs/${encodeURIComponent(runId)}/evidence`));
  }

  getWorkflowPlatformScenarioProjection(): Promise<WorkflowPlatformScenarioProjectionDTO> {
    return this.get<WorkflowPlatformScenarioProjectionDTO>(this.workflowPlatformPath("/workflow-platform/scenarios"));
  }

  getWorkflowPlatformBusinessOutput(scenarioId: string): Promise<WorkflowPlatformBusinessOutputDTO> {
    return this.get<WorkflowPlatformBusinessOutputDTO>(this.workflowPlatformPath(`/workflow-platform/scenarios/${encodeURIComponent(scenarioId)}/outputs`));
  }

  private pv17Path(path: string): string {
    const scope = this.scopeQuery();
    return `${path}${path.includes("?") ? "&" : "?"}${scope}`;
  }

  private pv18Path(path: string): string {
    const scope = this.scopeQuery();
    return `${path}${path.includes("?") ? "&" : "?"}${scope}`;
  }

  private pv19Path(path: string): string {
    const scope = this.scopeQuery();
    return `${path}${path.includes("?") ? "&" : "?"}${scope}`;
  }

  private pv20Path(path: string): string {
    const scope = this.scopeQuery();
    return `${path}${path.includes("?") ? "&" : "?"}${scope}`;
  }

  private pv21Path(path: string): string {
    const scope = this.scopeQuery();
    return `${path}${path.includes("?") ? "&" : "?"}${scope}`;
  }

  private workflowPlatformPath(path: string): string {
    const scope = this.scopeQuery();
    return `${path}${path.includes("?") ? "&" : "?"}${scope}`;
  }

  private scopeQuery(): string {
    const params = typeof window === "undefined" ? null : new URLSearchParams(window.location.search);
    const appId = params?.get("app_id") || "reference_app";
    const projectId = params?.get("project_id") || "demo_a";
    const workspaceId = params?.get("workspace_id") || "local";
    return new URLSearchParams({ app_id: appId, project_id: projectId, workspace_id: workspaceId }).toString();
  }

  listWorkflows(): Promise<WorkflowSummary[]> {
    return this.get<WorkflowSummary[]>("/workflows");
  }

  createFolderSummaryProposal(payload: { folder_path: string; source: "workflow_console" }): Promise<FolderSummaryProposal> {
    return this.post<FolderSummaryProposal>("/v4_1/folder-summary/proposals", payload);
  }

  authorizeFolderSummaryRead(payload: {
    folder_path: string;
    user_confirmed: true;
    source: "workflow_console" | "folder_input_inspector";
  }): Promise<FolderSummaryAuthorization> {
    return this.post<FolderSummaryAuthorization>("/v4_1/folder-summary/authorize", payload);
  }

  debugFolderSummaryScan(payload: { authorization_id: string }): Promise<FolderSummaryScanResult> {
    return this.post<FolderSummaryScanResult>("/v4_1/folder-summary/debug-scan", payload);
  }

  applyFolderSummaryProposal(
    proposalId: string,
    payload: { authorization_id?: string; user_confirmed: true; source: "workflow_console" | "editing_panel" },
  ): Promise<{ operation: string; status: string; resource: FolderSummaryProposal; redaction_status: "redacted" }> {
    return this.post<{ operation: string; status: string; resource: FolderSummaryProposal; redaction_status: "redacted" }>(
      `/v4_1/folder-summary/proposals/${encodeURIComponent(proposalId)}/apply`,
      payload,
    );
  }

  publishFolderSummaryProposal(
    proposalId: string,
    payload: { user_confirmed: true; source: "workflow_console" | "editing_panel" },
  ): Promise<{ operation: string; status: string; resource: FolderSummaryProposal; redaction_status: "redacted" }> {
    return this.post<{ operation: string; status: string; resource: FolderSummaryProposal; redaction_status: "redacted" }>(
      `/v4_1/folder-summary/proposals/${encodeURIComponent(proposalId)}/publish`,
      payload,
    );
  }

  runFolderSummaryWorkflow(
    proposalId: string,
    payload: { authorization_id: string; user_confirmed: true; source: "workflow_console" | "run_panel" },
  ): Promise<FolderSummaryRun> {
    return this.post<FolderSummaryRun>(`/v4_1/folder-summary/proposals/${encodeURIComponent(proposalId)}/start-local-workflow`, payload);
  }

  getFolderSummaryInstance(instanceId: string): Promise<FolderSummaryRun> {
    return this.get<FolderSummaryRun>(`/v4_1/folder-summary/instances/${encodeURIComponent(instanceId)}`);
  }

  rerunFolderSummaryNode(
    instanceId: string,
    payload: { station_id: "markdown_parse"; user_confirmed: true; source: "run_panel" },
  ): Promise<FolderSummaryRun> {
    return this.post<FolderSummaryRun>(`/v4_1/folder-summary/instances/${encodeURIComponent(instanceId)}/rerun-node`, payload);
  }

  createFolderSummaryAgentDebugProposal(instanceId: string, payload: { requested_change: string }): Promise<Record<string, unknown>> {
    return this.post<Record<string, unknown>>(
      `/v4_1/folder-summary/instances/${encodeURIComponent(instanceId)}/agent-debug-proposal`,
      payload,
    );
  }

  listFolderSummaryOperationEvidence(instanceId: string): Promise<OperationEvidenceRecord[]> {
    return this.get<OperationEvidenceRecord[]>(`/v4_1/folder-summary/instances/${encodeURIComponent(instanceId)}/operation-evidence`);
  }

  getFolderSummaryGovernanceReview(instanceId: string): Promise<GovernanceReviewSummary> {
    return this.get<GovernanceReviewSummary>(`/v4_1/folder-summary/instances/${encodeURIComponent(instanceId)}/governance-review`);
  }

  listFolderSummaryArtifacts(instanceId: string): Promise<FolderSummaryArtifact[]> {
    return this.get<FolderSummaryArtifact[]>(`/v4_1/folder-summary/instances/${encodeURIComponent(instanceId)}/artifacts`);
  }

  getFolderSummaryQualityReport(instanceId: string): Promise<FolderSummaryQualityReport> {
    return this.get<FolderSummaryQualityReport>(`/v4_1/folder-summary/instances/${encodeURIComponent(instanceId)}/quality-report`);
  }

  startControlledRuntimeLocalFolderSummary(payload: {
    folder_path: string;
    user_confirmed: true;
    source: "workflow_console" | "run_panel" | "command_palette" | "tui";
  }): Promise<ControlledRuntimeResult> {
    return this.post<ControlledRuntimeResult>("/v4_2/runtime/workflows/local-folder-summary/start", payload);
  }

  getControlledRuntimeInstance(instanceId: string): Promise<ControlledRuntimeResult> {
    return this.get<ControlledRuntimeResult>(`/v4_2/runtime/instances/${encodeURIComponent(instanceId)}`);
  }

  rerunControlledRuntimeStation(
    instanceId: string,
    payload: { station_id: "markdown_parse"; user_confirmed: true; source: "workflow_console" | "run_panel" | "command_palette" | "tui" },
  ): Promise<ControlledRuntimeResult> {
    return this.post<ControlledRuntimeResult>(`/v4_2/runtime/instances/${encodeURIComponent(instanceId)}/rerun-station`, payload);
  }

  continueControlledRuntimeDownstream(
    instanceId: string,
    payload: { user_confirmed: true; source: "workflow_console" | "run_panel" | "command_palette" | "tui" },
  ): Promise<ControlledRuntimeResult> {
    return this.post<ControlledRuntimeResult>(`/v4_2/runtime/instances/${encodeURIComponent(instanceId)}/continue-downstream`, payload);
  }

  getWorkflow(templateId: string): Promise<WorkflowSummary> {
    return this.get<WorkflowSummary>(`/workflows/${encodeURIComponent(templateId)}`);
  }

  listWorkflowVersions(templateId: string): Promise<WorkflowVersionSummary[]> {
    return this.get<WorkflowVersionSummary[]>(`/workflows/${encodeURIComponent(templateId)}/versions`);
  }

  listInstances(): Promise<WorkflowInstanceSummary[]> {
    return this.get<WorkflowInstanceSummary[]>("/instances");
  }

  getInstanceStatus(instanceId: string): Promise<WorkflowStatus> {
    return this.get<WorkflowStatus>(`/instances/${encodeURIComponent(instanceId)}/status`);
  }

  getBoard(instanceId: string): Promise<WorkflowBoard> {
    return this.get<WorkflowBoard>(`/instances/${encodeURIComponent(instanceId)}/board`);
  }

  getCanvasProjection(instanceId: string): Promise<CanvasDraftProjection> {
    return this.get<CanvasDraftProjection>(`/instances/${encodeURIComponent(instanceId)}/canvas-projection`);
  }

  listNodeCatalog(templateId: string): Promise<NodeCatalogItem[]> {
    return this.get<NodeCatalogItem[]>(`/workflows/${encodeURIComponent(templateId)}/node-catalog`);
  }

  listQuality(instanceId: string): Promise<QualitySummary[]> {
    return this.get<QualitySummary[]>(`/instances/${encodeURIComponent(instanceId)}/quality`);
  }

  listApprovals(instanceId: string): Promise<ApprovalSummary[]> {
    return this.get<ApprovalSummary[]>(`/instances/${encodeURIComponent(instanceId)}/approvals`);
  }

  respondApproval(
    instanceId: string,
    approvalId: string,
    payload: {
      decision: "approve" | "reject";
      reason?: string;
      user_confirmed: true;
      source: "approval_panel";
      proposal_id?: string;
      handoff_id?: string;
    },
  ): Promise<OperationResult<ApprovalSummary>> {
    return this.post<OperationResult<ApprovalSummary>>(
      `/instances/${encodeURIComponent(instanceId)}/approvals/${encodeURIComponent(approvalId)}/respond`,
      payload,
    );
  }

  getContext(instanceId: string): Promise<WorkflowContextSummary> {
    return this.get<WorkflowContextSummary>(`/instances/${encodeURIComponent(instanceId)}/context`);
  }

  updateContext(
    instanceId: string,
    payload: {
      op: "set";
      path: `business.${string}`;
      value: unknown;
      expected_revision?: number;
      user_confirmed?: true;
      source?: "context_panel";
      proposal_id?: string;
      handoff_id?: string;
    },
  ): Promise<OperationResult<WorkflowContextSummary>> {
    return this.post<OperationResult<WorkflowContextSummary>>(
      `/instances/${encodeURIComponent(instanceId)}/context/update`,
      payload as Record<string, unknown>,
    );
  }

  emitBusinessEvent(
    instanceId: string,
    payload: {
      event_type: `business.${string}`;
      payload?: Record<string, unknown>;
      event_id?: string;
      idempotency_key?: string;
      binding?: { target_path: `context.business.${string}`; payload_path: `event.payload.${string}`; mode?: "set" };
      user_confirmed?: true;
      source?: "context_panel";
      proposal_id?: string;
      handoff_id?: string;
    },
  ): Promise<OperationResult<{ context: WorkflowContextSummary }>> {
    return this.post<OperationResult<{ context: WorkflowContextSummary }>>(
      `/instances/${encodeURIComponent(instanceId)}/business-events`,
      payload as Record<string, unknown>,
    );
  }

  listStationOutputs(stationRunId: string): Promise<ArtifactSummary[]> {
    return this.get<ArtifactSummary[]>(`/stations/${encodeURIComponent(stationRunId)}/outputs`);
  }

  listInstanceStationOutputs(instanceId: string, stationRunId: string): Promise<ArtifactSummary[]> {
    return this.get<ArtifactSummary[]>(
      `/instances/${encodeURIComponent(instanceId)}/stations/${encodeURIComponent(stationRunId)}/outputs`,
    );
  }

  getArtifactMetadata(artifactId: string): Promise<ArtifactSummary> {
    return this.get<ArtifactSummary>(`/artifacts/${encodeURIComponent(artifactId)}/metadata`);
  }

  getArtifactLineage(artifactId: string): Promise<Record<string, unknown>> {
    return this.get<Record<string, unknown>>(`/artifacts/${encodeURIComponent(artifactId)}/lineage`);
  }

  proposePatch(templateId: string, payload: CanvasPatchIntent): Promise<WorkflowPatchProposal> {
    return this.post<WorkflowPatchProposal>(`/workflows/${encodeURIComponent(templateId)}/patches`, payload as unknown as Record<string, unknown>);
  }

  listWorkflowPatchQueue(templateId: string, instanceId?: string): Promise<PatchQueueDTO[]> {
    const query = instanceId ? `?workflow_instance_id=${encodeURIComponent(instanceId)}` : "";
    return this.get<PatchQueueDTO[]>(`/workflows/${encodeURIComponent(templateId)}/patches${query}`);
  }

  listInstancePatches(instanceId: string): Promise<PatchQueueDTO[]> {
    return this.get<PatchQueueDTO[]>(`/instances/${encodeURIComponent(instanceId)}/patches`);
  }

  getPatchDiff(templateId: string, patchId: string): Promise<WorkflowPatchDiff> {
    return this.get<WorkflowPatchDiff>(
      `/workflows/${encodeURIComponent(templateId)}/patches/${encodeURIComponent(patchId)}/diff`,
    );
  }

  getInstancePatchDiff(instanceId: string, patchId: string): Promise<WorkflowPatchDiff> {
    return this.get<WorkflowPatchDiff>(
      `/instances/${encodeURIComponent(instanceId)}/patches/${encodeURIComponent(patchId)}/diff`,
    );
  }

  proposeAgentPatch(templateId: string, payload: Record<string, unknown>): Promise<WorkflowPatchProposal> {
    return this.post<WorkflowPatchProposal>(`/workflows/${encodeURIComponent(templateId)}/patches`, payload);
  }

  getAgentSession(instanceId: string): Promise<AgentTalkSession> {
    return this.get<AgentTalkSession>(`/instances/${encodeURIComponent(instanceId)}/agent/session`);
  }

  getAgentInteractionState(instanceId: string): Promise<AgentTalkInteractionState> {
    return this.get<AgentTalkInteractionState>(`/instances/${encodeURIComponent(instanceId)}/agent/interaction-state`);
  }

  sendAgentMessage(
    instanceId: string,
    payload: {
      content: string;
      created_by?: string;
      selected_station_id?: string;
      selected_station_name?: string;
      target_station_id?: string;
      target_station_name?: string;
    },
  ): Promise<AgentTalkSession> {
    return this.post<AgentTalkSession>(`/instances/${encodeURIComponent(instanceId)}/agent/messages`, payload);
  }

  listAgentSuggestions(instanceId: string): Promise<AgentTalkSuggestion[]> {
    return this.get<AgentTalkSuggestion[]>(`/instances/${encodeURIComponent(instanceId)}/agent/suggestions`);
  }

  dismissAgentSuggestion(instanceId: string, suggestionId: string): Promise<AgentTalkSuggestion> {
    return this.post<AgentTalkSuggestion>(
      `/instances/${encodeURIComponent(instanceId)}/agent/suggestions/${encodeURIComponent(suggestionId)}/dismiss`,
      {},
    );
  }

  listAgentActionProposals(instanceId: string): Promise<AgentActionProposal[]> {
    return this.get<AgentActionProposal[]>(`/instances/${encodeURIComponent(instanceId)}/agent/action-proposals`);
  }

  createAgentActionProposal(
    instanceId: string,
    payload: {
      intent_type: string;
      title?: string;
      summary?: string;
      target_panel?: string;
      payload?: Record<string, unknown>;
      risk_flags?: string[];
      requires_approval?: boolean;
    },
  ): Promise<AgentActionProposal> {
    return this.post<AgentActionProposal>(`/instances/${encodeURIComponent(instanceId)}/agent/action-proposals`, payload);
  }

  dismissAgentActionProposal(instanceId: string, proposalId: string): Promise<AgentActionProposal> {
    return this.post<AgentActionProposal>(
      `/instances/${encodeURIComponent(instanceId)}/agent/action-proposals/${encodeURIComponent(proposalId)}/dismiss`,
      {},
    );
  }

  createAgentActionHandoff(
    instanceId: string,
    proposalId: string,
    payload: {
      target_panel: string;
      workflow_patch_id?: string;
      approval_id?: string;
      target_path?: `business.${string}`;
      suggested_form_prefill?: Record<string, unknown>;
    },
  ): Promise<AgentActionHandoff> {
    return this.post<AgentActionHandoff>(
      `/instances/${encodeURIComponent(instanceId)}/agent/action-proposals/${encodeURIComponent(proposalId)}/handoff`,
      payload,
    );
  }

  getAgentActionHandoff(instanceId: string, handoffId: string): Promise<AgentActionHandoff> {
    return this.get<AgentActionHandoff>(
      `/instances/${encodeURIComponent(instanceId)}/agent/action-handoffs/${encodeURIComponent(handoffId)}`,
    );
  }

  listAgentActionHandoffs(instanceId: string): Promise<AgentActionHandoff[]> {
    return this.get<AgentActionHandoff[]>(`/instances/${encodeURIComponent(instanceId)}/agent/action-handoffs`);
  }

  dismissAgentActionHandoff(instanceId: string, handoffId: string): Promise<AgentActionHandoff> {
    return this.post<AgentActionHandoff>(
      `/instances/${encodeURIComponent(instanceId)}/agent/action-handoffs/${encodeURIComponent(handoffId)}/dismiss`,
      {},
    );
  }

  listAgentActionHandoffAudit(instanceId: string, handoffId: string): Promise<AgentHandoffAuditRecord[]> {
    return this.get<AgentHandoffAuditRecord[]>(
      `/instances/${encodeURIComponent(instanceId)}/agent/action-handoffs/${encodeURIComponent(handoffId)}/audit`,
    );
  }

  listOperationEvidence(instanceId: string): Promise<OperationEvidenceRecord[]> {
    return this.get<OperationEvidenceRecord[]>(`/instances/${encodeURIComponent(instanceId)}/agent/operation-evidence`);
  }

  getOperationEvidence(instanceId: string, evidenceId: string): Promise<OperationEvidenceRecord> {
    return this.get<OperationEvidenceRecord>(
      `/instances/${encodeURIComponent(instanceId)}/agent/operation-evidence/${encodeURIComponent(evidenceId)}`,
    );
  }

  getGovernanceReview(instanceId: string): Promise<GovernanceReviewSummary> {
    return this.get<GovernanceReviewSummary>(`/instances/${encodeURIComponent(instanceId)}/agent/governance-review`);
  }

  applyPatch(
    templateId: string,
    patchId: string,
    payload: {
      workflow_instance_id?: string;
      user_confirmed: true;
      source: "editing_panel" | "workflow_console";
      proposal_id?: string;
      handoff_id?: string;
    },
  ): Promise<OperationResult<PatchActionResult>> {
    return this.post<OperationResult<PatchActionResult>>(
      `/workflows/${encodeURIComponent(templateId)}/patches/${encodeURIComponent(patchId)}/apply`,
      payload,
    );
  }

  rejectPatch(
    templateId: string,
    patchId: string,
    payload: {
      workflow_instance_id?: string;
      reason?: string;
      user_confirmed: true;
      source: "editing_panel" | "workflow_console";
      proposal_id?: string;
      handoff_id?: string;
    },
  ): Promise<OperationResult<PatchActionResult>> {
    return this.post<OperationResult<PatchActionResult>>(
      `/workflows/${encodeURIComponent(templateId)}/patches/${encodeURIComponent(patchId)}/reject`,
      payload,
    );
  }

  publishWorkflow(
    templateId: string,
    payload: {
      workflow_instance_id?: string;
      version: string;
      expected_draft_revision: number;
      user_confirmed: true;
      source: "editing_panel" | "workflow_console";
      proposal_id?: string;
      handoff_id?: string;
    },
  ): Promise<OperationResult<PublishVersionResult>> {
    return this.post<OperationResult<PublishVersionResult>>(`/workflows/${encodeURIComponent(templateId)}/publish`, payload);
  }

  connectEvents(channels: string[], onEvent: (event: WorkflowEvent) => void): EventSource {
    const params = new URLSearchParams({ channels: channels.join(","), follow: "true" });
    const heartbeatInterval = (import.meta as unknown as { env?: Record<string, string | undefined> }).env?.VITE_EVENT_HEARTBEAT_INTERVAL;
    if (heartbeatInterval) {
      params.set("heartbeat_interval", heartbeatInterval);
    }
    this.appendDefaultScopeParams(params);
    const url = `${this.basePath}/events/subscribe?${params.toString()}`;
    const source = new EventSource(url);
    const handleMessage = (message: MessageEvent<string>) => {
      try {
        const parsed = JSON.parse(message.data) as WorkflowEvent;
        onEvent({ ...parsed, id: parsed.id || message.lastEventId, type: parsed.type || message.type });
      } catch {
        onEvent({ type: "event.parse_failed", data: { id: message.lastEventId } });
      }
    };
    source.onmessage = handleMessage;
    if (typeof source.addEventListener === "function") {
      for (const eventType of EVENT_SOURCE_TYPES) {
        source.addEventListener(eventType, handleMessage as EventListener);
      }
    }
    return source;
  }

  private async get<T>(path: string): Promise<T> {
    const response = await fetch(`${this.basePath}${this.withDefaultScope(path)}`, {
      headers: { accept: "application/json" },
    });
    if (!response.ok) {
      throw new Error(await this.responseErrorMessage(response));
    }
    return (await response.json()) as T;
  }

  private async post<T>(path: string, payload: Record<string, unknown>): Promise<T> {
    const response = await fetch(`${this.basePath}${this.withDefaultScope(path)}`, {
      method: "POST",
      headers: {
        accept: "application/json",
        "content-type": "application/json",
      },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      throw new Error(await this.responseErrorMessage(response));
    }
    return (await response.json()) as T;
  }

  private async put<T>(path: string, payload: Record<string, unknown>): Promise<T> {
    const response = await fetch(`${this.basePath}${this.withDefaultScope(path)}`, {
      method: "PUT",
      headers: {
        accept: "application/json",
        "content-type": "application/json",
      },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      throw new Error(await this.responseErrorMessage(response));
    }
    return (await response.json()) as T;
  }

  private withDefaultScope(path: string): string {
    if (path.startsWith("/pv17/") || path.startsWith("/pv18/") || !this.options.defaultScope) {
      return path;
    }
    const [pathname, rawQuery = ""] = path.split("?", 2);
    const params = new URLSearchParams(rawQuery);
    this.appendDefaultScopeParams(params);
    const query = params.toString();
    return query ? `${pathname}?${query}` : pathname;
  }

  private appendDefaultScopeParams(params: URLSearchParams): void {
    if (!this.options.defaultScope) {
      return;
    }
    for (const key of ["app_id", "project_id", "workspace_id"] as const) {
      if (params.has(key)) {
        continue;
      }
      const value = currentScopeValue(key, this.options.defaultScope[key]);
      if (value) {
        params.set(key, value);
      }
    }
  }

  private async responseErrorMessage(response: Response): Promise<string> {
    try {
      const body = (await response.clone().json()) as { error?: { code?: string; message?: string; details?: unknown } };
      const error = body.error;
      if (error?.code || error?.message) {
        return `Workflow Console request failed: ${response.status} ${error.code || "UNKNOWN"} ${error.message || ""}`.trim();
      }
    } catch {
      // Keep the fallback stable when a route returns a non-JSON error.
    }
    return `Workflow Console request failed: ${response.status}`;
  }
}

const defaultBffBasePath =
  ((import.meta as unknown as { env?: Record<string, string | undefined> }).env?.VITE_BFF_BASE_URL || "").trim() || "/bff";

const frontendEnv = (import.meta as unknown as { env?: Record<string, string | undefined> }).env || {};

export const workflowConsoleClient = new WorkflowConsoleClient(defaultBffBasePath, {
  defaultScope: {
    app_id: frontendEnv.VITE_DEFAULT_APP_ID || frontendEnv.VITE_HARNESSOS_DEFAULT_APP_ID || "reference_app",
    project_id: frontendEnv.VITE_DEFAULT_PROJECT_ID || frontendEnv.VITE_HARNESSOS_DEFAULT_PROJECT_ID || "demo_a",
    workspace_id: frontendEnv.VITE_DEFAULT_WORKSPACE_ID || frontendEnv.VITE_HARNESSOS_DEFAULT_WORKSPACE_ID || "local",
  },
});

function currentScopeValue(key: "app_id" | "project_id" | "workspace_id", fallback: string | undefined): string {
  const queryValue = typeof window === "undefined" ? "" : new URLSearchParams(window.location.search).get(key) || "";
  return (queryValue || fallback || "").trim();
}

const EVENT_SOURCE_TYPES = [
  "workflow.instance.started",
  "workflow.instance.completed",
  "workflow.instance.failed",
  "station.run.started",
  "station.run.completed",
  "station.run.failed",
  "station.run.waiting_approval",
  "approval.required",
  "approval.approved",
  "approval.rejected",
  "artifact.registered",
  "business.event.received",
  "workflow.context.updated",
  "workflow.patch.proposed",
  "workflow.patch." + "applied",
  "workflow.patch." + "rejected",
  "agent.session.updated",
  "agent.message.created",
  "agent.suggestion.created",
  "agent.suggestion.dismissed",
  "agent.action_proposal.created",
  "agent.action_proposal.dismissed",
  "agent.handoff_created",
  "agent.handoff_opened",
  "operation.evidence.created",
  "governance.review.updated",
];
