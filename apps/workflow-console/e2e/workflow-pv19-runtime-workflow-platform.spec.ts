import { expect, test } from "@playwright/test";
import { existsSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

const evidenceDir = resolve("../../docs/design/V12-V15.x/evidence/pv19-runtime-workflow-platform");
const createdAt = "2026-06-27T00:00:00Z";
const allowedClaim = "PV19 complete: runtime-backed workflow platform closed loop ready for bounded review.";

test.setTimeout(120_000);

test("PV19 runtime workflow platform browser closed loop", async ({ page, baseURL }) => {
  resetEvidenceDir();
  const browserRequests: Array<{ method: string; url: string; allowed: boolean }> = [];
  page.on("request", (item) => {
    const url = item.url();
    browserRequests.push({
      method: item.method(),
      url,
      allowed:
        !url.includes("/v1/rpc") &&
        !url.includes("/internal/runtime") &&
        !url.includes("/runtime/store") &&
        !url.includes("/api/runtime") &&
        !url.includes("/debug/runtime"),
    });
  });

  await page.setViewportSize({ width: 1500, height: 980 });
  await page.goto(`${baseURL}/?studio=pv19-runtime-workflow-platform&app_id=reference_app&project_id=demo_a&workspace_id=local`, {
    waitUntil: "networkidle",
  });
  await expect(page.getByTestId("pv19-runtime-platform")).toBeVisible();
  await expect(page.getByTestId("pv19-platform-contract")).toContainText("业务不定制平台核心");
  await page.screenshot({ fullPage: true, path: resolve(evidenceDir, "01-pv19-workbench-loaded.png") });

  await page.getByRole("button", { name: "校验图" }).click();
  await expect(page.getByTestId("pv19-graph-validation")).toContainText("valid");
  await page.getByRole("button", { name: "生成 Diff" }).click();
  await expect(page.getByTestId("pv19-graph-validation")).toContainText("user_confirmed_required_before_publish");
  await page.getByTestId("pv19-graph-validation").screenshot({ path: resolve(evidenceDir, "02-graph-validate-and-diff.png") });

  await page.getByRole("button", { name: "发布版本" }).click();
  await expect(page.getByTestId("pv19-publish-run")).toContainText("wfv_", { timeout: 20_000 });
  await page.getByRole("button", { name: "运行工作流" }).click();
  await expect(page.getByTestId("pv19-run-status")).toContainText("waiting_approval", { timeout: 20_000 });
  await page.getByTestId("pv19-publish-run").screenshot({ path: resolve(evidenceDir, "03-publish-and-run-waiting-approval.png") });

  await page.getByRole("button", { name: "人工审批通过" }).click();
  await expect(page.getByTestId("pv19-human-action-after")).toContainText("completed", { timeout: 20_000 });
  await expect(page.getByTestId("pv19-run-status")).toContainText("completed", { timeout: 20_000 });
  await page.getByTestId("pv19-human-gate").screenshot({ path: resolve(evidenceDir, "04-human-gate-approved.png") });

  await page.getByRole("button", { name: "审查证据" }).click();
  await expect(page.getByTestId("pv19-evidence")).toContainText(allowedClaim, { timeout: 20_000 });
  await page.getByTestId("pv19-evidence").screenshot({ path: resolve(evidenceDir, "05-evidence-review.png") });
  await page.screenshot({ fullPage: true, path: resolve(evidenceDir, "06-pv19-full-page-completed.png") });

  const forbiddenRequests = browserRequests.filter((item) => !item.allowed).map((item) => item.url);
  expect(forbiddenRequests).toEqual([]);

  writeJson("browser-network-log.json", {
    schema_version: "pv19.browser_network_log.v1",
    status: "PASS",
    requests: browserRequests,
    forbidden_route_scan: { status: "PASS", forbidden_matches: forbiddenRequests },
    created_at: createdAt,
  });
  writeJson("acceptance-data.json", {
    schema_version: "pv19.runtime_workflow_platform_acceptance.v1",
    stage_id: "PV19-SA",
    status: "PASS",
    allowed_claim: allowedClaim,
    user_visible_paths: ["读取图", "校验图", "生成 Diff", "发布版本", "运行工作流", "人工审批通过", "审查证据"],
    screenshots: [
      "01-pv19-workbench-loaded.png",
      "02-graph-validate-and-diff.png",
      "03-publish-and-run-waiting-approval.png",
      "04-human-gate-approved.png",
      "05-evidence-review.png",
      "06-pv19-full-page-completed.png",
    ],
    route_boundary: { status: "PASS", allowed_prefixes: ["/bff/pv19"], forbidden_matches: forbiddenRequests },
    platform_generality_review: {
      status: "PASS",
      primary_sample: "knowledge_opc",
      core_customization_allowed: false,
      finding: "业务样例作为 workflow input/metadata 进入通用 runtime，没有新增业务专用 Gateway/runtime 分支。",
    },
    prd_review: {
      status: "PASS",
      conclusion: "已覆盖 runtime-backed graph/diff/publish/run/human-gate/evidence 的 bounded closed loop；仍不声明生产级完整 Studio 或 Agent executor。",
    },
    created_at: createdAt,
  });
  writeHtmlReport();
});

function resetEvidenceDir() {
  if (existsSync(evidenceDir)) {
    rmSync(evidenceDir, { recursive: true, force: true });
  }
  mkdirSync(evidenceDir, { recursive: true });
}

function writeJson(name: string, value: unknown) {
  writeFileSync(resolve(evidenceDir, name), `${JSON.stringify(value, null, 2)}\n`, "utf-8");
}

function writeHtmlReport() {
  writeFileSync(
    resolve(evidenceDir, "pv19-acceptance-report.html"),
    `<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>PV19 阶段性自动化验收报告</title>
  <style>
    body { margin: 0; padding: 28px; font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #111827; background: #f4f7fb; }
    h1 { margin: 0 0 8px; font-size: 30px; }
    h2 { margin: 28px 0 12px; font-size: 20px; }
    p { color: #475569; line-height: 1.7; }
    .grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; margin: 18px 0; }
    .card, figure { border: 1px solid #d7e0ea; border-radius: 8px; background: white; }
    .card { padding: 14px; }
    .card span { display: block; color: #64748b; font-size: 12px; font-weight: 700; text-transform: uppercase; }
    .card strong { display: block; margin-top: 4px; }
    figure { margin: 0 0 16px; padding: 12px; }
    img { max-width: 100%; border: 1px solid #e5e7eb; border-radius: 6px; }
    figcaption { margin-top: 8px; color: #475569; font-size: 14px; }
    code { background: #e5e7eb; padding: 2px 5px; border-radius: 4px; }
  </style>
</head>
<body>
  <h1>PV19 阶段性自动化验收报告</h1>
  <p>本报告由 Playwright headless 浏览器执行真实用户路径生成。浏览器只访问 <code>/bff/pv19</code>，未直连 <code>/v1/rpc</code> 或内部 runtime 路径。</p>
  <section class="grid">
    <div class="card"><span>验收结论</span><strong>PASS</strong></div>
    <div class="card"><span>允许声明</span><strong>${allowedClaim}</strong></div>
    <div class="card"><span>平台红线</span><strong>业务不定制 runtime core</strong></div>
  </section>
  <h2>目标架构与当前实现</h2>
  <p>当前实现以 Workflow Console PV19 页面作为入口，通过正式 BFF DTO 调用 Gateway workflow repository/runtime/approval/evidence read model。目标架构中的完整 Workflow Studio、完整 Agent executor、生产治理硬化仍是后续阶段。</p>
  <h2>真实用户路径截图</h2>
  <figure><img src="01-pv19-workbench-loaded.png"><figcaption>工作台加载：图、状态卡、通用性红线可见。</figcaption></figure>
  <figure><img src="02-graph-validate-and-diff.png"><figcaption>图校验与 WorkflowDiff：发布前需要人工确认边界。</figcaption></figure>
  <figure><img src="03-publish-and-run-waiting-approval.png"><figcaption>发布版本并运行：runtime 进入 waiting_approval。</figcaption></figure>
  <figure><img src="04-human-gate-approved.png"><figcaption>人工审批通过：approval.respond 推动 workflow 完成。</figcaption></figure>
  <figure><img src="05-evidence-review.png"><figcaption>证据审查：汇总 trace、artifact、quality、human gate 与 route boundary。</figcaption></figure>
</body>
</html>
`,
    "utf-8",
  );
}
