# Tutorial 1: Detecting a Semantic Gap

This tutorial walks through the core SpecGap workflow: three specification layers, constraint extraction, and Z3 implication checking over an abstract sandbox model.

**Prerequisites:** Python 3.10+. From the Omega repository root:

```bash
cd specgap
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

On system Python with PEP 668 errors, the venv step is required (see README **Known setup issues**).

---

## Background

SpecGap compares three layers of a sandbox specification:

1. **Stakeholder intent** — what was asked for in plain language
2. **Formalized policy** — what was written into the policy document
3. **Implementation claim** — what the runtime or deployment claims to enforce

Each layer is parsed into canonical constraints (`no_network`, `localhost_only`, …). SpecGap then asks Z3 whether downstream layers **imply** the upstream intent within a small propositional model of sandbox behavior.

A failed implication check means: there exists a behavior permitted by the downstream layer that the intent forbids. Z3 returns a concrete counterexample over abstract variables — not a kernel exploit proof.

---

## The example

File: `examples/sandbox_no_network.json`

| Layer | Text (abbreviated) |
| --- | --- |
| Intent | "The sandbox must have **no network access**." |
| Policy | "Localhost connections are **allowed** for the metrics collector." |
| Implementation | "Only **loopback** traffic is permitted." |

Each rephrasing sounds reasonable in isolation. Together they may permit behavior the stakeholder believed was forbidden.

---

## Step 1 — Run the analysis

```bash
python -m specgap.cli examples/sandbox_no_network.json --out reports/01_semantic_gap_report.md
```

**Expected terminal output:**

```
SpecGap: analyzed 'Network-isolated analysis sandbox' (extractor: rule)
  semantic divergences: 3
  failed implication checks: 2 of 2
  report written to: reports/01_semantic_gap_report.md
```

Open `reports/01_semantic_gap_report.md` for the full report.

---

## Step 2 — Inspect extracted constraints

In the report, find **Extracted Constraints**:

```
**Stakeholder Intent**
- `no_network` — No network access [network/strict, via rule]

**Formalized Policy**
- `localhost_only` — Localhost/loopback network allowed [network/partial, via rule]

**Implementation Claim**
- `localhost_only` — Localhost/loopback network allowed [network/partial, via rule]
```

### What happened?

The rule extractor mapped the intent phrase "no network access" to the strict atom `no_network`. The policy and implementation both mention localhost/loopback, which maps to the weaker atom `localhost_only`.

Structural comparison flags this as a **weakened constraint**: the downstream layers express a partial network permission where the intent expressed a strict prohibition.

---

## Step 3 — Read the Z3 implication check

In **Z3 Formal Check**, SpecGap asks whether each downstream layer implies the intent constraints. For the negated query, Z3 returns `sat` when a permitted-but-forbidden behavior exists.

**Expected excerpt (Formalized Policy ⇒ Stakeholder Intent):**

```
- **Result: implication FAILS.** Z3 returned `sat` for the negation: there is a behavior
  permitted by Formalized Policy that Stakeholder Intent forbids.
- Violated target constraint(s): `no_network`

Counterexample behavior:
- `network_send = true` — a network connection is opened
- `dest_localhost = true` — the connection destination is localhost / loopback
```

The same counterexample appears for **Implementation Claim ⇒ Stakeholder Intent**.

### What happened?

Within SpecGap's abstract sandbox model, `localhost_only` permits `network_send = true` when `dest_localhost = true`. The intent constraint `no_network` forbids any network send. Therefore the policy does not imply the intent — Z3 constructs a satisfying assignment demonstrating the gap.

This is a **semantic divergence**: the words changed ("no network" → "localhost allowed" → "loopback permitted"), but the extracted constraints no longer nest correctly.

---

## Why this is semantic divergence (not a syntax error)

- The JSON is valid and each sentence is grammatically fine.
- A reviewer reading only the policy might agree that blocking external egress while allowing localhost is sensible engineering.
- The stakeholder reading only the intent might believe *all* network I/O is forbidden, including loopback.
- SpecGap does not adjudicate which reading is "correct." It reports that the extracted constraints from the three layers are not in an implication relationship.

Localhost is still network access in the abstract model. The counterexample is minimal and inspectable: two boolean variables, one violating assignment.

---

## What SpecGap is NOT proving

- SpecGap does **not** prove the sandbox implementation is insecure or exploitable.
- SpecGap does **not** model a real kernel, seccomp filter, or container runtime.
- SpecGap does **not** prove the stakeholder's intent was the right requirement.
- A passing implication check would mean *no divergence was detected over extracted constraints in the abstract model* — not that the specification is correct.

Counterexamples are illustrative behaviors in the abstraction, not exploit proofs.

---

## Limitations

- Extraction is vocabulary-bound. Phrasing outside the rule set is silently not extracted (see Tutorial 2).
- The Z3 layer checks whatever constraints extraction produced. Wrong extraction → wrong obligation, checked faithfully.
- Three fixed layers only; no version history or multi-document specs.
- Severity labels in the structural diff are heuristics over constraint kinds, not a risk score.

---

## Next step

- Run Tutorial 2 to see what happens when rule extraction misses paraphrased intent ("air-gapped").
- Inspect `examples/sandbox_readonly_fs.json` and `examples/syscall_policy_mismatch.json` for filesystem and privilege divergence patterns.
- Extend the rule vocabulary in `specgap/extractor.py` if your domain uses phrasing not yet covered — then re-run implication checks unchanged.
