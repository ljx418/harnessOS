import assert from "node:assert/strict";
import test from "node:test";
import { WorkflowConsoleClient } from "../api/workflowConsoleClient.js";

test("operation client uses structured BFF routes only", async () => {
  const calls: Array<{ url: string; body?: string }> = [];
  const originalFetch = globalThis.fetch;
  globalThis.fetch = (async (input: RequestInfo | URL, init?: RequestInit) => {
    calls.push({ url: String(input), body: typeof init?.body === "string" ? init.body : undefined });
    return new Response(JSON.stringify({ operation: "ok", status: "ok", resource: {} }), { status: 200 });
  }) as typeof fetch;
  try {
    const client = new WorkflowConsoleClient("/bff");
    await client.respondApproval("wfi_1", "appr_1", { decision: "approve", user_confirmed: true, source: "approval_panel" });
    await client.updateContext("wfi_1", { op: "set", path: "business.note", value: "ok", expected_revision: 1 });
    await client.emitBusinessEvent("wfi_1", { event_type: "business.workflow.note_submitted", payload: { note: "ok" } });
    await client.listInstanceStationOutputs("wfi_1", "sr_1");
    await client.proposePatch("wf_1", {
      source: "inspector",
      intent_type: "inspector_update",
      operation: "update_station_prompt",
      workflow_instance_id: "wfi_1",
      payload: { station_id: "station_b", prompt_patch: "优化分镜" },
    });
    await client.applyPatch("wf_1", "wfp_1", { workflow_instance_id: "wfi_1", user_confirmed: true, source: "editing_panel" });
    await client.rejectPatch("wf_1", "wfp_1", { workflow_instance_id: "wfi_1", user_confirmed: true, source: "editing_panel" });
    await client.publishWorkflow("wf_1", { version: "2.0.0", expected_draft_revision: 3, user_confirmed: true, source: "editing_panel" });
  } finally {
    globalThis.fetch = originalFetch;
  }
  assert.equal(calls.length, 8);
  assert(calls.slice(0, 4).every((call) => call.url.startsWith("/bff/instances/wfi_1/")));
  assert.equal(calls[4].url, "/bff/workflows/wf_1/patches");
  assert.equal(calls[5].url, "/bff/workflows/wf_1/patches/wfp_1/apply");
  assert.equal(calls[6].url, "/bff/workflows/wf_1/patches/wfp_1/reject");
  assert.equal(calls[7].url, "/bff/workflows/wf_1/publish");
  assert(calls.some((call) => call.body?.includes('"user_confirmed":true')));
  for (const call of calls) {
    assert(!call.url.includes("/v1/rpc"));
    assert(!call.url.includes("/v1/events/subscribe"));
  }
});

test("event bridge client follows the BFF stream", () => {
  const originalEventSource = globalThis.EventSource;
  const urls: string[] = [];
  class FakeEventSource {
    onmessage: ((message: MessageEvent) => void) | null = null;
    constructor(url: string) {
      urls.push(url);
    }
    close() {}
  }
  globalThis.EventSource = FakeEventSource as unknown as typeof EventSource;
  try {
    const client = new WorkflowConsoleClient("/bff");
    const source = client.connectEvents(["approval", "workflow_patch"], () => undefined);
    source.close();
  } finally {
    globalThis.EventSource = originalEventSource;
  }
  assert.equal(urls.length, 1);
  assert(urls[0].startsWith("/bff/events/subscribe?"));
  assert(urls[0].includes("channels=approval%2Cworkflow_patch"));
  assert(urls[0].includes("follow=true"));
});

