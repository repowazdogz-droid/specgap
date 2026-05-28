# SpecGap

**Layer:** Assurance

## Position in OMEGA Lab

Pre-runtime specification divergence evidence. Does not replace runtime evaluation. See [docs/ASSURANCE_BOUNDARY.md](docs/ASSURANCE_BOUNDARY.md). Stack map: [omega-contracts TRUST_STACK](https://github.com/repowazdogz-droid/omega-contracts/blob/main/docs/TRUST_STACK.md).

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![pytest](https://img.shields.io/badge/tests-pytest-49%20passed-brightgreen)
[![test](https://github.com/repowazdogz-droid/specgap/actions/workflows/test.yml/badge.svg)](https://github.com/repowazdogz-droid/specgap/actions/workflows/test.yml)

**Pre-runtime specification assurance** for layered sandbox specs — intent, policy, and implementation claims.

SpecGap checks whether downstream policy and implementation layers still logically preserve upstream intent under a declared abstract model, while preserving disagreement between independent evaluators instead of collapsing them into a single verdict.

## External readers

Sharing with MATS, AISI, formal methods, or infrastructure/security contacts:

| Link | Use |
| --- | --- |
| [`docs/SPECGAP_ABSTRACT.md`](docs/SPECGAP_ABSTRACT.md) | Paste into forms, emails, fellowship fields |
| [`docs/SPECGAP_FAQ.md`](docs/SPECGAP_FAQ.md) | Quick objections and boundary questions |
| [`docs/SHAREABLE_LINKS.md`](docs/SHAREABLE_LINKS.md) | Curated map — pick depth without reading the whole repo |

## Quick demo paths

Skim → run → understand thesis (≤10 min):

| Link | Use |
| --- | --- |
| [`docs/DEMO_PATHS.md`](docs/DEMO_PATHS.md) | 2 / 10 / 30 minute walkthroughs with exact files |
| [`docs/EXAMPLE_INDEX.md`](docs/EXAMPLE_INDEX.md) | Scenario table — what diverged vs what is not proven |
| [`docs/DIAGRAMS.md`](docs/DIAGRAMS.md) | Three small Mermaid diagrams |

## For researchers / operators

DMs, fellowships, one-link sends:

| Link | Use |
| --- | --- |
| [`docs/OUTREACH_PACKETS.md`](docs/OUTREACH_PACKETS.md) | Audience A–E: what to send, what to avoid |
| [`docs/RESEARCHER_ENTRY_POINTS.md`](docs/RESEARCHER_ENTRY_POINTS.md) | Route by person type + follow-up artifact |
| [`docs/SPECGAP_POSITIONING_ANTI_PATTERNS.md`](docs/SPECGAP_POSITIONING_ANTI_PATTERNS.md) | Overclaim checklist before you hit send |

## Project status

Publication freeze · citeable research object · v0.1.0:

| Link | Use |
| --- | --- |
| [`docs/STABILITY_STATUS.md`](docs/STABILITY_STATUS.md) | Stable vs experimental vs absent |
| [`docs/VERSIONING_AND_SCOPE.md`](docs/VERSIONING_AND_SCOPE.md) | Breaking vs doc-only changes |
| [`docs/PUBLICATION_STATE.md`](docs/PUBLICATION_STATE.md) | What exists today (inventory snapshot) |

Bounded assurance/replay — not a universal AI safety framework. Active maintenance; narrow scope.

## Understand SpecGap in 5 minutes

| Start here | Why |
| --- | --- |
| [`docs/SPECGAP_ONE_PAGE.md`](docs/SPECGAP_ONE_PAGE.md) | Problem, boundaries, quickstart on one screen |
| [`docs/REPLAYABLE_EVIDENCE_EXAMPLE.md`](docs/REPLAYABLE_EVIDENCE_EXAMPLE.md) | One example input → report → replay |
| [`docs/OPERATIONAL_EXAMPLES.md`](docs/OPERATIONAL_EXAMPLES.md) | Three operator-framed scenarios |
| [`docs/ARCHITECTURE_OVERVIEW.md`](docs/ARCHITECTURE_OVERVIEW.md) | Pipeline diagram + TCB pointers |
| [`docs/WHY_DISAGREEMENT_MATTERS.md`](docs/WHY_DISAGREEMENT_MATTERS.md) | Triangulation rationale |
| [`docs/THREAT_MODEL_SUMMARY.md`](docs/THREAT_MODEL_SUMMARY.md) | In-scope vs out-of-scope detection |

Then run [quickstart](#quickstart-3-minutes) below.

| If you have… | Go to |
| --- | --- |
| **3 minutes** | [Quickstart](#quickstart-3-minutes) |
| **10 minutes** | [Extended evaluation](#extended-evaluation-10-minutes) |
| **Hackathon review** | [`HACKATHON_JUDGE_GUIDE.md`](HACKATHON_JUDGE_GUIDE.md) |
| **Assurance boundary** | [What SpecGap does not claim](#what-specgap-does-not-claim) |

---

## The problem

**Specification assurance** breaks when semantic drift accumulates across layers. Each layer reads plausibly alone; downstream policy may permit behavior upstream intent forbids.

Stakeholder language becomes predicates, then implementation claims. Automated checks discharge obligations quickly — the bottleneck is whether the obligation still matches what stakeholders meant.

---

## The aha example

| Layer | Text |
| --- | --- |
| **Intent** | “No network access” |
| **Policy** | “Only localhost access” |
| **Result** | **FAIL** — downstream permits `network_send=true, dest_localhost=true`, which violates upstream `no_network`. |

SpecGap surfaces drift **before** deployment or adversarial evaluation. It does not run sandboxes or observe live infrastructure.

---

## Quickstart (3 minutes)

```bash
git clone https://github.com/repowazdogz-droid/specgap.git
cd specgap
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m specgap.cli examples/sandbox_no_network.json --out reports/demo_report.md
```

**Expected terminal output:**

```
SpecGap: analyzed 'Network-isolated analysis sandbox' (extractor: rule)
  semantic divergences: 3
  failed implication checks: 2 of 2
  report written to: reports/demo_report.md
```

**Inspect** [`reports/demo_report.md`](reports/demo_report.md):

| Section | What to look for |
| --- | --- |
| Extracted constraints | Intent `no_network` vs policy `localhost_only` |
| Z3 Formal Check | **Implication FAILS** — logical preservation failed in the abstract model |
| Counterexample | `network_send=true, dest_localhost=true` *(model behavior, not a runtime exploit)* |

<details>
<summary>Expected report excerpt</summary>

```markdown
### Formalized Policy ⇒ Stakeholder Intent

- **Result: implication FAILS.** … there is a behavior permitted by Formalized Policy
  that Stakeholder Intent forbids.
- Violated target constraint(s): `no_network`

Counterexample behavior:
- `network_send = true`
- `dest_localhost = true`
```

</details>

**Requires:** Python 3.10+, [Z3](https://github.com/Z3Prover/z3) via `z3-solver`.

---

## What's different

Most spec checkers collapse independent signals into one verdict. SpecGap is built around three constraints:

1. **Declared abstract model** — Z3 checks logical preservation inside a documented propositional sandbox encoding, not over live infrastructure.
2. **Independent mechanisms** — structural weakening lattice and Z3 implication run separately; outcomes are triangulated, not merged.
3. **Replayable evidence** — same JSON input and `--extractor rule` yield the same extraction and Z3 results; reports and structured envelopes are regenerable artifacts.

→ Research note: [`docs/WHY_DISAGREEMENT_MATTERS.md`](docs/WHY_DISAGREEMENT_MATTERS.md)

---

## Structured output (`analyze_structured`)

The primary programmatic surface is **`analyze_structured()`**, which returns a versioned **AssuranceResult** envelope (`assurance_result_schema: "1.0"`, `kind: "specgap"`). Integrators (MCP, `@omega-protocol/contracts`) consume this shape; Markdown reports remain the human-readable view from the CLI.

```python
from specgap import analyze_structured, input_fingerprint
from specgap.models import SpecInput
import json

spec = SpecInput.from_dict(json.loads(open("examples/sandbox_no_network.json")))
result = analyze_structured(spec, mode="rule")

# Envelope (top level)
result["kind"]                    # "specgap"
result["verdict"]                 # divergence_detected | no_divergence_detected | extraction_failure
result["input_fingerprint"]       # RFC 8785 JCS SHA-256 over spec ingress (replay anchor)
result["producer"]                # {"name": "specgap", "version": "0.1.0"}

# SpecGap payload (full analysis — constraints, Z3, triangulation)
detail = result["detail"]
detail["triangulation"]           # TriangulationSummary.to_dict() — disagreement preserved
detail["implication_checks"]      # Z3 results + counterexample atoms
detail["divergences"]             # structural diff records
detail["extracted_constraints"]   # per-layer canonical constraints
detail["encoding_version"]        # "sandbox-propositional/1.0"
```

**Ingress fingerprint:** `input_fingerprint(spec)` hashes `{title, stakeholder_intent, formalized_policy, implementation_claim}` with [RFC 8785 JCS](https://www.rfc-editor.org/rfc/rfc8785) (`rfc8785` package), aligned byte-for-byte with `@omega-protocol/contracts` `fingerprint()`. Cross-language anchor: [`fixtures/specgap/fingerprint_vector.json`](fixtures/specgap/fingerprint_vector.json).

**Schemas:** [`schemas/assurance-result-1.0.schema.json`](schemas/assurance-result-1.0.schema.json) (envelope), [`schemas/specgap-detail-1.0.schema.json`](schemas/specgap-detail-1.0.schema.json) (`detail`).

**Contracts adapter:** `@omega-protocol/contracts` ships `specgapAssuranceAdapter` — projects the envelope to a summarized canonical `AssuranceResult` for record composition (C0+C1; `OmegaRecord.assurance` slot pending).

**MCP:** `analyze_spec` nests the full envelope under `result`; legacy top-level fields are deprecated for one version — see [`specgap-mcp/README.md`](specgap-mcp/README.md).

---

## Architecture

<p align="center">
  <a href="docs/assets/specgap_architecture.svg">
    <img src="docs/assets/specgap_architecture.png" alt="SpecGap: specification layers through extraction, SMT checking, independent evaluators, disagreement preservation, replayable evidence" width="640"/>
  </a>
</p>

_SVG: [`docs/assets/specgap_architecture.svg`](docs/assets/specgap_architecture.svg)_

**Pipeline:** extract constraints → structural divergence → Z3 implication → triangulation → **AssuranceResult envelope** (`analyze_structured`) and/or Markdown report (CLI).

Optional (same trust boundary): `--evaluate-candidates`, [`specgap-mcp/`](specgap-mcp/README.md), [`docs/BOXARENA_POSITIONING.md`](docs/BOXARENA_POSITIONING.md).

---

## Extended evaluation (10 minutes)

After [quickstart](#quickstart-3-minutes):

```bash
python -m specgap.cli examples/06_triangulation_disagreement.json --out reports/06_triangulation_disagreement_report.md
python -m specgap.cli examples/05_candidate_policy_ranking.json --evaluate-candidates --out reports/05_candidate_evaluation_report.md
python -m specgap.cli examples/04_paraphrased_sandbox.json --out reports/04_paraphrased_sandbox_report.md
pip install -r requirements-dev.txt && pytest -q
```

| Example | Purpose |
| --- | --- |
| [`sandbox_no_network.json`](examples/sandbox_no_network.json) | Semantic weakening + implication failure *(quickstart)* |
| [`06_triangulation_disagreement.json`](examples/06_triangulation_disagreement.json) | Structural silent, Z3 fails — **disagreement preserved** |
| [`05_candidate_policy_ranking.json`](examples/05_candidate_policy_ranking.json) | Candidate comparison — A PASS, B/C FAIL *(not a security score)* |
| [`04_paraphrased_sandbox.json`](examples/04_paraphrased_sandbox.json) | Extraction failure on paraphrase — vocabulary boundary |

**Also in repo:** [`sandbox_readonly_fs.json`](examples/sandbox_readonly_fs.json), [`syscall_policy_mismatch.json`](examples/syscall_policy_mismatch.json), [`boxarena_preflight_*.json`](examples/). Step-by-step: [`tutorials/README.md`](tutorials/README.md).

<details>
<summary>How to read triangulation disagreement</summary>

In `06_triangulation_disagreement_report.md`, look for **Agreement = no**:

```markdown
| Layer              | Structural              | Z3 implication | Agreement |
| Formalized Policy  | no_divergence_detected  | fails          | **no**    |
```

Structural diff and Z3 captured different abstraction-level properties. SpecGap reports both — it does not pick a winner.

</details>

---

## Why disagreement matters

- **Structural diff** — name-level `WEAKER_OF` lattice over extracted constraint names
- **Z3** — propositional formulas over behavior atoms in the abstract model

When they diverge, both signals stay visible. That may indicate a lattice gap, encoding incompleteness, or abstraction mismatch — not that one mechanism is wrong.

---

## What SpecGap does not claim

SpecGap does **NOT**:

- prove runtime security
- verify infrastructure or execute sandboxes
- replace adversarial evaluation
- guarantee extraction completeness
- turn **PASS** into “secure”

| Outcome | Meaning |
| --- | --- |
| **PASS** | No divergence found under the current extraction rules and declared abstract model. |
| **FAIL** | Logical preservation failed within the abstract model — often with a counterexample. |

Counterexamples are illustrative model behaviors, not confirmed exploits.

**Assurance docs:** [`docs/SPECIFICATION.md`](docs/SPECIFICATION.md) · [`docs/ASSURANCE_BOUNDARY.md`](docs/ASSURANCE_BOUNDARY.md) · [`docs/TCB.md`](docs/TCB.md) · [`docs/ENCODING.md`](docs/ENCODING.md)

**Onboarding:** [`docs/SPECGAP_ONE_PAGE.md`](docs/SPECGAP_ONE_PAGE.md) · [`docs/ARCHITECTURE_OVERVIEW.md`](docs/ARCHITECTURE_OVERVIEW.md) · [`docs/OPERATIONAL_EXAMPLES.md`](docs/OPERATIONAL_EXAMPLES.md) · [`docs/REPLAYABLE_EVIDENCE_EXAMPLE.md`](docs/REPLAYABLE_EVIDENCE_EXAMPLE.md)

**Research framing:** [`docs/SPECGAP_POSITIONING.md`](docs/SPECGAP_POSITIONING.md) · [`docs/RESEARCH_DIRECTIONS.md`](docs/RESEARCH_DIRECTIONS.md) · [`docs/THREAT_MODEL_SUMMARY.md`](docs/THREAT_MODEL_SUMMARY.md) · [`docs/WHY_DISAGREEMENT_MATTERS.md`](docs/WHY_DISAGREEMENT_MATTERS.md)

---

## Rigor signals

| Signal | Where |
| --- | --- |
| **49 pytest cases** | `tests/` — Z3 implication checks not mocked; RFC 8785 fingerprint vector |
| **CI** | [`.github/workflows/test.yml`](.github/workflows/test.yml) — `pytest -q` on push |
| **Deterministic CLI** | Same JSON + `--extractor rule` → same results |
| **Reference reports** | [`reports/demo_report.md`](reports/demo_report.md), whitelisted under `reports/` |
| **Explicit TCB** | [`docs/TCB.md`](docs/TCB.md), [`docs/ENCODING.md`](docs/ENCODING.md) |
| **Bounded wording** | Reports and CLI label abstract-model limits |

Record input path, extractor mode, Python version, and `z3-solver` version when citing results.

---

## Repository map

```
specgap/              Core — extractor, semantic_diff, z3_checker, triangulation, assurance, reporter, cli
specgap-mcp/          stdio MCP wrapper (nested `result` envelope)
schemas/              AssuranceResult envelope + specgap detail JSON Schemas
fixtures/specgap/     Cross-language fingerprint vector + native sample
examples/             Input JSON specs
reports/              Regenerable reference reports
tests/                pytest suite
docs/                 Specification, assurance boundary, architecture assets
tutorials/            Verified walkthroughs
submission/           Hackathon summary and freeze record
```

```bash
pip install -r requirements.txt -r requirements-dev.txt && pytest -q
```

---

## Submission links

| Document | Purpose |
| --- | --- |
| [`HACKATHON_JUDGE_GUIDE.md`](HACKATHON_JUDGE_GUIDE.md) | Copy-paste judge paths |
| [`submission/HACKATHON_SUMMARY.md`](submission/HACKATHON_SUMMARY.md) | Track fit, novelty, limitations |
| [`submission/SUBMISSION_FREEZE.md`](submission/SUBMISSION_FREEZE.md) | Verified commands, freeze record |
