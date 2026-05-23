"""Tests for BoxArena pre-flight integration (SpecGap before runtime eval)."""

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from specgap.integrations.boxarena_adapter import (
    BoxArenaContext,
    enrich_implementation_claim,
    load_spec_with_boxarena_context,
    run_boxarena_preflight,
)
from specgap.models import SpecInput

EXAMPLES = pathlib.Path(__file__).resolve().parents[1] / "examples"


def test_enrich_implementation_claim_adds_baseline_and_quest():
    spec = SpecInput(
        title="t",
        stakeholder_intent="no network",
        formalized_policy="policy",
        implementation_claim="claim",
    )
    ctx = BoxArenaContext(
        quest="docker_socket",
        append_baseline_compose_claim=True,
    )
    enriched = enrich_implementation_claim(spec, ctx)
    assert "docker/compose.yaml" in enriched.implementation_claim
    assert "docker_socket" in enriched.implementation_claim
    assert enriched.implementation_claim.startswith("claim")


def test_preflight_divergence_example_fails():
    spec, ctx = load_spec_with_boxarena_context(
        EXAMPLES / "boxarena_preflight_divergence.json")
    result = run_boxarena_preflight(spec, ctx)
    assert result.verdict == "fail"
    assert result.proceed_to_boxarena is False
    assert result.failed_implication_checks >= 1
    assert result.divergence_count >= 1
    assert result.boxarena_quest == "net_lateral"
    assert "harness run" in result.suggested_boxarena_command
    assert "BoxArena Pre-Flight Bridge" in result.specgap_report_markdown
    payload = json.loads(result.to_json())
    assert payload["phase"] == "specgap_preflight"
    assert payload["tool"] == "specgap"
    assert "specgap_report_markdown" not in payload
    assert any("not runtime verification" in d.lower() for d in payload["disclaimers"])


def test_preflight_evidence_chain_written(tmp_path):
    spec, ctx = load_spec_with_boxarena_context(
        EXAMPLES / "boxarena_preflight_divergence.json")
    result = run_boxarena_preflight(spec, ctx)
    out = tmp_path / "evidence.json"
    out.write_text(result.to_json() + "\n", encoding="utf-8")
    data = json.loads(out.read_text())
    assert data["verdict"] == "fail"
    assert data["boxarena_quest"] == "net_lateral"


def test_preflight_pass_example():
    spec, ctx = load_spec_with_boxarena_context(
        EXAMPLES / "boxarena_preflight_pass.json")
    result = run_boxarena_preflight(spec, ctx)
    assert result.verdict == "pass"
    assert result.proceed_to_boxarena is True
    assert result.failed_implication_checks == 0
    assert result.divergence_count == 0


def test_load_spec_with_boxarena_context():
    spec, ctx = load_spec_with_boxarena_context(
        EXAMPLES / "boxarena_preflight_divergence.json")
    assert spec.title.startswith("BoxArena")
    assert ctx.quest == "net_lateral"
    assert ctx.append_baseline_compose_claim is True
