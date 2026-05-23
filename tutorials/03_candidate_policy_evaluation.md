# Tutorial 3: Candidate Policy Evaluation

This tutorial covers **spec-conditioned candidate evaluation**: one stakeholder intent, multiple candidate policies, mechanical discrimination by implication failure count.

**Prerequisites:** Tutorials 1–2. Venv active with requirements installed.

---

## Background

When several policy drafts exist, SpecGap can evaluate each candidate independently against the same extracted intent constraints.

```bash
python -m specgap.cli <candidate-spec.json> --evaluate-candidates [--out report.md]
```

For each candidate, SpecGap:

1. Extracts constraints from the candidate policy text (same rule or fuzzy mode as elsewhere).
2. Checks whether those constraints **imply** each strict intent constraint in the abstract sandbox model.
3. Records PASS (all implications hold) or FAIL (≥1 counterexample).

Candidates are ordered mechanically: passing first, then ascending implication-failure count, ties preserving input order.

**This is not heuristic scoring.** There is no quality leaderboard, no weighted rubric, no security grade. The ordering reports only how many intent constraints each candidate failed to preserve over extracted atoms.

---

## The example

File: `examples/05_candidate_policy_ranking.json`

**Stakeholder intent (abbreviated):**

> No network access of any kind. Process must never escalate privilege.

**Candidates:**

| ID | Label | Deliberate weakness |
| --- | --- | --- |
| A | Reference policy (intent-aligned wording) | Author label — SpecGap only checks extracted constraints |
| B | Localhost network exception | Allows localhost for metrics |
| C | Setuid execution allowance | Permits setuid maintenance helper |

---

## Step 1 — Run candidate evaluation

```bash
cd specgap
python -m specgap.cli examples/05_candidate_policy_ranking.json --evaluate-candidates --out reports/03_candidate_report.md
```

**Expected terminal output:**

```
SpecGap: evaluated 3 candidate(s) for 'Candidate sandbox policies for a network-isolated, privilege-bounded cell' (extractor: rule)
  Candidate A: PASS
  Candidate B: FAIL (1 implication failure(s))
  Candidate C: FAIL (1 implication failure(s))
  candidate order (fewest implication failures first): A > B > C
  report written to: reports/03_candidate_report.md
```

---

## Step 2 — Inspect extracted intent constraints

**Expected excerpt from the report:**

```
Extracted intent constraints — the specification every candidate is evaluated against:

- `no_network` — No network access [network/strict, via rule]
- `no_privilege_escalation` — No privilege escalation [privilege/strict, via rule]
```

Every candidate is checked against this same pair.

---

## Step 3 — Read validation outcomes

**Expected excerpt (Validation Outcomes table):**

```
| Candidate | Result | Implication failures | Violated intent constraint(s) |
| --- | --- | --- | --- |
| Candidate A | PASS | 0 | — |
| Candidate B | FAIL | 1 | `no_network` |
| Candidate C | FAIL | 1 | `no_privilege_escalation` |
```

### What happened?

- **Candidate A** extracts `no_network` and `no_privilege_escalation`. Z3 finds no behavior permitted by A that violates the intent atoms → **PASS**.
- **Candidate B** extracts `localhost_only` instead of strict `no_network`. Z3 returns a counterexample for `no_network` → **FAIL (1)**.
- **Candidate C** extracts `setuid_allowed`, breaking `no_privilege_escalation` → **FAIL (1)**.

B and C each fail exactly one intent constraint, so they tie on failure count. Input order breaks the tie: B before C.

---

## Step 4 — Inspect counterexamples

**Candidate B — network divergence:**

```
- `network_send = true` — a network connection is opened
- `dest_localhost = true` — the connection destination is localhost / loopback
```

Same abstract counterexample as Tutorials 1 and 2: localhost permission does not imply strict no-network in the model.

**Candidate C — privilege divergence:**

```
- `privilege_gain = true` — the process gains elevated privileges
- `setuid_exec = true` — a setuid binary is executed
```

Allowing setuid execution permits privilege gain via the setuid vector in the abstract privilege model, violating `no_privilege_escalation`.

### What happened?

Each FAIL row links a **specific intent atom** to a **concrete satisfying assignment** in the abstraction. The failures are incomparable in "severity" — B breaks network intent, C breaks privilege intent. SpecGap does not rank B vs C; it reports both as single-failure candidates.

---

## What this is NOT

| Misread | Actual behavior |
| --- | --- |
| "Candidate A is proven secure" | A **passed implication checks over extracted constraints** in the abstract model |
| "B is worse than C because it ranked first among failures" | Ordering is **mechanical tie-breaking**, not a quality judgment |
| "SpecGap picked the best policy" | SpecGap **discriminates** supplied candidates; it does not synthesize or repair policies |
| "FAIL means exploitable" | FAIL means **implication failure in the abstraction**, not a confirmed runtime bug |

Passing means: no semantic divergence detected within the abstract sandbox model and extracted constraints. **It does not prove semantic correctness.**

---

## Implementation discrimination vs scoring

SpecGap performs **implication-failure comparison**:

```
candidate order (fewest implication failures first): A > B > C
```

Interpretation:

- **A (0 failures)** — extracted candidate constraints imply both intent atoms
- **B (1 failure)** — localhost exception breaks `no_network`
- **C (1 failure)** — setuid allowance breaks `no_privilege_escalation`

No numeric score beyond the failure count. No weighting of network vs privilege. Researchers extending the system should preserve this discipline if they add reporting — aggregation is easy to misread as certification.

---

## Limitations

- Candidates are only as complete as extraction. A policy could PASS by omission if the extractor misses a weakening phrase.
- Single intent string; no multi-stakeholder conflict resolution.
- Abstract model only — not seccomp, not cgroups, not capability bounding as implemented in Linux.
- `--extractor fuzzy` applies to intent and candidate extraction alike; fuzzy intent atoms inherit the same human-review requirement as Tutorial 2.
- SpecGap does not generate alternative policies or suggest fixes.

---

## Next step

- Author a new `examples/` JSON with your own intent and 2–3 draft policies; run `--evaluate-candidates` and inspect counterexamples.
- Wire candidate evaluation into a pre-deploy checklist (SpecGap as pre-flight spec check; runtime testing remains separate).
- See `specgap/candidate_eval.py` and `tests/test_candidate_eval.py` for the evaluation loop before adding features.
- Read `docs/BOXARENA_POSITIONING.md` for how spec checking complements adversarial sandbox testing.
