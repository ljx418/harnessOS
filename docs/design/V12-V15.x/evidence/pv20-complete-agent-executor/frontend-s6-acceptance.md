# PV20-S6 Frontend Acceptance

用途：记录 PV20 浏览器可见 Agent executor evidence path 的前端验收结果。
阅读对象：开发、测试、审计人员。
边界：本文只证明 bounded browser evidence page 和 BFF client route；不证明完整工作台、完整审批 UI、生产级前端或 unrestricted MCP。

## Result

状态：PASS

## Verified Scope

- `?studio=pv20-agent-executor` 已注册为前端入口。
- `PV20AgentExecutor` 页面可读取 state、contract、evidence，并显示 execution refs、allowed claim、not-claimed boundaries。
- 前端按钮通过 BFF 调用 skill/tool/MCP execution routes，并包含 `user_confirmed=true`。
- `WorkflowConsoleClient` PV20 方法只使用 `/bff/pv20/*` 路由。
- MCP fixture 缺失时 UI 保留错误展示路径，不伪造成功。

## Commands

```text
node node_modules/typescript/bin/tsc -p tsconfig.test.json && node --test dist-test/__tests__/*.test.js
node node_modules/typescript/bin/tsc -p tsconfig.json && node node_modules/vite/bin/vite.js build
```

## Evidence Notes

- Frontend tests: 85 passed.
- Frontend build: passed.
- Vite emitted a chunk-size warning for the existing bundle; it is not a PV20 functional failure.
