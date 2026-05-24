# SpecGap — Submission Freeze Record

**Frozen:** 2026-05-23  
**Repo:** https://github.com/repowazdogz-droid/specgap  
**Branch:** `main`

## Canonical framing

SpecGap checks whether downstream policy and implementation layers still logically preserve upstream intent under a declared abstract model, while preserving disagreement between independent evaluators instead of collapsing them into a single verdict.

## Commands verified (exit 0)

```bash
cd specgap
source .venv/bin/activate
pytest -q
python -m specgap.cli examples/sandbox_no_network.json --out reports/demo_report.md
python -m specgap.cli examples/06_triangulation_disagreement.json --out reports/06_triangulation_disagreement_report.md
python -m specgap.cli examples/05_candidate_policy_ranking.json --evaluate-candidates --out reports/05_candidate_evaluation_report.md
```

| Check | Result |
| --- | --- |
| pytest | 41 passed |
| sandbox_no_network | 3 divergences, 2/2 implication failures |
| triangulation_disagreement | structural silent, Z3 fails, disagreement preserved |
| candidate ranking | A PASS, B/C FAIL, order A > B > C |

## 3-minute demo path

1. `HACKATHON_JUDGE_GUIDE.md` → clone, install, run `sandbox_no_network.json`
2. Open `reports/demo_report.md` → Z3 FAIL + counterexample
3. Skim architecture diagram in README

## Known limitations (judge-facing)

- Fixed phrase vocabulary; paraphrase may not extract (`examples/04_paraphrased_sandbox.json`)
- Counterexamples are abstract-model behaviors, not runtime exploit proofs
- PASS means no divergence under current extraction/model — not security or correctness
- No runtime sandbox execution in core pipeline

## Out of repo (by design)

- 256-page PDF (`submission/SPECGAP_FINAL_REPORT.pdf`)
- Vercel demo site / presentation slideshow (`demo-site/`)

## Freeze rule

No new capabilities, architecture changes, or dependency churn until submission closes.