test("PV17 product closed loop client uses formal BFF routes only", async () => {
  const calls: Array<{ url: string; method: string; body?: string }> = [];
  const originalFetch = globalThis.fetch;
  globalThis.fetch = (async (input: RequestInfo | URL, init?: RequestInit) => {
    calls.push({ url: String(input), method: init?.method || "GET", body: typeof init?.body === "string" ? init.body : undefined });
    const url = String(input);
    const body = url.includes("/health")
      ? { schema_version: "pv17.product_closed_loop.v1", status: "ok", api_status: "ok", gateway_status: "ok", workflow_store_status: "ok", frontend_config_status: "ok", redaction_status: "redacted" }
      : url.includes("/product-console/state")
        ? { schema_version: "pv17.product_closed_loop.v1", workflows: [], station_agents: [], workspace: { entity_kind: "workspace", entity_id: "local", redaction_status: "redacted" }, project: { entity_kind: "project", entity_id: "demo", redaction_status: "redacted" }, app: { entity_kind: "app", entity_id: "reference_app", redaction_status: "redacted" }, evidence_summary: { status: "empty", redaction_status: "redacted" }, audit_refs: [], redaction_status: "redacted" }
        : url.includes("/entities/")
          ? { schema_version: "pv17.product_closed_loop.v1", status: "accepted", entity_ref: { entity_kind: "station_agent", entity_id: "agent" }, audit_ref: { audit_ref_id: "audit", operation: "product_entity.station_agent.upsert", redaction_status: "redacted" }, policy_decision_ref: "policy", redaction_status: "redacted" }
          : url.includes("/patches")
            ? { schema_version: "pv17.product_closed_loop.v1", status: "proposed", workflow_patch: { workflow_patch_id: "wfp_1", workflow_template_id: "wf_1", workflow_draft_id: "wfd_1", operation: "update_station_prompt", status: "proposed" }, audit_refs: [], redaction_status: "redacted" }
            : url.includes("/publish")
              ? { schema_version: "pv17.product_closed_loop.v1", status: "published", publish: { workflow_template_id: "wf_1", workflow_version_id: "wfv_1", version: "2.0.0" }, audit_refs: [], redaction_status: "redacted" }
              : url.includes("/confirm-run")
                ? { schema_version: "pv17.product_closed_loop.v1", status: "started", workflow_instance: { workflow_instance_id: "wfi_1", workflow_template_id: "wf_1", workflow_version_id: "wfv_1", status: "completed" }, station_runs: [], runtime_event_refs: [], trace_refs: [], audit_refs: [], redaction_status: "redacted" }
                : url.includes("/inspect")
                  ? { schema_version: "pv17.product_closed_loop.v1", workflow_instance: { workflow_instance_id: "wfi_1", workflow_template_id: "wf_1", workflow_version_id: "wfv_1", status: "completed" }, status: { workflow_instance_id: "wfi_1", status: "completed", current_station_ids: [] }, station_runs: [], runtime_event_refs: [], trace_refs: [], artifact_refs: [], quality_refs: [], approval_refs: [], audit_refs: [], redaction_status: "redacted" }
                  : url.includes("/evidence/")
                    ? { schema_version: "pv17.product_closed_loop.v1", claims: [], route_boundary: { allowed_prefix: "/bff/pv17", browser_denylist: ["/v1/rpc"], status: "specified" }, redaction: { status: "redacted", secret_allowed: false, provider_payload_allowed: false, artifact_content_allowed: false }, artifact_lineage: { artifact_refs: [] }, trace_timeline: { trace_refs: [] }, missing_evidence: [], allowed_claim: "PV17 complete: product closed loop implementation ready for bounded review.", audit_refs: [], redaction_status: "redacted" }
                    : { schema_version: "pv17.product_closed_loop.v1", workflow_template: { workflow_template_id: "wf_1", name: "Workflow" }, draft: {}, versions: [], graph: { nodes: [], edges: [], redaction_status: "redacted" }, inspector: {}, patch_queue: [], audit_refs: [], redaction_status: "redacted" };
    return new Response(JSON.stringify(body), { status: 200 });
  }) as typeof fetch;
  try {
    const client = new WorkflowConsoleClient("/bff");
    await client.getPV17SystemHealth();
    await client.getPV17ProductConsoleState();
    await client.mutatePV17Entity("station-agents", {
      entity_kind: "station_agent",
      operation: "upsert",
      user_confirmed: true,
      source: "product_console",
      idempotency_key: "pv17-agent",
      payload: { entity_id: "agent" },
    });
    await client.getPV17StudioWorkflow("wf_1");
    await client.proposePV17Patch("wf_1", {
      source: "inspector",
      intent_type: "inspector_update",
      operation: "update_station_prompt",
      workflow_instance_id: "wfi_1",
      payload: { station_id: "station_b", prompt_ref: "pv17.prompt" },
    });
    await client.publishPV17Workflow("wf_1", {
      user_confirmed: true,
      source: "mission_studio",
      idempotency_key: "pv17-publish",
      expected_draft_revision: 1,
      version: "2.0.0",
    });
    await client.confirmPV17Run("wf_1", {
      user_confirmed: true,
      source: "run_panel",
      idempotency_key: "pv17-run",
      workflow_template_id: "wf_1",
      workflow_version_id: "wfv_1",
    });
    await client.inspectPV17Instance("wfi_1");
    await client.getPV17EvidenceSummary("wfi_1");
  } finally {
    globalThis.fetch = originalFetch;
  }
  assert.equal(calls.length, 9);
  assert(calls.every((call) => call.url.startsWith("/bff/pv17/")));
  assert(calls.every((call) => !call.url.includes("/bff/pv16/")));
  assert(calls.every((call) => !call.url.includes("/v1/rpc")));
  assert(calls.some((call) => call.body?.includes('"user_confirmed":true')));
});
