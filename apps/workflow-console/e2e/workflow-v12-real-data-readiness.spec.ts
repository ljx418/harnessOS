import { expect, test, type APIRequestContext } from "@playwright/test";
import { mkdirSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

const bffBaseURL = `http://127.0.0.1:${process.env.WORKFLOW_CONSOLE_BFF_PORT || "18040"}`;
const evidenceDir = resolve("../../docs/design/V12-V15.x/evidence/v12-current-stage-real-data");

test("V12 current stage uses BFF-shaped real DTO data for read-only workbench acceptance", async ({ page, request }) => {
  mkdirSync(evidenceDir, { recursive: true });
  const browserRequests: Array<{ method: string; url: string; allowed: boolean }> = [];
  page.on("request", (browserRequest) => {
    const url = browserRequest.url();
    browserRequests.push({
      method: browserRequest.method(),
      url,
      allowed: !url.includes("/v1/rpc") && !url.includes("/v1/events/subscribe") && !url.includes("/v1/internal"),
    });
  });

  const health = await readJson(request, `${bffBaseURL}/bff/v12/system/health`);
  const workspaces = await readJson(request, `${bffBaseURL}/bff/v12/workspaces`);
  const workspace = workspaces.workspaces[0];
  const projects = await readJson(request, `${bffBaseURL}/bff/v12/workspaces/${workspace.workspace_id}/projects`);
  const project = projects.projects[0];
  const apps = await readJson(request, `${bffBaseURL}/bff/v12/projects/${project.project_id}/apps`);
  const app = apps.apps[0];
  const agents = await readJson(request, `${bffBaseURL}/bff/v12/apps/${app.app_id}/station-agents`);
  const canvas = await readJson(request, `${bffBaseURL}/bff/v12/apps/${app.app_id}/canvas`);
  const selectedNode = canvas.nodes.find((node: { node_id: string }) => node.node_id === "quality_check") ?? canvas.nodes[0];
  const inspector = await readJson(request, `${bffBaseURL}/bff/v12/canvas/nodes/${selectedNode.node_id}/inspector`);
  const wrongWorkspace = await request.get(`${bffBaseURL}/bff/v12/workspaces/wrong-workspace/projects`);
  expect(wrongWorkspace.status()).toBe(404);

  await page.setViewportSize({ width: 1440, height: 960 });
  await page.goto("/?studio=v12-readonly-canvas");

  await expect(page.getByTestId("v12-readonly-workbench")).toBeVisible();
  await expect(page.getByTestId("v12-bff-source")).toContainText("real BFF projection");
  await expect(page.getByTestId("v12-api-health")).toContainText("OK");
  await expect(page.getByTestId("v12-entity-sidebar")).toContainText(workspace.name);
  await expect(page.getByTestId("v12-entity-sidebar")).toContainText(project.name);
  await expect(page.getByTestId("v12-entity-sidebar")).toContainText(app.name);
  await expect(page.getByTestId("v12-bff-boundary")).toContainText(canvas.canvas_read_model_id);
  await expect(page.getByTestId("v12-agent-profile")).toContainText(inspector.goal);
  await expect(page.getByTestId("v12-workflowdiff-handoff")).toContainText(inspector.audit_ref);
  await expect(page.getByTestId("v12-workflowdiff-handoff")).toContainText("提案证据，不发布、不运行");

  await page.screenshot({
    fullPage: true,
    path: resolve(evidenceDir, "v12-real-data-readonly-workbench.png"),
  });

  const forbiddenMatches = browserRequests.filter((entry) => !entry.allowed).map((entry) => entry.url);
  expect(forbiddenMatches).toEqual([]);
  const bodyText = await page.locator("body").innerText();
  for (const forbidden of [
    "Xpert parity complete",
    "production ready",
    "complete Workflow Studio ready",
    "Agent executor ready",
    "raw_secret",
    "Bearer",
    "signed URL",
  ]) {
    expect(bodyText).not.toContain(forbidden);
  }

  writeJson("bff-route-log.json", {
    schema_version: "v12.current_stage_bff_route_log.v1",
    status: "PASS",
    routes: [
      "/bff/v12/system/health",
      "/bff/v12/workspaces",
      `/bff/v12/workspaces/${workspace.workspace_id}/projects`,
      `/bff/v12/projects/${project.project_id}/apps`,
      `/bff/v12/apps/${app.app_id}/station-agents`,
      `/bff/v12/apps/${app.app_id}/canvas`,
      `/bff/v12/canvas/nodes/${selectedNode.node_id}/inspector`,
    ],
    wrong_workspace_status: wrongWorkspace.status(),
    created_at: "2026-06-23T00:00:00Z",
  });
  writeJson("browser-network-log.json", {
    schema_version: "v12.browser_network_log.v1",
    test_run_id: "v12-current-stage-real-data",
    page_url: page.url(),
    requests: browserRequests,
    forbidden_route_scan: {
      status: "PASS",
      forbidden_matches: forbiddenMatches,
    },
    created_at: "2026-06-23T00:00:00Z",
  });
  writeJson("product-entity-projection.json", {
    schema_version: "v12.product_entity_projection.v1",
    workspace,
    project,
    app,
    service_account_ref: "svc-v12-readonly-redacted-ref",
    evidence_scope: "browser_e2e",
    created_at: "2026-06-23T00:00:00Z",
  });
  writeJson("canvas-read-model.json", canvas);
  writeJson("canvas-inspector-projection.json", inspector);
  writeJson("station-agents.json", agents);
  writeJson("system-health.json", health);
  writeJson("v12-current-stage-acceptance-data.json", {
    schema_version: "v12.current_stage_acceptance.v1",
    stage_id: "V12-current-stage-real-data",
    status: "PASS",
    evidence_scope: "browser_e2e_bff_shaped_real_data",
    runtime_backed: false,
    browser_backed: true,
    bff_backed: true,
    canvas_foundation_backed: true,
    xpert_reference_used_as_runtime_evidence: false,
    scenario_results: [
      { scenario_id: "US-V12-01", status: "PASS" },
      { scenario_id: "US-V12-03", status: "PASS" },
      { scenario_id: "US-V12-04", status: "PASS" },
      { scenario_id: "US-V12-05", status: "PASS" },
      { scenario_id: "US-V12-06", status: "PASS" },
    ],
    claim_scan: "PASS",
    redaction_scan: "PASS",
    created_at: "2026-06-23T00:00:00Z",
  });
});

async function readJson(request: APIRequestContext, url: string) {
  const response = await request.get(url);
  const body = await response.text();
  expect(response.ok(), body).toBe(true);
  return JSON.parse(body);
}

function writeJson(name: string, data: unknown) {
  writeFileSync(resolve(evidenceDir, name), `${JSON.stringify(data, null, 2)}\n`, "utf-8");
}
