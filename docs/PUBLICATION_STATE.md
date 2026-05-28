# SpecGap publication state

**Snapshot date:** 2026-05-25  
**Repo:** [github.com/repowazdogz-droid/specgap](https://github.com/repowazdogz-droid/specgap)  
**Version:** `0.1.0`

What exists **today** — not a roadmap.

---

## Public artifacts (code)

| Artifact | Path | Runnable |
| --- | --- | --- |
| CLI pipeline | `specgap/` package | `python -m specgap.cli` |
| MCP stdio wrapper | `specgap-mcp/` | optional |
| Tests + CI | `tests/`, `.github/workflows/test.yml` | `pytest -q` (41 cases) |
| Reference reports | `reports/` | regenerable |

---

## Runnable examples

| Example | Purpose |
| --- | --- |
| `examples/sandbox_no_network.json` | Canonical quickstart |
| `examples/operational/` (×3) | Operator-framed fixtures + pre-gen evidence |
| `examples/06_triangulation_disagreement.json` | Disagreement demo |
| `examples/05_candidate_policy_ranking.json` | Candidate mode |
| `examples/04_paraphrased_sandbox.json` | Extraction boundary |
| `examples/sandbox_readonly_fs.json`, `syscall_policy_mismatch.json` | Core sandbox set |
| `examples/boxarena_preflight_*.json` | Optional pre-flight |

Index: [`EXAMPLE_INDEX.md`](EXAMPLE_INDEX.md)

---

## Assurance docs

| Doc | Role |
| --- | --- |
| [`SPECIFICATION.md`](SPECIFICATION.md) | Correctness target |
| [`ASSURANCE_BOUNDARY.md`](ASSURANCE_BOUNDARY.md) | Claim limits |
| [`TCB.md`](TCB.md) | Trusted components |
| [`ENCODING.md`](ENCODING.md) | Atoms and formulas |
| [`THREAT_MODEL_SUMMARY.md`](THREAT_MODEL_SUMMARY.md) | Detect / cannot detect |
| [`WHY_DISAGREEMENT_MATTERS.md`](WHY_DISAGREEMENT_MATTERS.md) | Triangulation rationale |
| [`SPECGAP_POSITIONING.md`](SPECGAP_POSITIONING.md) | OMEGA Lab layer role |
| [`RESEARCH_DIRECTIONS.md`](RESEARCH_DIRECTIONS.md) | Falsifiable questions (not promises) |

---

## Onboarding docs

| Doc | Role |
| --- | --- |
| [`SPECGAP_ONE_PAGE.md`](SPECGAP_ONE_PAGE.md) | Single-screen intro |
| [`SPECGAP_ABSTRACT.md`](SPECGAP_ABSTRACT.md) | Paste-friendly abstract |
| [`SPECGAP_FAQ.md`](SPECGAP_FAQ.md) | Short Q&A |
| [`REPLAYABLE_EVIDENCE_EXAMPLE.md`](REPLAYABLE_EVIDENCE_EXAMPLE.md) | End-to-end walkthrough |
| [`ARCHITECTURE_OVERVIEW.md`](ARCHITECTURE_OVERVIEW.md) | Pipeline diagrams |
| [`OPERATIONAL_EXAMPLES.md`](OPERATIONAL_EXAMPLES.md) | Operational mapping |
| [`DEMO_PATHS.md`](DEMO_PATHS.md) | 2 / 10 / 30 min paths |
| [`DIAGRAMS.md`](DIAGRAMS.md) | Three Mermaid sketches |
| [`EXAMPLE_INDEX.md`](EXAMPLE_INDEX.md) | Scenario table |
| [`SHAREABLE_LINKS.md`](SHAREABLE_LINKS.md) | Link map |

---

## Outreach docs

| Doc | Role |
| --- | --- |
| [`OUTREACH_PACKETS.md`](OUTREACH_PACKETS.md) | Audience send guidance |
| [`RESEARCHER_ENTRY_POINTS.md`](RESEARCHER_ENTRY_POINTS.md) | Person-type routing |
| [`SPECGAP_POSITIONING_ANTI_PATTERNS.md`](SPECGAP_POSITIONING_ANTI_PATTERNS.md) | Overclaim checklist |

---

## Freeze / stability docs

| Doc | Role |
| --- | --- |
| [`STABILITY_STATUS.md`](STABILITY_STATUS.md) | Stable vs experimental |
| [`VERSIONING_AND_SCOPE.md`](VERSIONING_AND_SCOPE.md) | Version policy |
| [`PUBLICATION_STATE.md`](PUBLICATION_STATE.md) | This inventory |

---

## Known gaps (acknowledged)

| Gap | Status |
| --- | --- |
| MCP/agent-native constraint vocabulary | Research; mapped via sandbox atoms in operational examples |
| Partial English extraction | By design; unmatched text omitted |
| omega-contracts provenance slot | Integrator-side; not first-class in SpecGap output |
| Fuzzy/LLM extraction authority | Experimental; not default |
| BoxArena runtime verification | Separate tool; pre-flight only |
| Package publish to PyPI | Not required for citation; clone + CLI |

---

## Intentionally deferred

Not scheduled — may be explored via issues/fixtures only:

- Platform UI, dashboard, or SaaS wrapper
- Autonomous deploy gates
- Compliance mapping products
- Benchmark suites / leaderboards
- Kernel-accurate models
- Universal agent governance integration

See [`STABILITY_STATUS.md`](STABILITY_STATUS.md) non-goals.

---

## Citation one-liner

> SpecGap v0.1.0 (2026-05-25): pre-runtime layered specification divergence checks with triangulated structural and Z3 evidence; OMEGA Lab Assurance layer. https://github.com/repowazdogz-droid/specgap

Detailed status: [`STABILITY_STATUS.md`](STABILITY_STATUS.md)
