"""PV22 bounded external app contract registry."""

from __future__ import annotations

from typing import Any

from core.protocol.contracts.error_inventory import ERROR_INVENTORY
from core.protocol.contracts.event_inventory import EVENT_INVENTORY
from core.protocol.contracts.method_inventory import METHOD_INVENTORY
from core.protocol.schemas.methods import METHOD_SCHEMAS


CONTRACT_VERSION = "pv22.external_app_contract.v1"
DEFAULT_EXTERNAL_METHODS = (
    "session.start",
    "turn.start",
    "events.subscribe",
    "artifact.list",
    "artifact.read_metadata",
    "artifact.register_external",
    "artifact.lineage",
    "job.get",
    "job.list",
    "approval.respond",
    "connector.health",
    "pack.list",
    "pack.get",
)
DEFAULT_EXTERNAL_CHANNELS = ("chat", "job", "artifact", "approval")
DEFAULT_EXTERNAL_ERRORS = (
    "INVALID_PARAMS",
    "AUTH_REQUIRED",
    "AUTH_INVALID",
    "AUTH_FORBIDDEN",
    "CAPABILITY_DENIED",
    "SCOPE_MISMATCH",
    "METHOD_FORBIDDEN",
    "SESSION_NOT_FOUND",
    "APP_PROFILE_NOT_FOUND",
    "SUBSCRIPTION_TOKEN_INVALID",
    "SUBSCRIPTION_TOKEN_SCOPE_MISMATCH",
    "SUBSCRIPTION_TOKEN_CHANNEL_DENIED",
    "APPROVAL_CONFLICT",
    "APPROVAL_NOT_FOUND",
    "ARTIFACT_READ_BLOCKED",
    "PACK_NOT_FOUND",
    "CONNECTOR_NOT_FOUND",
)


def build_pv22_external_app_contract_registry() -> dict[str, Any]:
    """Build the bounded PV22 registry from existing protocol inventories."""
    methods_by_name = {str(entry["method"]): entry for entry in METHOD_SCHEMAS}
    method_inventory = {str(entry["method"]): entry for entry in METHOD_INVENTORY}
    selected_methods = []
    for method in DEFAULT_EXTERNAL_METHODS:
        schema = dict(methods_by_name[method])
        inventory = method_inventory.get(method, {})
        selected_methods.append(
            {
                "method": method,
                "capability": schema["capability"],
                "stability": schema["stability"],
                "status": schema["status"],
                "sdk_exposure": schema["sdk_exposure"],
                "runtime_handler": schema["runtime_handler"],
                "scope_required": schema["scope_required"],
                "auth_required": True,
                "errors": list(schema["errors"]),
                "handler_ref": inventory.get("handler_ref"),
            }
        )

    forbidden_methods = [
        {
            "method": str(entry["method"]),
            "capability": str(entry.get("capability") or ""),
            "reason": str(entry.get("forbidden_reason") or "not part of PV22 default external surface"),
        }
        for entry in METHOD_INVENTORY
        if entry.get("surface") == "forbidden_by_default"
    ]
    forbidden_methods.append(
        {
            "method": "method.list",
            "capability": "rpc",
            "reason": "introspection is not part of the default external SDK/BFF surface",
        }
    )

    capabilities = sorted({str(method["capability"]) for method in selected_methods})
    events = [
        {
            "type": str(event["type"]),
            "channel": str(event["channel"]),
            "status": str(event["status"]),
            "replayable": bool(event["replayable"]),
        }
        for event in EVENT_INVENTORY
        if event.get("channel") in DEFAULT_EXTERNAL_CHANNELS
    ]
    errors = [
        {
            "code": str(error["code"]),
            "category": str(error["category"]),
            "retryable": bool(error["retryable"]),
            "status": str(error["status"]),
        }
        for error in ERROR_INVENTORY
        if error.get("code") in DEFAULT_EXTERNAL_ERRORS
    ]
    return {
        "contract_version": CONTRACT_VERSION,
        "allowed_claim": "PV22 external app contract ready for bounded integration review.",
        "default_scope": {
            "app_id": "reference_app",
            "project_id": "demo",
            "workspace_id": "local",
        },
        "methods": selected_methods,
        "events": events,
        "errors": errors,
        "capabilities": capabilities,
        "forbidden_methods": forbidden_methods,
        "route_boundary": {
            "browser_allowed_prefixes": ["/bff/"],
            "browser_forbidden_prefixes": ["/v1/rpc", "/v1/internal/", "/runtime/"],
            "sdk_server_route": "/v1/rpc",
        },
        "not_claimed": [
            "production ready",
            "external ecosystem complete",
            "commercial readiness complete",
            "unrestricted third-party app access",
            "complete Workflow Studio ready",
            "Agent executor ready",
        ],
    }


def validate_pv22_external_app_contract_registry(registry: dict[str, Any]) -> list[str]:
    """Return registry validation errors."""
    errors: list[str] = []
    method_names = {str(item.get("method")) for item in registry.get("methods", [])}
    if method_names != set(DEFAULT_EXTERNAL_METHODS):
        errors.append("method subset drift")
    forbidden = {str(item.get("method")) for item in registry.get("forbidden_methods", [])}
    if method_names & forbidden:
        errors.append("forbidden method exposed")
    if any(str(item.get("capability")) in {"admin", "debug", "internal"} for item in registry.get("methods", [])):
        errors.append("admin/debug/internal capability exposed")
    if "/v1/rpc" not in registry.get("route_boundary", {}).get("browser_forbidden_prefixes", []):
        errors.append("browser raw rpc boundary missing")
    if registry.get("contract_version") != CONTRACT_VERSION:
        errors.append("contract version drift")
    return errors
