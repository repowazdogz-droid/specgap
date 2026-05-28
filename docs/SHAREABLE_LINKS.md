# SpecGap — shareable links

Curated entry map for fellowship applications, DMs, and “send me something” requests. All paths relative to repo root.

**Live repo:** [github.com/repowazdogz-droid/specgap](https://github.com/repowazdogz-droid/specgap)

---

## 2-minute intro

| Link | Why read this |
| --- | --- |
| [`docs/SPECGAP_ABSTRACT.md`](SPECGAP_ABSTRACT.md) | Paste-friendly summary (250–400 words) for forms and emails |
| [`docs/SPECGAP_FAQ.md`](SPECGAP_FAQ.md) | Nine common questions, one paragraph each |

---

## 5-minute technical read

| Link | Why read this |
| --- | --- |
| [`docs/SPECGAP_ONE_PAGE.md`](SPECGAP_ONE_PAGE.md) | Full problem + boundaries + quickstart on one screen |
| [`docs/REPLAYABLE_EVIDENCE_EXAMPLE.md`](REPLAYABLE_EVIDENCE_EXAMPLE.md) | One input JSON → FAIL report → replay `diff` |
| [`examples/sandbox_no_network.json`](../examples/sandbox_no_network.json) | Minimal spec triple to run locally |

**One command:**

```bash
python -m specgap.cli examples/sandbox_no_network.json --out /tmp/specgap_demo.md
```

---

## Operational examples

| Link | Why read this |
| --- | --- |
| [`docs/OPERATIONAL_EXAMPLES.md`](OPERATIONAL_EXAMPLES.md) | Why MCP / multi-agent / config drift map onto the TCB |
| [`examples/operational/README.md`](../examples/operational/README.md) | Index of three replayable scenarios |
| [`examples/operational/02_multi_agent_policy_divergence/`](../examples/operational/02_multi_agent_policy_divergence/) | Best demo of triangulation **disagreement** |

---

## Assurance boundaries

| Link | Why read this |
| --- | --- |
| [`docs/ASSURANCE_BOUNDARY.md`](ASSURANCE_BOUNDARY.md) | Hard limits on what reports may claim |
| [`docs/THREAT_MODEL_SUMMARY.md`](THREAT_MODEL_SUMMARY.md) | In-scope vs out-of-scope detection classes |
| [`docs/TCB.md`](TCB.md) | What you must trust to interpret a result |
| [`docs/WHY_DISAGREEMENT_MATTERS.md`](WHY_DISAGREEMENT_MATTERS.md) | Why triangulation is not merged into one score |

---

## Architecture

| Link | Why read this |
| --- | --- |
| [`docs/ARCHITECTURE_OVERVIEW.md`](ARCHITECTURE_OVERVIEW.md) | Pipeline + boundary diagrams (visual-first) |
| [`docs/ENCODING.md`](ENCODING.md) | Behavior atoms and formulas (for FM readers) |
| [`docs/SPECIFICATION.md`](SPECIFICATION.md) | Correctness target and check definitions |

---

## Doctrine relationship (OMEGA Lab)

| Link | Why read this |
| --- | --- |
| [`docs/SPECGAP_POSITIONING.md`](SPECGAP_POSITIONING.md) | Assurance layer role in the six-layer trunk |
| [omega-contracts TRUST_STACK](https://github.com/repowazdogz-droid/omega-contracts/blob/main/docs/TRUST_STACK.md) | How repos compose into `OmegaRecord` slots |
| [OMEGA Lab profile](https://github.com/repowazdogz-droid/repowazdogz-droid) | Public trunk orientation (not a product pitch) |
| [omega-lean-proof](https://github.com/repowazdogz-droid/omega-lean-proof) | Doctrine / Lean scaffolding — separate from SpecGap checks |

---

## Suggested paste for a DM

```
SpecGap — pre-runtime layered spec divergence checks with replayable evidence.
Abstract: github.com/repowazdogz-droid/specgap/blob/main/docs/SPECGAP_ABSTRACT.md
FAQ: …/docs/SPECGAP_FAQ.md
5-min walkthrough: …/docs/REPLAYABLE_EVIDENCE_EXAMPLE.md
```

Replace `…` with the branch path you want the reader to land on.
