# SpecGap

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![pytest](https://img.shields.io/badge/tests-pytest-41%20passed-brightgreen)

SpecGap checks whether downstream policy and implementation layers still logically preserve upstream intent under a declared abstract model, while preserving disagreement between independent evaluators instead of collapsing them into a single verdict.

Layered sandbox specifications drift: intent, formalized policy, and implementation claims each read plausibly alone. SpecGap extracts constrained obligations, runs **structural divergence** analysis and **Z3 implication checks**, and emits **replayable Markdown/JSON evidence** — implication failures and counterexamples inside the model when logical preservation fails.

**Start here:** [3-minute path](#3-minute-evaluator-path) · [Judge guide](HACKATHON_JUDGE_GUIDE.md)

---

## The problem

**Specification assurance** breaks when semantic drift accumulates across layers. Automated checks discharge obligations quickly; the bottleneck is whether downstream policy still matches upstream intent.

Stakeholder language becomes predicates, then runtime claims. Each refinement can weaken constraints without anyone noticing until behavior is already permitted.

---

## The aha example

| Layer | Text |
| --- | --- |
| **Intent** | “No network access” |
| **Policy** | “Only localhost access” |
| **Result** | **FAIL** — downstream permits `network_send=true, dest_localhost=true`, which violates upstream `no_network`. |

SpecGap surfaces this **before** deployment or adversarial evaluation. It does not run sandboxes or observe live infrastructure.

---

## Architecture

<p align="center">
  <a href="docs/assets/specgap_architecture.svg">
    <img src="docs/assets/specgap_architecture.png" alt="SpecGap architecture: intent and policy layers through extraction, SMT checking, independent evaluators, disagreement preservation, and replayable evidence artifacts" width="680"/>
  </a>
</p>

_SVG: [`docs/assets/specgap_architecture.svg`](docs/assets/specgap_architecture.svg)_

---

## What SpecGap does

1. **Extract** canonical constraints from text (`no_network`, `localhost_only`, …) — deterministic rule mode by default.
2. **Compare** layers with a structural weakening lattice (`STRICT` / `WEAKER_OF`).
3. **Check** with Z3 whether downstream layers imply upstream intent over the declared abstract sandbox model.
4. **Triangulate** structural diff vs Z3 per layer — disagreement is preserved, not merged into one score.
5. **Report** implication failures, counterexample atoms, and assumption boundaries as replayable artifacts.

Optional integrations (same trust boundary): candidate evaluation (`--evaluate-candidates`), MCP wrapper ([`specgap-mcp/`](specgap-mcp/README.md)), pre-runtime evidence export ([`docs/BOXARENA_POSITIONING.md`](docs/BOXARENA_POSITIONING.md)).

---

## 3-minute evaluator path

```bash
git clone https://github.com/repowazdogz-droid/specgap.git
cd specgap
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m specgap.cli examples/sandbox_no_network.json --out reports/demo_report.md
```

**Inspect:** [`reports/demo_report.md`](reports/demo_report.md)

| Section | What to look for |
| --- | --- |
| Extracted constraints | Intent `no_network` vs policy `localhost_only` |
| Z3 Formal Check | **Implication FAILS** — downstream permits behavior upstream forbids |
| Counterexample | `network_send=true, dest_localhost=true` *(abstract model only)* |

**Deeper walkthrough:** [`HACKATHON_JUDGE_GUIDE.md`](HACKATHON_JUDGE_GUIDE.md)

---

## 10-minute evaluator path

After the [3-minute setup](#3-minute-evaluator-path):

```bash
python -m specgap.cli examples/06_triangulation_disagreement.json --out reports/06_triangulation_disagreement_report.md
python -m specgap.cli examples/05_candidate_policy_ranking.json --evaluate-candidates --out reports/05_candidate_evaluation_report.md
python -m specgap.cli examples/04_paraphrased_sandbox.json --out reports/04_paraphrased_sandbox_report.md
pip install -r requirements-dev.txt && pytest -q
```

| Example | What it shows |
| --- | --- |
| `06_triangulation_disagreement.json` | Structural diff silent, Z3 fails — **disagreement preserved** |
| `05_candidate_policy_ranking.json` | Candidate A PASS, B/C FAIL — policy comparison, not a security score |
| `04_paraphrased_sandbox.json` | Extraction failure on paraphrase — vocabulary boundary, not a clean PASS |

---

## Example map

| File | Research contribution |
| --- | --- |
| [`examples/sandbox_no_network.json`](examples/sandbox_no_network.json) | Basic semantic weakening + Z3 implication failure |
| [`examples/04_paraphrased_sandbox.json`](examples/04_paraphrased_sandbox.json) | Extraction-boundary / paraphrase brittleness guard |
| [`examples/05_candidate_policy_ranking.json`](examples/05_candidate_policy_ranking.json) | Candidate policy comparison vs one intent |
| [`examples/06_triangulation_disagreement.json`](examples/06_triangulation_disagreement.json) | Disagreement preservation across independent mechanisms |

**Additional examples:** [`sandbox_readonly_fs.json`](examples/sandbox_readonly_fs.json), [`syscall_policy_mismatch.json`](examples/syscall_policy_mismatch.json), [`boxarena_preflight_*.json`](examples/) — same pipeline, different constraint domains.

**Tutorials:** [`tutorials/README.md`](tutorials/README.md) (step-by-step walkthroughs for each row above).

---

## Why disagreement matters

Structural diff and Z3 operate **independently** over extracted constraints:

- **Structural diff** — name-level weakening lattice
- **Z3** — propositional abstract sandbox model

When they diverge, SpecGap reports both signals. Collapsing to one verdict would hide lattice gaps, encoding incompleteness, or abstraction mismatch. That preservation is the core research contribution.

→ [`docs/WHY_DISAGREEMENT_MATTERS.md`](docs/WHY_DISAGREEMENT_MATTERS.md)

---

## What SpecGap does NOT claim

SpecGap does **NOT**:

- prove runtime security
- verify infrastructure or execute sandboxes
- replace adversarial evaluation
- guarantee extraction completeness
- turn **PASS** into “secure”

| Outcome | Meaning |
| --- | --- |
| **PASS** | No divergence found under the current extraction rules and declared abstract model. |
| **FAIL** | Logical preservation failed inside the abstract model — often with a counterexample. |

Counterexamples are illustrative behaviors in the model, not confirmed exploits. A clean report is bounded specification assurance, not semantic approval of stakeholder intent.

**Assurance docs:** [`docs/SPECIFICATION.md`](docs/SPECIFICATION.md) · [`docs/ASSURANCE_BOUNDARY.md`](docs/ASSURANCE_BOUNDARY.md) · [`docs/TCB.md`](docs/TCB.md) · [`docs/ENCODING.md`](docs/ENCODING.md)

---

## Repository map

```
specgap/                 CLI package — extractor, semantic_diff, z3_checker, triangulation, reporter
specgap-mcp/             stdio MCP wrapper (analyze_spec, evaluate_candidates, boxarena_preflight)
examples/                Input JSON specs (tracked)
reports/                 Reference reports (regenerate via CLI)
tests/                   pytest suite — Z3 checks not mocked
docs/                    Specification, assurance boundary, encoding, architecture assets
tutorials/               Verified walkthroughs
submission/              Hackathon summary and freeze record
.github/workflows/       CI — pytest on push
```

---

## Development / tests

**Requires:** Python 3.10+, [Z3](https://github.com/Z3Prover/z3) via `z3-solver`.

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest -q
```

- **Deterministic CLI** — same JSON + `--extractor rule` → same extraction and Z3 results
- **41 tests** — real Z3 implication checks, not mocked
- **CI** — `.github/workflows/test.yml` runs `pytest -q` on `main`

Record input path, extractor mode, Python version, and `z3-solver` version when citing results.

---

## Submission links

| Document | Purpose |
| --- | --- |
| [`HACKATHON_JUDGE_GUIDE.md`](HACKATHON_JUDGE_GUIDE.md) | 3- and 10-minute judge paths, copy-paste commands |
| [`submission/HACKATHON_SUMMARY.md`](submission/HACKATHON_SUMMARY.md) | Track fit, novelty, limitations |
| [`submission/SUBMISSION_FREEZE.md`](submission/SUBMISSION_FREEZE.md) | Verified commands and freeze record |
| [`docs/WHY_DISAGREEMENT_MATTERS.md`](docs/WHY_DISAGREEMENT_MATTERS.md) | Research contribution (one page) |
