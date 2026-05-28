# Replayable evidence — one example end-to-end

Walkthrough of the canonical quickstart: [`examples/sandbox_no_network.json`](../examples/sandbox_no_network.json). Total time: ~3 minutes.

---

## 1. Input specs

Three layers in one JSON file:

```json
{
  "title": "Network-isolated analysis sandbox",
  "stakeholder_intent": "The sandbox must have no network access. Code running inside it cannot reach the internet or any host.",
  "formalized_policy": "Network egress is restricted: localhost connections are allowed for the local metrics collector.",
  "implementation_claim": "The runtime blocks all external network destinations; only loopback (localhost) traffic is permitted.",
  "expected_issue": "The policy and implementation permit localhost network traffic, which the stakeholder intent ('no network access') appears to forbid. Localhost is still network access."
}
```

`expected_issue` is an **author annotation** — SpecGap does not treat it as a verdict.

---

## 2. Run

```bash
python -m specgap.cli examples/sandbox_no_network.json --out reports/demo_report.md
```

Terminal:

```
SpecGap: analyzed 'Network-isolated analysis sandbox' (extractor: rule)
  triangulation: structural diff and Z3 agree
  semantic divergences: 3
  failed implication checks: 2 of 2
  report written to: reports/demo_report.md
```

---

## 3. Normalization (extracted constraints)

| Layer | Extracted |
| --- | --- |
| Intent | `no_network` |
| Policy | `localhost_only` |
| Claim | `localhost_only` |

Rule-based extraction matched fixed phrases ("no network", "localhost"). Unmatched wording is omitted — not interpreted.

---

## 4. Implication result

SpecGap asks: does downstream **imply** upstream intent in the abstract model?

**Formalized Policy ⇒ Stakeholder Intent:** **FAIL**

```markdown
- Violated target constraint(s): `no_network`

Counterexample behavior:
- `network_send = true` — a network connection is opened
- `dest_localhost = true` — the connection destination is localhost / loopback
```

**Implementation Claim ⇒ Stakeholder Intent:** **FAIL** (same counterexample shape).

The counterexample is a **model assignment** — illustrative behavior inside the encoding, not a captured network packet or confirmed exploit.

---

## 5. Divergence finding (structural)

Structural diff also fires (triangulation **agrees** with Z3 here):

| Kind | Summary |
| --- | --- |
| `weakened_constraint` | `no_network` weakened to `localhost_only` in policy and claim |
| `claim_not_implied` | `localhost_only` permission not stated in strict intent |

Three structural divergences · 2/2 implication checks failed · 0 internally inconsistent layers.

---

## 6. Generated evidence artifact

Output file: `reports/demo_report.md` (or regenerate to any path with `--out`).

Report sections an independent reviewer uses:

| Section | Purpose |
| --- | --- |
| **Summary** | At-a-glance FAIL + triangulation state |
| **Triangulation Summary** | Structural vs Z3 per layer |
| **Extracted Constraints** | What entered the model |
| **Semantic Divergence** | Structural findings |
| **Z3 Formal Check** | Implication proofs + counterexamples |
| **Limitations** | Bounded claims restated |

Pre-checked copy in repo: [`reports/demo_report.md`](../reports/demo_report.md).

---

## 7. Replayability value

| Property | Why it matters |
| --- | --- |
| **Deterministic** | Same JSON + `--extractor rule` → same extraction and Z3 results |
| **Regenerable** | Reviewer clones repo, runs one command, compares reports |
| **Inspectable TCB** | Extraction rules, lattice, and encoding are source-visible |
| **No vendor attestation** | Evidence is a file on disk, not a platform badge |

**Replay test:**

```bash
python -m specgap.cli examples/sandbox_no_network.json --out /tmp/run1.md
python -m specgap.cli examples/sandbox_no_network.json --out /tmp/run2.md
diff /tmp/run1.md /tmp/run2.md   # expect no differences
```

When citing results, record: input path, `--extractor` mode, Python version, `z3-solver` version.

---

## What this walkthrough does NOT show

- Live sandbox execution or network probes
- Triangulation **disagreement** (see [`02_multi_agent_policy_divergence`](../examples/operational/02_multi_agent_policy_divergence/))
- Fuzzy/LLM extraction (`--extractor fuzzy`)
- Candidate policy ranking (`--evaluate-candidates`)

Next: [`OPERATIONAL_EXAMPLES.md`](OPERATIONAL_EXAMPLES.md) for operator-framed scenarios · [`ARCHITECTURE_OVERVIEW.md`](ARCHITECTURE_OVERVIEW.md) for full pipeline.
