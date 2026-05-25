# Why disagreement matters

Short essay on SpecGap's epistemic design. Technical companion: [`ASSURANCE_BOUNDARY.md`](ASSURANCE_BOUNDARY.md), [`THREAT_MODEL_SUMMARY.md`](THREAT_MODEL_SUMMARY.md).

---

## The problem with one verdict

Most specification tools optimize for a **single authoritative answer**: PASS or FAIL, green or red, safe or unsafe. That is convenient for dashboards. It is dangerous for assurance.

Independent check mechanisms operate at **different abstractions**. When they agree, you learn that two bounded views align **inside a declared model**. When they disagree, you learn that **your model stack is incomplete or misaligned** — often more valuable than another green check.

Collapsing heterogeneous signals into consensus is **confidence theater**: it looks like certainty without adding inspectable evidence.

---

## Preserving contradiction

SpecGap runs two mechanisms on the same extracted constraints:

| Mechanism | Abstraction | Question |
| --- | --- | --- |
| **Structural diff** | Constraint names + weakening lattice | Did downstream names weaken upstream strict constraints? |
| **Z3 implication** | Propositional formulas over behavior atoms | Does downstream permit a behavior intent forbids in the model? |

Outcomes can **contradict**. Example: [`examples/06_triangulation_disagreement.json`](../examples/06_triangulation_disagreement.json) — structural diff reports no divergence; Z3 reports implication failure with a counterexample.

SpecGap **preserves the contradiction** in the report. It does not pick a winner, average scores, or hide the losing mechanism.

**Why:** A contradiction often means:

- The lattice does not encode a weakening Z3 sees (lattice gap)
- The encoding represents behavior the structural layer does not name (encoding gap)
- The two mechanisms answer related but non-identical questions (abstraction mismatch)

Any of these is actionable for a spec author. A forced single verdict would destroy the diagnostic.

---

## Triangulation over consensus

**Triangulation** here means: report each mechanism's outcome, an agreement flag, and counterexamples when SMT fails — **without merging into one confidence number**.

Triangulation is **not**:

- Voting between mechanisms
- Cross-validation that doubles certainty
- Proof that disagreement implies runtime vulnerability
- An excuse to ignore structural results when Z3 passes

Triangulation **is**:

- Legible heterogeneous evidence
- A prompt for reviewers to ask *which abstraction failed*
- Operational hygiene for layered specs where no single view is complete

When **Agreement = yes** on a failure, both mechanisms saw a problem — stronger **within TCB**, still not a runtime proof.

When **Agreement = no**, slow down. That row is often the contribution.

---

## Operational danger of premature convergence

Premature convergence happens when teams:

- Ship because "the spec checker passed"
- Treat a clean adversarial run as proof the **written** policy was faithful
- Merge structural, SMT, lint, and human review into one KPI
- Hide extraction failures behind a green aggregate score

In production assurance, premature convergence produces **false negatives at review time**: the organization believes alignment was checked when only a **slice** of the spec entered the model.

SpecGap's design choice is conservative: **fail visible** on extraction emptiness, **report separate** mechanism rows, and **never** upgrade "no violation in model" to "spec is correct."

---

## Assurance evidence vs confidence theater

| Assurance evidence | Confidence theater |
| --- | --- |
| Named constraints extracted | Opaque "all good" |
| Counterexample assignments | Generic risk scores |
| Disagreement rows preserved | Single blended grade |
| Regenerable CLI artifacts | Screenshot of a dashboard |
| Explicit TCB and omissions | "AI-verified safe" |

Evidence should let a reviewer answer: **what was checked, under what assumptions, and what was left out?** If those questions cannot be answered from the artifact, the tool is performing theater.

---

## Research-engineering takeaway

SpecGap optimizes for **replayable evidence artifacts** that preserve when independent abstractions diverge — not for maximizing pass rates.

For collaborators: extend vocabulary, lattice, and encoding with **fixtures that keep disagreement examples stable**. For reviewers: treat triangulation **Agreement = no** as signal, not tool error.

Further reading:

- [`tutorials/04_triangulation_disagreement.md`](../tutorials/04_triangulation_disagreement.md) — worked example
- [`SPECIFICATION.md`](SPECIFICATION.md) — implication direction
- [`RESEARCH_DIRECTIONS.md`](RESEARCH_DIRECTIONS.md) — open falsifiable questions
