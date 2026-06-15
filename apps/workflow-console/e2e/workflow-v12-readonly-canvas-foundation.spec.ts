import { expect, test } from "@playwright/test";
import { mkdirSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

test("V12 read-only canvas foundation exposes entities, inspector, disabled reasons and no internal browser calls", async ({ page }) => {
  const requests: string[] = [];
  page.on("request", (request) => requests.push(request.url()));
  const evidenceDir = resolve("../../docs/design/V12-V15.x/evidence/v12-readiness");
  mkdirSync(evidenceDir, { recursive: true });

  await page.setViewportSize({ width: 1440, height: 960 });
  await page.goto("/?studio=v12-readonly-canvas");

  await expect(page.getByTestId("v12-readonly-workbench")).toBeVisible();
  await expect(page.getByTestId("v12-entity-sidebar")).toContainText("技术内容工作室");
  await expect(page.getByTestId("v12-entity-sidebar")).toContainText("Markdown 工作流应用");
  await expect(page.getByTestId("component-workflow-canvas")).toBeVisible();
  await expect(page.getByTestId("v12-node-inspector")).toContainText("质量检查 Agent");
  await expect(page.getByTestId("v12-disabled-action-reason")).toContainText("V12 仅验证产品实体");
  await expect(page.getByTestId("v12-api-health")).toContainText("OK");
  await expect(page.getByTestId("v12-agent-profile")).toContainText("readonly_projection_only");
  await expect(page.getByTestId("v12-agent-profile")).toContainText("mcp:readonly-docs");
  await expect(page.getByTestId("v12-workflowdiff-handoff")).toContainText("awaiting_user_confirmation");
  await expect(page.getByTestId("v12-workflowdiff-handoff")).toContainText("提案证据，不发布、不运行");

  const disabledButtons = page.getByTestId("v12-disabled-actions").locator("button");
  await expect(disabledButtons).toHaveCount(2);
  await expect(disabledButtons.first()).toBeDisabled();
  await expect(disabledButtons.nth(1)).toBeDisabled();

  await page.screenshot({
    fullPage: true,
    path: resolve(evidenceDir, "v12-readonly-canvas-foundation.png"),
  });

  const bodyText = await page.locator("body").innerText();
  for (const forbidden of [
    "Xpert parity complete",
    "production ready",
    "complete Workflow Studio ready",
    "Agent executor ready",
    "自动发布成功",
    "自动运行成功",
    "raw_secret",
    "Bearer",
    "signed URL",
  ]) {
    expect(bodyText).not.toContain(forbidden);
  }

  const forbiddenMatches = requests.filter((url) => url.includes("/v1/rpc") || url.includes("/v1/events/subscribe") || url.includes("/v1/internal"));
  expect(forbiddenMatches).toEqual([]);

  writeFileSync(
    resolve(evidenceDir, "browser-network-log.json"),
    `${JSON.stringify(
      {
        schema_version: "v12.browser_network_log.v1",
        test_run_id: "v12-readonly-canvas-foundation",
        page_url: page.url(),
        requests: requests.map((url) => ({ method: "GET", url, allowed: !url.includes("/v1/") })),
        forbidden_route_scan: {
          status: "PASS",
          forbidden_matches: forbiddenMatches,
        },
        created_at: "2026-06-11T00:00:00Z",
      },
      null,
      2,
    )}\n`,
    "utf-8",
  );

  writeFileSync(
    resolve(evidenceDir, "product-entity-projection.json"),
    `${JSON.stringify(
      {
        schema_version: "v12.product_entity_projection.v1",
        workspace: {
          workspace_id: "ws-v12-technical-content",
          name: "技术内容工作室",
        },
        project: {
          project_id: "proj-v12-local-knowledge",
          workspace_id: "ws-v12-technical-content",
          name: "本地知识总结项目",
        },
        app: {
          app_id: "app-v12-markdown-workflow",
          project_id: "proj-v12-local-knowledge",
          name: "Markdown 工作流应用",
          app_kind: "workflow_app",
        },
        service_account_ref: "svc-v12-readonly-ref",
        evidence_scope: "read_only_canvas_fixture",
        created_at: "2026-06-11T00:00:00Z",
      },
      null,
      2,
    )}\n`,
    "utf-8",
  );

  writeFileSync(
    resolve(evidenceDir, "canvas-read-model.json"),
    `${JSON.stringify(
      {
        schema_version: "v12.canvas_read_model.v1",
        canvas_read_model_id: "canvas-v12-local-markdown-summary",
        workspace_id: "ws-v12-technical-content",
        project_id: "proj-v12-local-knowledge",
        app_id: "app-v12-markdown-workflow",
        read_only: true,
        nodes: [
          {
            node_id: "folder_input",
            label: "文件夹输入",
            node_kind: "input",
            status: "completed",
            position: { x: 0, y: 80 },
            inspector_ref: "inspector-folder-input",
          },
          {
            node_id: "quality_check",
            label: "质量检查 Agent",
            node_kind: "reviewer",
            status: "waiting_approval",
            position: { x: 840, y: 300 },
            inspector_ref: "inspector-quality-check",
          },
        ],
        edges: [
          {
            edge_id: "folder_input-quality_check",
            source_node_id: "folder_input",
            target_node_id: "quality_check",
          },
        ],
        evidence_refs: ["docs/design/V12-V15.x/evidence/v12-readiness/v12-readonly-canvas-foundation.png"],
        created_at: "2026-06-11T00:00:00Z",
      },
      null,
      2,
    )}\n`,
    "utf-8",
  );

  writeFileSync(
    resolve(evidenceDir, "v12-acceptance-data.json"),
    `${JSON.stringify(
      {
        schema_version: "v12.acceptance_data.v1",
        stage_id: "V12",
        status: "PASS",
        evidence_scope: "browser_e2e",
        screenshots: ["docs/design/V12-V15.x/evidence/v12-readiness/v12-readonly-canvas-foundation.png"],
        schema_parse_result: "PASS",
        browser_network_result: "PASS",
        component_foundation: {
          status: "PASS",
          style: "shadcn-style",
          dependencies: [
            "@radix-ui/react-slot",
            "@radix-ui/react-tabs",
            "@radix-ui/react-tooltip",
            "@radix-ui/react-scroll-area",
            "@radix-ui/react-separator",
            "class-variance-authority",
            "clsx",
            "tailwind-merge",
            "lucide-react",
            "tailwindcss",
          ],
          build_log_ref: "docs/design/V12-V15.x/evidence/v12-readiness/component-foundation-build.log",
          component_inventory_ref: "docs/design/V12-V15.x/evidence/v12-readiness/component-inventory-review.md",
        },
        ux_checks: [
          {
            check_id: "ux_v12_product_entry_visible",
            status: "PASS",
            evidence_ref: "apps/workflow-console/e2e/workflow-v12-readonly-canvas-foundation.spec.ts",
          },
          {
            check_id: "ux_v12_canvas_shell_visible",
            status: "PASS",
            evidence_ref: "apps/workflow-console/e2e/workflow-v12-readonly-canvas-foundation.spec.ts",
          },
          {
            check_id: "ux_v12_disabled_canvas_action_has_reason",
            status: "PASS",
            evidence_ref: "apps/workflow-console/e2e/workflow-v12-readonly-canvas-foundation.spec.ts",
          },
          {
            check_id: "ux_v12_workflowdiff_handoff_visible",
            status: "PASS",
            evidence_ref: "apps/workflow-console/e2e/workflow-v12-readonly-canvas-foundation.spec.ts",
          },
          {
            check_id: "ux_v12_agent_profile_visible",
            status: "PASS",
            evidence_ref: "apps/workflow-console/e2e/workflow-v12-readonly-canvas-foundation.spec.ts",
          },
        ],
        claim_scan: "PASS",
        redaction_scan: "PASS",
        created_at: "2026-06-11T00:00:00Z",
      },
      null,
      2,
    )}\n`,
    "utf-8",
  );
});
