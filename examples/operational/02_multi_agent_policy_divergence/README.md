# 02 — Multi-agent policy divergence

**Operational pressure:** A **planner** agent commits to readonly / human-review escalation rules; an **executor** agent's policy permits writes to `/var`. Each layer reads plausibly alone; together they weaken global intent.

**Primary signal:** **Triangulation disagreement** — structural diff is silent, Z3 implication fails. Treat as heterogeneous evidence; do not merge into one PASS/FAIL.

**Operational interpretation:** When implication fails and triangulation disagrees, operators should **HOLD** deployment until planner and executor specs are reconciled. SpecGap does not emit OMEGA `HELD` records — this is human/integrator action on the evidence.

## Layered specs

| Layer | Role in scenario |
| --- | --- |
| Stakeholder intent | Planner: readonly root, no scope broadening without review |
| Formalized policy | Executor: write access to `/var` |
| Implementation claim | Executor repeats write policy |

## Run

```bash
python -m specgap.cli examples/operational/02_multi_agent_policy_divergence/spec.json \
  --out examples/operational/02_multi_agent_policy_divergence/evidence/report.md
```

## Expected terminal output

```
SpecGap: analyzed 'Multi-agent escalation divergence — planner readonly vs executor write scope' (extractor: rule)
  triangulation: disagreement between structural diff and Z3
  semantic divergences: 0
  failed implication checks: 2 of 2
  report written to: examples/operational/02_multi_agent_policy_divergence/evidence/report.md
```

## Expected report excerpt

```markdown
| Formalized Policy | no_divergence_detected | fails | **no** | yes |

### Formalized Policy ⇒ Stakeholder Intent

- **Result: implication FAILS.** …
- Violated target constraint(s): `readonly_root_fs`

Counterexample behavior:
- `fs_write = true` — a filesystem write occurs
- `write_other = true` — the write target is outside /tmp
```

Pre-generated copy: [`evidence/report.md`](evidence/report.md)

## What this does NOT prove

- Does **not** model agent message traces or runtime hand-offs.
- Does **not** show which agent actually executed a write.
- Does **not** enforce a HOLD gate autonomously.
- Disagreement preservation is about **evidence shape**, not multi-agent orchestration correctness.
