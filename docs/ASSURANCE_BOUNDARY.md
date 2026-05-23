# Assurance Boundary

Verification is meaningful only **inside an explicit boundary**. Outside that boundary lies whatever the tool does not model, enforce, or observe. Every boundary implies a **trusted computing base (TCB)** — components whose correctness is assumed — and an **attack surface** — stages where errors, omissions, or mis-specification can invalidate conclusions even when the machinery “works as designed.” This is the central lesson of boundary-explicit verification (see e.g. Kiran Gopinathan on verification boundaries, TCB, and attack surface).

SpecGap follows this discipline: it generates **bounded evidence** about specification alignment over **extracted constraints** in an **abstract sandbox model**. It does not certify runtimes, policies in production, or English prose.

Related: [`TCB.md`](TCB.md), [`SPECIFICATION.md`](SPECIFICATION.md), [`ENCODING.md`](ENCODING.md), [`BOXARENA_POSITIONING.md`](BOXARENA_POSITIONING.md).

---

## SpecGap’s assurance boundary

**SpecGap stops at evidence generation.**

Inside the boundary, SpecGap answers:

> Given these three (or N candidate) specification layers, do the extracted constraints show structural divergence, implication failure, or triangulation disagreement relative to stakeholder intent in the declared abstract model?

Outside the boundary, SpecGap does **not** answer:

> Does the sandbox actually confine adversaries at runtime? Is the deployment secure? Did the English text mean what stakeholders believe?

That outer question belongs to empirical evaluation, enforcement layers, and operational assurance — not to SpecGap alone.

---

## Inside the boundary

| What is checked | Mechanism |
| --- | --- |
| Text → canonical constraints | Rule-based extraction (optional fuzzy, advisory) |
| Name-level weakening / missing obligations | Structural divergence analysis (`WEAKER_OF` lattice) |
| Downstream ⇒ intent over abstract behaviors | Z3 implication queries |
| Independent mechanism outcomes | Triangulation (agreement / disagreement preserved) |
| Audit artifacts | Markdown reports, JSON evidence chains, MCP summaries |

**Primary TCB** (assumed correct for interpretation):

- Rule extractor phrase vocabulary
- Hand-authored weakening lattice
- Propositional abstract sandbox model and encoding
- Z3 satisfiability for the queries issued
- Deterministic CLI/reporter pipeline (`extractor=rule`)

See [`TCB.md`](TCB.md) for the full trusted / partially trusted / not-trusted breakdown.

---

## Outside the boundary

SpecGap explicitly does **not** establish:

- Runtime behavior or container escape resistance
- Seccomp, namespace, or kernel semantics
- Correctness of natural-language specifications
- Completeness of extraction (unmatched phrases are omitted)
- Exploit proofs (counterexamples are abstract assignments)
- That a built system matches written claims

Optional **BoxArena** pre-flight and **MCP** wrappers do not expand this boundary — they expose or sequence the same SpecGap checks. BoxArena runtime evaluation remains downstream.

---

## Pipeline stages as attack surface

Each stage is a place where conclusions can fail even if later stages run successfully.

| Stage | Attack surface | Typical failure mode |
| --- | --- | --- |
| **Input JSON** | Author supplies wrong or incomplete layers | Scenario does not match deployment |
| **Constraint extraction** | Fixed vocabulary; silent omission | Intent never enters the model; false “clean” structural view |
| **Structural diff** | `STRICT` / `WEAKER_OF` coverage gaps | Partial constraints (e.g. `readonly_root_fs`) not lattice-checked; divergence missed |
| **Z3 implication** | Abstract encoding ≠ real system | Implication holds/fails in model but not in production |
| **Triangulation** | Misread as single verdict | Collapsing disagreeing signals into false confidence |
| **Report / evidence** | Human misreads PASS wording | “No divergence detected” treated as correctness |
| **Optional fuzzy / LLM extraction** | Non-deterministic or advisory input | Constraints accepted without review |

Preserving **disagreement** between structural diff and Z3 (see [`examples/06_triangulation_disagreement.json`](../examples/06_triangulation_disagreement.json)) treats heterogeneous evidence as first-class — not as noise to average away.

---

## Why BoxArena complements SpecGap

SpecGap and BoxArena sit on opposite sides of the same trust boundary:

| | SpecGap | BoxArena |
| --- | --- | --- |
| **Question** | Did specification meaning drift before runtime? | What does the runtime do under adversarial pressure? |
| **Evidence** | Extracted constraints, implication counterexamples | Empirical quest outcomes, runtime observations |
| **When** | Pre-flight / pre-deploy | After build, on running sandboxes |

A clean BoxArena run does not repair a divergent spec. A SpecGap pass does not predict escape resistance. Together: **align the spec first**, then **stress the implementation** — complementary, not redundant.

See [`BOXARENA_POSITIONING.md`](BOXARENA_POSITIONING.md).

---

## Triangulation and disagreement preservation

Structural diff and Z3 operate over **different abstractions**:

- Structural analysis compares **constraint names** via a hand-authored weakening lattice.
- Z3 checks **propositional formulas** over behavior atoms.

They can **agree** (both signal a problem or neither does) or **disagree** (e.g. structural silent, Z3 fails). Disagreement is **diagnostic**:

- Possible lattice gap (`WEAKER_OF` incomplete for partial constraints)
- Encoding incompleteness (vacuous permission formulas)
- Abstraction mismatch between name-level and propositional semantics

SpecGap reports both signals without merging them into a consensus score. That is intentional epistemic hygiene — not cross-validation and not a confidence boost.

---

## “No divergence detected” is not correctness

A report stating **no divergence detected** or **no implication failure** means only:

> Under the TCB above, for the **extracted** constraints, no violation was found in the **abstract sandbox model**.

It does **not** mean:

- The specification is true or complete in English
- The sandbox is safe to deploy
- Runtime enforcement matches the document
- All relevant obligations were extracted

Passing SpecGap is a **necessary-style check on a declared obligation**, not a certificate. Operational assurance still requires enforcement fidelity, testing, and — where appropriate — empirical adversarial evaluation.

---

## Summary

| Inside boundary | Outside boundary |
| --- | --- |
| Extracted constraint alignment | Runtime confinement |
| Structural + Z3 + triangulation evidence | Kernel / seccomp fidelity |
| Abstract counterexamples | Exploit demonstrations |
| Replayable CLI artifacts | Production security claims |

When reviewing SpecGap output, ask: **What is trusted? What is modeled? What is omitted?** Those three questions define the assurance boundary — not the headline verdict.
