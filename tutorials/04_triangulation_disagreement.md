# Tutorial 4: When Structural Diff and Z3 Disagree

This tutorial demonstrates **triangulation disagreement**: the structural weakening lattice reports no divergence, but Z3 finds an implication failure. That is intentional — the two mechanisms operate over different abstractions.

**Prerequisites:** Tutorials [1](01_detecting_a_semantic_gap.md) and the triangulation section in any recent report. From the repository root:

```bash
source .venv/bin/activate   # if using a venv
```

---

## Background

SpecGap runs two **independent** checks over extracted constraints:

1. **Structural diff** — compares constraint *names* using a hand-authored `WEAKER_OF` lattice over **strict** intent obligations (`no_network`, `readonly_fs`, …).
2. **Z3 implication check** — asks whether downstream layers imply upstream intent in the **abstract propositional sandbox model** (`docs/ENCODING.md`).

They can disagree. Disagreement is **diagnostic information**, not a sign that one tool is broken. SpecGap preserves both signals rather than merging them into one verdict.

---

## The example

File: `examples/06_triangulation_disagreement.json`

| Layer | Text (abbreviated) |
| --- | --- |
| Intent | "The **root filesystem is read-only** per container policy." |
| Policy | "**Write access to /var** is allowed for application logs." |
| Implementation | Same as policy |

Extracted constraints:

| Layer | Constraint |
| --- | --- |
| Intent | `readonly_root_fs` (partial — not in the STRICT lattice) |
| Policy | `write_allowed` |
| Implementation | `write_allowed` |

**Why structural diff is silent:** `readonly_root_fs` is a *partial* filesystem constraint. The structural pass only applies the weakening lattice to **strict** intent names. It does not currently map `write_allowed` as a weakening of `readonly_root_fs`.

**Why Z3 fails:** In the propositional model, `write_allowed` is vacuous (permits any write). The intent's `readonly_root_fs` requires writes to stay under `/tmp`. Z3 finds a counterexample: `fs_write = true`, `write_other = true`.

---

## Step 1 — Run the analysis

```bash
python -m specgap.cli examples/06_triangulation_disagreement.json \
  --out reports/06_triangulation_disagreement_report.md
```

**Expected terminal output (abridged):**

```
SpecGap: analyzed 'Partial read-only root vs general write permission' (extractor: rule)
  triangulation: disagreement between structural diff and Z3
  semantic divergences: 0
  failed implication checks: 2 of 2
  report written to: reports/06_triangulation_disagreement_report.md
```

Note **`semantic divergences: 0`** alongside **`failed implication checks: 2`** and **`triangulation: disagreement`**.

---

## Step 2 — Read the Triangulation Summary

In the report, find **Triangulation Summary**:

| Layer | Structural | Z3 implication | Agreement | Counterexample |
| --- | --- | --- | --- | --- |
| Formalized Policy | no_divergence_detected | fails | **no** | yes |
| Implementation Claim | no_divergence_detected | fails | **no** | yes |

**Structural says OK. Z3 says FAIL. Agreement is no.**

This is the disagreement-preserving design: heterogeneous evidence stays visible.

---

## Step 3 — Inspect the counterexample

Under **Z3 Formal Check** / **Counterexample**:

```
- `fs_write = true` — a filesystem write occurs
- `write_other = true` — the write target is outside /tmp
```

This behavior is permitted by `write_allowed` but violates the intent's partial read-only encoding.

---

## What this is NOT

- **Not** proof that the structural layer is wrong — it applies a deliberate, bounded name-level lattice.
- **Not** proof that Z3 is always right — the model is an abstract sandbox, not a kernel.
- **Not** cross-validation or consensus — SpecGap does not vote between mechanisms.
- **Not** runtime verification — no container was built or executed.

---

## Limitations

- The gap exists because `readonly_root_fs` is outside the STRICT set; extending `WEAKER_OF` would change structural behavior (out of scope for this tutorial).
- Rule extraction must recognize both phrases; unrecognized text is silently omitted.
- Counterexamples are illustrative behaviors in the abstract model, not exploit proofs.

---

## Next steps

- Compare with [Tutorial 1](01_detecting_a_semantic_gap.md) where structural diff and Z3 **agree** (both detect network drift).
- Read [`docs/TCB.md`](../docs/TCB.md) for trusted components and [`docs/ENCODING.md`](../docs/ENCODING.md) for atom semantics.
