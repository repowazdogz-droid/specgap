# SpecGap tutorials

Step-by-step walkthroughs with verified commands and expected output. Run all commands from the repository root (after `git clone` and `cd specgap`).

Assurance context: [`docs/SPECIFICATION.md`](../docs/SPECIFICATION.md), [`docs/TCB.md`](../docs/TCB.md), [`docs/ENCODING.md`](../docs/ENCODING.md).

## 10-minute path

1. [README evaluator path](../README.md#10-minute-evaluator-path) — venv, install, headline demo
2. [01 — Detecting a semantic gap](01_detecting_a_semantic_gap.md)
3. [04 — Triangulation disagreement](04_triangulation_disagreement.md) *(optional; ~5 min)*
4. `pip install -r requirements-dev.txt && pytest`

## 30-minute path

Read in order:

1. [01 — Detecting a semantic gap](01_detecting_a_semantic_gap.md) — intent / policy / implementation, Z3 implication failure
2. [02 — Rule vs fuzzy extraction](02_rule_vs_fuzzy_extraction.md) — extraction failure guard, fuzzy recovery
3. [03 — Candidate policy evaluation](03_candidate_policy_evaluation.md) — implementation discrimination, not scoring
4. [04 — Triangulation disagreement](04_triangulation_disagreement.md) — when structural diff and Z3 diverge

## Start here

New to constrained extraction + SMT implication checks? Begin with **Tutorial 1**. If rule extraction misses your phrasing, read **Tutorial 2** before changing the extractor. If comparing policy drafts, skip to **Tutorial 3** after Tutorial 1.

**PASS cases:** Tutorial 3’s candidate A (and any aligned intent/policy pair under the same encoding) produces **no implication failures** in the abstract model — the tool reports failures and non-failures; it is not tuned to fail only.
