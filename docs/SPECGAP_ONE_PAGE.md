# SpecGap — one page

**Pre-runtime assurance for layered specification divergence.** SpecGap checks whether downstream policy and implementation claims still preserve upstream intent under a declared abstract model — and preserves disagreement between independent check mechanisms instead of collapsing them into one verdict.

**Layer:** Assurance · [OMEGA Lab](https://github.com/repowazdogz-droid/repowazdogz-droid) · Stack: [TRUST_STACK](https://github.com/repowazdogz-droid/omega-contracts/blob/main/docs/TRUST_STACK.md)

---

## What problem SpecGap solves

Teams write specifications in layers: stakeholder intent, formalized policy, implementation claims. Each layer often reads fine on its own. The failure mode is **semantic drift across layers** — downstream text quietly permits behavior upstream intent forbade.

That drift is expensive to find late:

- After deploy, when logs cannot reconstruct what was *meant*
- After a clean runtime test, when "no escape this time" is mistaken for "spec was correct"
- After adversarial evaluation budget is spent on a spec stack that was already inconsistent on paper

SpecGap runs **before** build, deploy, or sandbox execution. It emits **replayable evidence** (Markdown reports) about whether extracted constraints still logically preserve intent in a documented abstract model.

---

## Why layered specs drift

| Layer | Typical author | Failure pattern |
| --- | --- | --- |
| **Stakeholder intent** | Product, security, legal | Strict language ("no network access") |
| **Formalized policy** | Platform, policy engine | Partial relaxation ("localhost only for metrics") |
| **Implementation claim** | Engineering, SRE | Restates policy; adds unstated permissions |

Drift is rarely malicious. It accumulates through hand-offs, paraphrase, and local optima. Automated linters catch syntax; they rarely ask whether **layer B still implies layer A** under an explicit model.

Classic illustration (also the quickstart example):

| Layer | Text |
| --- | --- |
| Intent | "No network access" |
| Policy | "Localhost allowed for metrics" |
| Result | **FAIL** — `localhost_only` weakens `no_network` in the model |

---

## Why disagreement matters

SpecGap runs two **independent** mechanisms on extracted constraints:

1. **Structural diff** — name-level weakening lattice (`WEAKER_OF` over constraint names)
2. **Z3 implication** — propositional formulas over sandbox behavior atoms

They can **agree** or **disagree**. When structural diff is silent but Z3 fails, both signals stay visible in the report. That is often the most informative row — it may indicate a lattice gap, encoding incompleteness, or abstraction mismatch.

Most checkers merge heterogeneous signals into one PASS/FAIL. SpecGap treats **disagreement as evidence**, not noise to average away. See [`WHY_DISAGREEMENT_MATTERS.md`](WHY_DISAGREEMENT_MATTERS.md).

---

## What SpecGap actually checks

Given a JSON spec triple (`stakeholder_intent`, `formalized_policy`, `implementation_claim`):

| Step | What happens |
| --- | --- |
| **Extract** | Rule-based mapping of matched phrases → canonical constraints (network, filesystem, privilege, syscall) |
| **Structural diff** | Detect weakening, missing constraints, claim-not-implied between layers |
| **Z3 implication** | Ask whether downstream constraints imply upstream intent in the abstract encoding |
| **Triangulate** | Report structural vs Z3 agreement per layer |
| **Emit evidence** | Markdown report with counterexamples where implication fails |

**Core question (inside the boundary):**

> Do downstream **extracted** constraints preserve upstream **extracted** constraints in the declared model?

SpecGap does not judge whether intent was wise — only whether downstream layers preserve it **as encoded**.

---

## What SpecGap explicitly does NOT prove

| Not proven | Why |
| --- | --- |
| Runtime security or isolation | No execution, kernel, or container model |
| Complete English semantics | Unmatched phrases are not extracted |
| Compliance or certification | Evidence for reviewers, not attestation |
| That PASS means "secure" | PASS = no divergence found under current TCB and extraction |
| Exploit existence | Counterexamples are model assignments, not packet captures |

Optional MCP wrappers and BoxArena pre-flight hooks **do not expand** the assurance boundary. Full limits: [`ASSURANCE_BOUNDARY.md`](ASSURANCE_BOUNDARY.md) · [`THREAT_MODEL_SUMMARY.md`](THREAT_MODEL_SUMMARY.md).

---

## Three operational examples

Narratives map real operator pressure onto the sandbox TCB (fixed extraction vocabulary). Each is tiny, replayable, and includes "what this does NOT prove."

| # | Scenario | Primary signal |
| --- | --- | --- |
| [01 MCP tool drift](../examples/operational/01_mcp_tool_drift/) | Declared read-only surface vs hidden capability | Implication FAIL (privilege layer) |
| [02 Multi-agent divergence](../examples/operational/02_multi_agent_policy_divergence/) | Planner vs executor escalation rules | Triangulation **disagreement** |
| [03 Configuration drift](../examples/operational/03_configuration_drift/) | Config broadens network; health checks pass | Structural weakening + implication FAIL |

Index: [`examples/operational/README.md`](../examples/operational/README.md) · Rationale: [`OPERATIONAL_EXAMPLES.md`](OPERATIONAL_EXAMPLES.md).

---

## 5-minute quickstart

```bash
git clone https://github.com/repowazdogz-droid/specgap.git && cd specgap
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m specgap.cli examples/sandbox_no_network.json --out reports/demo_report.md
```

**Expect:** `failed implication checks: 2 of 2` · open `reports/demo_report.md` → Z3 counterexample block.

**Replay check:** run the same command twice; report content matches (`--extractor rule` is deterministic).

**Requires:** Python 3.10+, `z3-solver`. Walkthrough: [`REPLAYABLE_EVIDENCE_EXAMPLE.md`](REPLAYABLE_EVIDENCE_EXAMPLE.md).

---

## Relationship to OMEGA Lab

SpecGap is the **Assurance** entry in the public six-layer trunk:

| Layer | Role | SpecGap |
| --- | --- | --- |
| **Assurance** | Evidence before runtime | **This repo** — spec divergence |
| **Doctrine** | Lean predicate scaffolding | Conceptual alignment; no Lean export in SpecGap artifacts today |
| **Substrate** | `OmegaRecord` envelope | Integrators may attach evidence to provenance; not a first-class slot yet |
| **Replay** | Decision traces (clearpath) | Complementary: SpecGap checks specs **before** action; clearpath records **after** |

SpecGap is a **research object** and evidence generator — not a governance platform, agent framework, or runtime gate. Deeper positioning: [`SPECGAP_POSITIONING.md`](SPECGAP_POSITIONING.md). Architecture: [`ARCHITECTURE_OVERVIEW.md`](ARCHITECTURE_OVERVIEW.md).

---

## Where to go next

| Time | Document |
| --- | --- |
| +3 min | [`ARCHITECTURE_OVERVIEW.md`](ARCHITECTURE_OVERVIEW.md) — pipeline diagram |
| +5 min | [`OPERATIONAL_EXAMPLES.md`](OPERATIONAL_EXAMPLES.md) — three scenarios |
| +10 min | [`TCB.md`](TCB.md) + [`ENCODING.md`](ENCODING.md) — trust boundaries |

Collaboration: issues/PRs with **fixtures + reports**, not roadmap hype — [`RESEARCH_DIRECTIONS.md`](RESEARCH_DIRECTIONS.md).
