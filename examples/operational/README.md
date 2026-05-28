# Operational examples

Three small, replayable assurance scenarios. Each maps a **real operational pressure** (MCP tool surface, multi-agent hand-off, deployment config) onto SpecGap's **declared abstract sandbox model** — not live infrastructure.

| # | Scenario | Primary signal |
| --- | --- | --- |
| [01_mcp_tool_drift](01_mcp_tool_drift/) | Declared tool surface vs callable capability | Implication **FAIL** (privilege layer) |
| [02_multi_agent_policy_divergence](02_multi_agent_policy_divergence/) | Planner vs executor escalation rules | Triangulation **disagreement** + implication **FAIL** |
| [03_configuration_drift](03_configuration_drift/) | Config broadens scope; runtime still "works" | Implication **FAIL** (network layer) |

**Time budget:** under 5 minutes total (clone → install → three commands).

```bash
cd specgap
python3 -m venv .venv && source .venv/bin/activate
pip install -q -r requirements.txt
for d in 01_mcp_tool_drift 02_multi_agent_policy_divergence 03_configuration_drift; do
  python -m specgap.cli "examples/operational/${d}/spec.json" \
    --out "examples/operational/${d}/evidence/report.md"
done
```

See also: [`docs/OPERATIONAL_EXAMPLES.md`](../../docs/OPERATIONAL_EXAMPLES.md).
