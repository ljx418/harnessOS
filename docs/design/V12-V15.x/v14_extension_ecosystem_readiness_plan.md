# V14 Plugin Skill Tool MCP Ecosystem Readiness Plan

## Current Decision

V14 is blocked until V12 scope/policy evidence and V13 Studio/DSL evidence
exist. This document supports V14 implementation-readiness review after those
dependencies pass.

Allowed after dependency PASS:

- Plugin, skill, tool and MCP manifest planning.
- Compatibility resolver planning.
- Scoped activation and binding planning.
- Unsafe package denial and evidence planning.

Blocked:

- Executing unreviewed plugin code.
- Unrestricted MCP/tool invocation.
- Raw secret exposure.
- Production marketplace or unrestricted plugin ecosystem claim.

## V14 Objective

V14 gives HarnessOS a governed extension ecosystem inspired by Xpert's plugin
and tool management, while preserving HarnessOS policy boundaries. Users can
inspect, install, activate and bind approved plugins, skills, tools and MCP
capabilities to selected workspace/project/app/station scopes.

## Required Schemas And DTOs

- `PluginPackageManifest`
- `SkillPackageManifest`
- `ToolCapabilityManifest`
- `McpConnectorManifest`
- `ExtensionCompatibilityDecision`
- `ExtensionInstallDecision`
- `ExtensionActivationDecision`
- `ExtensionConfigRef`
- `ScopedCapabilityBinding`
- `UnsafePackageDenial`

Common required fields:

- `schema_version`
- `package_id`
- `package_type`
- `workspace_id`
- `project_id`
- `app_id`
- `requested_scope`
- `permission_refs`
- `credential_ref_requirements`
- `compatibility_decision_ref`
- `policy_decision_ref`
- `audit_ref`

Forbidden raw fields:

- raw secret
- raw token
- raw connector payload
- raw provider payload
- arbitrary executable payload without review

## Compatibility Resolver Rules

Must check:

- HarnessOS runtime version
- package schema version
- required permissions
- required credential refs
- allowed workspace/project/app/station scope
- source trust level
- declared tool/MCP operations
- redaction policy
- sandbox policy

Decision values:

- `approved`
- `denied`
- `needs_review`
- `incompatible`
- `blocked_by_policy`

## Implementation Slices

### V14-1 Manifest And Compatibility

Exit evidence:

- valid manifest PASS
- incompatible version denied
- unknown permission denied
- raw secret rejected

### V14-2 Install / Disable / Uninstall Lifecycle

Exit evidence:

- install decision
- activation decision
- disable decision
- uninstall evidence
- audit refs

### V14-3 Agent Binding UI And BFF

Exit evidence:

- Agent configuration panel shows scoped capabilities
- unsafe package remains unavailable
- browser network only uses BFF routes
- scoped binding refs match policy decisions

### V14-4 Unsafe Denial And MCP Boundary

Exit evidence:

- unsafe package denied with reason
- MCP/tool invocation cannot bypass capability resolver
- credential config uses redacted refs only

## User Scenarios

### US-V14-01 Install Approved Skill

User installs a workspace skill and binds it to one station Agent.

PASS:

- manifest validates
- compatibility approved
- scoped activation visible
- Agent panel shows skill only in allowed scope

### US-V14-02 Deny Unsafe Plugin

User attempts to install a plugin with unsafe permission or unknown executable
payload.

PASS:

- install denied
- denial reason visible
- audit ref recorded
- plugin not available to Agents

### US-V14-03 MCP Connector Scoped Binding

User configures an MCP connector ref for a station Agent.

PASS:

- config uses redacted refs
- capability binding is scoped
- invocation outside scope denied

## V14 Evidence Package

```text
docs/design/V12-V15.x/evidence/v14-extension-ecosystem/
```

Required:

- `v14-acceptance-data.json`
- `plugin-manifest.json`
- `skill-manifest.json`
- `mcp-connector-manifest.json`
- `compatibility-decision.json`
- `install-decision.json`
- `activation-decision.json`
- `unsafe-package-denial.json`
- `agent-binding-screenshot.png`
- `browser-network-log.json`
- `redaction-scan.txt`
- `no-false-green-scan.txt`
- `prd-spec-review.md`

## V14 Stop Conditions

- Plugin install executes unreviewed code.
- Raw secret or token appears in config or evidence.
- Tool/MCP bypasses capability resolver.
- Unsafe package appears as active capability.
- Agent configuration claims unrestricted tool execution.
- UI copy claims unrestricted plugin ecosystem ready.

