# SpecGap — Hackathon Judge Guide

**Repo:** https://github.com/repowazdogz-droid/specgap

SpecGap checks whether downstream policy and implementation layers still logically preserve upstream intent under a declared abstract model, while preserving disagreement between independent evaluators instead of collapsing them into a single verdict.

It detects **specification divergence** across layered sandbox specs and emits **bounded evidence** — Z3 implication failures and counterexamples in an abstract model — without running sandboxes or claiming security proofs.

![SpecGap architecture](docs/assets/specgap_architecture.png)

_Full diagram: [`docs/assets/specgap_architecture.svg`](docs/assets/specgap_architecture.svg)_

---

## 3-minute path

```bash
git clone https://github.com/repowazdogz-droid/specgap.git
cd specgap
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m specgap.cli examples/sandbox_no_network.json --out reports/demo_report.md
```

Open `reports/demo_report.md`. Look for:

1. **Extracted constraints** — intent says `no_network`, policy says `localhost_only`
2. **Z3 implication FAILS** — downstream permits behavior upstream forbids
3. **Counterexample** — `network_send=true, dest_localhost=true` (abstract model only; not a runtime exploit proof)

**Takeaway:** Each layer reads fine alone; together they quietly redefine the proof obligation.

---

## 10-minute path

```bash
# After 3-minute setup above:

# Triangulation disagreement (structural silent, Z3 fails)
python -m specgap.cli examples/06_triangulation_disagreement.json \
  --out reports/06_triangulation_disagreement_report.md

# Candidate policy ranking (A PASS, B/C FAIL)
python -m specgap.cli examples/05_candidate_policy_ranking.json \
  --evaluate-candidates --out reports/05_candidate_evaluation_report.md

# Tests (real Z3, not mocked)
pip install -r requirements-dev.txt && pytest -q

# Extraction brittleness (optional): rule mode misses paraphrase; fuzzy is advisory
python -m specgap.cli examples/04_paraphrased_sandbox.json --extractor rule
```

Then skim:

- [`docs/WHY_DISAGREEMENT_MATTERS.md`](docs/WHY_DISAGREEMENT_MATTERS.md) — why two independent checks matter
- [`docs/ASSURANCE_BOUNDARY.md`](docs/ASSURANCE_BOUNDARY.md) — what is and is not claimed
- [`submission/HACKATHON_SUMMARY.md`](submission/HACKATHON_SUMMARY.md) — track fit and novelty

---

## What to look for

| Signal | Where | Meaning |
| --- | --- | --- |
| Implication failure | Report **Z3 Formal Check** | Downstream layer permits abstract behavior upstream forbids |
| Counterexample atoms | Report **Counterexample** | Illustrative behavior in the abstract model (not an exploit proof) |
| Structural divergence | Report **Semantic Divergence** | Name-level weakening detected via `WEAKER_OF` lattice |
| Triangulation disagreement | Report **Triangulation Summary** | Structural and Z3 disagree — both signals preserved |
| Candidate ranking | `--evaluate-candidates` output | Which policy candidate has fewest implication failures vs intent |
| Determinism | `pytest -q` | 41 tests pass; Z3 checks are not mocked |

---

## What SpecGap does NOT claim

- Does **not** prove semantic correctness, security, or that stakeholder intent was right
- Does **not** verify sandboxes, run containers, or observe runtime behavior
- Does **not** model real kernels, seccomp, or container runtimes
- Does **not** use LLMs in the core pipeline (rule extraction is deterministic; fuzzy mode is advisory substring matching)
- A **PASS** or clean report means **no divergence detected under current extraction and abstract model** — nothing stronger

Use disciplined phrasing: “detects specification divergence,” “emits bounded evidence,” “counterexample in the abstract model.”

Avoid: “proves secure,” “verifies sandbox,” “understands intent,” “guarantees correctness.”

---

## Why preserving disagreement matters

SpecGap runs two **independent** checks over extracted constraints:

1. **Structural diff** — hand-authored weakening lattice over constraint names
2. **Z3 implication** — propositional abstract sandbox model

They capture different abstraction levels. When they agree, that is heterogeneous confirmation within the TCB — not end-to-end assurance. When they **disagree** (see `examples/06_triangulation_disagreement.json`), collapsing to one verdict would hide a lattice gap, encoding incompleteness, or abstraction mismatch.

SpecGap preserves both signals. That is the core research contribution. See [`docs/WHY_DISAGREEMENT_MATTERS.md`](docs/WHY_DISAGREEMENT_MATTERS.md).

---

## Exact commands (copy-paste)

```bash
git clone https://github.com/repowazdogz-droid/specgap.git
cd specgap
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python -m specgap.cli examples/sandbox_no_network.json --out reports/demo_report.md
python -m specgap.cli examples/06_triangulation_disagreement.json --out reports/06_triangulation_disagreement_report.md
python -m specgap.cli examples/05_candidate_policy_ranking.json --evaluate-candidates --out reports/05_candidate_evaluation_report.md

pip install -r requirements-dev.txt && pytest -q
```

**Expected:** 41 passed; demo report shows 2 of 2 implication checks failed; triangulation example shows structural/Z3 **disagreement**.
