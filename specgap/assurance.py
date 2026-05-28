"""AssuranceResult envelope for SpecGap (kind=specgap).

Produces a versioned, deterministic JSON artifact suitable for MCP, adapters,
and replay tests. PolicyWitness and other tools reuse the same envelope later.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict

from importlib.metadata import PackageNotFoundError, version

from .cli import analyze
from .models import Constraint, SpecInput
from .triangulation import TCB_SCOPE, triangulate_analysis

ASSURANCE_RESULT_SCHEMA = "1.0"
SPECGAP_KIND = "specgap"
SPECGAP_DETAIL_SCHEMA = "1.0"
ENCODING_VERSION = "sandbox-propositional/1.0"

try:
    _PKG_VERSION = version("specgap")
except PackageNotFoundError:
    _PKG_VERSION = "0.1.0"

LIMITATIONS = (
    "Bounded by extracted constraints and the abstract sandbox model. "
    "Not runtime verification, not semantic understanding, not a "
    "correctness or security guarantee."
)

_LAYER_KEYS = (
    "stakeholder_intent",
    "formalized_policy",
    "implementation_claim",
)


def _canonical_json_bytes(value: object) -> bytes:
    """Deterministic UTF-8 JSON for fingerprinting (sorted keys, compact)."""
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def specgap_input_payload(spec: SpecInput) -> dict:
    """Canonical ingress object for fingerprinting (excludes annotations)."""
    return {
        "title": spec.title,
        "stakeholder_intent": spec.stakeholder_intent,
        "formalized_policy": spec.formalized_policy,
        "implementation_claim": spec.implementation_claim,
    }


def input_fingerprint(spec: SpecInput) -> str:
    """SHA-256 hex over canonical spec triple JSON."""
    return hashlib.sha256(_canonical_json_bytes(specgap_input_payload(spec))).hexdigest()


def _constraint_dict(constraint: Constraint) -> dict:
    return asdict(constraint)


def _implication_dict(result) -> dict:
    data = asdict(result)
    # Normalise counterexample booleans for stable JSON (Z3 may yield plain bool).
    counterexample = data.get("counterexample") or {}
    data["counterexample"] = {
        key: bool(counterexample[key]) for key in sorted(counterexample)
    }
    return data


def _verdict(analysis, *, intent_empty: bool) -> str:
    if intent_empty:
        return "extraction_failure"
    failed = sum(
        1 for r in analysis.implications if r.status == "implication_failed"
    )
    if failed or analysis.diff_result.high_severity or analysis.diff_result.divergences:
        return "divergence_detected"
    return "no_divergence_detected"


def _build_specgap_detail(analysis, spec: SpecInput, mode: str) -> dict:
    intent_empty = not analysis.by_source["stakeholder_intent"]
    failed = sum(
        1 for r in analysis.implications if r.status == "implication_failed"
    )
    inconsistent = sum(1 for c in analysis.consistencies if not c.consistent)
    tri = triangulate_analysis(
        analysis.diff_result, analysis.implications, intent_empty=intent_empty,
    )
    return {
        "specgap_detail_schema": SPECGAP_DETAIL_SCHEMA,
        "extractor_mode": mode,
        "encoding_version": ENCODING_VERSION,
        "tcb_scope": list(TCB_SCOPE),
        "title": spec.title,
        "intent_empty": intent_empty,
        "counts": {
            "semantic_divergences": len(analysis.diff_result.divergences),
            "high_severity_divergences": len(analysis.diff_result.high_severity),
            "failed_implication_checks": failed,
            "implication_checks_total": len(analysis.implications),
            "inconsistent_layers": inconsistent,
        },
        "triangulation": tri.to_dict(),
        "divergences": [asdict(d) for d in analysis.diff_result.divergences],
        "implication_checks": [_implication_dict(r) for r in analysis.implications],
        "consistency_checks": [asdict(c) for c in analysis.consistencies],
        "extracted_constraints": {
            layer: [_constraint_dict(c) for c in analysis.by_source[layer]]
            for layer in _LAYER_KEYS
        },
        "limitations": LIMITATIONS,
    }


def build_assurance_envelope(analysis, spec: SpecInput, mode: str) -> dict:
    """Wrap an existing ``cli.analyze`` result in an AssuranceResult envelope."""
    if mode not in ("rule", "fuzzy"):
        raise ValueError("mode must be 'rule' or 'fuzzy'")
    intent_empty = not analysis.by_source["stakeholder_intent"]
    return {
        "assurance_result_schema": ASSURANCE_RESULT_SCHEMA,
        "kind": SPECGAP_KIND,
        "producer": {
            "name": "specgap",
            "version": _PKG_VERSION,
        },
        "input_fingerprint": input_fingerprint(spec),
        "verdict": _verdict(analysis, intent_empty=intent_empty),
        "availability": {
            "verdict": "available",
            "input_fingerprint": "available",
        },
        "detail": _build_specgap_detail(analysis, spec, mode),
    }


def analyze_structured(spec: SpecInput, mode: str = "rule") -> dict:
    """Run SpecGap and return an AssuranceResult envelope (kind=specgap)."""
    return build_assurance_envelope(analyze(spec, mode=mode), spec, mode)
