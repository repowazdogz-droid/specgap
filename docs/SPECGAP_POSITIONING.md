# SpecGap positioning

**Layer:** Assurance (OMEGA Lab public trunk)

SpecGap is a **pre-runtime assurance tool** for **layered specification divergence**. It produces **replayable evidence** about whether downstream policy and implementation claims still preserve upstream intent **under a declared abstract model** — while **preserving disagreement** between independent check mechanisms.

This document states what SpecGap is, what it is not, and how it fits the OMEGA Lab stack. For mechanism detail see [`SPECIFICATION.md`](SPECIFICATION.md), [`ASSURANCE_BOUNDARY.md`](ASSURANCE_BOUNDARY.md), [`TCB.md`](TCB.md).

---

## What SpecGap is

| Property | Meaning |
| --- | --- |
| **Pre-runtime** | Runs on written specification layers before build, deploy, or adversarial sandbox evaluation |
| **Layered** | Compares stakeholder intent, formalized policy, implementation claims, and optional candidate policies |
| **Evidence generator** | Emits Markdown reports and JSON evidence chains from deterministic CLI runs |
| **Triangulated** | Structural weakening analysis and Z3 implication run independently; outcomes are reported together |
| **Bounded** | Claims apply only to **extracted constraints** in the **abstract sandbox encoding** |
| **Replayable** | Same input JSON and `--extractor rule` reproduce extraction and SMT results |

**Core question (inside the boundary):**

> Given these specification layers, do the extracted constraints show structural divergence, implication failure, or triangulation disagreement relative to upstream intent in the declared model?

---

## What SpecGap is not

SpecGap is **not**:

- A runtime sandbox, MCP server enforcement layer, or agent
- A substitute for seccomp, namespaces, kernel analysis, or penetration testing
- A natural-language understanding system (extraction is rule-based; fuzzy paths are advisory)
- A compliance or certification engine
- A single PASS/FAIL oracle that merges heterogeneous signals
- Proof that a deployment is safe, aligned, or "trustworthy"

Optional MCP wrappers and BoxArena pre-flight hooks **do not expand** the assurance boundary. They expose or sequence the same checks.

---

## Why pre-runtime assurance matters

Semantic drift accumulates **across layers**, not inside one document. Each layer can read plausibly in isolation while the composed system permits behavior upstream intent forbade.

Catching drift **before** build or adversarial evaluation is cheaper than:

- Reconstructing intent from logs after an incident
- Treating a clean runtime test as proof the written spec was faithful
- Collapsing "no escape this time" into "spec was correct"

SpecGap targets the **specification stack**, not the running system. Runtime assurance remains a separate obligation.

---

## Layered specification divergence

Typical inputs (see `examples/`):

1. **Stakeholder intent** — human-facing requirement ("no network access")
2. **Formalized policy** — machine-oriented rules ("localhost only")
3. **Implementation claim** — what the built artifact asserts it enforces
4. **Candidate policies** (optional) — ranked alternatives for the same intent

Failure modes include:

- **Weakening** — downstream strictly permits more than upstream (`no_network` → `localhost_only`)
- **Claim not implied** — implementation asserts permissions intent never granted
- **Extraction failure** — intent never entered the model (reported explicitly, not silently passed)

SpecGap does not judge whether intent was **wise** — only whether downstream **extracted** constraints preserve upstream **extracted** constraints in the model.

---

## Triangulation and disagreement preservation

Two mechanisms operate on different abstractions:

- **Structural diff** — name-level weakening via a hand-authored lattice
- **Z3 implication** — propositional formulas over behavior atoms

They can agree or **disagree**. Disagreement is **first-class output**, not noise to average away. See [`WHY_DISAGREEMENT_MATTERS.md`](WHY_DISAGREEMENT_MATTERS.md).

---

## Bounded guarantees

A SpecGap report that states **no divergence detected** or **no implication failure** means only:

> Under the documented TCB, for the **extracted** constraints, no violation was found in the **abstract model**.

It does **not** mean the English text is complete, the sandbox is safe, or runtime enforcement matches the document.

Passing SpecGap is a **check on a declared obligation**, not a certificate.

---

## Operational honesty

SpecGap is designed for operators and researchers who need to answer:

1. **What is trusted?** (extractor vocabulary, lattice, encoding, Z3)
2. **What is modeled?** (propositional sandbox atoms, not the kernel)
3. **What is omitted?** (unmatched phrases, partial constraints, runtime)

Reports should be read as **assurance evidence**, not confidence theater. Triangulation rows with **Agreement = no** are often the most informative.

---

## Relationship to OMEGA Lab

| OMEGA layer | Role | SpecGap relationship |
| --- | --- | --- |
| **Assurance** | Evidence before runtime | SpecGap is the assurance-layer entry for spec divergence |
| **Doctrine** | Lean predicate scaffolding | Conceptual alignment only; no Lean export in SpecGap artifacts today |
| **Substrate** | `OmegaRecord` envelope | Integrators may attach SpecGap evidence to provenance; not a first-class slot yet |
| **Replay** | Decision traces (clearpath) | Complementary: SpecGap checks specs **before** action; clearpath records decisions **after** |
| **Authority / Materiality** | consent-ledger, assumption-registry | SpecGap does not enforce gates or register assumptions; see [`RESEARCH_DIRECTIONS.md`](RESEARCH_DIRECTIONS.md) for lineage directions |

Stack map: [omega-contracts TRUST_STACK](https://github.com/repowazdogz-droid/omega-contracts/blob/main/docs/TRUST_STACK.md)

Lab profile: [github.com/repowazdogz-droid/repowazdogz-droid](https://github.com/repowazdogz-droid/repowazdogz-droid)

---

## Where to start (10 minutes)

| Time | Document / action |
| --- | --- |
| 3 min | README quickstart + `examples/sandbox_no_network.json` |
| 3 min | This file + [`ASSURANCE_BOUNDARY.md`](ASSURANCE_BOUNDARY.md) |
| 2 min | [`WHY_DISAGREEMENT_MATTERS.md`](WHY_DISAGREEMENT_MATTERS.md) |
| 2 min | [`THREAT_MODEL_SUMMARY.md`](THREAT_MODEL_SUMMARY.md) |

Collaboration surface: [`RESEARCH_DIRECTIONS.md`](RESEARCH_DIRECTIONS.md), issues/PRs on constraint vocabulary, lattice coverage, encodings, and replayable evidence formats.
