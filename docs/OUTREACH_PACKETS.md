# SpecGap outreach packets

Audience-specific send guidance. One repo link is enough: [github.com/repowazdogz-droid/specgap](https://github.com/repowazdogz-droid/specgap). Paste block: [`SHAREABLE_LINKS.md`](SHAREABLE_LINKS.md).

---

## A. Formal methods researchers

| Field | Guidance |
| --- | --- |
| **What to send** | [`SPECGAP_ABSTRACT.md`](SPECGAP_ABSTRACT.md) + link to [`ENCODING.md`](ENCODING.md) + [`examples/sandbox_no_network.json`](../examples/sandbox_no_network.json) |
| **What NOT to send** | OMEGA Lean proof as if SpecGap is verified; hackathon submission pack; commercial compliance drafts |
| **3-file path** | 1. [`ARCHITECTURE_OVERVIEW.md`](ARCHITECTURE_OVERVIEW.md) · 2. [`TCB.md`](TCB.md) · 3. [`REPLAYABLE_EVIDENCE_EXAMPLE.md`](REPLAYABLE_EVIDENCE_EXAMPLE.md) |
| **Strongest angle** | Bounded implication checking + explicit TCB + triangulation that preserves mechanism disagreement |
| **Biggest skepticism** | "Toy propositional sandbox / fixed extractor — not real FM" |
| **Wrong framing** | "We formally verified agent safety" · "Kernel-level guarantees" |

**DM one-liner:** Pre-runtime layered spec implication checks with Z3 + structural triangulation; counterexamples are model assignments; TCB is documented.

---

## B. AI safety researchers

| Field | Guidance |
| --- | --- |
| **What to send** | [`SPECGAP_ABSTRACT.md`](SPECGAP_ABSTRACT.md) + [`WHY_DISAGREEMENT_MATTERS.md`](WHY_DISAGREEMENT_MATTERS.md) + [`EXAMPLE_INDEX.md`](EXAMPLE_INDEX.md) (multi-agent row) |
| **What NOT to send** | Alignment-solution language; MATS/AISI application PDFs unless they asked; runtime gate / P5 enforcement claims |
| **3-file path** | 1. [`SPECGAP_FAQ.md`](SPECGAP_FAQ.md) · 2. [`THREAT_MODEL_SUMMARY.md`](THREAT_MODEL_SUMMARY.md) · 3. [`examples/operational/02_multi_agent_policy_divergence/`](../examples/operational/02_multi_agent_policy_divergence/) |
| **Strongest angle** | Spec drift before deploy; disagreement preserved instead of collapsed oracle; falsifiable fixtures not leaderboard hype |
| **Biggest skepticism** | "Another governance wrapper / not eval-relevant" |
| **Wrong framing** | "Scalable oversight" · "Alignment infrastructure" · "Trustworthy AI" |

**DM one-liner:** Assurance evidence for layered spec divergence—useful where evals assume specs were faithful; bounded to extracted constraints; not an oversight product.

---

## C. Infrastructure / security engineers

| Field | Guidance |
| --- | --- |
| **What to send** | [`DEMO_PATHS.md`](DEMO_PATHS.md) (10-minute path) + [`EXAMPLE_INDEX.md`](EXAMPLE_INDEX.md) + one operational example link (MCP or config drift) |
| **What NOT to send** | Full repo tour; mcp-boundary-audit as public trunk; Immunefi / bounty artifacts as SpecGap proof |
| **3-file path** | 1. [`OPERATIONAL_EXAMPLES.md`](OPERATIONAL_EXAMPLES.md) · 2. [`REPLAYABLE_EVIDENCE_EXAMPLE.md`](REPLAYABLE_EVIDENCE_EXAMPLE.md) · 3. [`ASSURANCE_BOUNDARY.md`](ASSURANCE_BOUNDARY.md) |
| **Strongest angle** | Catch config/policy drift while health checks still pass; replayable Markdown evidence for review tickets |
| **Biggest skepticism** | "Doesn't touch prod / rule-based extraction too brittle" |
| **Wrong framing** | "Runtime MCP enforcement" · "Replaces pentest" · "Blocks deploy automatically" |

**DM one-liner:** Pre-runtime spec stack linter with Z3 implication failures + counterexamples—run locally in one command; not a WAF or runtime monitor.

---

## D. Governance / audit people

| Field | Guidance |
| --- | --- |
| **What to send** | [`SPECGAP_ABSTRACT.md`](SPECGAP_ABSTRACT.md) + [`ASSURANCE_BOUNDARY.md`](ASSURANCE_BOUNDARY.md) + [`SPECGAP_POSITIONING.md`](SPECGAP_POSITIONING.md) (OMEGA table only) |
| **What NOT to send** | EU AI Act / ISO mapping tables as "satisfies"; enterprise DPO outreach templates; pilot pricing |
| **3-file path** | 1. [`SPECGAP_FAQ.md`](SPECGAP_FAQ.md) · 2. [`THREAT_MODEL_SUMMARY.md`](THREAT_MODEL_SUMMARY.md) · 3. [`examples/operational/03_configuration_drift/`](../examples/operational/03_configuration_drift/) |
| **Strongest angle** | Evidence artifact for "did written layers still match intent?"—audit-friendly replay, explicit limits |
| **Biggest skepticism** | "Not a compliance engine / doesn't sign attestations" |
| **Wrong framing** | "Compliance automation" · "Certification layer" · "Satisfies Article X" |

**DM one-liner:** Review-support evidence for layered specs—not certification, not legal consent proof; reports state what was and wasn't checked.

---

## E. Potential collaborators

| Field | Guidance |
| --- | --- |
| **What to send** | [`RESEARCH_DIRECTIONS.md`](RESEARCH_DIRECTIONS.md) + [`EXAMPLE_INDEX.md`](EXAMPLE_INDEX.md) + invite to open issue with **failing fixture** |
| **What NOT to send** | Roadmap promises; "join the platform"; co-marketing before they've run one example |
| **3-file path** | 1. [`SPECGAP_POSITIONING.md`](SPECGAP_POSITIONING.md) · 2. [`WHY_DISAGREEMENT_MATTERS.md`](WHY_DISAGREEMENT_MATTERS.md) · 3. [`examples/operational/README.md`](../examples/operational/README.md) |
| **Strongest angle** | Fixture-driven collaboration on vocabulary, lattice, encoding—disagreement examples kept stable in CI |
| **Biggest skepticism** | "Solo repo / unclear maintenance / scope creep into runtime" |
| **Wrong framing** | "Partnership opportunity" · "Integrate our stack day one" · "We're building the standard" |

**DM one-liner:** Looking for critique via PR/issue on a minimal fixture that shows drift your domain cares about—SpecGap stays pre-runtime, bounded TCB.

---

## Universal do-not-send

- Whole OMEGA monorepo link without context
- omegaprotocol.org product/compliance narrative as SpecGap proof
- Sentinel, MCP audit tools, or runtime enforcement repos as the same thing
- Application essays unless they requested them
- Calls scheduled before they've skimmed abstract + one example

## Universal paste (any audience)

```
SpecGap — pre-runtime layered spec divergence, replayable evidence.
https://github.com/repowazdogz-droid/specgap/blob/main/docs/SPECGAP_ABSTRACT.md
10-min path: …/docs/DEMO_PATHS.md
Anti-hype: …/docs/SPECGAP_POSITIONING_ANTI_PATTERNS.md
```

Entry routing: [`RESEARCHER_ENTRY_POINTS.md`](RESEARCHER_ENTRY_POINTS.md)
