"""PV22 external app contract bounded acceptance tests."""

from __future__ import annotations

import json
from pathlib import Path

from core.apps.profiles import build_default_app_registry
from core.protocol.contracts.pv22_external_app_contract import (
    build_pv22_external_app_contract_registry,
    validate_pv22_external_app_contract_registry,
)
from scripts.pv22_external_app_contract_acceptance import EVIDENCE_DIR, main


ROOT = Path(__file__).resolve().parents[1]


def test_pv22_contract_registry_is_valid_and_bounded() -> None:
    registry = build_pv22_external_app_contract_registry()
    assert validate_pv22_external_app_contract_registry(registry) == []
    assert registry["contract_version"] == "pv22.external_app_contract.v1"
    assert {item["method"] for item in registry["methods"]} >= {"session.start", "turn.start", "events.subscribe"}
    assert "method.list" in {item["method"] for item in registry["forbidden_methods"]}
    assert "/v1/rpc" in registry["route_boundary"]["browser_forbidden_prefixes"]
    assert not {"admin", "debug", "internal"} & set(registry["capabilities"])


def test_reference_app_profile_is_registered_for_external_contract() -> None:
    profile = build_default_app_registry().get("reference_app")
    assert profile.default_pack == "reference_app_pack"
    assert "http://localhost:5173" in profile.allowed_origins
    assert not {"admin", "debug", "internal"} & set(profile.default_capabilities)
    assert profile.metadata["contract"] == "pv22.external_app_contract.v1"


def test_pv22_acceptance_runner_generates_evidence_package() -> None:
    assert main() == 0
    acceptance = json.loads((EVIDENCE_DIR / "acceptance-data.json").read_text(encoding="utf-8"))
    manifest = json.loads((EVIDENCE_DIR / "artifact-manifest.json").read_text(encoding="utf-8"))
    assert acceptance["status"] == "PASS"
    assert acceptance["reports"]["negative_fixtures"] == "PASS"
    assert acceptance["reports"]["reference_app"] == "PASS"
    assert manifest["status"] == "PASS"
    assert manifest["count"] >= 10
    assert (EVIDENCE_DIR / "acceptance-report.html").exists()
