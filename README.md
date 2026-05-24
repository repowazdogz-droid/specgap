# SpecGap

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![pytest](https://img.shields.io/badge/tests-pytest-41%20passed-brightgreen)

SpecGap detects **specification divergence** across layered sandbox specs — intent, policy, and implementation claims — and emits **bounded evidence**: Z3 implication failures and **counterexamples in the abstract model**, with structural/Z3 disagreement preserved when the independent checks diverge.

**Judge path:** [HACKATHON_JUDGE_GUIDE.md](HACKATHON_JUDGE_GUIDE.md) · **10-minute run:** [below](#10-minute-evaluator-path)

---

## The problem

Stakeholder intent drifts as specs pass through policy and implementation. Each layer reads fine in isolation; together they may permit behavior the stakeholder believed was forbidden.

**Aha example**

| Layer | Text |
| --- | --- |
| **Intent** | “No network access” |
| **Policy** | “Only localhost access” |
| **Result** | **FAIL** — downstream permits `network_send=true, dest_localhost=true`, which violates upstream `no_network`. |

Automated verification discharges obligations quickly. The bottleneck is whether the obligation still matches what stakeholders meant. SpecGap checks alignment **before** deployment or runtime evaluation — it does not run sandboxes or observe live behavior.

---

## Architecture

SpecGap checks whether downstream policy and implementation layers still logically preserve upstream intent under a declared abstract model, while preserving disagreement between independent evaluators instead of collapsing them into a single verdict.

<p align="center">
  <a href="docs/assets/specgap_architecture.svg">
    <img src="docs/assets/specgap_architecture.png" alt="SpecGap architecture: specification layers flow through extraction and SMT checking to independent evaluators, disagreement preservation, and replayable assurance artifacts" width="680"/>
  </a>
</p>

_SVG: [`docs/assets/specgap_architecture.svg`](docs/assets/specgap_architecture.svg)_

1. **Extract** canonical constraints from text (`no_network`, `localhost_only`, …) — rule mode by default.
2. **Compare** constraint sets across layers (structural specification-divergence signals).
3. **Check** with Z3 whether downstream layers imply upstream intent over the abstract sandbox model.
4. **Triangulate** structural diff vs Z3 per layer — [disagreement is preserved](docs/WHY_DISAGREEMENT_MATTERS.md), not collapsed.
5. **Report** implication failures and counterexample behaviors as replayable Markdown/JSON.

Optional: candidate evaluation (`--evaluate-candidates`), BoxArena pre-flight ([docs/BOXARENA_POSITIONING.md](docs/BOXARENA_POSITIONING.md)), MCP wrapper ([specgap-mcp/](specgap-mcp/README.md)).

---

## 10-minute evaluator path

```bash
git clone https://github.com/repowazdogz-droid/specgap.git
cd specgap
python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Headline divergence (network drift)
python -m specgap.cli examples/sandbox_no_network.json --out reports/demo_report.md

# Triangulation disagreement (structural silent, Z3 fails)
python -m specgap.cli examples/06_triangulation_disagreement.json --out reports/06_triangulation_disagreement_report.md

# Candidate ranking
python -m specgap.cli examples/05_candidate_policy_ranking.json --evaluate-candidates --out reports/05_candidate_evaluation_report.md

pip install -r requirements-dev.txt && pytest -q
```

Open `reports/demo_report.md` — see **Z3 Formal Check** and **Counterexample** sections.

**Requires:** Python 3.10+, [Z3](https://github.com/Z3Prover/z3) via `z3-solver`.

---

## Example output

From `reports/demo_report.md` (regenerate with the command above):

```markdown
### Formalized Policy ⇒ Stakeholder Intent

- **Result: implication FAILS.** Z3 returned `sat` for the negation: there is a behavior
  permitted by Formalized Policy that Stakeholder Intent forbids.
- Violated target constraint(s): `no_network`

Counterexample behavior:
- `network_send = true` — a network connection is opened
- `dest_localhost = true` — the connection destination is localhost / loopback
```

Triangulation can also **disagree** — structural diff silent while Z3 fails (see `examples/06_triangulation_disagreement.json`):

```markdown
| Layer              | Structural              | Z3 implication | Agreement |
| Formalized Policy  | no_divergence_detected  | fails          | **no**    |
```

Full reference reports: [`reports/demo_report.md`](reports/demo_report.md), [`reports/06_triangulation_disagreement_report.md`](reports/06_triangulation_disagreement_report.md).

---

## Why disagreement is preserved

Structural diff and Z3 operate **independently** over extracted constraints:

- **Structural diff** — name-level weakening lattice (`STRICT` / `WEAKER_OF`)
- **Z3** — propositional abstract sandbox model

When they diverge, SpecGap surfaces both signals rather than forcing one verdict. Disagreement may indicate a lattice gap, encoding incompleteness, or abstraction mismatch — not that one mechanism is wrong.

→ Full treatment: [`docs/WHY_DISAGREEMENT_MATTERS.md`](docs/WHY_DISAGREEMENT_MATTERS.md)

---

## Scope and assurance boundary

**SpecGap does:**

- Detect specification divergence over extracted constraints
- Emit bounded evidence (implication failures, counterexamples in the abstract model)
- Preserve heterogeneous signals from independent check mechanisms

**SpecGap does NOT:**

- Prove semantic correctness, security, or that intent was right
- Verify sandboxes, run containers, or observe runtime behavior
- Model real kernels, seccomp, or container runtimes
- Certify fuzzy extraction (advisory; requires human review)
- Generate or repair policies

A clean report means **no divergence detected under current extraction and model** — nothing stronger.

| Document | Contents |
| --- | --- |
| [`docs/SPECIFICATION.md`](docs/SPECIFICATION.md) | Correctness target, scope, implication direction, replayability |
| [`docs/ASSURANCE_BOUNDARY.md`](docs/ASSURANCE_BOUNDARY.md) | Assurance boundary, attack surfaces, inside/outside scope |
| [`docs/TCB.md`](docs/TCB.md) | Trusted computing base and abstraction limits |
| [`docs/ENCODING.md`](docs/ENCODING.md) | Behavior atoms, constraint formulas, known vacuities |

---

## Tutorials

| Tutorial | Topic |
| --- | --- |
| [tutorials/01_detecting_a_semantic_gap.md](tutorials/01_detecting_a_semantic_gap.md) | Intent/policy/implementation, Z3 implication failure |
| [tutorials/02_rule_vs_fuzzy_extraction.md](tutorials/02_rule_vs_fuzzy_extraction.md) | Vocabulary-bound rules, extraction-failure guard, fuzzy recovery |
| [tutorials/03_candidate_policy_evaluation.md](tutorials/03_candidate_policy_evaluation.md) | Candidate evaluation, implementation discrimination |
| [tutorials/04_triangulation_disagreement.md](tutorials/04_triangulation_disagreement.md) | Structural vs Z3 disagreement (triangulation) |

See [tutorials/README.md](tutorials/README.md) for 10- and 30-minute reading paths.

## Examples

| File | Divergence |
| --- | --- |
| `examples/sandbox_no_network.json` | `no_network` vs `localhost_only` |
| `examples/sandbox_readonly_fs.json` | read-only intent vs writable `/tmp` |
| `examples/syscall_policy_mismatch.json` | no privesc vs setuid allowed |
| `examples/04_paraphrased_sandbox.json` | "air-gapped" paraphrase (rule fails, fuzzy recovers) |
| `examples/05_candidate_policy_ranking.json` | Three candidates vs one intent (A: no implication failure) |
| `examples/06_triangulation_disagreement.json` | Structural silent, Z3 fails — triangulation disagreement |
| `examples/boxarena_preflight_divergence.json` | BoxArena pre-flight fail (network spec drift) |
| `examples/boxarena_preflight_pass.json` | BoxArena pre-flight pass (aligned read-only spec) |

## Docs and submission

| Resource | Purpose |
| --- | --- |
| [HACKATHON_JUDGE_GUIDE.md](HACKATHON_JUDGE_GUIDE.md) | 3- and 10-minute judge paths |
| [submission/HACKATHON_SUMMARY.md](submission/HACKATHON_SUMMARY.md) | Track fit, novelty, demo commands |
| [docs/WHY_DISAGREEMENT_MATTERS.md](docs/WHY_DISAGREEMENT_MATTERS.md) | Core research contribution |
| [docs/BOXARENA_POSITIONING.md](docs/BOXARENA_POSITIONING.md) | Pre-flight → runtime evaluation workflow |

## Replayability

- **Deterministic CLI** — same JSON input and `--extractor rule` yield the same extraction and Z3 results
- **Reproducible examples** — `examples/*.json` tracked in the repository
- **Reference reports** — whitelisted under `reports/` (regenerate via CLI)
- **pytest** — 41 tests; Z3 implication checks are not mocked

Record input path, extractor mode, Python version, and `z3-solver` version when citing results.

## Project structure

```
specgap/
├── specgap/           # Python package (cli, extractor, z3_checker, reporter, …)
│   └── integrations/  # boxarena_adapter.py — pre-runtime bridge (not runtime eval)
├── specgap-mcp/       # Local stdio MCP wrapper
├── docs/              # Specification, assurance boundary, TCB, encoding
├── examples/          # Input JSON specs
├── tutorials/         # Research onboarding walkthroughs
├── reports/           # Reference Markdown reports (regenerate via CLI)
├── tests/             # pytest suite
├── submission/        # Hackathon summary and validation record
├── requirements.txt
└── pyproject.toml
```

## Limitations

- Rule extraction uses a fixed vocabulary; unrecognized phrasing is not extracted.
- Fuzzy mode is opt-in; extracted fuzzy constraints require human review.
- Z3 model is propositional abstraction — counterexamples are illustrative, not exploit proofs.
- Three fixed layers (or N candidates); no multi-document specs or version history.
