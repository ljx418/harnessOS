import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import test from "node:test";

const source = readFileSync(resolve("src/ui/v12/V12ReadOnlyWorkbench.tsx"), "utf-8");

test("V12 read-only workbench source exposes product entities, inspector and boundary copy", () => {
  for (const expected of [
    "HarnessOS Product Workbench",
    "产品实体",
    "技术内容工作室",
    "本地知识总结项目",
    "只读 Workflow Canvas Foundation",
    "节点 Inspector",
    "Chat Workbench 提案",
    "Station Agent Profile",
    "readonly_projection_only",
    "WorkflowDiff",
    "API Health",
    "禁用原因",
    "浏览器只允许读取 BFF / DTO 投影",
  ]) {
    assert(source.includes(expected), `${expected} missing from V12 workbench source`);
  }

  for (const forbidden of [
    "/v1/rpc",
    "/v1/events/subscribe",
    "Agent executor ready",
    "Xpert parity complete",
    "production ready",
    "complete Workflow Studio ready",
    "自动发布成功",
    "自动运行成功",
    "raw_secret",
    "Bearer",
  ]) {
    assert(!source.includes(forbidden), `${forbidden} leaked into V12 read-only workbench source`);
  }
});
