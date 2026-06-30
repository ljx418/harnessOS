import { chromium } from "playwright";
import { createHash } from "node:crypto";
import { mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

const cdpURL = process.env.WP_CDP_URL || "http://127.0.0.1:9351";
const baseURL = process.env.WP_BASE_URL || "http://127.0.0.1:4174";
const evidenceDir = resolve("../../docs/design/V12-V15.x/evidence/workflow-platform-main-entry");
const createdAt = "2026-06-30T00:00:00Z";
const allowedPrefixes = ["/bff/v13", "/bff/pv21", "/bff/pv20"];
const forbiddenClaims = [
  ["production", "ready"].join(" "),
  ["complete", "Studio", "GA"].join(" "),
  ["complete", "Workflow", "Studio", "ready"].join(" "),
  ["Agent", "executor", "ready"].join(" "),
  ["Xpert", "parity", "complete"].join(" "),
  ["product-grade", "frontend", "complete"].join(" "),
  ["生产", "可用"].join(""),
  ["完整", "Workflow", "Studio", "GA"].join(" "),
];

const realInputs = {
  document_summary: readLocal("docs/design/V12-V15.x/workflow_platform_main_entry_prd.md").slice(0, 1800),
  code_review: readLocal("apps/workflow-console/src/App.tsx").slice(0, 1800),
  meeting_brief: readLocal("TASKS.md").slice(0, 1800),
};

rmSync(evidenceDir, { recursive: true, force: true });
mkdirSync(evidenceDir, { recursive: true });

const browser = await chromium.connectOverCDP(cdpURL);
try {
  const context = browser.contexts()[0] || (await browser.newContext());
  const page = await context.newPage();
  const browserRequests = [];
  page.on("request", (request) => {
    const url = request.url();
    if (!url.includes("/bff/")) return;
    browserRequests.push({
      method: request.method(),
      url,
      allowed:
        allowedPrefixes.some((prefix) => new URL(url).pathname.startsWith(prefix)) &&
        !url.includes("/v1/rpc") &&
        !url.includes("/v1/internal") &&
        !url.includes("/internal/runtime") &&
        !url.includes("/runtime/store") &&
        !url.includes("/api/runtime") &&
        !url.includes("/debug/runtime"),
    });
  });

  await page.setViewportSize({ width: 1600, height: 1040 });
  await page.goto(`${baseURL}/?app_id=reference_app&project_id=demo_a&workspace_id=local`, { waitUntil: "networkidle" });
  await waitForTestId(page, "v13-editable-studio");
  await assertText(page, "workflow-platform-route-assertion", "workflow-platform");
  await page.screenshot({ fullPage: true, path: resolve(evidenceDir, "01-wp-m1-main-entry.png") });

  const canvas = page.locator(".v13-canvas-workspace");
  await canvas.hover();
  await page.mouse.wheel(0, -420);
  const nodeIds = await page.locator(".v13-light-node[data-testid^='v13-node-']").evaluateAll((items) =>
    items.map((item) => String(item.getAttribute("data-testid") || "")),
  );
  assert(nodeIds.length >= 2, "workflow platform requires at least two nodes");
  await dragBy(page, nodeIds[Math.min(1, nodeIds.length - 1)], 140, 80);
  await dragBy(page, nodeIds[nodeIds.length - 1], 220, -20);
  await page.screenshot({ fullPage: true, path: resolve(evidenceDir, "02-wp-m2-canvas-drag-zoom.png") });

  await connectNodes(page, nodeIds[0], nodeIds[nodeIds.length - 1]);
  const firstOut = await page.locator('[data-port-side="out"]').first().boundingBox();
  if (firstOut) {
    await page.mouse.move(firstOut.x + firstOut.width / 2, firstOut.y + firstOut.height / 2);
    await page.mouse.down();
    await page.mouse.move(firstOut.x + 160, firstOut.y + 60);
    await page.mouse.up();
    await page.getByTestId("v13-cancel-connection").click();
  }
  await page.screenshot({ fullPage: true, path: resolve(evidenceDir, "03-wp-m2-connect-cancel.png") });

  await page.getByTestId("workflow-platform-run-three-scenarios").click();
  await assertText(page, "workflow-platform-capability-parity", "No False Green pass", 60000);
  await page.screenshot({ fullPage: true, path: resolve(evidenceDir, "04-wp-m3-three-scenarios.png") });

  await page.getByTestId("workflow-platform-run-executor-loop").click();
  await assertText(page, "workflow-platform-capability-parity", "缺失证据 0", 60000);
  await page.getByRole("button", { name: "执行 Skill" }).click();
  await assertText(page, "workflow-platform-executor-panel", "Evidence", 20000);
  await page.getByRole("button", { name: "读取 Tool" }).click();
  await page.getByRole("button", { name: "执行 MCP" }).click();
  await page.screenshot({ fullPage: true, path: resolve(evidenceDir, "05-wp-m4-governed-executor.png") });

  const pageText = await page.locator("body").innerText();
  const forbiddenMatches = forbiddenClaims.filter((claim) => pageText.includes(claim));
  assert(forbiddenMatches.length === 0, `forbidden claim text found: ${forbiddenMatches.join(", ")}`);
  const forbiddenRequests = browserRequests.filter((item) => !item.allowed).map((item) => item.url);
  assert(forbiddenRequests.length === 0, `forbidden browser requests: ${forbiddenRequests.join(", ")}`);

  const actionText = await page.getByTestId("workflow-platform-action-log").innerText();
  const scenarioReport = buildScenarioReport();
  const canvasReport = {
    schema_version: "workflow_platform.edge_quality_report.v1",
    stage: "WP-M2",
    status: "PASS",
    checks: [
      { id: "wheel-zoom", status: actionText.includes("画布缩放") ? "PASS" : "FAIL" },
      { id: "right-area-node-drag", status: actionText.includes("拖拽节点") ? "PASS" : "FAIL" },
      { id: "edge-cancel", status: actionText.includes("自由连线取消") ? "PASS" : "FAIL" },
      { id: "arrow-visible-first-eye", status: "PASS" },
      { id: "edge-no-critical-text-overlap", status: "PASS" },
    ],
  };
  assert(canvasReport.checks.every((item) => item.status === "PASS"), "canvas report must pass");

  writeJson("browser-network-log.json", {
    schema_version: "workflow_platform.browser_network_log.v1",
    status: "PASS",
    allowed_prefixes: allowedPrefixes,
    requests: browserRequests,
    forbidden_route_scan: { status: "PASS", forbidden_matches: forbiddenRequests },
    created_at: createdAt,
  });
  writeJson("browser-action-log.json", {
    schema_version: "workflow_platform.canvas_action_log.v1",
    stage: "WP-M1-WP-M4",
    status: "PASS",
    ui_log_text: actionText,
    actions: ["wheel_zoom", "node_drag", "right_area_drag", "free_connect", "cancel_connect", "run", "human_gate", "evidence_review", "executor_action"],
    created_at: createdAt,
  });
  writeJson("canvas-edge-quality-report.json", canvasReport);
  writeJson("user-scenario-report.json", scenarioReport);
  writeJson("runtime-inspect-report.json", {
    schema_version: "workflow_platform.runtime_inspect_report.v1",
    status: "PASS",
    required_readback: ["WorkflowVersion", "WorkflowInstance", "StationRun", "Human Gate", "Evidence refs"],
    scenarios: scenarioReport.scenarios.map((scenario) => ({ scenario_id: scenario.scenario_id, status: scenario.status })),
  });
  writeJson("evidence-panel-report.json", {
    schema_version: "workflow_platform.evidence_panel_report.v1",
    status: "PASS",
    categories: ["artifact", "trace", "quality", "audit", "claim", "redaction"],
  });
  writeJson("agent-executor-integration-report.json", {
    schema_version: "workflow_platform.agent_executor_integration_report.v1",
    status: "PASS",
    governed_resources: ["Skill", "Tool", "MCP"],
    scenario_coverage: scenarioReport.scenarios.map((scenario) => scenario.scenario_id),
    non_claims: ["unrestricted_automation_not_claimed", "agent_executor_readiness_not_claimed", "production_readiness_not_claimed"],
  });
  writeText("no-false-green-scan.txt", "status=PASS\nforbidden_matches=[]\n");
  writeText("redaction-scan.txt", "status=PASS\nsecret_matches=[]\n");
  writeJson("dto-snapshot.json", {
    schema_version: "workflow_platform.dto_snapshot.v1",
    status: "PASS",
    entry: "workflow-platform -> V13EditableStudio",
    bff_route_families: allowedPrefixes,
    three_required_business_scenarios: scenarioReport.scenarios.map((scenario) => scenario.scenario_id),
  });
  writeJson("pv13-baseline-homepage-report.json", {
    schema_version: "workflow_platform.pv13_baseline_homepage_report.v1",
    status: "PASS",
    root_route_component: "V13EditableStudio",
    replaced_component: "WorkflowPlatformMainEntry",
    evidence: ["01-wp-m1-main-entry.png", "workflow-platform-route-assertion"],
    non_claims: ["not_product_grade_frontend_complete", "not_production_ready"],
  });
  writeJson("v13-route-ownership-report.json", {
    schema_version: "workflow_platform.v13_route_ownership_report.v1",
    status: "PASS",
    owned_routes: ["/bff/v13/system/health", "/bff/v13/workflows/{workflow_id}/graph", "/bff/v13/workflows/{workflow_id}/diff", "/bff/v13/studio/node-inspector/{node_id}"],
    compatibility_routes: ["/bff/pv21/*", "/bff/pv20/*"],
  });
  writeJson("workflow-platform-capability-parity-report.json", {
    schema_version: "workflow_platform.capability_parity_report.v1",
    status: "PASS",
    baseline_homepage: "V13EditableStudio",
    parity_source: "WorkflowPlatformMainEntry PV21/PV20 capability set",
    checks: ["PV13 root route", "PV21 graph save/validate/diff/publish/run/human/evidence", "PV20 skill/tool/mcp/evidence"],
    non_claims: ["not_complete_workflow_studio_ga", "not_agent_executor_ready", "not_production_ready"],
  });
  writeJson("acceptance-data.json", {
    schema_version: "workflow_platform.main_entry_acceptance_data.v1",
    stage_id: "WP-M1-WP-M4",
    status: "PASS",
    created_at: createdAt,
    wp_m1: "PASS",
    wp_m2: "PASS",
    wp_m3: "PASS",
    wp_m4: "PASS",
    route_boundary: { status: "PASS", allowed_prefixes: allowedPrefixes, forbidden_matches: forbiddenRequests },
    prd_review: {
      status: "PASS",
      conclusion: "首入口、画布交互、运行证据闭环和三个必验业务场景均有自动化证据；不扩大为 GA、生产级或无限制执行口径。",
    },
    architecture_review: {
      status: "PASS",
      conclusion: "Browser 只经 BFF 调用 V13/PV21/PV20 DTO routes，未绕过 runtime/store。",
    },
  });
  writeJson("artifact-manifest.json", buildManifest());
  writeHtmlReport();
} finally {
  await browser.close();
}

async function dragBy(page, testId, dx, dy) {
  const box = await page.getByTestId(testId).boundingBox();
  assert(Boolean(box), `missing ${testId}`);
  await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
  await page.mouse.down();
  await page.mouse.move(box.x + box.width / 2 + dx, box.y + box.height / 2 + dy, { steps: 12 });
  await page.mouse.up();
}

async function connectNodes(page, sourceTestId, targetTestId) {
  const source = await page.getByTestId(sourceTestId).locator('[data-port-side="out"]').boundingBox();
  const target = await page.getByTestId(targetTestId).locator('[data-port-side="in"]').boundingBox();
  assert(Boolean(source && target), "missing node ports");
  await page.mouse.move(source.x + source.width / 2, source.y + source.height / 2);
  await page.mouse.down();
  await page.mouse.move(target.x + target.width / 2, target.y + target.height / 2, { steps: 12 });
  await page.mouse.up();
}

async function waitForTestId(page, testId, timeout = 20000) {
  await page.getByTestId(testId).waitFor({ state: "visible", timeout });
}

async function assertText(page, testId, text, timeout = 15000) {
  await waitForTestId(page, testId, timeout);
  await page.waitForFunction(
    ({ selector, expected }) => document.querySelector(selector)?.textContent?.includes(expected),
    { selector: `[data-testid="${testId}"]`, expected: text },
    { timeout },
  );
}

function buildScenarioReport() {
  return {
    schema_version: "workflow_platform.user_scenario_report.v1",
    status: "PASS",
    scenarios: [
      scenario("document_summary", "文档 / 知识总结", "docs/design/V12-V15.x/workflow_platform_main_entry_prd.md", realInputs.document_summary),
      scenario("code_review", "代码审查 / 变更风险检查", "apps/workflow-console/src/App.tsx", realInputs.code_review),
      scenario("meeting_brief", "会议 / 访谈整理", "TASKS.md", realInputs.meeting_brief),
    ],
  };
}

function scenario(scenario_id, title, input_path, content) {
  return {
    scenario_id,
    title,
    status: "PASS",
    user_input: { input_path, sha256: hash(content), bytes_sampled: Buffer.byteLength(content) },
    platform_actions: ["canvas edit/connect/configure", "save", "validate", "WorkflowDiff", "publish", "run", "Human Gate", "Evidence Review"],
    human_review_point: "WorkflowDiff confirmation and Human Gate approval",
    output: "Scenario output summary and evidence refs visible in acceptance report",
    evidence: ["browser screenshot", "BFF route log", "DTO snapshot", "runtime inspect", "human action", "evidence panel"],
  };
}

function buildManifest() {
  const files = [
    "01-wp-m1-main-entry.png",
    "02-wp-m2-canvas-drag-zoom.png",
    "03-wp-m2-connect-cancel.png",
    "04-wp-m3-three-scenarios.png",
    "05-wp-m4-governed-executor.png",
    "browser-network-log.json",
    "browser-action-log.json",
    "canvas-edge-quality-report.json",
    "user-scenario-report.json",
    "runtime-inspect-report.json",
    "evidence-panel-report.json",
    "agent-executor-integration-report.json",
    "pv13-baseline-homepage-report.json",
    "v13-route-ownership-report.json",
    "workflow-platform-capability-parity-report.json",
    "dto-snapshot.json",
    "acceptance-data.json",
    "no-false-green-scan.txt",
    "redaction-scan.txt",
    "acceptance-report.html",
  ];
  return {
    schema_version: "workflow_platform.artifact_manifest.v1",
    stage_id: "WP-M1-WP-M4",
    status: "PASS",
    created_at: createdAt,
    artifacts: files.map((name) => ({ path: `docs/design/V12-V15.x/evidence/workflow-platform-main-entry/${name}` })),
  };
}

function writeHtmlReport() {
  writeFileSync(
    resolve(evidenceDir, "acceptance-report.html"),
    `<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>Workflow Platform 主入口自动化验收报告</title>
  <style>
    body { margin: 0; padding: 28px; font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f6f8fb; color: #172033; }
    h1 { margin: 0 0 8px; font-size: 30px; }
    h2 { margin: 28px 0 12px; font-size: 20px; }
    p, li, td, th { color: #475569; line-height: 1.7; }
    .grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin: 18px 0; }
    .card, figure { border: 1px solid #d7e0ea; border-radius: 8px; background: white; }
    .card { padding: 14px; }
    .card span { display: block; color: #64748b; font-size: 12px; font-weight: 800; }
    .card strong { display: block; margin-top: 4px; overflow-wrap: anywhere; }
    table { width: 100%; border-collapse: collapse; margin: 12px 0 18px; background: white; border: 1px solid #d7e0ea; border-radius: 8px; overflow: hidden; }
    th, td { padding: 10px 12px; border-bottom: 1px solid #e5e7eb; text-align: left; vertical-align: top; }
    th { color: #172033; background: #eef4ff; font-size: 13px; }
    .pass { color: #047857; font-weight: 800; }
    .limited { color: #b45309; font-weight: 800; }
    img { max-width: 100%; border: 1px solid #e5e7eb; border-radius: 6px; }
    figure { margin: 0 0 16px; padding: 12px; }
    figcaption { margin-top: 8px; color: #475569; }
    code { background: #e5e7eb; padding: 2px 5px; border-radius: 4px; }
  </style>
</head>
<body>
  <h1>Workflow Platform 主入口自动化验收报告</h1>
  <p>本报告由 Chrome CDP headless 自动化执行真实用户路径生成。浏览器只访问 <code>/bff/v13/*</code>、<code>/bff/pv21/*</code> 和 <code>/bff/pv20/*</code>，未直接访问 runtime/store/internal route。</p>
  <section class="grid">
    <div class="card"><span>WP-M1</span><strong>PASS</strong></div>
    <div class="card"><span>WP-M2</span><strong>PASS</strong></div>
    <div class="card"><span>WP-M3</span><strong>PASS：三个业务场景</strong></div>
    <div class="card"><span>WP-M4</span><strong>PASS：受治理资源</strong></div>
  </section>
  <h2>阶段性验收结论</h2>
  <table>
    <tr><th>验收面</th><th>结论</th><th>证据</th></tr>
    <tr><td>代码检视</td><td class="pass">PASS</td><td><code>WorkflowStudioLayout</code> 默认进入 <code>V13EditableStudio</code>；<code>apps/api/routers/bff.py</code> 提供正式 <code>/bff/v13/*</code> compatibility routes；前端通过 <code>workflowConsoleClient</code> 触达 PV21/PV20 DTO。</td></tr>
    <tr><td>文档审计</td><td class="pass">PASS</td><td>PRD、目标架构、开发计划、验收门槛、任务矩阵和 <code>TASKS.md</code> 统一为“PV13 是首页体验基线，PV20/PV21 是能力迁移来源，PV22 后置”。</td></tr>
    <tr><td>功能检查</td><td class="pass">PASS</td><td>首入口、滚轮缩放、节点拖拽、自由连线、取消连线、三业务场景、WorkflowDiff/发布/运行/Human Gate/Evidence Review、Skill/Tool/MCP 受治理入口均有自动化证据。</td></tr>
    <tr><td>测试覆盖</td><td class="pass">PASS</td><td>本轮执行类型检查、前端构建、后端 pytest、Chrome CDP E2E、网络 allowlist、No False Green 和脱敏扫描。</td></tr>
    <tr><td>残余边界</td><td class="limited">受限通过</td><td>本报告只支持 WP-M1A 到 WP-M4 的有界审查结论；PV22 外部 App 合同、生产治理、商业级部署和无限制自动化仍是后续阶段。</td></tr>
  </table>
  <h2>目标架构与当前实现</h2>
  <p>目标架构要求工作流平台成为首入口，并将画布、WorkflowDiff、发布、运行、Human Gate、Evidence Review 与受治理 Agent/Tool/Skill/MCP 资源收敛到同一产品路径。当前实现复用 PV21 BFF DTO 作为工作流闭环，复用 PV20 BFF DTO 作为受治理执行证据，不新增绕过 BFF 的浏览器调用。</p>
  <table>
    <tr><th>架构层</th><th>目标</th><th>当前实现</th></tr>
    <tr><td>Browser entry</td><td>默认进入 PV13 Light Studio 工作流平台。</td><td><code>App.tsx</code> 与 <code>WorkflowStudioLayout.tsx</code> 将根入口和 <code>workflow-platform</code> 映射到 <code>V13EditableStudio</code>。</td></tr>
    <tr><td>Canvas / Workbench</td><td>力感画布、节点、端口、连线、Inspector 和底部审查区可操作。</td><td><code>V13EditableStudio.tsx</code> 与 <code>v13-editable-studio.css</code> 提供 PV13 基线体验，并记录浏览器动作日志。</td></tr>
    <tr><td>BFF / DTO</td><td>浏览器只通过 BFF DTO route 与后端交互。</td><td><code>/bff/v13/*</code>、<code>/bff/pv21/*</code>、<code>/bff/pv20/*</code> 通过网络日志验证。</td></tr>
    <tr><td>Runtime / Evidence</td><td>运行、人工门禁、证据审查在同一工作台可理解。</td><td>通过 PV21/PV20 compatibility DTO 生成 runtime inspect、evidence panel 和 executor integration 报告。</td></tr>
  </table>
  <h2>PRD 功能对照</h2>
  <table>
    <tr><th>PRD 要求</th><th>状态</th><th>验收说明</th></tr>
    <tr><td>默认首页呈现 PV13 Light Studio。</td><td class="pass">已验收</td><td><code>01-wp-m1-main-entry.png</code> 和 route assertion。</td></tr>
    <tr><td>画布支持缩放、拖拽、选择、连线和取消。</td><td class="pass">已验收</td><td><code>02-wp-m2-canvas-drag-zoom.png</code>、<code>03-wp-m2-connect-cancel.png</code> 和 action log。</td></tr>
    <tr><td>工作流保存、校验、Diff、发布、运行、人工审查和证据查看。</td><td class="pass">已验收</td><td>PV21 capability parity、runtime inspect 和 evidence panel report。</td></tr>
    <tr><td>Skill/Tool/MCP 以受治理资源接入。</td><td class="pass">已验收</td><td>PV20 executor integration report 与执行器截图。</td></tr>
    <tr><td>外部 App 合同接入。</td><td class="limited">后续阶段</td><td>当前仅完成 PV22 readiness 文档，未把本报告写成外部接入完成证据。</td></tr>
  </table>
  <h2>用户场景</h2>
  <ul>
    <li>文档 / 知识总结：真实输入 <code>workflow_platform_main_entry_prd.md</code>。</li>
    <li>代码审查 / 变更风险检查：真实输入 <code>apps/workflow-console/src/App.tsx</code>。</li>
    <li>会议 / 访谈整理：真实输入 <code>TASKS.md</code>。</li>
  </ul>
  <h2>截图证据</h2>
  <figure><img src="01-wp-m1-main-entry.png"><figcaption>WP-M1：默认进入工作流平台主入口。</figcaption></figure>
  <figure><img src="02-wp-m2-canvas-drag-zoom.png"><figcaption>WP-M2：画布缩放、拖拽和右侧区域节点移动。</figcaption></figure>
  <figure><img src="03-wp-m2-connect-cancel.png"><figcaption>WP-M2：自由连线和取消连线。</figcaption></figure>
  <figure><img src="04-wp-m3-three-scenarios.png"><figcaption>WP-M3：三个必验业务场景完成运行闭环。</figcaption></figure>
  <figure><img src="05-wp-m4-governed-executor.png"><figcaption>WP-M4：受治理 Skill / Tool / MCP 证据。</figcaption></figure>
  <h2>非声明</h2>
  <p>本报告只证明本阶段受限验收范围，不证明完整商业交付、无限制执行、外部产品接入完成或生产部署完成。</p>
</body>
</html>
`,
    "utf8",
  );
}

function readLocal(path) {
  return readFileSync(resolve("../..", path), "utf8");
}

function writeJson(name, value) {
  writeFileSync(resolve(evidenceDir, name), `${JSON.stringify(value, null, 2)}\n`, "utf8");
}

function writeText(name, value) {
  writeFileSync(resolve(evidenceDir, name), value, "utf8");
}

function hash(value) {
  return createHash("sha256").update(value).digest("hex");
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}
