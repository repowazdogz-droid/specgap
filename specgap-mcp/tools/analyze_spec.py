"""MCP tool: analyze_spec — standard intent/policy/implementation triple."""

from __future__ import annotations

from pathlib import Path

from ._common import (
    ensure_specgap_importable,
    json_text,
    resolve_input_path,
    resolve_output_path,
    triangulation_label,
)


def run(
    input: str,
    extractor: str = "rule",
    output: str | None = None,
) -> dict:
    """Run SpecGap analysis and return a bounded summary dict."""
    ensure_specgap_importable()
    from specgap.cli import analyze
    from specgap.models import SpecInput
    from specgap.reporter import build_report
    from specgap.triangulation import triangulate_analysis

    if extractor not in ("rule", "fuzzy"):
        raise ValueError("extractor must be 'rule' or 'fuzzy'")

    input_path = resolve_input_path(input)
    if not input_path.is_file():
        raise FileNotFoundError(f"spec input not found: {input_path}")

    spec = SpecInput.from_dict(
        __import__("json").loads(input_path.read_text(encoding="utf-8"))
    )
    analysis = analyze(spec, mode=extractor)
    intent_empty = not analysis.by_source["stakeholder_intent"]
    failed = sum(
        1 for r in analysis.implications if r.status == "implication_failed"
    )
    tri = triangulate_analysis(
        analysis.diff_result, analysis.implications, intent_empty=intent_empty
    )

    if intent_empty:
        verdict = "extraction_failure"
    elif failed or analysis.diff_result.high_severity:
        verdict = "divergence_detected"
    elif analysis.diff_result.divergences:
        verdict = "divergence_detected"
    else:
        verdict = "no_divergence_detected"

    out_path = resolve_output_path(
        output, default_name=f"analyze_{input_path.stem}.md"
    )
    report = build_report(
        spec,
        analysis.by_source,
        analysis.diff_result,
        analysis.implications,
        analysis.consistencies,
        extractor_mode=extractor,
    )
    out_path.write_text(report + "\n", encoding="utf-8")

    return {
        "tool": "analyze_spec",
        "input": str(input_path),
        "report_path": str(out_path),
        "extractor": extractor,
        "title": spec.title,
        "verdict": verdict,
        "intent_empty": intent_empty,
        "semantic_divergences": len(analysis.diff_result.divergences),
        "high_severity_divergences": len(analysis.diff_result.high_severity),
        "failed_implication_checks": failed,
        "implication_checks_total": len(analysis.implications),
        "triangulation": triangulation_label(
            intent_empty=intent_empty, any_disagreement=tri.any_disagreement
        ),
        "triangulation_records": [r.to_dict() for r in tri.records],
        "limitations": (
            "Bounded by extracted constraints and the abstract sandbox model. "
            "Not runtime verification, not semantic understanding, not a "
            "correctness or security guarantee."
        ),
    }


def run_json(input: str, extractor: str = "rule", output: str | None = None) -> str:
    return json_text(run(input=input, extractor=extractor, output=output))
