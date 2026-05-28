"""Tests for SpecGap MCP tool handlers (direct invocation, no stdio protocol)."""

import json
import pathlib
import sys

import pytest

MCP_DIR = pathlib.Path(__file__).resolve().parents[1] / "specgap-mcp"
sys.path.insert(0, str(MCP_DIR))

from tools.analyze_spec import run as analyze_spec  # noqa: E402
from tools.boxarena_preflight import run as boxarena_preflight  # noqa: E402
from tools.evaluate_candidates import run as evaluate_candidates  # noqa: E402

FORBIDDEN_OUTPUT = ("verified", " guarantees ", " formally verified ")


@pytest.mark.parametrize(
    "runner,arg",
    [
        (analyze_spec, "examples/sandbox_no_network.json"),
        (analyze_spec, "examples/06_triangulation_disagreement.json"),
        (evaluate_candidates, "examples/05_candidate_policy_ranking.json"),
        (boxarena_preflight, "examples/boxarena_preflight_divergence.json"),
    ],
)
def test_mcp_tool_serializes(runner, arg):
    result = runner(input=arg)
    text = json.dumps(result)
    assert "tool" in result
    assert "limitations" in result
    for phrase in FORBIDDEN_OUTPUT:
        assert phrase not in text.lower()
    # round-trip
    json.loads(text)


def test_analyze_spec_triangulation_disagreement():
    result = analyze_spec(input="examples/06_triangulation_disagreement.json")
    assert result["result"]["assurance_result_schema"] == "1.0"
    assert result["result"]["kind"] == "specgap"
    assert result["semantic_divergences"] == 0
    assert result["failed_implication_checks"] == 2
    assert result["triangulation"] == "disagree"


def test_analyze_spec_nested_result_matches_deprecated_aliases():
    result = analyze_spec(input="examples/sandbox_no_network.json")
    nested = result["result"]
    assert result["verdict"] == nested["verdict"]
    assert result["intent_empty"] == nested["detail"]["intent_empty"]
    assert result["semantic_divergences"] == nested["detail"]["counts"]["semantic_divergences"]


def test_boxarena_preflight_does_not_run_boxarena():
    result = boxarena_preflight(input="examples/boxarena_preflight_divergence.json")
    assert result["boxarena_executed"] is False
    assert result["proceed_to_boxarena_advisory"] is False
    assert pathlib.Path(result["evidence_path"]).is_file()
