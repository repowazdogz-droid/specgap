"""MCP tool: boxarena_preflight — SpecGap pre-flight before BoxArena runtime eval."""

from __future__ import annotations

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
    evidence_out: str | None = None,
    boxarena_quest: str | None = None,
    boxarena_runtime: str | None = None,
    boxarena_model: str | None = None,
    boxarena_root: str | None = None,
) -> dict:
    """Run BoxArena pre-flight (SpecGap only — does not execute BoxArena)."""
    ensure_specgap_importable()
    from specgap.integrations.boxarena_adapter import (
        BoxArenaContext,
        load_spec_with_boxarena_context,
        run_boxarena_preflight,
        write_evidence_chain,
    )

    if extractor not in ("rule", "fuzzy"):
        raise ValueError("extractor must be 'rule' or 'fuzzy'")

    input_path = resolve_input_path(input)
    if not input_path.is_file():
        raise FileNotFoundError(f"preflight input not found: {input_path}")

    spec, ctx = load_spec_with_boxarena_context(input_path)
    if boxarena_quest:
        ctx.quest = boxarena_quest
    if boxarena_runtime:
        ctx.runtime = boxarena_runtime
    if boxarena_model:
        ctx.model = boxarena_model
    if boxarena_root:
        ctx.boxarena_root = boxarena_root

    result = run_boxarena_preflight(spec, ctx, extractor_mode=extractor)

    report_path = resolve_output_path(
        output, default_name=f"boxarena_preflight_{input_path.stem}.md"
    )
    report_path.write_text(result.specgap_report_markdown + "\n", encoding="utf-8")

    evidence_path = resolve_output_path(
        evidence_out,
        default_name=f"boxarena_evidence_{input_path.stem}.json",
    )
    write_evidence_chain(result, evidence_path)

    return {
        "tool": "boxarena_preflight",
        "input": str(input_path),
        "report_path": str(report_path),
        "evidence_path": str(evidence_path),
        "extractor": extractor,
        "title": result.title,
        "preflight_verdict": result.verdict,
        "proceed_to_boxarena_advisory": result.proceed_to_boxarena,
        "semantic_divergences": result.divergence_count,
        "failed_implication_checks": result.failed_implication_checks,
        "triangulation": (
            "disagree" if result.triangulation_any_disagreement else "agree"
        ),
        "boxarena_quest": result.boxarena_quest,
        "boxarena_runtime": result.boxarena_runtime,
        "suggested_boxarena_command": result.suggested_boxarena_command,
        "boxarena_executed": False,
        "limitations": (
            "Pre-flight specification analysis only. Does not run BoxArena, "
            "does not verify runtime confinement. proceed_to_boxarena is advisory."
        ),
    }


def run_json(
    input: str,
    extractor: str = "rule",
    output: str | None = None,
    evidence_out: str | None = None,
    boxarena_quest: str | None = None,
    boxarena_runtime: str | None = None,
    boxarena_model: str | None = None,
    boxarena_root: str | None = None,
) -> str:
    return json_text(
        run(
            input=input,
            extractor=extractor,
            output=output,
            evidence_out=evidence_out,
            boxarena_quest=boxarena_quest,
            boxarena_runtime=boxarena_runtime,
            boxarena_model=boxarena_model,
            boxarena_root=boxarena_root,
        )
    )
