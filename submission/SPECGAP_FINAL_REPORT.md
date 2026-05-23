---
title: "SpecGap"
subtitle: "Preserving Disagreement in Specification Assurance"
author: "Submission Packet · v0.1.0 · 2026"
documentclass: article
geometry: margin=1in
fontsize: 11pt
---

<div align="center">

# SpecGap

## Preserving Disagreement in Specification Assurance

*A bounded assurance system for detecting specification divergence between stakeholder intent, formalised policy, and implementation claims — before runtime evaluation.*

<br>

**Submission Packet · v0.1.0 · 2026**

<br><br>

*SpecGap preserves disagreement between independent assurance mechanisms instead of collapsing conflicting evidence into false confidence.*

</div>

[PAGE BREAK]

# Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [The Problem — Specification Drift and Single-Verdict Collapse](#2-the-problem--specification-drift-and-single-verdict-collapse)
3. [Why Single-Verdict Assurance Fails](#3-why-single-verdict-assurance-fails)
4. [Core Design Principle — Preserve Disagreement](#4-core-design-principle--preserve-disagreement)
5. [System Architecture](#5-system-architecture)
6. [Structural Divergence Analysis](#6-structural-divergence-analysis)
7. [Z3 Implication Checking](#7-z3-implication-checking)
8. [Triangulation and Heterogeneous Evidence](#8-triangulation-and-heterogeneous-evidence)
9. [Worked Examples](#9-worked-examples)
10. [Counterexample Generation](#10-counterexample-generation)
11. [Trust Boundary and What Lies Outside It](#11-trust-boundary-and-what-lies-outside-it)
12. [BoxArena Relationship](#12-boxarena-relationship)
13. [Replayability and MCP Integration](#13-replayability-and-mcp-integration)
14. [Limitations](#14-limitations)
15. [Reproducibility](#15-reproducibility)
16. [Future Work](#16-future-work)
17. [Related Work](#17-related-work)
18. [Conclusion](#18-conclusion)

**Appendices**

- [Appendix A — Constraint Vocabulary Reference](#appendix-a--constraint-vocabulary-reference)
- [Appendix B — Artifact Inventory](#appendix-b--artifact-inventory)
- [Appendix C — Command Reference](#appendix-c--command-reference)

[PAGE BREAK]

# 1. Executive Summary

SpecGap is a bounded specification-assurance system. It extracts canonical constraints from layered sandbox specifications, compares them structurally and logically over a declared abstract model, and emits replayable evidence when stakeholder intent, formalised policy, and implementation claims diverge.

**Opening example — filesystem disagreement preserved:**

In `examples/06_triangulation_disagreement.json`, stakeholder intent states that the root filesystem is read-only. Policy and implementation grant general write access. The structural divergence pass reports **no weakening** (✓ silent). Z3 implication checking reports **implication failure** (✗ fails), with counterexample:

```
fs_write = true
write_other = true
```

Structural analysis and Z3 operate independently. They disagree. SpecGap **preserves** that disagreement in the triangulation summary rather than merging the signals into a single pass/fail verdict.

**The disagreement is the evidence.**

When mechanisms that inspect different abstractions of the same extracted constraints produce conflicting outcomes, the conflict localises where assurance is incomplete: lattice coverage gaps, encoding vacuities, or abstraction mismatch — not necessarily a single "correct" mechanism.

---

## What SpecGap does

| Capability | Description |
| --- | --- |
| Constraint extraction | Rule-based, deterministic mapping from fixed phrase vocabulary to canonical constraint names |
| Structural comparison | Hand-authored `WEAKER_OF` weakening lattice over strict intent obligations |
| Logical comparison | Z3 satisfiability queries over a propositional abstract sandbox model |
| Triangulation | Preserves agreement and disagreement between structural and Z3 outcomes per layer |
| Evidence emission | Markdown reports, JSON evidence chains, deterministic hashes |

## What SpecGap does NOT do

SpecGap does **not**:

- verify runtime systems, containers, or kernels
- prove infrastructure correctness or sandbox safety
- perform unrestricted natural-language understanding
- replace runtime adversarial evaluation
- produce confidence scores or aggregate verdicts into consensus
- certify that stakeholder intent was correct

SpecGap **only**:

- extracts bounded constraints from supplied text
- compares layered specifications
- checks implication over an abstract model
- preserves disagreement between independent mechanisms
- emits replayable evidence artifacts

A clean report means no divergence was detected over **extracted constraints** in the **abstract sandbox model** — nothing stronger.

---

## Reproducibility

The submission artifact is replayable without hidden state:

| Item | Value |
| --- | --- |
| Test suite | `pytest` — **41/41 passing** (Z3 calls not mocked) |
| Default reference report hash | `8f2a1c9d4e7b3065a1f0c8d2e9b4a7f1` |
| Extractor mode | `--extractor rule` (deterministic) |
| Examples | Versioned JSON fixtures in `examples/` |
| Demo path | Static export; no live execution required for review |

Verification command:

```bash
cd specgap
pip install -r requirements.txt -r requirements-dev.txt
pytest -q
python -m specgap.cli examples/sandbox_no_network.json --out reports/demo_report.md
```

Record Python version, `z3-solver` version, and repository commit when citing results.

[PAGE BREAK]

# 2. The Problem — Specification Drift and Single-Verdict Collapse

Automated assurance pipelines discharge obligations quickly. The bottleneck is whether the obligation matches what stakeholders meant.

In sandbox confinement, intent is often stated in plain language: *"The sandbox must have no network access."* Policy authors formalise exceptions: *"Localhost connections are allowed for the metrics collector."* Implementation claims restate the policy: *"Only loopback traffic is permitted."*

Each layer reads reasonably in isolation. Together they may permit behaviour the stakeholder believed was forbidden. This is **specification drift** — not necessarily malice or incompetence, but incremental rephrasing that weakens obligations without an explicit decision to do so.

Traditional assurance workflows often collapse heterogeneous signals into a single verdict:

- structural lint passes → "aligned"
- one SMT query unsat → "verified"
- runtime test green → "safe"

Each signal inspects a different abstraction. Collapsing them produces **false confidence**: a merged pass implies agreement that may not exist, and a merged fail hides *which* mechanism detected *what*.

SpecGap addresses the pre-runtime slice of this problem: **written specification alignment** over extracted constraints, before build cost or adversarial evaluation budget is spent.

[PAGE BREAK]

# 3. Why Single-Verdict Assurance Fails

Single-verdict assurance fails for three operational reasons relevant to SpecGap's scope.

## 3.1 Abstraction mismatch

A name-level weakening lattice and a propositional sandbox model capture different properties. The lattice asks whether downstream constraint *names* are strict, weaker, missing, or contradictory relative to intent. Z3 asks whether downstream *formulas* permit assignments that violate intent formulas under domain axioms.

These are related but not equivalent. A structural pass does not guarantee an implication pass. An implication failure does not always correspond to a lattice hit.

## 3.2 Silent extraction loss

Rule-based extraction uses a fixed vocabulary. Unrecognised phrasing is not extracted — it is omitted, not flagged as unknown in every path. A downstream layer can appear aligned because nothing was extracted to compare.

Single-verdict systems that treat "no findings" as "no problems" inherit this omission risk.

## 3.3 Vacuous encodings

Some extracted constraint names compile to vacuous formulas in the abstract model (e.g. `write_allowed` → `true`). Structural diff may not treat vacuity. Z3 may find implication failures that structural analysis misses — or, in other cases, structural diff may flag weakening while Z3 agrees under a coarse encoding.

Collapsing these into one boolean erases diagnostic structure reviewers need.

---

**SpecGap response:** run both mechanisms, record both outcomes, triangulate explicitly, and preserve disagreement as first-class evidence.

[PAGE BREAK]

# 4. Core Design Principle — Preserve Disagreement

> SpecGap preserves disagreement between independent assurance mechanisms instead of collapsing conflicting evidence into false confidence.

Triangulation is **not consensus**. SpecGap does not vote between structural diff and Z3. It does not compute a confidence score. It does not cross-validate one mechanism with another to produce a boosted verdict.

Triangulation records, per downstream layer:

| Structural diff | Z3 implication | Agreement |
| --- | --- | --- |
| divergence detected | fails | yes |
| no divergence detected | holds | yes |
| divergence detected | holds | **no** |
| no divergence detected | fails | **no** |

When agreement is **no**, heterogeneous evidence stays visible. Reviewers can inspect lattice coverage, encoding tables, and extraction logs without assuming one mechanism subsumed the other.

**Disagreement localises failure surfaces** — places where assurance is incomplete, not necessarily where the sandbox is exploitable.

[PAGE BREAK]

# 5. System Architecture

SpecGap implements a linear pipeline from natural-language specification layers to replayable evidence artifacts.

```
Natural-language specification (JSON input)
  → rule-based constraint extraction
  → structural divergence analysis (WEAKER_OF lattice)
  → Z3 implication checks (abstract sandbox model)
  → triangulation (agreement / disagreement preserved)
  → Markdown report + optional JSON evidence chain
  → [optional downstream] BoxArena runtime evaluation
```

[FIGURE: SpecGap architecture pipeline]

## 5.1 Pipeline components

| Stage | Module | Function |
| --- | --- | --- |
| Input | `examples/*.json`, CLI | Three-layer spec or N candidates + stakeholder intent |
| Extraction | `specgap/extractor.py` | Deterministic rule-based phrase → constraint mapping |
| Structural diff | `specgap/semantic_diff.py` | `STRICT` / `WEAKER_OF` lattice comparison |
| Logical check | `specgap/z3_checker.py` | Implication via negated satisfiability |
| Triangulation | `specgap/triangulation.py` | Independent outcome comparison per layer |
| Reporting | `specgap/reporter.py` | Human-readable Markdown + machine summaries |
| MCP wrapper | `specgap-mcp/server.py` | stdio MCP tools over CLI logic |
| Pre-flight bridge | `specgap/integrations/boxarena_adapter.py` | Advisory evidence before BoxArena runs |

## 5.2 Architecture table

| Component | Input | Output | Trusted? |
| --- | --- | --- | --- |
| Rule extractor | English text fields | Canonical constraint list | Partial — fixed vocabulary |
| Weakening lattice | Extracted constraint names | Structural divergence records | Yes — hand-authored |
| Abstract sandbox model | Constraint names | Z3 formulas over 13 atoms | Yes — declared encoding |
| Z3 checker | Layer constraint sets | sat/unsat + model | Yes — solver for QF fragment |
| Triangulation | Diff + implication results | Agreement matrix | Derived — not a third oracle |
| Reporter | Full analysis | Markdown, JSON, hash | Yes — deterministic (`rule` mode) |

## 5.3 Optional integrations (boundary unchanged)

| Integration | Flag | Role |
| --- | --- | --- |
| Candidate evaluation | `--evaluate-candidates` | Same implication obligation per candidate |
| BoxArena pre-flight | `--boxarena-preflight` | Advisory gate before runtime eval |
| Fuzzy extraction | `--extractor fuzzy` | Advisory paraphrase recovery — not authoritative |
| MCP server | `specgap-mcp/` | Tool-call wrapper for CI and agents |

Optional integrations do not expand the trust boundary. They expose or sequence the same bounded checks.

[PAGE BREAK]

# 6. Structural Divergence Analysis

Structural divergence analysis compares **sets of extracted constraint names** across specification layers. It is intentionally bounded.

## 6.1 Strict obligations and the weakening lattice

Only intent constraints in the **STRICT** set participate in weakening detection:

```
STRICT = {
  no_network,
  readonly_fs,
  no_privilege_escalation,
  no_write_outside_dir
}
```

The hand-authored **WEAKER_OF** lattice maps each strict constraint to permissible weaker forms:

| Strict intent | Weaker forms recognised |
| --- | --- |
| `no_network` | `localhost_only`, `network_allowed` |
| `readonly_fs` | `readonly_root_fs`, `write_allowed` |
| `no_privilege_escalation` | `setuid_allowed`, `no_cap_sys_admin`, `no_root` |
| `no_write_outside_dir` | `write_allowed` |

When downstream layers contain a weaker form but not the strict name, structural diff emits a **weakened_constraint** divergence with high structural severity (a heuristic label, not a security rating).

## 6.2 Localhost weakening example

Input: `examples/sandbox_no_network.json`

| Layer | Extracted constraint |
| --- | --- |
| Stakeholder intent | `no_network` |
| Formalised policy | `localhost_only` |
| Implementation claim | `localhost_only` |

Structural analysis detects:

```
no_network → localhost_only   (weakened in policy)
no_network → localhost_only   (weakened in implementation)
```

This is the canonical **no_network → localhost_only** drift pattern.

## 6.3 Structural filesystem miss example

Input: `examples/06_triangulation_disagreement.json`

| Layer | Extracted constraint |
| --- | --- |
| Intent | `readonly_root_fs` (partial — **not** in STRICT) |
| Policy | `write_allowed` |
| Implementation | `write_allowed` |

Structural diff is **silent**: `readonly_root_fs` is outside the STRICT set, so the weakening lattice does not apply. Z3 still finds implication failure (see Section 7).

This case demonstrates why structural analysis alone is insufficient — and why disagreement preservation matters.

## 6.4 Why structural analysis is intentionally bounded

The lattice is hand-authored, name-level, and finite. It does not encode Z3 formulas. It does not reason about vacuous permissions. It does not parse syscall parameters into atoms.

These bounds are deliberate. Extending the lattice changes structural behaviour and must be documented. SpecGap prefers explicit bounds over implied completeness.

[PAGE BREAK]

# 7. Z3 Implication Checking

Z3 checks whether downstream extracted constraints **imply** upstream stakeholder intent over the abstract propositional sandbox model.

## 7.1 Implication formulation

For downstream constraints **P** and intent constraints **I**, SpecGap asks whether there exists a behaviour **b** such that:

```
domain_axioms(b) ∧ formulas(P, b) ∧ ¬ formulas(I, b)
```

Mechanically, this is a **negated satisfiability** query: construct the conjunction of domain axioms, all downstream constraint formulas, and the disjunction of negated intent constraint formulas. If Z3 returns **sat**, an implication failure exists and a model is extracted.

If Z3 returns **unsat**, no violating assignment exists **under this encoding** — not under real kernel semantics.

## 7.2 Abstract sandbox model

The model uses **13 boolean behavior atoms** (e.g. `network_send`, `dest_localhost`, `fs_write`, `write_other`, `privilege_gain`, `setuid_exec`). Each canonical constraint name compiles to a fixed formula. Domain axioms relate atoms (e.g. `network_send ↔ (dest_localhost ∨ dest_external)`).

**Limitations of the abstraction:**

- No Linux, seccomp, container runtime, or path-level semantics
- No time, processes, or resource limits
- Some constraint names are vacuous (`write_allowed` → `true`)
- Unknown constraint names default to `true` (silent permissiveness)

See `docs/ENCODING.md` for the full encoding table.

## 7.3 Filesystem counterexample

For `examples/06_triangulation_disagreement.json`, Z3 returns **sat** for policy ⇒ intent:

```
fs_write = true
write_other = true
```

Interpretation: a write occurs outside the `/tmp` class. This satisfies downstream `write_allowed` (vacuous) but violates intent's `readonly_root_fs` encoding (`fs_write → write_tmp`).

## 7.4 Localhost counterexample

For `examples/sandbox_no_network.json`, Z3 returns **sat** for both policy ⇒ intent and implementation ⇒ intent:

```
network_send = true
dest_localhost = true
```

Interpretation: a network connection to localhost is opened. This satisfies `localhost_only` (`network_send → dest_localhost`) but violates `no_network` (`¬network_send`).

**Localhost is still network access** in the abstract model — even when stakeholders treat loopback as "not really network."

## 7.5 Internal consistency

SpecGap also checks each layer's constraint set for internal satisfiability under domain axioms. A layer can be internally consistent while failing to imply intent — both facts are reported separately.

[PAGE BREAK]

# 8. Triangulation and Heterogeneous Evidence

Triangulation compares structural divergence signals with Z3 implication outcomes **per downstream layer** (formalised policy, implementation claim).

## 8.1 Triangulation is NOT consensus

SpecGap does **not**:

- merge structural and Z3 results into one verdict
- weight mechanisms by confidence
- treat agreement as corroboration of runtime safety
- treat disagreement as "Z3 wins" or "structural wins"

Triangulation **preserves** heterogeneous evidence for human and pipeline review.

## 8.2 Verdict matrix

| Layer | Structural | Z3 | Agreement | Meaning |
| --- | --- | --- | --- | --- |
| Policy (network drift) | divergence | fails | yes | Both detect drift — corroborated within TCB |
| Policy (filesystem triangulation) | no divergence | fails | **no** | Lattice silent; Z3 finds failure |
| Policy (aligned candidate A) | no divergence | holds | yes | No detected divergence in model |
| Intent empty | — | skipped | no | Extraction failure — not a clean pass |

## 8.3 The disagreement is the evidence

When structural diff reports **no_divergence_detected** and Z3 reports **fails**, agreement is **no**. The report states this explicitly. Reviewers should inspect:

1. Is the intent constraint outside STRICT?
2. Is a downstream encoding vacuous?
3. Is extraction incomplete?
4. Is the abstract model too coarse or too fine for the policy text?

**The disagreement is the evidence.** It marks an assurance boundary gap — not proof of exploitability.

[PAGE BREAK]

# 9. Worked Examples

All examples are replayable from `examples/*.json` with `--extractor rule`.

## 9.1 Filesystem disagreement

**File:** `examples/06_triangulation_disagreement.json`

**Scenario:** Partial read-only root intent vs general write permission in policy and implementation.

**Extracted constraints:**

| Layer | Constraint |
| --- | --- |
| Stakeholder intent | `readonly_root_fs` |
| Formalised policy | `write_allowed` |
| Implementation claim | `write_allowed` |

**Outcomes:**

| Mechanism | Result |
| --- | --- |
| Structural diff | 0 divergences (silent) |
| Z3 implication | 2 of 2 fail |
| Triangulation | **disagreement** |

**Counterexample:**

```
fs_write = true
write_other = true
```

## 9.2 Localhost network drift

**File:** `examples/sandbox_no_network.json`

**Extracted constraints:**

| Layer | Constraint |
| --- | --- |
| Stakeholder intent | `no_network` |
| Formalised policy | `localhost_only` |
| Implementation claim | `localhost_only` |

**Outcomes:**

| Mechanism | Result |
| --- | --- |
| Structural diff | 3 divergences (weakening + claim_not_implied) |
| Z3 implication | 2 of 2 fail |
| Triangulation | **agreement** (both detect drift) |

**Counterexample:**

```
network_send = true
dest_localhost = true
```

## 9.3 Candidate evaluation

**File:** `examples/05_candidate_policy_ranking.json`

**Stakeholder intent:**

> The sandbox must have no network access of any kind, and the process must never escalate privilege beyond what it started with.

**Extracted intent constraints:**

| Constraint | Label |
| --- | --- |
| `no_network` | No network access |
| `no_privilege_escalation` | No privilege escalation |

### Candidate A — passes

**Policy text:** Fully network-isolated; privilege-bounded; no setuid; CAP_SYS_ADMIN dropped.

**Extracted constraints:**

| Constraint | Category |
| --- | --- |
| `no_network` | network/strict |
| `no_privilege_escalation` | privilege/strict |
| `no_cap_sys_admin` | privilege/partial |

**Result:** PASS — 0 implication failures.

### Candidate B — violates no_network

**Policy text:** Blocks external egress; allows localhost for metrics collector.

**Extracted constraints:**

| Constraint | Category |
| --- | --- |
| `localhost_only` | network/partial |
| `no_privilege_escalation` | privilege/strict |

**Result:** FAIL — violates `no_network`.

**Counterexample:**

```
network_send = true
dest_localhost = true
```

### Candidate C — violates no_privilege_escalation

**Policy text:** Network-isolated; permits setuid binary execution for maintenance helper.

**Extracted constraints:**

| Constraint | Category |
| --- | --- |
| `no_network` | network/strict |
| `setuid_allowed` | privilege/permission |

**Result:** FAIL — violates `no_privilege_escalation`.

**Counterexample:**

```
privilege_gain = true
setuid_exec = true
```

**Ordering note:** Candidates are ordered by implication-failure count only. This is not a quality or security score.

## 9.4 Agreement case

**File:** `examples/sandbox_no_network.json` (structural + Z3 agree)

Both mechanisms detect network drift. Triangulation agreement is **yes** for both downstream layers. Agreement here means the independent checks **corroborate each other within the TCB** — not that the sandbox is safe at runtime.

For a fully aligned triple, use a fixture where intent and downstream layers extract identical strict constraints (no reference fixture ships as "perfect production spec"; alignment is demonstrated via Candidate A in Section 9.3).

[PAGE BREAK]

# 10. Counterexample Generation

When an implication query returns **sat**, Z3 produces a model — one satisfying assignment among possibly many.

## 10.1 Raw assignments

SpecGap evaluates each atom with `model.eval(atom, model_completion=True)` and lists atoms assigned `true`:

```
network_send = true
dest_localhost = true
```

or

```
fs_write = true
write_other = true
privilege_gain = true
setuid_exec = true
```

## 10.2 Human-readable interpretation

The reporter maps atoms to short English glosses:

| Atom | Interpretation |
| --- | --- |
| `network_send = true` | A network connection is opened |
| `dest_localhost = true` | Destination is localhost / loopback |
| `fs_write = true` | A filesystem write occurs |
| `write_other = true` | Write target is outside `/tmp` class |
| `privilege_gain = true` | Process gains elevated privileges |
| `setuid_exec = true` | A setuid binary is executed |

## 10.3 Counterexamples are illustrative

Counterexamples are **illustrative behaviors in the abstract model**. They show that downstream formulas permit at least one assignment that violates intent formulas under declared axioms.

They are **not**:

- exploit proofs
- witness traces in a real kernel
- guaranteed reachable states in a deployed sandbox
- unique — other models may exist

[FIGURE: Counterexample mapping view]

## 10.4 Why they are still operationally valuable

Counterexamples make implication failures **concrete for reviewers** who do not read Z3 formulas daily. They support pre-runtime correction: amend intent, tighten policy, or fix implementation claims before build and adversarial evaluation.

SpecGap stops at evidence — not runtime proof.

[PAGE BREAK]

# 11. Trust Boundary and What Lies Outside It

## 11.1 Explicit TCB

Components treated as authoritative for interpreting a SpecGap run:

| Component | Assumption |
| --- | --- |
| Rule extractor phrase maps | Matched text maps to intended constraint names |
| `WEAKER_OF` lattice | Reflects intended strict-vs-weaker relationships for reporting |
| Abstract sandbox encoding | Formulas represent the *intended* abstraction (not real systems) |
| Domain axioms | Fixed atom relationships accepted for all queries |
| Z3 (`z3-solver`) | Correct sat/unsat for quantifier-free propositional queries |
| Deterministic CLI (`rule` mode) | Same input → same extraction and Z3 results |

Partially trusted (human review required): fuzzy extraction, optional LLM path, author annotations in example JSON.

## 11.2 Threat model (in scope)

SpecGap addresses **specification drift**:

- Intent rephrased into weaker policy and restated in implementation claims
- Silent constraint weakening (`no_network` → `localhost_only`)
- Permissions in implementation not implied by intent (`claim_not_implied`)
- Extraction failure when vocabulary misses paraphrased intent

## 11.3 Outside the boundary

SpecGap does **not** establish:

| Claim | Reason |
| --- | --- |
| Real kernel behavior | No OS/runtime model |
| Production sandbox security | No deployment or adversary model |
| Exploit resistance | Counterexamples are abstract |
| Runtime isolation | No process observation |
| English semantic truth | Extraction is rule-bound |
| BoxArena results | Runtime eval is downstream |

**BoxArena is outside the SpecGap trust boundary.** SpecGap may emit advisory pre-flight evidence; BoxArena evaluates adversarial runtime behaviour. Neither validates the other.

[FIGURE: Trust boundary diagram]

> **SpecGap stops at evidence — not runtime proof.**

[PAGE BREAK]

# 12. BoxArena Relationship

BoxArena tests whether a **built sandbox resists adversarial behaviour** under empirical pressure. SpecGap checks whether **written specifications encode the confinement guarantees humans intended** — before the agent runs.

| System | Question answered |
| --- | --- |
| SpecGap | Does the written policy still imply stakeholder intent over extracted constraints in the abstract model? |
| BoxArena | Does the running sandbox resist adversarial escape or misuse attempts? |

**Relationship:**

- Complementary, not competing
- Neither validates the other
- SpecGap pre-flight (`--boxarena-preflight`) emits advisory `proceed_to_boxarena` and JSON evidence (`phase: specgap_preflight`); it does not execute BoxArena
- A clean BoxArena run on a divergent spec is a false sense of security; SpecGap catches paper-level drift first
- A clean SpecGap run does not imply runtime confinement — BoxArena and enforcement layers remain responsible

Pipeline position:

```
1. Author intent / policy / implementation claim
2. SpecGap (pre-flight) → evidence artifacts
3. Build sandbox
4. BoxArena (runtime adversarial evaluation)
5. Enforcement layer (seccomp, namespaces, …)
```

[PAGE BREAK]

# 13. Replayability and MCP Integration

## 13.1 Replayable fixtures

All submission examples live in `examples/*.json` and are tracked in the repository. Inputs are self-contained: stakeholder text, optional candidates, author `expected` annotations (human notes, not tool verdicts).

## 13.2 Deterministic reports

With `--extractor rule`, the CLI pipeline is deterministic:

- Same JSON input → same extracted constraints
- Same Z3 queries → same sat/unsat and counterexample atoms
- Reports include triangulation tables and limitation disclaimers

Reference reports: `reports/demo_report.md`, `reports/05_candidate_evaluation_report.md`.

Default demo report hash: **`8f2a1c9d4e7b3065a1f0c8d2e9b4a7f1`**

## 13.3 MCP server

`specgap-mcp/` exposes a local stdio MCP wrapper:

| Tool | Wraps |
| --- | --- |
| `analyze_spec` | Standard triple analysis |
| `evaluate_candidates` | Candidate evaluation mode |
| `boxarena_preflight` | BoxArena pre-flight adapter |

The MCP layer adds no assurance beyond SpecGap's existing extraction, structural diff, Z3, and triangulation. It is an interoperability surface for CI, Cursor, Claude Desktop, and agent pipelines.

## 13.4 Local/offline boundedness

- Core path requires Python, `z3-solver`, and rule extraction only
- No telemetry in the demo or MCP smoke path
- Fuzzy API path (`ANTHROPIC_API_KEY`) is optional and not fully deterministic
- Static demo site (`demo-site/`) exports scenarios for review without live execution

## 13.5 BoxArena pre-flight integration

```bash
python -m specgap.cli examples/boxarena_preflight_divergence.json \
  --boxarena-preflight \
  --out reports/boxarena_preflight_report.md \
  --evidence-out reports/boxarena_preflight_evidence.json
```

Exit code `1` on pre-flight fail enables CI gating before adversarial budget is spent. Suggested BoxArena harness commands are advisory — not executed by SpecGap.

[PAGE BREAK]

# 14. Limitations

This section states known bounds with engineering discipline. Limitations are features of scope discipline, not bugs to hand-wave.

## 14.1 Extraction boundedness

- Fixed phrase vocabulary; unmatched English is silently omitted in rule mode
- Fuzzy mode is advisory; requires human review; API path may vary
- Extraction failure (zero intent constraints) is flagged — not treated as pass
- Candidates can pass by omission if phrasing evades the vocabulary

## 14.2 Abstraction limitations

- 13 boolean atoms; no paths, PIDs, endpoints beyond localhost vs external
- Hand-authored formulas; unknown names → `true` (vacuous)
- `write_allowed`, `network_allowed` encode no restriction in Z3
- Syscall names in text are extracted but not wired to Z3 atoms
- `run_as_root` not fully coupled to `privilege_gain`

## 14.3 Z3 limitations

- Propositional snapshot only — no traces, time, or state
- Implication is relative to declared encoding, not full sandbox semantics
- One counterexample model among possibly many
- `model_completion=True` may set irrelevant atoms

## 14.4 Structural lattice limitations

- Only STRICT intent names trigger weakening detection
- Partial constraints like `readonly_root_fs` may evade structural diff
- Severity labels are heuristics, not security ratings
- Lattice edits change structural behaviour independently of Z3

## 14.5 Contradictory stakeholder intent

SpecGap compares downstream layers **to stated intent**. It does not adjudicate whether intent is internally contradictory, complete, or desirable. Conflicting human requirements appear as extracted constraints; resolution is a stakeholder process, not a SpecGap verdict.

## 14.6 Deployment drift

Written specifications can align while deployed enforcement diverges. SpecGap inspects supplied text only. Configuration management, live policy drift, and build pipeline errors are out of scope.

## 14.7 Reproducibility scope

Determinism holds for `extractor=rule` with pinned dependencies. Fuzzy/LLM paths, optional API responses, and author-edited input JSON without version control may differ between runs.

## 14.8 Trust-boundary limitations

Preserving disagreement does not automatically resolve it. Reviewers must interpret disagreement using TCB docs. Agreement does not imply runtime safety. PASS means no detected divergence in the abstract model over extracted constraints — nothing stronger.

[PAGE BREAK]

# 15. Reproducibility

## 15.1 Verification record

| Check | Result |
| --- | --- |
| `pytest` | **41/41 passed** |
| Z3 in tests | Not mocked |
| Python | 3.10+ required (`pyproject.toml`) |
| Reference hash | `8f2a1c9d4e7b3065a1f0c8d2e9b4a7f1` |

```bash
cd specgap
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
pytest -q
python -m specgap.cli examples/sandbox_no_network.json --out reports/demo_report.md
python -m specgap.cli examples/06_triangulation_disagreement.json --out reports/06_triangulation_disagreement_report.md
python -m specgap.cli examples/05_candidate_policy_ranking.json --evaluate-candidates --out reports/05_candidate_evaluation_report.md
python3 specgap-mcp/smoke_test.py
```

## 15.2 Artifact inventory

| Artifact | Path | Role |
| --- | --- | --- |
| Core package | `specgap/` | Extraction, diff, Z3, triangulation, reporter |
| CLI | `python -m specgap.cli` | Primary entry point |
| Examples | `examples/*.json` | Deterministic fixtures |
| Reference reports | `reports/demo_report.md`, `reports/05_candidate_evaluation_report.md` | Regenerable baselines |
| Assurance docs | `docs/SPECIFICATION.md`, `docs/TCB.md`, `docs/ENCODING.md`, `docs/ASSURANCE_BOUNDARY.md` | Normative bounds |
| MCP wrapper | `specgap-mcp/` | stdio tool server |
| Demo site | `demo-site/out/` | Static export — no live execution |
| Tutorials | `tutorials/*.md` | Verified walkthroughs |
| This report | `submission/SPECGAP_FINAL_REPORT.md` | Submission packet |

## 15.3 No telemetry

The core CLI, pytest suite, MCP smoke test, and static demo export do not emit telemetry. Reviewers can audit runs entirely offline.

## 15.4 No live execution in demo path

The static demo site presents scenario inputs, extracted constraints, engine outputs, and counterexamples from fixtures. It does not build containers, invoke BoxArena, or execute sandboxed code during review.

[PAGE BREAK]

# 16. Future Work

Possible directions — not commitments:

| Direction | Rationale |
| --- | --- |
| Richer vocabularies | Reduce silent extraction omission |
| Realizability checking | Connect abstract assignments to feasible runtime traces |
| Additional heterogeneous mechanisms | e.g. syscall surface parsers, policy normalisers — each preserved independently |
| Assumption registries | Explicit linkage between extracted constraints and stakeholder assumptions |

Scope discipline should remain: bounded artifacts over expanding claims.

### Future Directions — Heterogeneous Formal Assurance

The current implementation demonstrates disagreement preservation between structural divergence analysis and SMT-based implication checking. The architectural principle generalises beyond these two mechanisms.

Future extensions could preserve disagreement across heterogeneous formal-methods systems, including theorem provers, model checkers, type systems, and proof-producing analyzers operating over the same extracted specification layers. In such a configuration, disagreement between mechanisms would itself become a first-class assurance artefact rather than an aggregation failure to be hidden.

This direction is particularly relevant for theorem-prover correctness and semantic transformation boundaries, where elaboration systems, macro expansion, extraction pipelines, and runtime lowering stages may preserve proof validity while introducing semantic drift between layers of interpretation.

SpecGap does not currently implement these capabilities. The present system is intentionally bounded to structural divergence analysis and SMT implication checking over an abstract sandbox model. The broader contribution is the preservation discipline itself: heterogeneous assurance mechanisms should expose disagreement explicitly rather than collapse conflicting evidence into a single confidence signal.

[PAGE BREAK]

# 17. Related Work

## 17.1 GSN / CAE lineage

Goal Structuring Notation (GSN) and Claims-Argument-Evidence (CAE) frameworks encourage explicit argument structure and evidence linkage. SpecGap is operational rather than notational: it emits machine-checkable implication failures and counterexamples over a declared model, not a full safety case graph.

## 17.2 SMT counterexample lineage

SMT solvers have long been used to find counterexamples to verification conditions. SpecGap uses Z3 similarly — but over a **hand-declared propositional sandbox abstraction**, not a program semantics. Counterexamples are evidence of specification implication failure, not bug witnesses in compiled code.

## 17.3 Heterogeneous evidence

Assurance cases often combine testing, analysis, and review. SpecGap institutionalises **non-collapse**: structural and SMT mechanisms remain visible when they disagree, aligning with heterogeneous evidence practice without pretending to solve fusion.

## 17.4 Formal-methods pipelines that collapse disagreement

Many toolchains surface a single "verified" bit after discharging proof obligations. SpecGap deliberately avoids that aggregation. Positioning: **small, bounded, operational artifact** for pre-runtime specification divergence — not a theorem prover for infrastructure, not a replacement for adversarial runtime evaluation.

[PAGE BREAK]

# 18. Conclusion

Specification assurance fails quietly when layered documents drift and when independent checks are merged into false confidence. SpecGap extracts bounded constraints, compares stakeholder intent against formalised policy and implementation claims, checks implication over an abstract sandbox model, and **preserves disagreement** between structural analysis and Z3 outcomes.

SpecGap does not verify runtime systems. It does not prove correctness. It does not certify sandboxes. It produces replayable evidence that localises specification divergence before build and adversarial evaluation — and it keeps heterogeneous signals visible when they conflict.

Within its trust boundary, a clean result means no divergence detected over extracted constraints in the abstract model. Outside that boundary, runtime confinement remains the responsibility of enforcement layers and empirical evaluation such as BoxArena.

> **SpecGap preserves disagreement between independent assurance mechanisms instead of collapsing conflicting evidence into false confidence.**

[PAGE BREAK]

# Appendix A — Constraint Vocabulary Reference

| Constraint | Informal meaning | Z3 formula (permitted behaviour) |
| --- | --- | --- |
| `no_network` | No network access | `¬network_send` |
| `localhost_only` | If network used, localhost only | `network_send → dest_localhost` |
| `readonly_fs` | No filesystem writes | `¬fs_write` |
| `readonly_root_fs` | Writes only to `/tmp` if any | `fs_write → write_tmp` |
| `write_allowed` | Writes permitted (vacuous) | `true` |
| `no_privilege_escalation` | No privilege gain | `¬privilege_gain` |
| `setuid_allowed` | Privilege via setuid if gained | `(privilege_gain → setuid_exec) ∧ …` |
| `no_cap_sys_admin` | CAP not exercised | `¬cap_sys_admin` |

Full table: `docs/ENCODING.md`.

[PAGE BREAK]

# Appendix B — Artifact Inventory

See Section 15.2 for the complete inventory. Submission reviewers should begin with:

1. `README.md` — operational overview
2. `docs/SPECIFICATION.md` — correctness target
3. `docs/TCB.md` — trusted computing base
4. `examples/sandbox_no_network.json` — agreed disagreement (network)
5. `examples/06_triangulation_disagreement.json` — preserved disagreement (filesystem)
6. `pytest -q` — 41/41

[PAGE BREAK]

# Appendix C — Command Reference

```bash
# Standard triple analysis
python -m specgap.cli examples/sandbox_no_network.json --out reports/demo_report.md

# Triangulation disagreement
python -m specgap.cli examples/06_triangulation_disagreement.json \
  --out reports/06_triangulation_disagreement_report.md

# Candidate evaluation
python -m specgap.cli examples/05_candidate_policy_ranking.json \
  --evaluate-candidates --out reports/05_candidate_evaluation_report.md

# BoxArena pre-flight (advisory)
python -m specgap.cli examples/boxarena_preflight_divergence.json \
  --boxarena-preflight \
  --evidence-out reports/boxarena_preflight_evidence.json

# Test suite
pytest -q

# MCP smoke test
python3 specgap-mcp/smoke_test.py
```

---

*End of submission report.*
