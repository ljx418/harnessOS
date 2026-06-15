# V12 Product Entity And Workbench Contracts

## Schema Rules

All V12 DTOs and schemas must use explicit required fields and reject unknown
fields. Evidence and UI projections must use redacted refs only.

Required common fields:

- `schema_version`
- `tenant_id`
- `workspace_id`
- `project_id`
- `app_id` where applicable
- `actor_id`
- `request_id`
- `correlation_id`
- `audit_ref`
- `created_at`
- `updated_at` where mutable

Forbidden raw fields:

- raw secret
- raw token
- raw provider payload
- raw connector payload
- raw prompt
- raw artifact content
- signed URL

## Product Entity Schemas

### StudioWorkspace

Required:

- `workspace_id`
- `tenant_id`
- `name`
- `owner_actor_id`
- `status`
- `audit_ref`
- `created_at`

Status values:

- `active`
- `archived`
- `blocked`

### StudioProject

Required:

- `project_id`
- `workspace_id`
- `tenant_id`
- `name`
- `description`
- `status`
- `audit_ref`
- `created_at`

### StudioApp

Required:

- `app_id`
- `project_id`
- `workspace_id`
- `tenant_id`
- `name`
- `runtime_scope_ref`
- `audit_ref`
- `created_at`

### StudioFileAsset

Required:

- `file_asset_id`
- `project_id`
- `workspace_id`
- `tenant_id`
- `display_name`
- `mime_type`
- `redacted_content_ref`
- `audit_ref`
- `created_at`

Must not expose raw file content.

### StationAgentProfile

Required:

- `agent_profile_id`
- `station_id`
- `workspace_id`
- `project_id`
- `app_id`
- `role`
- `goal`
- `memory_policy_ref`
- `model_profile_ref`
- `tool_binding_refs`
- `skill_binding_refs`
- `mcp_binding_refs`
- `credential_ref_policy`
- `audit_ref`
- `created_at`

Boundary:

- This is configuration, not proof of Agent executor readiness.
- Credential material must be represented as redacted refs only.

### StationAgentBinding

Required:

- `binding_id`
- `station_id`
- `agent_profile_id`
- `workflow_spec_ref`
- `policy_decision_ref`
- `capability_decision_ref`
- `audit_ref`
- `created_at`

### ToolCapabilityBinding / SkillPackageBinding / McpCapabilityBinding

Required:

- `binding_id`
- `workspace_id`
- `project_id`
- `app_id`
- `capability_ref`
- `scope`
- `policy_decision_ref`
- `audit_ref`
- `created_at`

Scope values:

- `workspace`
- `project`
- `app`
- `station`

## Workbench Schemas

## Canvas Workbench Schemas

### CanvasReadModel

Required:

- `canvas_read_model_id`
- `workspace_id`
- `project_id`
- `app_id`
- `node_refs`
- `edge_refs`
- `selected_node_ref`
- `inspector_projection_ref`
- `toolbar_state`
- `evidence_scope`
- `audit_ref`
- `created_at`

Boundary:

- This is a read-only browser projection in V12.
- It must not be treated as `WorkflowSpecGraph`, `WorkflowDraft`,
  `WorkflowVersion`, `WorkflowInstance` or runtime truth.

### CanvasNodeProjection

Required:

- `node_ref`
- `node_type`
- `display_title`
- `status`
- `position`
- `entity_ref`
- `port_refs`
- `evidence_refs`
- `audit_ref`

Node type values:

- `project`
- `station_agent`
- `workflow_proposal`
- `tool_capability`
- `skill_package`
- `mcp_capability`
- `quality`
- `evidence`

Boundary:

- V12 nodes are display projections only.
- Editable node/edge semantics belong to V13.

### CanvasInspectorProjection

Required:

- `inspector_projection_ref`
- `selected_node_ref`
- `entity_type`
- `role`
- `goal`
- `memory_policy_ref`
- `model_profile_ref`
- `tool_binding_refs`
- `skill_binding_refs`
- `mcp_binding_refs`
- `quality_refs`
- `evidence_refs`
- `redaction_status`
- `audit_ref`

Boundary:

- Inspector projection may show redacted refs and summaries only.
- It must not expose raw prompt, raw file content, raw credential material,
  raw provider payload or raw artifact content.

### WorkbenchConversation

Required:

- `conversation_id`
- `workspace_id`
- `project_id`
- `app_id`
- `participant_refs`
- `goal_summary`
- `message_refs`
- `proposal_timeline_ref`
- `evidence_scope`
- `audit_ref`
- `created_at`

Boundary:

- Conversation transcript is not runtime evidence.

### GoalIntakeMessage

Required:

- `message_id`
- `conversation_id`
- `actor_id`
- `role`
- `redacted_text_ref`
- `attachment_refs`
- `created_at`

Role values:

- `user`
- `assistant`
- `system`

### WorkbenchAttachmentRef

Required:

- `attachment_ref`
- `conversation_id`
- `file_asset_id`
- `redacted_content_ref`
- `audit_ref`

### WorkbenchProposalTimeline

Required:

- `proposal_timeline_id`
- `conversation_id`
- `workflow_diff_proposal_ref`
- `events`
- `current_state`
- `audit_ref`

States:

- `goal_received`
- `proposal_drafting`
- `proposal_ready`
- `awaiting_user_confirmation`
- `revised`
- `rejected`
- `handoff_ready`

## Negative Fixtures Required

- unknown field rejected
- missing tenant/workspace/project rejected
- wrong workspace denied
- raw credential field rejected
- raw prompt text field rejected
- station binding without policy decision rejected
- canvas read model marked as runtime truth rejected
- canvas node with unknown node type rejected
- canvas inspector with raw credential or raw prompt rejected
- workbench transcript marked as runtime evidence rejected
