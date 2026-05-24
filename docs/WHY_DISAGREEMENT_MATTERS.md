# Why Disagreement Matters

SpecGap's core research contribution is not a single verdict engine. It is **heterogeneous evidence preservation** across independent check mechanisms that operate at different abstraction levels over extracted sandbox constraints.

---

## Two independent mechanisms

| Mechanism | What it checks | Abstraction level |
| --- | --- | --- |
| **Structural diff** | Whether downstream constraint names weaken upstream strict constraints via the hand-authored `WEAKER_OF` lattice | Name-level partial order |
| **Z3 implication** | Whether downstream constraint formulas imply upstream formulas in the propositional abstract sandbox model | Behavior-atom satisfiability |

Both consume the same extracted constraint sets. Neither delegates to the other. Outcomes can **agree** or **disagree**.

---

## Agreement is not a merged verdict

When structural diff and Z3 agree (e.g. `examples/sandbox_no_network.json`), both mechanisms independently detect that downstream layers permit behavior inconsistent with upstream intent. Agreement is **confirmation within the trusted computing base (TCB)** — not proof of security, correctness, or runtime behavior.

See [`TCB.md`](TCB.md) and [`ASSURANCE_BOUNDARY.md`](ASSURANCE_BOUNDARY.md) for scope limits.

---

## Disagreement is signal, not noise

When the mechanisms diverge (e.g. `examples/06_triangulation_disagreement.json`), structural diff reports **no divergence detected** while Z3 reports **implication fails** with a concrete counterexample.

SpecGap **preserves this disagreement** rather than forcing a single PASS/FAIL. Possible interpretations:

1. **Lattice gap** — the `WEAKER_OF` relation does not encode the weakening the Z3 model captures (e.g. `readonly_root_fs` is partial, not in the strict lattice path structural diff expects).
2. **Encoding incompleteness** — the abstract model represents a property the structural layer does not name.
3. **Abstraction mismatch** — the two mechanisms answer related but non-identical questions over the same text.

Collapsing to one verdict would hide which mechanism fired and why. For specification assurance, that loss is worse than reporting heterogeneous evidence.

---

## Why not pick a winner?

- **Structural diff** is fast, auditable, and tied to human-readable constraint names — but bounded by the hand-authored lattice.
- **Z3** catches propositional implication failures the lattice may miss — but bounded by the abstract model in [`ENCODING.md`](ENCODING.md).

Neither subsumes the other. SpecGap triangulates: per layer, report structural outcome, Z3 outcome, agreement flag, and counterexample when Z3 fails.

This is **bounded assurance reporting**, not statistical consensus, voting, or cross-validation.

---

## Research-engineering takeaway

Most spec-checking tools optimize for a single authoritative answer. SpecGap optimizes for **replayable evidence artifacts** that preserve when independent abstractions diverge.

For judges and reviewers: look for triangulation rows where **Agreement = no**. That is where the tool adds information a single-mechanism checker would miss — without claiming the disagreement itself proves a runtime vulnerability.

---

## Further reading

- [`SPECIFICATION.md`](SPECIFICATION.md) — implication direction and correctness target
- [`ENCODING.md`](ENCODING.md) — behavior atoms and known vacuities
- [`tutorials/04_triangulation_disagreement.md`](../tutorials/04_triangulation_disagreement.md) — worked example with commands
- [`HACKATHON_JUDGE_GUIDE.md`](../HACKATHON_JUDGE_GUIDE.md) — judge evaluation path
