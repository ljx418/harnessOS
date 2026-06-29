# PV22 External App Contract Target Architecture

用途：定义 PV22 外部应用接入契约目标架构、代码实体、DTO 边界和交互关系。
阅读对象：架构、SDK、BFF、后端、安全和测试人员。
边界：本文描述目标架构，不是运行证据；不得据此声明外部应用接入已完成。

## 1. Architecture Intent

PV22 将现有 SDK、BFF template、AppProfile、capability token 和 Gateway 协议收敛为一条外部应用接入路径：

```text
External UI
  -> App-owned BFF Template
  -> HarnessOS SDK / HTTP Client
  -> Capability Token Auth
  -> Gateway RPC / BFF DTO
  -> Runtime / Artifact / Event / Evidence Stores
```

外部应用拥有自己的 UI 与业务 facade；HarnessOS 提供稳定 SDK、协议、权限和证据边界。

## 2. Concrete Code Entity Map

| Layer | Code entity | Current state | PV22 responsibility |
| --- | --- | --- | --- |
| App profile | `core/apps/profiles.py` | 已有 built-in profiles。 | 定义 external profile contract、allowed origins、default capabilities 和 compatibility notes。 |
| Capability auth | `apps/api/auth.py`, `core/protocol/auth.py` | 已有 token、scope、capability 校验。 | 冻结外部 auth negative fixture 和错误语义。 |
| Gateway protocol | `apps/gateway/service.py`, `apps/gateway/protocol.py` | 已有 RPC registry。 | 选择外部可用 method subset，并记录 forbidden method。 |
| Python SDK | `sdk/python/harnessos_client/*` | 已有 client/model/transport。 | 增加或验证最小 external app smoke。 |
| TypeScript SDK | `sdk/typescript/src/*` | 已有 client/embed/events/model。 | 增加或验证最小 external app smoke。 |
| BFF template | `templates/bff/fastapi/*` | 已有 full template。 | 验证 scope binding、capability forwarding、error mapping。 |
| Minimal BFF template | `templates/bff/fastapi_minimal/*` | 已有 minimal template。 | 验证最小 read/write route boundary。 |
| Reference app | `examples/reference_app/*` | 作为接入样例资产。 | 跑通 external app E2E 和 evidence package。 |
| Evidence | `docs/design/V12-V15.x/evidence/pv22-external-app-contract/` | 待生成。 | 保存 SDK logs、template smoke、negative fixtures 和 browser evidence。 |

## 3. Contract Planes

| Plane | Responsibility | Must expose | Must not expose |
| --- | --- | --- | --- |
| Protocol | 稳定外部 method/event/error contract。 | session、turn、event、artifact、workflow read subset。 | internal/debug/raw store。 |
| Identity | 绑定 app、origin、scope、capability。 | token claims、AppProfile bounds、scope mismatch errors。 | unrestricted admin by default。 |
| BFF | 外部 App 自己的服务端 facade。 | business route、safe DTO、redacted errors。 | browser raw `/v1/rpc` passthrough。 |
| SDK | 开发者调用入口。 | typed client、errors、events、protocol snapshot。 | secret logging、scope escalation。 |
| Evidence | 审计接入结果。 | route log、negative fixtures、redaction、No False Green。 | production claim。 |

## 4. External Contract Subset

PV22 首轮只冻结最小稳定子集，避免一次性承诺全量平台接口。

| Capability | Example operation | Notes |
| --- | --- | --- |
| `sessions` | create/read session | app/profile/scope bound。 |
| `turns` | submit user turn | 不允许 internal method。 |
| `events` | stream/read events | 只读外部事件流。 |
| `artifacts.read` | read artifact metadata/content | 必须 redaction。 |
| `workflows.read` | read visible workflow state | 不含 raw store。 |
| `approvals.read` | read approval state | mutation 需单独确认。 |

## 5. Interaction Flow

1. External app loads config with `app_id`, allowed origin and scope defaults.
2. App-owned BFF validates user/session and obtains a capability token.
3. BFF calls SDK with token and scope.
4. SDK calls HarnessOS external route or Gateway RPC.
5. Auth layer verifies token against `AppProfile`.
6. Gateway returns typed result or stable error.
7. BFF maps result into app-specific DTO.
8. Browser consumes app BFF DTO only.
9. Acceptance runner captures SDK logs, route log and negative fixtures.

## 6. Architecture Red Lines

- No external default admin capability.
- No `scope_mode=all`.
- No browser raw Gateway passthrough.
- No token origin outside AppProfile bounds.
- No undocumented method in the bounded contract claim.
- No production readiness claim.

