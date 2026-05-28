# Operational examples — why they matter

SpecGap's assurance boundary is **pre-runtime specification divergence** under a **declared abstract model**. These three examples show how that boundary meets **operator-visible pressure** without expanding scope into agents, benchmarks, or governance platforms.

**Location:** [`examples/operational/`](../examples/operational/)

---

## The operational gap

Teams ship layered specs — stakeholder intent, formalized policy, implementation claims — that each read fine in isolation. Failures often appear only when:

1. **Presentation ≠ execution** (declared MCP tool surface vs callable tools)
2. **Hand-offs weaken intent** (planner vs executor policy stacks)
3. **Config drifts while runtime stays green** (deploy values vs production intent)

SpecGap targets that gap **before** build, deploy, or adversarial sandbox spend. It produces **replayable Markdown evidence**, not a merged oracle score.

---

## Scenario map

| Example | Real pressure | SpecGap signal | Replay |
| --- | --- | --- | --- |
| [01 MCP tool drift](../examples/operational/01_mcp_tool_drift/) | Hidden capability behind declared read-only surface | 3 structural divergences; 2/2 implication FAIL | Same JSON + `--extractor rule` → same report |
| [02 Multi-agent divergence](../examples/operational/02_multi_agent_policy_divergence/) | Planner/executor interpret escalation differently | Triangulation **disagreement**; 2/2 implication FAIL | Disagreement rows stay visible in report |
| [03 Configuration drift](../examples/operational/03_configuration_drift/) | Config broadens network; health checks pass | 5 structural divergences; 2/2 implication FAIL | Pre-generated `evidence/report.md` in repo |

Each scenario includes `spec.json`, run command, expected terminal snippet, and **what this does NOT prove**.

---

## Abstract model honesty

Operational narratives (MCP, agents, Helm) are **author annotations**. SpecGap checks **extracted sandbox constraints** (network, filesystem, privilege, syscall) via:

- Rule-based extraction (fixed vocabulary)
- Structural weakening lattice
- Z3 implication over `docs/ENCODING.md`

If MCP-specific atoms are not in the TCB, the example still teaches **where SpecGap applies today** and **where vocabulary extension is research** (see [`RESEARCH_DIRECTIONS.md`](RESEARCH_DIRECTIONS.md) §1 MCP boundary assurance).

---

## Disagreement preservation (example 02)

Most checkers collapse independent signals. Example 02 shows **structural silent / Z3 fails**:

| Mechanism | Outcome |
| --- | --- |
| Structural diff | `no_divergence_detected` |
| Z3 implication | `fails` |
| Agreement | **no** |

Operators should treat this as **HOLD-grade evidence** — reconcile layers before deploy. SpecGap does not autonomously gate production; it preserves heterogeneous signals for human review.

---

## Five-minute path

```bash
git clone https://github.com/repowazdogz-droid/specgap.git && cd specgap
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m specgap.cli examples/operational/01_mcp_tool_drift/spec.json --out /tmp/op1.md
python -m specgap.cli examples/operational/02_multi_agent_policy_divergence/spec.json --out /tmp/op2.md
python -m specgap.cli examples/operational/03_configuration_drift/spec.json --out /tmp/op3.md
```

Open `/tmp/op2.md` → Triangulation Summary table → counterexample block.

---

## Bounded claims (stack context)

| SpecGap operational examples **are** | **Are not** |
| --- | --- |
| Pre-runtime drift detectors on written layers | Runtime MCP servers or K8s validators |
| Replayable evidence for reviewers | Compliance certification |
| Teaching triangulation + implication | AGI alignment or autonomous governance |
| Fixtures for collaboration / issues | Benchmark leaderboards |

Stack map: [`SPECGAP_POSITIONING.md`](SPECGAP_POSITIONING.md) · OMEGA Lab [`TRUST_STACK`](https://github.com/repowazdogz-droid/omega-contracts/blob/main/docs/TRUST_STACK.md) (Assurance layer).

---

## Related docs

- [`examples/operational/README.md`](../examples/operational/README.md) — index + batch command
- [`ASSURANCE_BOUNDARY.md`](ASSURANCE_BOUNDARY.md) — hard limits
- [`WHY_DISAGREEMENT_MATTERS.md`](WHY_DISAGREEMENT_MATTERS.md) — triangulation rationale
- [`THREAT_MODEL_SUMMARY.md`](THREAT_MODEL_SUMMARY.md) — in-scope drift classes
