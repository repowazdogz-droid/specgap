# SpecGap research directions

Ongoing assurance research for SpecGap — **not a roadmap of promised features**. Each direction is a **falsifiable question** with bounded scope. Contributions should preserve legibility, replayability, and disagreement in evidence artifacts.

Related: [`SPECGAP_POSITIONING.md`](SPECGAP_POSITIONING.md), [`THREAT_MODEL_SUMMARY.md`](THREAT_MODEL_SUMMARY.md), [`ASSURANCE_BOUNDARY.md`](ASSURANCE_BOUNDARY.md).

---

## 1. MCP boundary assurance

**Question:** Can tool-call boundary specifications (allowed tools, scopes, transformation rules) be expressed as layered constraints and checked for drift **before** an agent executes?

**In scope today:** Optional MCP summaries and evidence JSON under `reports/mcp/`; same SpecGap pipeline, no runtime interception.

**Open work:**

- Vocabulary for MCP-specific obligations (tool allowlists, argument transforms, egress)
- Evidence shape stable enough for cross-run diff and external review
- Explicit boundary: SpecGap checks **written** boundary specs, not live MCP traffic

**Falsifier:** A class of real MCP misconfigurations that never appear as extractable constraint divergence in the model.

---

## 2. Semantic drift across authoring surfaces

**Question:** How does intent change when the same requirement is authored in prose, YAML policy, and implementation comments — and can drift be detected without claiming NLU?

**In scope today:** Rule-based extraction with optional fuzzy advisory recovery; paraphrase examples in `examples/04_paraphrased_sandbox.json`.

**Open work:**

- Extraction failure as a first-class outcome (never silent pass)
- Paraphrase suites that stress vocabulary gaps, not benchmark scores
- Diff reports that show **which phrases** failed to extract

**Falsifier:** Drift that preserves extractable constraint names but changes meaning in ways the lattice and encoding miss.

---

## 3. Orchestration and configuration integrity

**Question:** When orchestration configs (delegation chains, env templates, feature flags) compose with sandbox policy, where does permissiveness enter relative to stated intent?

**In scope today:** Multi-layer JSON inputs; candidate policy evaluation mode.

**Open work:**

- Composition patterns for config + policy layers without exploding model size
- Structural diff coverage for partial and composite constraints
- Replay fixtures for "locally valid, globally weaker" stacks

**Falsifier:** Composed configs that pass layer-wise checks but violate end-to-end intent in production without appearing in the abstract model.

---

## 4. Multi-agent specification divergence

**Question:** When multiple agents or roles each carry specifications, where do hand-offs weaken global intent?

**In scope today:** Single-scenario layered specs; no agent graph model.

**Open work:**

- Minimal graph encoding for delegation edges as constraint layers
- Triangulation when sub-agent policy agrees locally but aggregate behavior diverges
- Linkage to OMEGA Lab authority/replay layers (records, not enforcement)

**Falsifier:** Divergence that only appears in runtime message traces, never in static spec layers.

---

## 5. Replayable assurance evidence

**Question:** What is the smallest evidence artifact that lets an independent reviewer reproduce "why SpecGap said FAIL" without re-trusting the author?

**In scope today:** Deterministic CLI, Markdown reports, JSON evidence chains, CI workflow badge.

**Open work:**

- Canonical evidence schema versioning and content hashes
- Integration hooks for `@omega-protocol/contracts` provenance slots
- Report sections stable enough for automated regression (golden reports)

**Falsifier:** Two reviewers with the same artifact draw incompatible conclusions about what was checked.

---

## 6. Assumption lineage

**Question:** Which load-bearing assumptions in a spec stack are implicit (never extracted) and how should their absence be reported?

**In scope today:** Extraction failure flags; no assumption registry integration.

**Open work:**

- Cross-reference patterns with assumption-registry semantics (materiality, not truth)
- "Implicit permission" and "implicit environment" classes in reports
- Pre-action **report labels** only — not autonomous gates

**Falsifier:** Critical implicit assumptions that SpecGap cannot name or flag under any vocabulary extension without false positives dominating.

---

## 7. Disagreement preservation under scale

**Question:** As mechanisms and layers increase, how do we avoid collapsing triangulation into a single score?

**In scope today:** Per-layer structural + Z3 + agreement flag; see [`WHY_DISAGREEMENT_MATTERS.md`](WHY_DISAGREEMENT_MATTERS.md).

**Open work:**

- Report UX that keeps disagreeing rows visible at a glance
- Teaching materials for reviewers (when disagreement implies lattice gap vs encoding gap)
- Property tests that disagreement examples stay stable across releases

**Falsifier:** Users consistently misread triangulation as consensus despite documentation.

---

## 8. Transformation-boundary attacks

**Question:** Can adversaries hide weakening by transforming specs at layer boundaries (rename, split, rephrase) while preserving superficial compliance?

**In scope today:** Structural lattice + implication over extracted sets; paraphrase tutorial.

**Open work:**

- Attack catalog: synonym drift, obligation splitting, permission laundering across layers
- Fixture suite derived from known transformation patterns (not CTF hype)
- Metrics: **detection rate within TCB**, not "security solved"

**Falsifier:** Transformations that leave all SpecGap mechanisms silent while monotonically weakening intent in English.

---

## Collaboration norms

- Prefer **fixtures + reports** over prose claims
- Extend **vocabulary / lattice / encoding** with tests, not ad hoc verdict logic
- Keep MCP, BoxArena, and runtime tools **downstream** of the assurance boundary unless the boundary document is updated explicitly
- No benchmark inflation: cite example IDs and report paths, not leaderboard scores

**Entry points:** `examples/`, `tutorials/`, `tests/`, `docs/`. Open an issue with a failing fixture or a proposed boundary change before large refactors.
