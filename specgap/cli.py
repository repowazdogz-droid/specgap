"""SpecGap command-line interface.

Usage:
    python -m specgap.cli examples/sandbox_no_network.json --out reports/demo_report.md
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

from .candidate_eval import evaluate_candidates
from .extractor import extract_all
from .models import CandidateSpec, SpecInput
from .reporter import build_candidate_report, build_report
from .semantic_diff import DiffResult, diff
from .triangulation import triangulate_analysis
from .z3_checker import (ConsistencyResult, ImplicationResult, check_consistency,
                         check_implication)


@dataclass
class Analysis:
    spec: SpecInput
    by_source: dict
    diff_result: DiffResult
    implications: list
    consistencies: list


def analyze(spec: SpecInput, mode: str = "rule") -> Analysis:
    """Run the full SpecGap pipeline for one specification triple."""
    by_source = extract_all(spec, mode=mode)
    diff_result = diff(by_source)

    intent = by_source["stakeholder_intent"]
    implications = [
        check_implication(by_source["formalized_policy"], intent,
                          "Formalized Policy", "Stakeholder Intent"),
        check_implication(by_source["implementation_claim"], intent,
                          "Implementation Claim", "Stakeholder Intent"),
    ]
    consistencies = [
        check_consistency(by_source["stakeholder_intent"], "Stakeholder Intent"),
        check_consistency(by_source["formalized_policy"], "Formalized Policy"),
        check_consistency(by_source["implementation_claim"], "Implementation Claim"),
    ]
    return Analysis(spec, by_source, diff_result, implications, consistencies)


def _load_spec(path: Path) -> SpecInput:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"error: input file not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"error: input file is not valid JSON: {exc}")
    try:
        return SpecInput.from_dict(data)
    except ValueError as exc:
        raise SystemExit(f"error: {exc}")


def _load_candidate_spec(path: Path) -> CandidateSpec:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"error: input file not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"error: input file is not valid JSON: {exc}")
    try:
        return CandidateSpec.from_dict(data)
    except ValueError as exc:
        raise SystemExit(f"error: {exc}")


def _run_candidate_evaluation(args: argparse.Namespace) -> int:
    """Candidate evaluation mode: evaluate one intent against N candidate policies."""
    spec = _load_candidate_spec(Path(args.input))
    evaluation = evaluate_candidates(spec, mode=args.extractor)
    report = build_candidate_report(evaluation, extractor_mode=args.extractor)

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report + "\n", encoding="utf-8")
        print(f"SpecGap: evaluated {len(evaluation.results)} candidate(s) for "
              f"'{spec.title}' (extractor: {args.extractor})")
        if not evaluation.intent_constraints:
            print("  WARNING: extraction failure — stakeholder intent yielded zero "
                  "constraints; candidate PASS/FAIL results are NOT meaningful")
        for r in sorted(evaluation.results, key=lambda x: x.candidate.id):
            verdict = ("PASS" if r.passed
                       else f"FAIL ({r.failure_count} implication failure(s))")
            print(f"  Candidate {r.candidate.id}: {verdict}")
        ordering = " > ".join(r.candidate.id for r in evaluation.results)
        print(f"  candidate order (fewest implication failures first): {ordering}")
        print(f"  report written to: {out_path}")
    else:
        print(report)
    return 0


def _run_boxarena_preflight(args: argparse.Namespace) -> int:
    """BoxArena pre-flight mode: SpecGap spec check before runtime evaluation."""
    from .integrations.boxarena_adapter import (
        BoxArenaContext,
        load_spec_with_boxarena_context,
        run_boxarena_preflight,
        write_evidence_chain,
    )

    input_path = Path(args.input)
    spec, ctx = load_spec_with_boxarena_context(input_path)
    if args.boxarena_quest:
        ctx.quest = args.boxarena_quest
    if args.boxarena_runtime:
        ctx.runtime = args.boxarena_runtime
    if args.boxarena_model:
        ctx.model = args.boxarena_model
    if args.boxarena_root:
        ctx.boxarena_root = args.boxarena_root

    result = run_boxarena_preflight(spec, ctx, extractor_mode=args.extractor)
    report = result.specgap_report_markdown

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report + "\n", encoding="utf-8")
    else:
        print(report)

    if args.evidence_out:
        write_evidence_chain(result, Path(args.evidence_out))

    print(f"SpecGap BoxArena pre-flight: '{result.title}' (extractor: {args.extractor})")
    print(f"  verdict: {result.verdict} | proceed_to_boxarena (advisory): "
          f"{'yes' if result.proceed_to_boxarena else 'no'}")
    print(f"  divergences: {result.divergence_count} | "
          f"failed implication checks: {result.failed_implication_checks}")
    if result.triangulation_any_disagreement:
        print("  triangulation: disagreement between structural diff and Z3")
    print("  NOTE: SpecGap pre-flight is NOT runtime verification or BoxArena execution.")
    if args.out:
        print(f"  report written to: {args.out}")
    if args.evidence_out:
        print(f"  evidence chain written to: {args.evidence_out}")
    print("  suggested BoxArena command (not run):")
    print(f"    {result.suggested_boxarena_command}")
    return 1 if result.verdict == "fail" else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="specgap",
        description="Specification-divergence detection: constrained extraction + Z3 over an abstract sandbox model.")
    parser.add_argument("input", help="Path to a spec example JSON file.")
    parser.add_argument("--out", help="Write the Markdown report to this path. "
                                      "If omitted, the report is printed to stdout.")
    parser.add_argument("--extractor", choices=("rule", "fuzzy"), default="rule",
                        help="Constraint extraction mode. 'rule' (default) is "
                             "deterministic. 'fuzzy' adds paraphrase-aware fallback "
                             "extraction (Anthropic API if ANTHROPIC_API_KEY is set, "
                             "otherwise the offline paraphrase map).")
    parser.add_argument("--evaluate-candidates", action="store_true",
                        help="Candidate evaluation mode: treat the input as one "
                             "stakeholder intent plus N candidate policies and "
                             "evaluate each candidate against the intent "
                             "(spec-conditioned candidate evaluation). Requires "
                             "the candidate input shape.")
    parser.add_argument("--boxarena-preflight", action="store_true",
                        help="BoxArena pre-flight mode: run SpecGap specification "
                             "divergence checks and emit an advisory evidence chain "
                             "before empirical BoxArena evaluation. Does NOT run "
                             "BoxArena or verify runtime confinement.")
    parser.add_argument("--boxarena-quest",
                        help="Override BoxArena quest id from input JSON "
                             "(e.g. net_lateral, fs_breakout).")
    parser.add_argument("--boxarena-runtime",
                        help="Override BoxArena OCI runtime flag (default: runc).")
    parser.add_argument("--boxarena-model",
                        help="Model pin for suggested BoxArena harness command.")
    parser.add_argument("--boxarena-root",
                        help="Path to BoxArena harness directory for suggested command.")
    parser.add_argument("--evidence-out",
                        help="Write JSON evidence-chain artifact for pre-flight "
                             "(SpecGap phase only; excludes full Markdown report).")
    args = parser.parse_args(argv)

    if args.boxarena_preflight:
        return _run_boxarena_preflight(args)

    if args.evaluate_candidates:
        return _run_candidate_evaluation(args)

    spec = _load_spec(Path(args.input))
    analysis = analyze(spec, mode=args.extractor)
    report = build_report(spec, analysis.by_source, analysis.diff_result,
                          analysis.implications, analysis.consistencies,
                          extractor_mode=args.extractor)

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report + "\n", encoding="utf-8")
        failed = sum(1 for r in analysis.implications if r.status == "implication_failed")
        print(f"SpecGap: analyzed '{spec.title}' (extractor: {args.extractor})")
        if not analysis.by_source["stakeholder_intent"]:
            print("  WARNING: extraction failure — stakeholder intent yielded zero "
                  "constraints; this is NOT a clean result")
        tri = triangulate_analysis(analysis.diff_result, analysis.implications,
                                   intent_empty=not analysis.by_source["stakeholder_intent"])
        if tri.any_disagreement:
            print("  triangulation: disagreement between structural diff and Z3")
        elif not analysis.by_source["stakeholder_intent"]:
            print("  triangulation: indeterminate (empty intent extraction)")
        else:
            print("  triangulation: structural diff and Z3 agree")
        print(f"  semantic divergences: {len(analysis.diff_result.divergences)}")
        print(f"  failed implication checks: {failed} of {len(analysis.implications)}")
        print(f"  report written to: {out_path}")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
