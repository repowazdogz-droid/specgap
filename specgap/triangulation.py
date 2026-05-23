"""Triangulation: preserve agreement/disagreement between structural diff and Z3.

Two independent mechanisms inspect extracted constraints:
- ``semantic_diff`` — hand-authored weakening lattice over constraint names
- ``z3_checker`` — implication queries over the abstract sandbox model

Disagreement between them is first-class evidence — not noise to collapse. See ``docs/TCB.md``.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal

from .semantic_diff import DiffResult
from .z3_checker import ImplicationResult

StructuralStatus = Literal["divergence_detected", "no_divergence_detected"]
Z3Status = Literal["fails", "holds", "skipped"]

# Components whose correctness is assumed when interpreting triangulation.
TCB_SCOPE: list[str] = [
    "rule-based constraint extraction (fixed phrase vocabulary)",
    "hand-authored WEAKER_OF structural weakening lattice",
    "abstract propositional sandbox model (docs/ENCODING.md)",
    "Z3 quantifier-free satisfiability (z3-solver)",
]

_DOWNSTREAM_KEYS = {
    "Formalized Policy": "formalized_policy",
    "Implementation Claim": "implementation_claim",
}


@dataclass
class TriangulationRecord:
    """Agreement state for one downstream layer vs stakeholder intent."""

    layer: str
    structural_diff: StructuralStatus
    z3_implication: Z3Status
    agreement: bool
    counterexample_present: bool
    tcb_scope: list[str] = field(default_factory=lambda: list(TCB_SCOPE))

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TriangulationSummary:
    """Triangulation across all downstream layers in the standard triple pipeline."""

    records: list[TriangulationRecord]
    intent_empty: bool = False

    @property
    def any_disagreement(self) -> bool:
        return any(not r.agreement for r in self.records)

    @property
    def all_agree(self) -> bool:
        return bool(self.records) and all(r.agreement for r in self.records)

    def to_dict(self) -> dict:
        return {
            "intent_empty": self.intent_empty,
            "any_disagreement": self.any_disagreement,
            "records": [r.to_dict() for r in self.records],
        }


def _structural_status(diff_result: DiffResult, downstream_key: str) -> StructuralStatus:
    hits = [d for d in diff_result.divergences if downstream_key in d.sources]
    return "divergence_detected" if hits else "no_divergence_detected"


def _z3_status(implication: ImplicationResult) -> Z3Status:
    if implication.status == "no_consequent":
        return "skipped"
    return "holds" if implication.implied else "fails"


def _agreement(structural: StructuralStatus, z3: Z3Status, *,
               intent_empty: bool) -> bool:
    if intent_empty or z3 == "skipped":
        # No intent obligation loaded — triangulation cannot corroborate assurance.
        return False
    if structural == "divergence_detected":
        return z3 == "fails"
    return z3 == "holds"


def triangulate_layer(layer_label: str, downstream_key: str,
                      diff_result: DiffResult,
                      implication: ImplicationResult, *,
                      intent_empty: bool = False) -> TriangulationRecord:
    """Compare structural divergence signals with one Z3 implication check."""
    structural = _structural_status(diff_result, downstream_key)
    z3 = _z3_status(implication)
    return TriangulationRecord(
        layer=layer_label,
        structural_diff=structural,
        z3_implication=z3,
        agreement=_agreement(structural, z3, intent_empty=intent_empty),
        counterexample_present=(
            implication.status == "implication_failed"
            and bool(implication.counterexample_atoms)
        ),
    )


def triangulate_analysis(diff_result: DiffResult,
                         implications: list[ImplicationResult], *,
                         intent_empty: bool = False) -> TriangulationSummary:
    """Triangulate the standard intent / policy / implementation pipeline."""
    labels = list(_DOWNSTREAM_KEYS.keys())
    records: list[TriangulationRecord] = []
    for label, implication in zip(labels, implications):
        records.append(triangulate_layer(
            label, _DOWNSTREAM_KEYS[label], diff_result, implication,
            intent_empty=intent_empty,
        ))
    return TriangulationSummary(records=records, intent_empty=intent_empty)
