"""Spec-conditioned candidate evaluation.

Given one stakeholder intent, this layer evaluates multiple candidate policy
implementations and mechanically orders them by the number of detected
implication failures over extracted constraints.

This is *candidate policy evaluation*, not synthesis. SpecGap does not generate
the candidates — it discriminates between candidate implementations by checking
whether extracted policy constraints preserve stakeholder intent within the
abstract model, reusing the existing extractor and the existing Z3 implication
check. Each candidate is evaluated independently: its extracted constraints are
checked for implication of the extracted stakeholder intent, exactly as the
formalized-policy layer is checked in the standard pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass

from .extractor import extract_constraints, fuzzy_extract
from .models import CandidateSpec, Constraint
from .z3_checker import ImplicationResult, check_implication


@dataclass
class CandidateResult:
    """The evaluation outcome for one candidate policy."""

    candidate: object                       # models.Candidate
    constraints: list                       # extracted from the candidate policy
    implication: ImplicationResult          # candidate constraints => intent
    passed: bool
    failure_count: int                      # violated intent constraints (0 if passed)
    rank: int = 0


@dataclass
class CandidateEvaluation:
    """The full result of evaluating one intent against N candidates."""

    spec: CandidateSpec
    intent_constraints: list                # extracted from the stakeholder intent
    results: list                           # list[CandidateResult], ordered


def _extract(text: str, source: str, mode: str) -> list[Constraint]:
    """Rule-first extraction, with the same opt-in fuzzy fallback as the
    standard pipeline (fuzzy only fills gaps the rules left)."""
    constraints = extract_constraints(text, source)
    if mode == "fuzzy":
        known = {c.name for c in constraints}
        for fc in fuzzy_extract(text, source):
            if fc.name not in known:
                known.add(fc.name)
                constraints.append(fc)
    return constraints


def evaluate_candidates(spec: CandidateSpec, mode: str = "rule") -> CandidateEvaluation:
    """Evaluate every candidate policy against the one stakeholder intent.

    The result list is mechanically ordered by detected implication failures
    over extracted constraints: passing candidates first, then ascending
    implication-failure count. Ties keep input order (stable sort). The order
    is not a quality score and not a leaderboard — it is purely the divergence
    count produced by the Z3 implication check.
    """
    intent_constraints = _extract(spec.stakeholder_intent, "stakeholder_intent", mode)

    results: list[CandidateResult] = []
    for cand in spec.candidates:
        constraints = _extract(cand.policy, "formalized_policy", mode)
        implication = check_implication(constraints, intent_constraints,
                                        f"Candidate {cand.id}", "Stakeholder Intent")
        passed = implication.implied
        # failure_count = number of intent constraints the candidate fails to
        # imply; at least 1 whenever the implication failed.
        failure_count = (0 if passed
                         else max(len(implication.consequent_violated), 1))
        results.append(CandidateResult(cand, constraints, implication,
                                       passed, failure_count))

    results.sort(key=lambda r: (not r.passed, r.failure_count))
    for i, r in enumerate(results, start=1):
        r.rank = i

    return CandidateEvaluation(spec, intent_constraints, results)
