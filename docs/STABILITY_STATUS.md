# SpecGap stability status

**As of:** 2026-05-25  
**Package version:** `0.1.0` ([`pyproject.toml`](../pyproject.toml))

SpecGap is a **bounded assurance and replay research object** in the OMEGA Lab public trunk. It is **not** a universal AI safety framework, governance platform, or runtime enforcement product.

---

## Stable assurance core

Considered **stable** for citation and reproduction (changes should be rare and documented):

| Component | Location | Stability note |
| --- | --- | --- |
| **Spec triple pipeline** | `specgap/cli.py`, `extractor.py`, `semantic_diff.py`, `z3_checker.py`, `triangulation.py`, `reporter.py` | Intent / policy / claim → report |
| **Rule extractor (default)** | `extractor.py`, `--extractor rule` | Deterministic; no API key |
| **Structural weakening lattice** | `semantic_diff.py` | `WEAKER_OF` relationships under test |
| **Z3 implication checks** | `z3_checker.py` + [`ENCODING.md`](ENCODING.md) | Propositional sandbox model |
| **Triangulation (disagreement preserved)** | `triangulation.py` | Independent structural + Z3 rows; no merge |
| **Assurance boundary docs** | [`ASSURANCE_BOUNDARY.md`](ASSURANCE_BOUNDARY.md), [`TCB.md`](TCB.md), [`THREAT_MODEL_SUMMARY.md`](THREAT_MODEL_SUMMARY.md) | Public claim discipline |
| **CI** | `.github/workflows/test.yml` | `pytest -q` on push (41 tests) |

**Thesis (frozen):** Pre-runtime layered spec divergence evidence; replayable reports; disagreement-first triangulation; explicit TCB.

---

## Operational examples

| Set | Status |
| --- | --- |
| [`examples/sandbox_no_network.json`](../examples/sandbox_no_network.json) | Stable canonical quickstart |
| [`examples/operational/`](../examples/operational/) (3 scenarios) | Stable **documentation fixtures**; narratives map to sandbox TCB |
| [`examples/06_triangulation_disagreement.json`](../examples/06_triangulation_disagreement.json) | Stable disagreement demo |
| Other `examples/*.json` | Supported; not all duplicated in operational index |

Operational examples are **stable as replay artifacts**, not as claims about MCP/K8s/live agent runtime.

---

## Replay evidence

| Property | Status |
| --- | --- |
| Markdown reports via `--out` | Stable |
| Same JSON + `--extractor rule` → same results | Stable contract |
| Pre-generated `examples/operational/*/evidence/report.md` | Regenerable snapshots for reviewers |
| BoxArena JSON evidence chain | Stable optional path; same assurance boundary |

**Do NOT infer:** Cryptographic attestation, signed reports, or on-chain replay proofs.

---

## Triangulation model

| Behavior | Status |
| --- | --- |
| Per-layer structural vs Z3 agreement table | Stable output shape |
| `Agreement = no` preserved in reports | Stable; not a bug to "fix" by merging |
| [`WHY_DISAGREEMENT_MATTERS.md`](WHY_DISAGREEMENT_MATTERS.md) | Stable rationale doc |

---

## Experimental

May change without a major version bump if bounded to opt-in paths:

| Item | Notes |
| --- | --- |
| **`--extractor fuzzy`** | Paraphrase / optional Anthropic path; advisory only |
| **`--evaluate-candidates`** | Candidate ranking mode; not a security score |
| **`--boxarena-preflight`** | Pre-flight adapter; does not run BoxArena |
| **`specgap-mcp/`** | stdio wrapper; same checks, optional surface |
| **MCP-specific vocabulary** | Research only — [`RESEARCH_DIRECTIONS.md`](RESEARCH_DIRECTIONS.md) §1 |

---

## Intentionally absent

Not missing by oversight — **out of scope**:

- Runtime execution, MCP live traffic, kernel/container models
- Autonomous deploy gates or agent enforcement
- Compliance certification, legal attestation, ISO/EU AI Act "satisfies"
- Full natural-language semantics / NLU extraction authority
- OmegaRecord first-class provenance slot (integrator-side today)
- Lean export / kernel-in-the-loop from SpecGap artifacts
- Benchmarks, leaderboards, performance SLO marketing

---

## Frozen (publication freeze)

For external citation, treat as **frozen surface** until [`VERSIONING_AND_SCOPE.md`](VERSIONING_AND_SCOPE.md) says otherwise:

- Assurance boundary wording in [`ASSURANCE_BOUNDARY.md`](ASSURANCE_BOUNDARY.md)
- Disagreement-preservation behavior (no collapsed oracle)
- Default `rule` extractor determinism contract
- Onboarding + outreach doc set (see [`PUBLICATION_STATE.md`](PUBLICATION_STATE.md))
- OMEGA Lab positioning: **Assurance layer only** — not product trunk

---

## Future work (may exist; not promised)

Documented as **research questions**, not roadmap deliverables:

- [`RESEARCH_DIRECTIONS.md`](RESEARCH_DIRECTIONS.md) — vocabulary, lattice, encoding extensions via fixtures
- [`OPERATIONAL_EXAMPLES.md`](OPERATIONAL_EXAMPLES.md) — honest TCB mapping for new domains
- omega-contracts provenance integration — integrator-defined

No commitment to platform features, agent frameworks, or universal safety coverage.

---

## Non-goals

SpecGap will **not** become:

- An AI governance or alignment platform
- A runtime monitor or MCP enforcement server
- A compliance automation product
- A single PASS/FAIL security score
- A substitute for adversarial evaluation or pentest

See also: [`SPECGAP_POSITIONING_ANTI_PATTERNS.md`](SPECGAP_POSITIONING_ANTI_PATTERNS.md).

---

## What should NOT be inferred

| Inference | Reality |
| --- | --- |
| "Stable repo = production-ready product" | Stable = **reproducible research object** with bounded claims |
| "41 tests = system verified" | Tests cover pipeline/TCB components, not deployed systems |
| "Operational examples = live validation" | Narrative fixtures on sandbox atoms |
| "Freeze = no commits" | Freeze = **conceptual and public-claim discipline**, not abandonment |
| "OMEGA Lab = SpecGap everywhere" | SpecGap is one Assurance entry; see [TRUST_STACK](https://github.com/repowazdogz-droid/omega-contracts/blob/main/docs/TRUST_STACK.md) |

**Cite as:** SpecGap v0.1.0 — pre-runtime layered specification divergence tool with replayable evidence (OMEGA Lab Assurance layer).
