"""Tests for spec-conditioned candidate evaluation.

These exercise the real extractor and real Z3 implication checks, not mocks.
"""

import json
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from specgap.candidate_eval import evaluate_candidates
from specgap.models import CandidateSpec
from specgap.reporter import PASSING_MEANING, build_candidate_report

EXAMPLES = pathlib.Path(__file__).resolve().parents[1] / "examples"


def _load():
    data = json.loads(
        (EXAMPLES / "05_candidate_policy_ranking.json").read_text(encoding="utf-8"))
    return CandidateSpec.from_dict(data)


def _by_id(evaluation):
    return {r.candidate.id: r for r in evaluation.results}


def test_intent_extracts_network_and_privilege_constraints():
    """The one shared intent must yield both strict constraints to check against."""
    names = {c.name for c in evaluate_candidates(_load()).intent_constraints}
    assert "no_network" in names
    assert "no_privilege_escalation" in names


def test_pass_fail_classification():
    """A is intent-aligned in the example; B and C are each weakened."""
    by_id = _by_id(evaluate_candidates(_load()))
    assert by_id["A"].passed is True
    assert by_id["B"].passed is False
    assert by_id["C"].passed is False


def test_ordering_passing_first_then_ascending_failures():
    """Ordering: the passing candidate is listed first, failing candidates follow."""
    evaluation = evaluate_candidates(_load())
    order = [r.candidate.id for r in evaluation.results]
    assert set(order) == {"A", "B", "C"}
    assert order[0] == "A"                       # only passing candidate ranks first
    assert [r.rank for r in evaluation.results] == [1, 2, 3]
    a_rank = next(r.rank for r in evaluation.results if r.candidate.id == "A")
    failing_ranks = [r.rank for r in evaluation.results if not r.passed]
    assert min(failing_ranks) > a_rank
    # B and C tie on failure count, so input order is preserved
    assert order == ["A", "B", "C"]


def test_candidate_b_localhost_counterexample():
    """B weakens 'no network' to a localhost exception."""
    b = _by_id(evaluate_candidates(_load()))["B"]
    assert b.implication.status == "implication_failed"
    assert "no_network" in b.implication.consequent_violated
    assert b.implication.counterexample["network_send"] is True
    assert b.implication.counterexample["dest_localhost"] is True


def test_candidate_c_privilege_escalation_counterexample():
    """C weakens 'no privilege escalation' by allowing setuid."""
    c = _by_id(evaluate_candidates(_load()))["C"]
    assert c.implication.status == "implication_failed"
    assert "no_privilege_escalation" in c.implication.consequent_violated
    assert c.implication.counterexample["privilege_gain"] is True
    assert c.implication.counterexample["setuid_exec"] is True
    assert c.implication.counterexample["cap_sys_admin"] is False


def test_report_states_passing_does_not_prove_correctness():
    """The report must explicitly bound what a PASS means."""
    report = build_candidate_report(evaluate_candidates(_load()))
    assert PASSING_MEANING in report
    assert "PASS" in report and "FAIL" in report


def test_candidate_spec_rejects_missing_candidates():
    with pytest.raises(ValueError):
        CandidateSpec.from_dict({"title": "x", "stakeholder_intent": "y"})
