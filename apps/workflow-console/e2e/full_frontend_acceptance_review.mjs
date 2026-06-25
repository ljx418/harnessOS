import { chromium } from "playwright";
import { mkdirSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

const cdpURL = process.env.FULL_REVIEW_CDP_URL || "http://127.0.0.1:9340";
const baseURL = process.env.FULL_REVIEW_BASE_URL || "http://127.0.0.1:4178";
const evidenceDir = resolve(process.env.FULL_REVIEW_EVIDENCE_DIR || "../../docs/design/V12-V15.x/evidence/full-stage-acceptance-review-2026-06-25");
const mode = process.env.FULL_REVIEW_MODE || "headless";
const createdAt = new Date().toISOString();

const blockedClaims = [
  "browser implementation complete",
  "BFF runtime evidence complete",
  "Xpert parity complete",
  "product-grade frontend complete",
  "complete Workflow Studio ready",
  "production ready",
  "Agent executor ready",
];

const forbiddenRoutes = ["/v1/rpc", "/v1/events/subscribe", "/v1/internal", "/internal/runtime", "/runtime/store"];

mkdirSync(evidenceDir, { recursive: true });

const browser = await chromium.connectOverCDP(cdpURL);
const context = browser.contexts()[0] || (await browser.newContext());
const page = await context.newPage();
const requests = [];
page.on("request", (request) => {
  const url = request.url();
  requests.push({
    method: request.method(),
    url,
    allowed: !forbiddenRoutes.some((route) => url.includes(route)),
  });
});

const scenarios = [];
try {
  await runV12(page);
  await runV13(page);
  await runV14(page);
  await runV15(page);
  await runPV16(page);
} finally {
  await browser.close();
}

const forbiddenRequestMatches = requests.filter((entry) => !entry.allowed).map((entry) => entry.url);
writeJson(`browser-scenario-results-${mode}.json`, {
  schema_version: "full_frontend_acceptance.browser_scenario_results.v1",
  status: scenarios.every((scenario) => scenario.status === "PASS") && forbiddenRequestMatches.length === 0 ? "PASS" : "FAIL",
  mode,
  base_url: baseURL,
  scenarios,
  browser_boundary: {
    status: forbiddenRequestMatches.length === 0 ? "PASS" : "FAIL",
    forbidden_matches: forbiddenRequestMatches,
  },
  blocked_claims: blockedClaims,
  created_at: createdAt,
});
writeJson(`browser-network-log-${mode}.json`, {
  schema_version: "full_frontend_acceptance.browser_network_log.v1",
  status: forbiddenRequestMatches.length === 0 ? "PASS" : "FAIL",
  mode,
  requests,
  forbidden_matches: forbiddenRequestMatches,
  created_at: createdAt,
});

async function runV12(activePage) {
  await activePage.setViewportSize({ width: 1500, height: 980 });
  await activePage.goto(`${baseURL}/?studio=v12-readonly-canvas`, { waitUntil: "networkidle" });
  await activePage.waitForSelector('[data-testid="v12-readonly-workbench"]', { timeout: 20000 });
  await clickOptional(activePage, "v12-open-graph-review");
  const checks = [
    await contains(activePage, "v12-entity-sidebar", "技术内容工作室"),
    await contains(activePage, "v12-node-inspector", "质量检查 Agent"),
    await contains(activePage, "v12-disabled-action-reason", "V12"),
    await contains(activePage, "v12-workflowdiff-handoff", "WorkflowDiff"),
  ];
  const text = await activePage.locator("body").innerText();
  await activePage.screenshot({ fullPage: true, path: resolve(evidenceDir, `${mode}-v12-readonly-workbench.png`) });
  scenarios.push({
    scenario_id: "V12-readonly-workbench",
    status: checks.every(Boolean) && noBlockedClaim(text) ? "PASS" : "FAIL",
    user_visible_result: "用户可查看实体侧栏、只读画布、Inspector、禁用动作原因和 WorkflowDiff handoff。",
    screenshot: `${mode}-v12-readonly-workbench.png`,
    runtime_backed: false,
  });
}

async function runV13(activePage) {
  await activePage.setViewportSize({ width: 1500, height: 980 });
  await activePage.goto(`${baseURL}/?studio=v13-editable-studio`, { waitUntil: "networkidle" });
  await activePage.waitForSelector('[data-testid="v13-editable-studio"]', { timeout: 20000 });
  for (const testId of ["v13-add-node", "v13-connect-node", "v13-move-node", "v13-configure-node", "v13-confirm-handoff"]) {
    await activePage.getByTestId(testId).click();
  }
  const checks = [
    await contains(activePage, "v13-validation-status", "PASS"),
    await contains(activePage, "v13-action-log", "添加节点"),
    await contains(activePage, "v13-action-log", "连接节点"),
    await contains(activePage, "v13-handoff-ref", "handoff"),
  ];
  const text = await activePage.locator("body").innerText();
  await activePage.screenshot({ fullPage: true, path: resolve(evidenceDir, `${mode}-v13-editable-studio.png`) });
  await activePage.getByTestId("v13-node-inspector").screenshot({ path: resolve(evidenceDir, `${mode}-v13-node-inspector.png`) });
  scenarios.push({
    scenario_id: "V13-editable-studio-pilot",
    status: checks.every(Boolean) && noBlockedClaim(text) ? "PASS" : "FAIL",
    user_visible_result: "用户可添加、连接、移动、配置节点并确认 WorkflowDiff handoff；不发布、不运行。",
    screenshot: `${mode}-v13-editable-studio.png`,
    runtime_backed: false,
  });
}

async function runV14(activePage) {
  await activePage.setViewportSize({ width: 1500, height: 980 });
  await activePage.goto(`${baseURL}/?studio=v14-extension-ecosystem`, { waitUntil: "networkidle" });
  await activePage.waitForSelector('[data-testid="v14-extension-ecosystem"]', { timeout: 20000 });
  await activePage.getByTestId("v14-activate-package").click();
  await activePage.getByTestId("v14-deny-unsafe-package").click();
  const checks = [
    await contains(activePage, "v14-compatibility-status", "兼容"),
    await contains(activePage, "v14-agent-binding-panel", "已 scoped activation"),
    await contains(activePage, "v14-action-log", "不安全扩展已拒绝"),
  ];
  const text = await activePage.locator("body").innerText();
  await activePage.screenshot({ fullPage: true, path: resolve(evidenceDir, `${mode}-v14-extension-ecosystem.png`) });
  scenarios.push({
    scenario_id: "V14-extension-ecosystem-pilot",
    status: checks.every(Boolean) && noBlockedClaim(text) ? "PASS" : "FAIL",
    user_visible_result: "用户可查看扩展包兼容性、执行 scoped activation、看到 unsafe package 被拒绝和 audit ref。",
    screenshot: `${mode}-v14-extension-ecosystem.png`,
    runtime_backed: false,
  });
}

async function runV15(activePage) {
  await activePage.setViewportSize({ width: 1500, height: 980 });
  await activePage.goto(`${baseURL}/?studio=v15-observability-deployment`, { waitUntil: "networkidle" });
  await activePage.waitForSelector('[data-testid="v15-observability-deployment"]', { timeout: 20000 });
  await activePage.getByTestId("v15-run-health-check").click();
  await activePage.getByTestId("v15-run-deployment-smoke").click();
  const checks = [
    await nonEmpty(activePage, "v15-trace-timeline"),
    await contains(activePage, "v15-health-result", "PASS"),
    await contains(activePage, "v15-smoke-output", "bounded local smoke"),
    await contains(activePage, "v15-action-log", "bounded deployment smoke PASS"),
  ];
  const text = await activePage.locator("body").innerText();
  await activePage.screenshot({ fullPage: true, path: resolve(evidenceDir, `${mode}-v15-observability-deployment.png`) });
  scenarios.push({
    scenario_id: "V15-observability-deployment-baseline",
    status: checks.every(Boolean) && noBlockedClaim(text) ? "PASS" : "FAIL",
    user_visible_result: "用户可查看 trace/metrics/audit/incident，执行本地 health check 和 bounded smoke。",
    screenshot: `${mode}-v15-observability-deployment.png`,
    runtime_backed: false,
  });
}

async function runPV16(activePage) {
  await activePage.setViewportSize({ width: 1500, height: 980 });
  await activePage.goto(`${baseURL}/?studio=pv16-product-runtime-hardening`, { waitUntil: "networkidle" });
  await activePage.waitForSelector('[data-testid="pv16-product-runtime-hardening"]', { timeout: 20000 });
  await activePage.getByTestId("pv16-run-entity-mutation").click();
  await activePage.getByTestId("pv16-run-ownership-denial").click();
  await activePage.getByTestId("pv16-confirm-runtime-run").click();
  await activePage.getByTestId("pv16-run-deployment-smoke").click();
  const checks = [
    await contains(activePage, "pv16-bff-source", "BFF-backed"),
    await contains(activePage, "pv16-entity-crud", "DENIED"),
    await contains(activePage, "pv16-runtime-inspect", "true"),
    await contains(activePage, "pv16-deployment-hardening", "health: PASS"),
    await contains(activePage, "pv16-product-runtime-journey", "产品实体"),
  ];
  const text = await activePage.locator("body").innerText();
  await activePage.screenshot({ fullPage: true, path: resolve(evidenceDir, `${mode}-pv16-product-runtime-hardening.png`) });
  await activePage
    .getByTestId("pv16-runtime-inspect")
    .screenshot({ path: resolve(evidenceDir, `${mode}-pv16-runtime-inspect.png`) });
  scenarios.push({
    scenario_id: "PV16-product-runtime-hardening-pilot",
    status: checks.every(Boolean) && noBlockedClaim(text) ? "PASS" : "FAIL",
    user_visible_result: "用户可更新产品实体、看到 ownership denial、确认 runtime-backed run/inspect，并运行 bounded deployment hardening smoke。",
    screenshot: `${mode}-pv16-product-runtime-hardening.png`,
    runtime_backed: true,
  });
}

async function contains(activePage, testId, expected) {
  try {
    await activePage.waitForFunction(
      ({ id, text }) => {
        const element = document.querySelector(`[data-testid="${id}"]`);
        return Boolean(element && element.textContent && element.textContent.includes(text));
      },
      { id: testId, text: expected },
      { timeout: 12000 },
    );
    return true;
  } catch {
    return false;
  }
}

async function nonEmpty(activePage, testId) {
  try {
    await activePage.waitForFunction(
      (id) => {
        const element = document.querySelector(`[data-testid="${id}"]`);
        return Boolean(element && element.textContent && element.textContent.trim().length > 0);
      },
      testId,
      { timeout: 12000 },
    );
    return true;
  } catch {
    return false;
  }
}

async function clickOptional(activePage, testId) {
  try {
    await activePage.getByTestId(testId).click({ timeout: 5000 });
  } catch {
    // Optional actions should not hide visibility checks.
  }
}

function noBlockedClaim(text) {
  return blockedClaims.every((claim) => !text.includes(claim));
}

function writeJson(name, data) {
  writeFileSync(resolve(evidenceDir, name), `${JSON.stringify(data, null, 2)}\n`, "utf-8");
}
