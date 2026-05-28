# SpecGap example index

Quick map of canonical scenarios. Run commands use repo root; `--extractor rule` is default.

| Scenario | Failure type | What diverged | What SpecGap detects | What it does NOT prove |
| --- | --- | --- | --- | --- |
| **Sandbox no-network** [`examples/sandbox_no_network.json`](../examples/sandbox_no_network.json) | Layer weakening + implication failure | Intent `no_network` → policy/claim `localhost_only` | 3 structural divergences; 2/2 implication FAIL; triangulation **agrees**; counterexample `network_send` + `dest_localhost` | Real network isolation; that localhost egress is exploitable; kernel/container behavior |
| **MCP tool drift** [`examples/operational/01_mcp_tool_drift/`](../examples/operational/01_mcp_tool_drift/) | Privilege weakening + claim not implied | Intent `no_privilege_escalation` → policy partial caps/denylist → claim adds `setuid_allowed` | 3 structural divergences; 2/2 implication FAIL; counterexample `privilege_gain` + `setuid_exec` | Live MCP `tools/list` vs `tools/call` probe; hidden GitHub tools; write/admin tool existence |
| **Multi-agent divergence** [`examples/operational/02_multi_agent_policy_divergence/`](../examples/operational/02_multi_agent_policy_divergence/) | Triangulation disagreement + implication failure | Planner `readonly_root_fs` vs executor `write_allowed` to `/var` | Structural **silent**; Z3 **fails**; Agreement = **no**; counterexample `fs_write` + `write_other` | Agent message traces; which agent ran; autonomous HOLD enforcement |
| **Configuration drift** [`examples/operational/03_configuration_drift/`](../examples/operational/03_configuration_drift/) | Weakening + contradiction + implication failure | Intent `no_network` → policy `localhost_only` → claim adds `network_allowed` | 5 structural divergences; 2/2 implication FAIL; contradictory `network_allowed` row | Live Helm/K8s values; production egress; health-check semantics |

---

## Run commands

```bash
# Canonical quickstart
python -m specgap.cli examples/sandbox_no_network.json --out /tmp/01.md

# Operational set
python -m specgap.cli examples/operational/01_mcp_tool_drift/spec.json --out /tmp/mcp.md
python -m specgap.cli examples/operational/02_multi_agent_policy_divergence/spec.json --out /tmp/agent.md
python -m specgap.cli examples/operational/03_configuration_drift/spec.json --out /tmp/cfg.md
```

Pre-generated reports: each operational folder has [`evidence/report.md`](../examples/operational/01_mcp_tool_drift/evidence/report.md) (regenerable).

---

## How to read the table

| Column | Meaning |
| --- | --- |
| **Failure type** | Primary signal class in the report |
| **What diverged** | Constraint-level story after extraction |
| **What SpecGap detects** | Documented checks that fired in the abstract model |
| **What it does NOT prove** | Common over-read to avoid |

Operational narratives (MCP, agents, config) are **author framing**. Checks run on **sandbox constraint vocabulary** only — see [`OPERATIONAL_EXAMPLES.md`](OPERATIONAL_EXAMPLES.md).

---

## Related

| Doc | Purpose |
| --- | --- |
| [`DEMO_PATHS.md`](DEMO_PATHS.md) | 2 / 10 / 30 minute paths |
| [`DIAGRAMS.md`](DIAGRAMS.md) | Three visual sketches |
| [`REPLAYABLE_EVIDENCE_EXAMPLE.md`](REPLAYABLE_EVIDENCE_EXAMPLE.md) | Sandbox no-network end-to-end |
