# PV17 目标架构检视

结论：PASS。

- Browser -> WorkflowConsoleClient -> apps/api/routers/bff.py -> GatewayService -> workflow store 的链路已由本次 E2E 观测。
- 浏览器请求只使用 /bff/pv17 正式前缀，没有 direct internal runtime/store 路径。
- Evidence Review 仅读取运行证据 refs，不构造 runtime truth。
- PV16 test-only BFF 未作为 PV17 正向路径使用。