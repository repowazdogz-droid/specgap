# SpecGap Correctness Target

This document defines what **correct** means in SpecGap. It is the canonical reference for implication checks, reports, and evaluation claims.

## Definition

**Correct relative to SpecGap** means:

For extracted constraint sets **I** (intent) and **P** (policy, implementation claim, or candidate policy), every assignment to abstract behavior atoms that satisfies **P** and the domain axioms must also satisfy every constraint in **I**.

**Violation** means:

There exists an assignment satisfying **P** and the domain axioms that violates at least one intent constraint in **I**.

This obligation is discharged by Z3 implication queries over the declared abstract sandbox model (see [`ENCODING.md`](ENCODING.md)).

This says **nothing** about:

- English semantic truth
- real kernel or runtime behavior
- exploitability
- production security guarantees

A clean result means no violation was found over **extracted constraints** in the **abstract model** — not that the specification or sandbox is correct in any stronger sense.

---

# Scope

## What SpecGap checks

- **Implication failures** between extracted constraint sets (downstream vs upstream intent)
- **Specification divergence** detected structurally (`semantic_diff`) and checked by SMT where intent constraints exist
- **Counterexample existence** — a concrete satisfying assignment in the abstract model when an implication fails
- **Internal consistency** of each layer’s extracted constraint set (satisfiability under domain axioms)
- **Candidate policy evaluation** — same implication obligation, applied independently to each supplied candidate

## What SpecGap does NOT check

- Runtime correctness or enforcement fidelity
- Sandbox escape resistance or adversarial robustness
- Syscall, seccomp, namespace, or kernel semantics beyond the propositional abstraction
- End-to-end formal verification of a deployment
- Natural language understanding (extraction is rule-based or advisory fuzzy recovery)
- That stakeholder intent was the right requirement
- That a passing candidate is safe to deploy

---

# Implication Direction

SpecGap compares **downstream** layers (formalized policy, implementation claim, or candidate policy) against **upstream** stakeholder intent.

**Obligation:** the downstream layer **must not permit** behaviors forbidden by upstream intent (as encoded in extracted constraints).

Mechanically, for constraint lists **P** (downstream) and **I** (intent), the tool asks Z3 whether:

```
∃ behavior b : domain_axioms(b) ∧ formulas(P, b) ∧ ¬ formulas(I, b)
```

If `sat`, a violating assignment exists — an **implication failure**. Reports label this as, e.g., `Formalized Policy ⇒ Stakeholder Intent` (read as: “does the policy-side encoding respect the intent-side encoding?”).

```
  Stakeholder Intent (I)
         ▲
         │  must not be violated by
         │
  Formalized Policy (P) ──► Implementation Claim (P′)
         │
         └── Candidate policies (P₁…Pₙ) in evaluation mode
```

**Downstream permissiveness is the failure mode.** If policy allows localhost network behavior but intent encodes strict `no_network`, a behavior with `network_send ∧ dest_localhost` may satisfy **P** and violate **I** — that is a reported divergence, not a proof that a real sandbox is insecure.

When intent extraction yields **zero** constraints, implication checks are skipped and the run is flagged as an **extraction failure**, not a clean pass.

---

# Why Z3

SpecGap uses Z3 for this scope because:

- **Implication queries** reduce to satisfiability of a quantifier-free propositional formula (domain axioms + downstream constraints + negated intent constraints)
- **Counterexamples** are concrete models (assignments to finitely many boolean atoms)
- The **abstract model is bounded** — a fixed atom vocabulary and hand-authored encodings (see [`ENCODING.md`](ENCODING.md))
- Full model checking or theorem proving over real sandbox semantics would be out of scope and would not match the current extraction pipeline

Z3 is used as an **SMT solver over a declared encoding**, not as a certificate that English specifications are correct.

---

# Replayability

Evidence for a SpecGap run should be reproducible without implicit context:

| Mechanism | Role |
| --- | --- |
| Deterministic CLI | Same input JSON + `--extractor rule` → same extracted constraints and Z3 results |
| Versioned examples | `examples/*.json` tracked in the repository |
| Reference reports | `reports/demo_report.md`, `reports/05_candidate_evaluation_report.md` (regenerate via CLI) |
| `pytest` suite | 41 tests; Z3 calls are not mocked |
| `requirements.txt` | Pins runtime dependency on `z3-solver` |
| Reports | Emit extracted constraints, implication outcomes, and counterexample atoms |

For audit, record: input file path, extractor mode, Python version, `z3-solver` version, and commit hash. Fuzzy mode with `ANTHROPIC_API_KEY` is not fully deterministic; treat fuzzy-extracted constraints as requiring human review.

See also [`TCB.md`](TCB.md) for trusted and untrusted components.
