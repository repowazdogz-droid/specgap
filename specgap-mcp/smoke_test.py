#!/usr/bin/env python3
"""Direct smoke test for SpecGap MCP tools (no MCP client required)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_MCP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_MCP_DIR))

from tools import analyze_spec, boxarena_preflight, evaluate_candidates  # noqa: E402

FORBIDDEN = ("verified", "safe", "correct", "semantic understanding")


def _check_payload(name: str, payload: dict) -> None:
    text = json.dumps(payload).lower()
    for word in FORBIDDEN:
        if word in text and "not " not in text.split(word)[0][-20:]:
            # allow negations in limitations strings
            if word in ("correct",) and "not a correctness" in text:
                continue
            if word in ("semantic understanding",) and "not semantic" in text:
                continue
            raise AssertionError(f"{name}: forbidden wording '{word}' in output")
    print(f"OK {name}: {payload.get('verdict') or payload.get('preflight_verdict')}")


def main() -> int:
    r1 = analyze_spec(input="examples/sandbox_no_network.json")
    _check_payload("analyze_spec", r1)
    assert r1["verdict"] == "divergence_detected"
    assert r1["triangulation"] == "agree"

    r2 = analyze_spec(input="examples/06_triangulation_disagreement.json")
    _check_payload("analyze_spec_disagree", r2)
    assert r2["semantic_divergences"] == 0
    assert r2["triangulation"] == "disagree"

    r3 = evaluate_candidates(input="examples/05_candidate_policy_ranking.json")
    _check_payload("evaluate_candidates", r3)
    assert r3["candidates_evaluated"] == 3
    assert r3["ordering"][0] == "A"

    r4 = boxarena_preflight(input="examples/boxarena_preflight_divergence.json")
    _check_payload("boxarena_preflight", r4)
    assert r4["boxarena_executed"] is False
    assert r4["preflight_verdict"] == "fail"

    print("smoke_test: all tools passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
