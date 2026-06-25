# V14 PRD And Architecture Coverage Audit

## Purpose

This audit maps the V14 governed extension ecosystem pilot to the V12-V15 PRD
and target architecture. It is used before implementation and again during
V14-SA aggregate acceptance.

## PRD Coverage

| PRD Scenario | V14 Coverage | Evidence Required |
| --- | --- | --- |
| Plugin/Skill install | User inspects an approved package and sees compatibility PASS. | package manifest, compatibility decision, browser screenshot |
| Scoped capability binding | User binds approved capability to selected Agent/Station scope. | activation decision, scoped binding refs, Agent binding screenshot |
| Unsafe package denial | User attempts unsafe package and sees denial reason. | unsafe denial fixture, audit ref, browser screenshot |
| MCP connector scoped binding | User configures MCP connector through redacted refs only. | MCP manifest, redacted config refs, scoped capability binding |
| Agent configuration panel | Agent panel shows only allowed capabilities after activation. | browser screenshot, BFF route log |

## Target Architecture Coverage

| Architecture Plane | V14 Responsibility | Status |
| --- | --- | --- |
| Plugin / Skill / Tool / MCP Ecosystem | Own manifests, compatibility, activation, denial and scoped binding. | Covered |
| Agent/Station Configuration | Surface scoped capability refs in Agent/Station inspector. | Covered |
| Studio BFF And DTO | Route browser extension actions through BFF DTOs. | Covered |
| Artifact / Evidence / Quality | Emit acceptance data, manifests, audit refs and scans. | Covered |
| Runtime Gateway And Controlled Execution | Must not be bypassed by extensions. | Boundary covered |
| Observability / Audit / Operations | Record policy decisions and audit refs only. | Covered |

## Evidence-To-Claim Matrix

| Claim | Minimum Evidence |
| --- | --- |
| V14 governed extension ecosystem pilot ready for review | acceptance data, artifact manifest, manifests, compatibility decisions, scoped activation, unsafe denial, screenshots, route logs and scans |
| Approved capability is scoped | activation decision, scoped binding refs and Agent panel screenshot |
| Unsafe package is denied | denial fixture, visible reason, audit ref and route log |
| Secrets are protected | redaction scan and redacted config refs |

## Blocking Risks

| Risk | Severity | Required Guard |
| --- | --- | --- |
| Plugin install executes unreviewed code | Fatal | V14 evidence must be manifest/activation pilot only unless reviewed execution is explicitly added later. |
| Global capability leakage | Major | Scoped activation must include workspace/project/app/Agent/Station refs. |
| Secret leakage | Fatal | Raw secret patterns cause redaction FAIL. |
| Product overclaim | Major | No False Green scan must block unrestricted ecosystem wording. |

## Audit Opinion

The V14 PRD and target architecture coverage is complete enough to guide the
next implementation slice after reviewer acceptance. The coverage remains
bounded to a governed extension ecosystem pilot.
