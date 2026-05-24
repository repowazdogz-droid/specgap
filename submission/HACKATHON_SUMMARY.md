# SpecGap — Hackathon Summary

## One-paragraph summary

SpecGap detects **specification divergence** across layered sandbox specifications — stakeholder intent, formalized policy, and implementation claims — before runtime deployment. It extracts constrained capability obligations via deterministic rule-based parsing, compares layers through an independent structural weakening lattice and Z3 implication checks over a declared abstract sandbox model, and emits **replayable evidence artifacts** including implication failures and counterexample behaviors. When structural diff and Z3 disagree, SpecGap **preserves both signals** rather than collapsing to a single verdict — surfacing lattice gaps, encoding incompleteness, or abstraction mismatches that a single-mechanism checker would hide.

---

## Track fit

| Track | Fit |
| --- | --- |
| **Primary — Specification Validation** | Checks whether downstream policy/implementation layers still imply upstream intent; emits formal counterexamples when they do not |
| **Secondary — Spec-driven development / vericoding** | Bridges informal stakeholder language to checkable constraints; candidate evaluation ranks policy variants by implication-failure count |

---

## Novelty claim

Most verification tooling optimizes for discharging proof obligations quickly. SpecGap targets the upstream question: **did the obligation still match what stakeholders meant after formalization?** Its distinguishing mechanism is **triangulation** — structural diff and Z3 operate independently, and disagreement is preserved as heterogeneous evidence rather than suppressed. This is bounded assurance engineering, not end-to-end sandbox verification.

---

## Limitations (explicit)

- Rule extraction uses a fixed phrase vocabulary; unrecognized text is not extracted
- Z3 operates over a propositional abstract model — counterexamples are illustrative, not exploit proofs
- Does not run sandboxes, observe runtime behavior, or model real kernels/seccomp
- Fuzzy extraction mode is advisory and requires human review
- A clean report means **no divergence detected under current extraction and model** — not security or correctness

---

## Demo commands

```bash
git clone https://github.com/repowazdogz-droid/specgap.git
cd specgap
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Headline: "no network" → "localhost only" → implication FAIL
python -m specgap.cli examples/sandbox_no_network.json --out reports/demo_report.md

# Research contribution: structural silent, Z3 fails — disagreement preserved
python -m specgap.cli examples/06_triangulation_disagreement.json \
  --out reports/06_triangulation_disagreement_report.md

# Candidate ranking: A PASS, B/C FAIL
python -m specgap.cli examples/05_candidate_policy_ranking.json \
  --evaluate-candidates --out reports/05_candidate_evaluation_report.md

pip install -r requirements-dev.txt && pytest -q
```

---

## Expected judge takeaway

Within ~10 minutes, a judge should see:

1. A concrete drift example where each spec layer reads fine alone but Z3 finds downstream permits `network_send=true, dest_localhost=true` against upstream `no_network`
2. A second example where structural diff is silent but Z3 still fails — and SpecGap reports **disagreement** instead of hiding it
3. 41 passing tests with real Z3 (not mocked)
4. Clear assurance boundary: bounded evidence generation, not sandbox verification or security proof

**Judge guide:** [`HACKATHON_JUDGE_GUIDE.md`](../HACKATHON_JUDGE_GUIDE.md)
