"""Tests for constraint extraction and structural semantic divergence."""

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from specgap.cli import analyze
from specgap.extractor import _fuzzy_extract_via_paraphrase_map, extract_all
from specgap.models import SpecInput
from specgap.reporter import EMPTY_INTENT_WARNING, build_report
from specgap.semantic_diff import diff

EXAMPLES = pathlib.Path(__file__).resolve().parents[1] / "examples"


def _load(name):
    return SpecInput.from_dict(json.loads((EXAMPLES / name).read_text(encoding="utf-8")))


def _kinds(result):
    return {d.kind for d in result.divergences}


def test_example_a_extraction():
    """'No network access' vs 'localhost only' extracts the expected constraints."""
    by_source = extract_all(_load("sandbox_no_network.json"))
    assert "no_network" in {c.name for c in by_source["stakeholder_intent"]}
    assert "localhost_only" in {c.name for c in by_source["formalized_policy"]}
    assert "localhost_only" in {c.name for c in by_source["implementation_claim"]}


def test_example_a_divergence():
    """Example A produces a weakened constraint and a claim-not-implied finding."""
    result = diff(extract_all(_load("sandbox_no_network.json")))
    kinds = _kinds(result)
    assert "weakened_constraint" in kinds
    assert "claim_not_implied" in kinds
    assert result.high_severity


def test_example_b_divergence():
    """'Read-only filesystem' vs 'writes allowed to /tmp' is a weakened constraint."""
    by_source = extract_all(_load("sandbox_readonly_fs.json"))
    assert "readonly_fs" in {c.name for c in by_source["stakeholder_intent"]}
    assert "write_allowed" in {c.name for c in by_source["formalized_policy"]}
    result = diff(by_source)
    assert "weakened_constraint" in _kinds(result)
    assert "claim_not_implied" in _kinds(result)


def test_example_c_divergence():
    """'No privilege escalation' vs 'setuid allowed' is weakened + claim-not-implied."""
    by_source = extract_all(_load("syscall_policy_mismatch.json"))
    assert "no_privilege_escalation" in {c.name for c in by_source["stakeholder_intent"]}
    assert "setuid_allowed" in {c.name for c in by_source["implementation_claim"]}
    assert "syscall_denylist" in {c.name for c in by_source["formalized_policy"]}
    result = diff(by_source)
    kinds = _kinds(result)
    assert "weakened_constraint" in kinds
    assert "claim_not_implied" in kinds


def test_comparison_table_has_rows():
    result = diff(extract_all(_load("sandbox_no_network.json")))
    assert result.table
    assert all("category" in row for row in result.table)


def test_write_path_is_extracted():
    by_source = extract_all(_load("sandbox_readonly_fs.json"))
    writes = [c for c in by_source["formalized_policy"] if c.name == "write_allowed"]
    assert writes and writes[0].params.get("path") == "/tmp"


# --- A: empty-intent guard ---------------------------------------------------

def test_empty_intent_guard_does_not_report_clean():
    """Rule mode on a paraphrased intent extracts nothing; the report must flag
    an extraction failure rather than claiming a clean / no-divergence result."""
    spec = _load("04_paraphrased_sandbox.json")
    analysis = analyze(spec, mode="rule")
    assert analysis.by_source["stakeholder_intent"] == []
    report = build_report(spec, analysis.by_source, analysis.diff_result,
                          analysis.implications, analysis.consistencies,
                          extractor_mode="rule")
    assert EMPTY_INTENT_WARNING in report
    assert "No divergence detected" not in report


# --- C/D: fuzzy extraction (offline paraphrase fallback) ---------------------

def test_offline_fuzzy_paraphrase_map_maps_airgapped_to_no_network():
    constraints = _fuzzy_extract_via_paraphrase_map(
        "The container must be air-gapped from any external service.",
        "stakeholder_intent")
    assert [c.name for c in constraints] == ["no_network"]
    c = constraints[0]
    assert c.method == "fuzzy"
    assert c.requires_human_review is True
    assert 0.0 < c.confidence <= 1.0


def test_fuzzy_mode_recovers_paraphrased_intent(monkeypatch):
    """E: with fuzzy extraction the air-gapped intent becomes no_network, and the
    policy's localhost allowance is a concrete implication failure."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)  # force offline fallback
    spec = _load("04_paraphrased_sandbox.json")
    analysis = analyze(spec, mode="fuzzy")
    intent = analysis.by_source["stakeholder_intent"]
    assert [c.name for c in intent] == ["no_network"]
    assert intent[0].method == "fuzzy"
    failed = [r for r in analysis.implications if r.status == "implication_failed"]
    assert failed
    counterexample = failed[0].counterexample
    assert counterexample["network_send"] is True
    assert counterexample["dest_localhost"] is True
