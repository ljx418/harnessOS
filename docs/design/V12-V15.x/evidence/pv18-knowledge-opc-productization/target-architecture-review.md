# PV18 目标架构检视

结论：PASS。

- 浏览器只调用 /bff/pv18/knowledge/*。
- BFF 通过 KnowledgeMcpWorkflowRunner 调用 data_service_mcp，不暴露内部 runtime 或 connector payload。
- 业务输入来自 source/query DTO，未把知识业务写成平台专用流程分支。
- evidence package 包含 DTO、路由、截图、artifact lineage 和 claim matrix。