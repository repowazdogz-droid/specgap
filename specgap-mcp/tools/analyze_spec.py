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


def _deprecated_aliases(result: dict) -> dict:
    """Top-level MCP fields deprecated in favour of ``result`` (one version)."""
    detail = result["detail"]
    tri = detail["triangulation"]
    return {
        "extractor": detail["extractor_mode"],
        "title": detail["title"],
        "verdict": result["verdict"],
        "intent_empty": detail["intent_empty"],
        "semantic_divergences": detail["counts"]["semantic_divergences"],
        "high_severity_divergences": detail["counts"]["high_severity_divergences"],
        "failed_implication_checks": detail["counts"]["failed_implication_checks"],
        "implication_checks_total": detail["counts"]["implication_checks_total"],
        "triangulation": triangulation_label(
            intent_empty=tri["intent_empty"],
            any_disagreement=tri["any_disagreement"],
        ),
        "triangulation_records": tri["records"],
        "limitations": detail["limitations"],
    }


def run(
    input: str,
    extractor: str = "rule",
    output: str | None = None,
) -> dict:
    """Run SpecGap analysis and return a bounded summary dict."""
    ensure_specgap_importable()
    from specgap.assurance import build_assurance_envelope
    from specgap.models import SpecInput
    from specgap.reporter import build_report
    from specgap.cli import analyze

    if extractor not in ("rule", "fuzzy"):
        raise ValueError("extractor must be 'rule' or 'fuzzy'")

    input_path = resolve_input_path(input)
    if not input_path.is_file():
        raise FileNotFoundError(f"spec input not found: {input_path}")

    spec = SpecInput.from_dict(
        __import__("json").loads(input_path.read_text(encoding="utf-8"))
    )
    analysis = analyze(spec, mode=extractor)
    result = build_assurance_envelope(analysis, spec, mode=extractor)

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

    payload = {
        "tool": "analyze_spec",
        "input": str(input_path),
        "report_path": str(out_path),
        "result": result,
    }
    payload.update(_deprecated_aliases(result))
    payload["limitations"] = (
        "Bounded by extracted constraints and the abstract sandbox model. "
        "Not runtime verification, not semantic understanding, not a "
        "correctness or security guarantee."
    )
    return payload


def run_json(input: str, extractor: str = "rule", output: str | None = None) -> str:
    return json_text(run(input=input, extractor=extractor, output=output))
