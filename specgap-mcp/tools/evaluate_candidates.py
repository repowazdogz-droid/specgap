"""MCP tool: evaluate_candidates — spec-conditioned candidate evaluation."""

from __future__ import annotations

from ._common import (
    ensure_specgap_importable,
    json_text,
    resolve_input_path,
    resolve_output_path,
)


def run(
    input: str,
    extractor: str = "rule",
    output: str | None = None,
) -> dict:
    """Evaluate candidate policies against one stakeholder intent."""
    ensure_specgap_importable()
    from specgap.candidate_eval import evaluate_candidates
    from specgap.models import CandidateSpec
    from specgap.reporter import build_candidate_report

    if extractor not in ("rule", "fuzzy"):
        raise ValueError("extractor must be 'rule' or 'fuzzy'")

    input_path = resolve_input_path(input)
    if not input_path.is_file():
        raise FileNotFoundError(f"candidate spec input not found: {input_path}")

    spec = CandidateSpec.from_dict(
        __import__("json").loads(input_path.read_text(encoding="utf-8"))
    )
    evaluation = evaluate_candidates(spec, mode=extractor)
    intent_empty = not evaluation.intent_constraints

    out_path = resolve_output_path(
        output, default_name=f"candidates_{input_path.stem}.md"
    )
    report = build_candidate_report(evaluation, extractor_mode=extractor)
    out_path.write_text(report + "\n", encoding="utf-8")

    candidates = []
    for r in evaluation.results:
        candidates.append({
            "id": r.candidate.id,
            "label": r.candidate.label,
            "passed": r.passed,
            "implication_failures": r.failure_count,
            "violated_intent_constraints": list(r.implication.consequent_violated),
            "extracted_constraints": [c.name for c in r.constraints],
        })

    ordering = [r.candidate.id for r in evaluation.results]

    return {
        "tool": "evaluate_candidates",
        "input": str(input_path),
        "report_path": str(out_path),
        "extractor": extractor,
        "title": spec.title,
        "intent_empty": intent_empty,
        "candidates_evaluated": len(evaluation.results),
        "candidates_passing": sum(1 for r in evaluation.results if r.passed),
        "candidate_outcomes": candidates,
        "ordering": ordering,
        "ordering_note": (
            "Mechanical order by implication-failure count over extracted "
            "constraints — not a quality score or leaderboard."
        ),
        "triangulation": None,
        "limitations": (
            "Candidate PASS/FAIL is over extracted constraints in the abstract "
            "sandbox model only. Not synthesis, not runtime evaluation."
        ),
    }


def run_json(input: str, extractor: str = "rule", output: str | None = None) -> str:
    return json_text(run(input=input, extractor=extractor, output=output))
