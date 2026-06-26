from __future__ import annotations

import asyncio
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from apps.gateway.approvals import ApprovalStore
from apps.gateway.artifacts import ArtifactRegistry
from apps.gateway.protocol import RpcRequest
from apps.gateway.runtime import GatewayRuntimePool
from apps.gateway.service import GatewayService
from apps.gateway.storage import GatewaySessionStore
from apps.gateway.traces import TraceStore
from core.apps.profiles import AppProfile


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = ROOT / "tests/fixtures/v3_6/dummy_pipeline"
SCOPE = {"app_id": "reference_app", "project_id": "demo_a", "workspace_id": "local"}
DEFAULT_CAPABILITIES = (
    "rpc",
    "events",
    "artifacts",
    "artifacts.read",
    "artifact_lineage",
    "jobs",
    "jobs.read",
    "approvals",
    "approvals.read",
    "workflows.read",
    "workflows.write",
    "workflows.execute",
    "workflow_versions.publish",
    "stations.read",
    "stations.execute",
    "quality.read",
    "quality.write",
    "board.read",
    "workflow_context.read",
    "workflow_context.write",
    "business_events.read",
    "business_events.write",
    "workflow_patches.read",
    "workflow_patches.write",
    "agent_talk.read",
    "agent_talk.write",
    "agent_suggestions.read",
    "agent_suggestions.write",
    "agent_actions.read",
    "agent_actions.write",
    "agent_handoffs.read",
    "agent_handoffs.write",
    "agent_audit.read",
    "operation_evidence.read",
    "governance_review.read",
)


def build_pv17_gateway(runtime_root: Path) -> GatewayService:
    runtime = GatewayRuntimePool(
        store=GatewaySessionStore(runtime_root / "sessions"),
        artifact_registry=ArtifactRegistry(runtime_root / "artifacts"),
        trace_store=TraceStore(runtime_root / "traces"),
        approval_store=ApprovalStore(runtime_root / "approvals"),
    )
    service = GatewayService(runtime_pool=runtime)
    service.app_registry.register(
        AppProfile(
            app_id="reference_app",
            display_name="Reference App",
            domain="reference",
            default_pack="reference_app",
            allowed_origins=(
                "http://127.0.0.1:5173",
                "http://127.0.0.1:4174",
                "http://127.0.0.1:4178",
                "http://127.0.0.1:5180",
                "http://localhost:5173",
                "http://localhost:4174",
            ),
            default_capabilities=DEFAULT_CAPABILITIES,
        )
    )
    return service


async def seed_pv17_gateway(service: GatewayService, *, template_id: str = "pv17_product_closed_loop_reference") -> dict[str, Any]:
    template = _load_template(template_id)
    created = await _rpc(service, "workflow.template.create", {"template": template, "scope": SCOPE})
    published = await _rpc(
        service,
        "workflow.template.publish",
        {"workflow_template_id": template_id, "version": "1.0.0", "scope": SCOPE},
    )
    started = await _rpc(
        service,
        "workflow.instance.start",
        {"workflow_version_id": published["version"]["workflow_version_id"], "scope": SCOPE},
    )
    instance = started["workflow_instance"]
    runs = (
        await _rpc(
            service,
            "station.run.list",
            {"workflow_instance_id": instance["workflow_instance_id"], "scope": SCOPE},
        )
    )["station_runs"]
    station_b = next(run for run in runs if run["station_id"] == "station_b")
    quality = await _rpc(
        service,
        "quality.evaluation.create",
        {
            "evaluation": {
                "workflow_instance_id": instance["workflow_instance_id"],
                "station_run_id": station_b["station_run_id"],
                "artifact_id": station_b["output_artifact_ids"][0],
                "rubric_id": "dummy_quality",
                "evaluator_type": "rule",
                "score": 0.92,
                "status": "passed",
                "issues": [{"summary": "PV17 reference output is reviewable."}],
                "suggestions": [{"summary": "Keep evidence refs visible and redacted."}],
                "metadata": {"source": "pv17_reference_seed"},
            },
            "auto_attach": True,
            "scope": SCOPE,
        },
    )
    await _rpc(
        service,
        "workflow.template.update_draft",
        {"workflow_template_id": template_id, "draft": deepcopy(published["version"]["snapshot"]), "scope": SCOPE},
    )
    patch = await _rpc(
        service,
        "workflow.patch.propose",
        {
            "workflow_template_id": template_id,
            "patch": {
                "operation": "update_station_prompt",
                "payload": {"station_id": "station_b", "prompt_ref": "reference.prompt.v2"},
                "actor_type": "agent",
                "actor_id": "agent_reference",
                "proposed_by": "agent_reference",
                "metadata": {"workflow_instance_id": instance["workflow_instance_id"]},
            },
            "scope": SCOPE,
        },
    )
    return {
        "template": created["template"],
        "version": published["version"],
        "instance": instance,
        "runs": runs,
        "quality": quality["evaluation"],
        "patch": patch["patch"],
    }


def create_seeded_gateway(runtime_root: Path) -> tuple[GatewayService, dict[str, Any]]:
    service = build_pv17_gateway(runtime_root)
    seeded = asyncio.run(seed_pv17_gateway(service))
    return service, seeded


async def _rpc(service: GatewayService, method: str, params: dict[str, Any]) -> Any:
    response = await service.handle_rpc(RpcRequest(id=method, method=method, params=params))
    if response.error is not None:
        raise RuntimeError(f"{method} failed: {response.error}")
    return response.result


def _load_template(template_id: str) -> dict[str, Any]:
    payload = json.loads((FIXTURE_DIR / "workflow_template.json").read_text(encoding="utf-8"))
    payload["workflow_template_id"] = template_id
    payload["name"] = "PV17 Product Closed Loop Reference"
    return payload
