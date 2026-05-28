# SpecGap versioning and scope

**Package:** `0.1.0` · **Policy effective:** 2026-05-25

Defines how conceptual changes relate to version numbers and public claims. SpecGap remains a **bounded assurance/replay research object** — not an expanding agent governance platform.

---

## Scope boundaries (invariant)

These do not relax without explicit boundary-doc revision and a **major** version bump:

1. **No hidden runtime guarantees** — all claims stop at written spec layers and the abstract model.
2. **No silent platform expansion** — MCP wrappers, BoxArena hooks, and fuzzy extraction do not widen assurance without updating [`ASSURANCE_BOUNDARY.md`](ASSURANCE_BOUNDARY.md).
3. **Replayability** — default `--extractor rule` stays deterministic for a pinned input + dependency set.
4. **Disagreement-first thesis** — triangulation outcomes are not merged into a single authoritative score.

---

## Breaking conceptual change (major bump: `1.0.0`, `2.0.0`, …)

Requires **major** version increment and changelog note:

| Change class | Example |
| --- | --- |
| **Assurance boundary moved** | Claiming runtime verification, compliance, or autonomous gating |
| **Default extractor behavior** | `rule` mode becomes non-deterministic or changes constraint mapping without migration |
| **Triangulation semantics** | Disagreement collapsed into one PASS/FAIL; agreement row removed |
| **TCB redefinition** | Atoms/axioms change meaning of existing counterexamples without fixture migration |
| **Report contract** | Sections that replay diffs depend on removed or renamed without version tag |
| **Implication direction** | Downstream→upstream check logic inverted |

Breaking changes require: updated [`TCB.md`](TCB.md) / [`ENCODING.md`](ENCODING.md), regenerated golden reports, and note in [`STABILITY_STATUS.md`](STABILITY_STATUS.md).

---

## Non-breaking change (minor: `0.2.0`, …)

**Minor** bump appropriate for:

| Change class | Example |
| --- | --- |
| **New optional constraint phrases** | Additional rule patterns with tests |
| **Lattice extension** | New `WEAKER_OF` edges with fixture coverage |
| **New examples** | Operational or core JSON fixtures |
| **New CLI flags (opt-in)** | Behind explicit flags; default path unchanged |
| **Report additive sections** | New rows/sections that do not alter existing semantics |

Must preserve: default quickstart repro, disagreement preservation, assurance boundary statements.

---

## Documentation refinement (patch: `0.1.1`, …)

**Patch** bump (or doc-only commit if no package release) for:

| Change class | Example |
| --- | --- |
| **Onboarding / outreach docs** | DEMO_PATHS, OUTREACH_PACKETS, anti-patterns |
| **Clarifications** | Wording that narrows claims, not widens them |
| **Diagrams / indexes** | EXAMPLE_INDEX, DIAGRAMS |
| **Typo fixes** | No semantic change |

Documentation that **widens** what SpecGap proves is **not** a refinement — treat as boundary violation; revert or major bump with boundary update.

---

## Pre-release (`0.x.y`)

While `0.x`: public API and report shape may still evolve, but **published freeze** ([`STABILITY_STATUS.md`](STABILITY_STATUS.md)) commits to:

- Bounded assurance claims
- Disagreement preservation
- Deterministic `rule` mode

`1.0.0` means: boundary docs, TCB, default pipeline, and triangulation contract treated as long-lived citation surface.

---

## What triggers a release tag

| Trigger | Action |
| --- | --- |
| Boundary or TCB change | Major + migration notes |
| New stable constraint vocabulary | Minor + tests + example if user-visible |
| Docs-only outreach/onboarding | Patch or docs commit |
| CI fix, no semantic change | Patch |

No release required for [`PUBLICATION_STATE.md`](PUBLICATION_STATE.md) inventory snapshots.

---

## Citation guidance

Include when citing results:

- Package version (`0.1.0`)
- `--extractor` mode (`rule` vs `fuzzy`)
- Input JSON path or hash
- Python + `z3-solver` versions

Do not cite SpecGap as "formal verification of [system X]" — cite **implication failure in the declared model for extracted constraints**.

---

## Related

| Doc | Role |
| --- | --- |
| [`STABILITY_STATUS.md`](STABILITY_STATUS.md) | What is stable / experimental / absent |
| [`PUBLICATION_STATE.md`](PUBLICATION_STATE.md) | What exists today |
| [`ASSURANCE_BOUNDARY.md`](ASSURANCE_BOUNDARY.md) | Hard limits |
