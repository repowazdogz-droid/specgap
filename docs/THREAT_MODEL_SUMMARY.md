# SpecGap threat model summary

Compact threat model for reviewers. Full boundary discipline: [`ASSURANCE_BOUNDARY.md`](ASSURANCE_BOUNDARY.md). Correctness target: [`SPECIFICATION.md`](SPECIFICATION.md).

SpecGap generates **bounded evidence** about **extracted constraints** in an **abstract model**. This document lists what that evidence can and cannot support.

---

## Assets

| Asset | Why it matters |
| --- | --- |
| **Stakeholder intent** | Upstream obligation the stack must preserve |
| **Downstream specs** | Policy, implementation claims, candidates |
| **Extracted constraints** | Machine-checkable slice of the above |
| **Evidence artifacts** | Reports and JSON chains used for review and replay |
| **Reviewer judgment** | Final interpretation stays human |

---

## What SpecGap can detect (inside TCB)

| Class | Example | Mechanism |
| --- | --- | --- |
| **Downstream weakening** | `no_network` → `localhost_only` | Structural lattice + Z3 implication |
| **Implication failure** | Policy permits behavior intent forbids in the model | Z3 counterexample assignment |
| **Unmatched implementation claims** | Permission in claim not implied by intent | Structural / implication paths |
| **Internal inconsistency** | Unsatisfiable constraint set in a layer | Z3 sat check |
| **Extraction failure** | Zero intent constraints extracted | Explicit flag; checks skipped |
| **Mechanism disagreement** | Structural silent, Z3 fails | Triangulation row preserved |
| **Candidate ranking signal** | Which candidate fails implication vs intent | Per-candidate evaluation mode |

Detection means: **a documented check fired on extracted constraints in the abstract model**. It is not a runtime exploit proof.

---

## What SpecGap cannot detect

| Class | Why not |
| --- | --- |
| **Runtime escape or mis-enforcement** | No execution, no kernel, no container |
| **Implementation bugs in enforced code** | Spec may be faithful; build may be wrong (BoxArena territory) |
| **Complete English semantics** | Extraction is partial by design |
| **Adversarial prose not in vocabulary** | Unmatched phrases are omitted, not interpreted |
| **Side channels, timing, covert channels** | Not in propositional sandbox atoms |
| **Social engineering or operator override** | Outside written spec layers |
| **Correctness of stakeholder intent** | Tool checks preservation, not wisdom |
| **Global security of a deployment** | No end-to-end system model |

---

## Limitation classes

### Symbolic-model limitations

- Behavior is encoded as **propositional atoms** (e.g. `network_send`, `dest_localhost`), not syscalls or packets.
- Domain axioms are **declared**, not derived from Linux or OCI specs.
- Counterexamples are **assignments in the model**, not packet captures or strace logs.
- Vacuous or incomplete formulas can yield misleading passes (see [`ENCODING.md`](ENCODING.md)).

### Runtime gap

SpecGap operates on **specifications**. Even a perfect implication pass does not predict:

- Seccomp profile matches policy file
- Namespace configuration matches claim
- MCP server honors tool allowlists at call time

Complement with runtime tests, enforcement audits, and adversarial evaluation (e.g. BoxArena).

### Parser / modeling gap

| Stage | Limitation |
| --- | --- |
| **Rule extractor** | Fixed phrase vocabulary; silent omission of unmatched text |
| **Fuzzy extractor** | Advisory, non-deterministic; not default TCB path |
| **Weakening lattice** | Hand-authored; partial constraints may evade `STRICT` / `WEAKER_OF` paths |
| **Layer pairing** | Wrong layer order in JSON produces wrong obligation direction |

**Attack:** Author writes intent that **reads** strict but **extracts** weak or empty — surfacing extraction failure is the defense; silent pass is the failure mode to prevent.

### Human interpretation gap

| Misread | Reality |
| --- | --- |
| "PASS" = safe to deploy | Pass = no violation in model for extracted constraints |
| "Counterexample" = exploit | Counterexample = abstract behavior assignment |
| "Agreement" = double confirmation | Agreement = two bounded mechanisms aligned **in TCB** |
| "Disagreement" = tool bug | Disagreement = diagnostic signal (lattice vs encoding gap) |
| Single headline verdict | Reports contain multiple independent rows |

### Adversarial specification attacks

Patterns SpecGap is designed to **partially** address (with TCB limits):

| Attack | SpecGap response | Residual risk |
| --- | --- | --- |
| **Silent weakening across layers** | Implication + structural diff | Lattice / encoding gaps |
| **Permission laundering** | Claim-not-implied detection | Extraction misses new phrasing |
| **Paraphrase to evade extractor** | Extraction failure or weak extraction | Novel prose outside vocabulary |
| **Obligation splitting** | May appear as clean per-layer passes | Needs multi-layer composition research |
| **False precision** (over-formal policy vs vague intent) | May extract asymmetric strength | Human review of extraction lists |
| **Consensus laundering** (merge signals externally) | Triangulation resists internal merge | External dashboards may still collapse |

SpecGap does **not** stop a malicious author from publishing a spec. It helps **reviewers** find drift and document evidence.

---

## Trust boundaries (summary)

```
  Written spec layers
        │
        ▼
  ┌─────────────────────────────────────┐
  │  SpecGap TCB                         │
  │  extract → structural → Z3 → report  │
  └─────────────────────────────────────┘
        │
        ▼
  Replayable evidence (bounded claims)
        │
        ▼
  Human review ──► build / deploy / runtime assurance (out of scope)
```

**Trusted (for interpretation):** rule extractor (default), lattice, encoding, Z3 queries, deterministic reporter.

**Not trusted:** English prose, optional fuzzy extraction, external merge of verdicts, runtime stack.

---

## Reviewer checklist

Before treating output as actionable:

1. List **extracted constraints** per layer — is intent nonempty?
2. Read **triangulation** — any Agreement = no rows?
3. If Z3 failed, inspect **counterexample atoms** — do they map to real concerns?
4. Ask whether **omitted phrases** could change the conclusion.
5. Separate **spec alignment evidence** from **runtime security claims**.

---

## Related documents

- [`TCB.md`](TCB.md) — trusted / partially trusted components
- [`ENCODING.md`](ENCODING.md) — behavior atoms and known vacuities
- [`BOXARENA_POSITIONING.md`](BOXARENA_POSITIONING.md) — runtime complement
- [`WHY_DISAGREEMENT_MATTERS.md`](WHY_DISAGREEMENT_MATTERS.md) — why signals stay separate
