# SpecGap Final Validation Record

**Timestamp (UTC):** 2026-05-22T14:33:25Z  
**Environment:** `Python 3.14.4`, macOS, `z3-solver` via `requirements.txt`  
**Mode:** Submission hardening — polish and reproducibility only (no new capabilities)

---

## pytest

```bash
cd specgap && pytest -q
```

| Metric | Result |
| --- | --- |
| Collected | 41 |
| Passed | 41 |
| Failed | 0 |
| Duration | ~0.09 s |

Z3 implication checks in tests are **not mocked**.

---

## README commands (all exit 0)

| # | Command | Key output |
| --- | --- | --- |
| R1 | `python -m specgap.cli examples/sandbox_no_network.json --out reports/demo_report.md` | divergences: 3, failed checks: 2 of 2 |
| R2 | `python -m specgap.cli examples/04_paraphrased_sandbox.json --extractor rule --out reports/04_rule_report.md` | WARNING extraction failure, 0 failed checks |
| R3 | `python -m specgap.cli examples/04_paraphrased_sandbox.json --extractor fuzzy --out reports/04_fuzzy_report.md` | divergences: 3, failed checks: 2 of 2 |
| R4 | `python -m specgap.cli examples/05_candidate_policy_ranking.json --evaluate-candidates` | A PASS, B/C FAIL (1 each), order A > B > C |
| R5 | `python -m specgap.cli examples/sandbox_readonly_fs.json --out reports/readonly.md` | divergences: 3, failed checks: 2 of 2 |
| R6 | `python -m specgap.cli examples/syscall_policy_mismatch.json --out reports/privesc.md` | divergences: 3, failed checks: 2 of 2 |
| R7 | `pytest` | 41 passed |

---

## Tutorial commands (all exit 0)

| Tutorial | Command | Verified output |
| --- | --- | --- |
| 01 | `examples/sandbox_no_network.json → reports/01_semantic_gap_report.md` | Same as R1 |
| 02 rule | `04_paraphrased_sandbox.json --extractor rule → reports/02_rule_report.md` | Same as R2 |
| 02 fuzzy | `04_paraphrased_sandbox.json --extractor fuzzy → reports/02_fuzzy_report.md` | Same as R3 |
| 03 | `05_candidate_policy_ranking.json --evaluate-candidates → reports/03_candidate_report.md` | Same as R4 |

Tutorial expected-output snippets match live CLI and report text (2026-05-22 run).

---

## Path reference audit

| Path | Status |
| --- | --- |
| `README.md` | Present |
| `requirements.txt`, `requirements-dev.txt` | Present |
| `tutorials/01_detecting_a_semantic_gap.md` | Present |
| `tutorials/02_rule_vs_fuzzy_extraction.md` | Present |
| `tutorials/03_candidate_policy_evaluation.md` | Present |
| `examples/*.json` (5 files) | Present, tracked via `!specgap/examples/*.json` |
| `reports/demo_report.md` | Present (reference) |
| `reports/05_candidate_evaluation_report.md` | Present (reference) |
| `docs/BOXARENA_POSITIONING.md` | Present |
| `submission/DEMO_RECORDING_CHECKLIST.md` | Present |

Generated reports (`reports/01_*`, `02_*`, `03_*`, `04_*`, `readonly.md`, `privesc.md`) are gitignored; regenerate with CLI.

---

## Repo cleanliness

- `specgap/.gitignore` ignores generated `reports/*` except whitelisted reference copies.
- Root `.gitignore` negates `specgap/examples/*.json` so examples remain trackable despite global `*.json` rule.
- No `__pycache__` or `.pytest_cache` tracked under `specgap/`.

---

## Known limitations (unchanged by hardening pass)

- Rule extraction: fixed vocabulary; silent omission of unrecognized phrasing.
- Fuzzy extraction: advisory; `requires_human_review=true`; offline map is small.
- Z3: propositional abstract sandbox model only.
- Counterexamples: illustrative behaviors, not exploit proofs.
- Candidate ordering: implication-failure count only — not policy quality or security score.
- Three-layer spec or N candidates; no multi-document specs or version history.

---

## Known setup caveats

- **PEP 668:** System Python may reject global `pip install`; use `python3 -m venv .venv` (documented in README and tutorials).
- **Python version:** Requires 3.10+ (`pyproject.toml`); validated on 3.14.4.
- **Optional fuzzy API:** `ANTHROPIC_API_KEY` enables API fuzzy path; offline demo works without it.
- **pytest:** Not in base `requirements.txt`; install via `requirements-dev.txt`.

---

## Terminology audit (reports + README)

Preferred terms used consistently: semantic divergence, implication failure, candidate policy evaluation, implementation discrimination, extracted constraints, abstract sandbox model.

Removed or avoided in user-facing docs: "semantically correct" as SpecGap verdict (example candidate A label renamed to author-side "Reference policy (intent-aligned wording)").

Internal code still uses `rank` field for ordering index — not exposed as "ranking score" in reports.

---

## Human review still recommended

- Example JSON `expected` / `expected_issue` strings are author annotations, not tool verdicts.
- Fuzzy confidence values may differ if Anthropic API path is enabled.
- Apart Research submission copy should not claim kernel-level or seccomp-level verification.
