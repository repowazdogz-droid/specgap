# Trusted Computing Base

SpecGap separates **what the tool assumes** from **what it checks**. Explicit trust boundaries are stronger than implied total assurance. This document declares the Trusted Computing Base (TCB) for interpretation of SpecGap results.

For the correctness target, see [`SPECIFICATION.md`](SPECIFICATION.md). For atom and formula definitions, see [`ENCODING.md`](ENCODING.md).

---

## Trusted

The following are treated as authoritative for interpreting a SpecGap run:

| Component | Assumption |
| --- | --- |
| **Python runtime** | CLI, extractor, and reporter execute as shipped; no tampering with source between audit and run |
| **Z3** | Correct satisfiability results for the quantifier-free propositional fragment used (`check-sat`, model extraction) |
| **Abstract sandbox encoding** | Behavior atoms, domain axioms, and constraint→formula mapping in `specgap/z3_checker.py` faithfully represent the *intended* abstraction (not real systems) |
| **Extractor phrase maps** | Rule-based substring patterns in `specgap/extractor.py` correctly map matched text to canonical constraint names |
| **Weakening lattice** | `STRICT`, `WEAKER_OF`, and related structural rules in `specgap/semantic_diff.py` reflect intended partial-vs-strict relationships for reporting |
| **Domain axioms** | Fixed relationships between atoms (e.g. privilege gain ↔ setuid ∨ cap_sys_admin) are accepted for all queries |
| **Dependency integrity** | `z3-solver` package matches declared requirements; venv/isolated install recommended (PEP 668) |
| **Example input honesty** | JSON fields describe the scenario under test; `expected_issue` / `expected` fields are author annotations, not tool verdicts |

---

## Partially trusted / human review required

| Component | Limitation |
| --- | --- |
| **Fuzzy extraction** | Opt-in (`--extractor fuzzy`); not authoritative |
| **Offline paraphrase map** | Small deterministic map (`air-gapped` → `no_network`, etc.); coverage is minimal |
| **Optional LLM extraction** | When `ANTHROPIC_API_KEY` is set; output is schema-loose, may differ between runs; failures fall back to offline map |
| **Author annotations** | Report section `## Human Annotation (outside tool evaluation)` — blockquoted HUMAN NOTE; not tool output |
| **Structural severity labels** | `high structural severity` in diff output is a heuristic over constraint kinds, not a security rating |

Human review is required before acting on any fuzzy-derived constraint or before treating structural diff alone as dispositive.

---

## Explicitly NOT trusted

SpecGap results do **not** establish:

| Claim | Reason |
| --- | --- |
| Real kernel behavior | No Linux, seccomp, or container runtime model |
| Production sandbox security | No deployment, enforcement, or adversary model |
| Exploit resistance | Counterexamples are abstract assignments, not exploits |
| Runtime isolation guarantees | No observation of running processes |
| Completeness of extraction vocabulary | Unmatched English is silently not extracted |
| English semantic truth | Text→constraint mapping is partial and rule-bound |
| Agreement between structural diff and Z3 | Two independent mechanisms; disagreement is possible and not yet surfaced as a first-class report quadrant |

A **PASS** or “no implication failure” outcome does not mean the sandbox is safe to run in production.

---

# Known abstraction limits

- **Finite atom vocabulary** — 13 boolean behavior atoms; no paths, PIDs, or network endpoints beyond localhost vs external
- **Hand-authored formulas** — each canonical constraint name maps to a fixed Z3 formula; unmaintained names default to `true` (vacuous)
- **Simplified privilege model** — privilege gain only via `setuid_exec` or `cap_sys_admin`; `run_as_root` is a separate atom not fully coupled to privilege gain
- **Propositional abstraction** — no time, state, sequences, or resource limits
- **Illustrative counterexamples** — one satisfying model among possibly many; `model_completion=True` may set irrelevant atoms
- **Vacuous permission encodings** — some extracted permissions (e.g. `write_allowed`, `network_allowed`) do not restrict the model (documented in [`ENCODING.md`](ENCODING.md))
- **Syscall surface** — denylist/allowlist text is extracted; parsed syscall names are not wired into Z3 atoms

---

# Philosophy

- **Explicit trust boundaries** beat vague “AI verification” language. SpecGap checks a declared encoding, not the world.
- **Disagreement and uncertainty should be preserved** where possible: extraction failures are surfaced; fuzzy output requires review; structural diff and Z3 can in principle diverge.
- **Methodology over moat** — reproducible CLI, documented encoding, and pytest evidence matter more than proprietary pipelines.
- **Right tool for the problem** — SMT over a small abstraction for implication spotting; not theorem proving over full sandbox semantics.

When in doubt, state the obligation from [`SPECIFICATION.md`](SPECIFICATION.md) and point reviewers to [`ENCODING.md`](ENCODING.md) before discussing “correctness.”
