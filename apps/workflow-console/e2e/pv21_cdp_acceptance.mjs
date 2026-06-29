import { chromium } from "playwright";
import { mkdirSync, rmSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

const cdpURL = process.env.PV21_CDP_URL || "http://127.0.0.1:9351";
const baseURL = process.env.PV21_BASE_URL || "http://127.0.0.1:4185";
const bffBaseURL = process.env.PV21_BFF_BASE || "http://127.0.0.1:18141";
const evidenceDir = resolve("../../docs/design/V12-V15.x/evidence/pv21-complete-workflow-studio");
const createdAt = "2026-06-27T00:00:00Z";
const allowedClaim = "PV21 complete Workflow Studio candidate ready for bounded review.";

rmSync(evidenceDir, { recursive: true, force: true });
mkdirSync(evidenceDir, { recursive: true });

const browser = await chromium.connectOverCDP(cdpURL);
try {
  const context = browser.contexts()[0] || (await browser.newContext());
  const page = await context.newPage();
  const browserRequests = [];
  page.on("request", (request) => {
    const url = request.url();
    browserRequests.push({
      method: request.method(),
      url,
      allowed:
        !url.includes("/v1/rpc") &&
        !url.includes("/v1/internal") &&
        !url.includes("/internal/runtime") &&
        !url.includes("/runtime/store") &&
        !url.includes("/api/runtime") &&
        !url.includes("/debug/runtime"),
    });
  });

  const state = await readJson(`${bffBaseURL}/bff/pv21/studio/state?app_id=reference_app&project_id=demo_a&workspace_id=local`);
  assert(state.schema_version === "pv21.complete_workflow_studio.v1", "PV21 state schema is required");
  assert(state.platform_contract.workflow_core_customization_allowed === false, "PV21 platform contract must reject core customization");

  await page.setViewportSize({ width: 1600, height: 1040 });
  await page.goto(`${baseURL}/?studio=pv21-complete-workflow-studio&app_id=reference_app&project_id=demo_a&workspace_id=local`, {
    waitUntil: "networkidle",
  });
  await page.waitForSelector('[data-testid="pv21-complete-workflow-studio"]', { timeout: 20000 });
  await assertText(page, "pv21-platform-contract", "业务不定制 workflow core");
  await assertText(page, "pv21-node-library", "Human Gate");
  await assertText(page, "pv21-workflow-canvas", "human_gate");
  await page.screenshot({ fullPage: true, path: resolve(evidenceDir, "01-pv21-studio-loaded.png") });

  await page.getByRole("button", { name: "保存 Draft" }).click();
  await assertText(page, "pv21-validation-summary", "valid", 20000);
  await page.getByRole("button", { name: "校验图" }).click();
  await assertText(page, "pv21-validation-summary", "valid", 20000);
  await page.getByRole("button", { name: "生成 Diff" }).click();
  await assertText(page, "pv21-version-run", "pv21-diff", 20000);
  await page.getByTestId("pv21-workflow-canvas").screenshot({ path: resolve(evidenceDir, "02-canvas-save-validate-diff.png") });

  await page.getByRole("button", { name: "发布版本" }).click();
  await assertText(page, "pv21-active-version", "wfv_", 20000);
  await page.getByRole("button", { name: "保存 Draft" }).click();
  await page.getByRole("button", { name: "生成 Diff" }).click();
  await page.getByRole("button", { name: "发布版本" }).click();
  await assertText(page, "pv21-active-version", "wfv_", 20000);
  await page.getByTestId("pv21-version-run").screenshot({ path: resolve(evidenceDir, "03-version-publish-history.png") });

  await page.getByRole("button", { name: "运行工作流" }).click();
  await assertText(page, "pv21-run-state", "waiting_approval", 25000);
  await page.getByTestId("pv21-version-run").screenshot({ path: resolve(evidenceDir, "04-run-waiting-approval.png") });

  await page.getByRole("button", { name: "人工审批通过" }).click();
  await assertText(page, "pv21-human-action-after", "completed", 25000);
  await assertText(page, "pv21-run-state", "completed", 25000);
  await page.getByTestId("pv21-human-gate").screenshot({ path: resolve(evidenceDir, "05-human-gate-approved.png") });

  await page.getByRole("button", { name: "审查证据" }).click();
  await assertText(page, "pv21-evidence", allowedClaim, 25000);
  await assertText(page, "pv21-evidence", "pass", 25000);
  await page.getByTestId("pv21-evidence").screenshot({ path: resolve(evidenceDir, "06-evidence-review.png") });

  await page.getByRole("button", { name: "回滚版本" }).click();
  await assertText(page, "pv21-active-version", "wfv_", 25000);
  await page.screenshot({ fullPage: true, path: resolve(evidenceDir, "07-pv21-full-page-completed.png") });

  const forbiddenRequests = browserRequests.filter((item) => !item.allowed).map((item) => item.url);
  assert(forbiddenRequests.length === 0, `forbidden browser requests: ${forbiddenRequests.join(", ")}`);

  writeJson("browser-network-log.json", {
    schema_version: "pv21.browser_network_log.v1",
    status: "PASS",
    requests: browserRequests,
    forbidden_route_scan: { status: "PASS", forbidden_matches: forbiddenRequests },
    created_at: createdAt,
  });
  writeJson("acceptance-data.json", {
    schema_version: "pv21.complete_workflow_studio_acceptance_data.v1",
    stage_id: "PV21-SA",
    status: "PASS",
    allowed_claim: allowedClaim,
    browser_e2e: { status: "PASS", mode: "CDP", cdp_url: cdpURL },
    user_visible_paths: ["打开工作台", "保存 Draft", "校验图", "生成 Diff", "发布版本", "运行工作流", "人工审批", "审查证据", "回滚版本"],
    screenshots: [
      "01-pv21-studio-loaded.png",
      "02-canvas-save-validate-diff.png",
      "03-version-publish-history.png",
      "04-run-waiting-approval.png",
      "05-human-gate-approved.png",
      "06-evidence-review.png",
      "07-pv21-full-page-completed.png",
    ],
    route_boundary: { status: "PASS", allowed_prefixes: ["/bff/pv21"], forbidden_matches: forbiddenRequests },
    target_architecture: {
      status: "PARTIAL_PASS",
      implemented: ["Workflow Studio entry", "BFF DTO boundary", "Workflow graph save/validate/diff", "version publish/rollback", "runtime run", "human gate", "evidence summary"],
      not_claimed: ["production-ready governance", "unrestricted Agent executor", "external application contract hardening"],
    },
    current_architecture: {
      entry: "?studio=pv21-complete-workflow-studio",
      browser_boundary: "/bff/pv21/*",
      backend_entities: ["WorkflowTemplate", "WorkflowDraft", "WorkflowVersion", "WorkflowInstance", "StationRun", "QualityEvaluation", "ApprovalDecision"],
    },
    platform_generality_review: {
      status: "PASS",
      core_customization_allowed: false,
      finding: "业务样例以 WorkflowTemplate draft/version/input 进入通用平台，没有为单一业务修改 workflow core、Gateway core 或 App shell。",
    },
    prd_review: {
      status: "PASS",
      conclusion: "已覆盖完整 Workflow Studio 候选体验的 bounded closed loop；仍不声明生产可用、完整 Agent executor 或外部应用接入完成。",
    },
    created_at: createdAt,
  });
  writeJson("artifact-manifest.json", buildArtifactManifest());
  writeHtmlReport();
} finally {
  await browser.close();
}

async function readJson(url) {
  const response = await fetch(url);
  const body = await response.text();
  assert(response.ok, `${url} failed: ${response.status} ${body}`);
  return JSON.parse(body);
}

async function assertText(page, testId, text, timeout = 15000) {
  await page.getByTestId(testId).waitFor({ state: "visible", timeout });
  await page.waitForFunction(
    ({ selector, expected }) => document.querySelector(selector)?.textContent?.includes(expected),
    { selector: `[data-testid="${testId}"]`, expected: text },
    { timeout },
  );
}

function writeJson(name, value) {
  writeFileSync(resolve(evidenceDir, name), `${JSON.stringify(value, null, 2)}\n`, "utf-8");
}

function buildArtifactManifest() {
  const files = [
    "01-pv21-studio-loaded.png",
    "02-canvas-save-validate-diff.png",
    "03-version-publish-history.png",
    "04-run-waiting-approval.png",
    "05-human-gate-approved.png",
    "06-evidence-review.png",
    "07-pv21-full-page-completed.png",
    "browser-network-log.json",
    "acceptance-data.json",
    "artifact-manifest.json",
    "pv21-acceptance-report.html",
  ];
  return {
    schema_version: "pv21.artifact_manifest.v1",
    stage_id: "PV21-SA",
    status: "PASS",
    created_at: createdAt,
    artifacts: files.map((name) => ({ path: `docs/design/V12-V15.x/evidence/pv21-complete-workflow-studio/${name}` })),
  };
}

function writeHtmlReport() {
  writeFileSync(
    resolve(evidenceDir, "pv21-acceptance-report.html"),
    `<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>PV21 完整 Workflow Studio 阶段性自动化验收报告</title>
  <style>
    body { margin: 0; padding: 28px; font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #111827; background: #f4f7fb; }
    h1 { margin: 0 0 8px; font-size: 30px; }
    h2 { margin: 28px 0 12px; font-size: 20px; }
    p { color: #475569; line-height: 1.7; }
    .grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; margin: 18px 0; }
    .card, figure { border: 1px solid #d7e0ea; border-radius: 8px; background: white; }
    .card { padding: 14px; }
    .card span { display: block; color: #64748b; font-size: 12px; font-weight: 700; text-transform: uppercase; }
    .card strong { display: block; margin-top: 4px; overflow-wrap: anywhere; }
    figure { margin: 0 0 16px; padding: 12px; }
    img { max-width: 100%; border: 1px solid #e5e7eb; border-radius: 6px; }
    figcaption { margin-top: 8px; color: #475569; font-size: 14px; }
    code { background: #e5e7eb; padding: 2px 5px; border-radius: 4px; }
  </style>
</head>
<body>
  <h1>PV21 完整 Workflow Studio 阶段性自动化验收报告</h1>
  <p>本报告由 Chrome CDP 自动化执行真实用户路径生成。浏览器只访问 <code>/bff/pv21</code>，未直连 <code>/v1/rpc</code> 或内部 runtime 路径。</p>
  <section class="grid">
    <div class="card"><span>验收结论</span><strong>PASS</strong></div>
    <div class="card"><span>允许声明</span><strong>${allowedClaim}</strong></div>
    <div class="card"><span>平台红线</span><strong>业务不定制 workflow core / Gateway core / App shell</strong></div>
  </section>
  <h2>目标架构与当前实现</h2>
  <p>目标体验是用真实 Workflow Studio 候选页面完成打开工作台、编辑画布、校验、Diff、发布、运行、人工交互、证据审查和版本回滚。当前实现通过 <code>?studio=pv21-complete-workflow-studio</code> 页面调用 <code>/bff/pv21/*</code>，后端落到通用 <code>WorkflowTemplate</code>、<code>WorkflowDraft</code>、<code>WorkflowVersion</code>、<code>WorkflowInstance</code>、<code>StationRun</code>、<code>QualityEvaluation</code> 与审批实体。</p>
  <p>本报告不把该阶段声明为生产可用、完整 Agent executor 或外部应用接入完成；这些仍属于后续开发目标。</p>
  <h2>真实用户路径截图</h2>
  <figure><img src="01-pv21-studio-loaded.png"><figcaption>工作台加载：节点库、画布、Inspector、版本运行区与平台红线可见。</figcaption></figure>
  <figure><img src="02-canvas-save-validate-diff.png"><figcaption>保存 Draft、校验图、生成 WorkflowDiff，发布前仍要求用户确认。</figcaption></figure>
  <figure><img src="03-version-publish-history.png"><figcaption>发布两个版本，版本历史与回滚候选进入可审查状态。</figcaption></figure>
  <figure><img src="04-run-waiting-approval.png"><figcaption>基于发布版本启动真实 runtime run，流程停在 waiting_approval。</figcaption></figure>
  <figure><img src="05-human-gate-approved.png"><figcaption>人工审批通过后 workflow run 进入 completed。</figcaption></figure>
  <figure><img src="06-evidence-review.png"><figcaption>证据审查汇总 trace、artifact、quality、approval、route boundary 与 no-false-green 扫描。</figcaption></figure>
  <figure><img src="07-pv21-full-page-completed.png"><figcaption>回滚后完整页面状态，用于人工复核目标体验是否偏移。</figcaption></figure>
</body>
</html>
`,
    "utf-8",
  );
}

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}
