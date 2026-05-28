# 01 — MCP tool drift

**Operational pressure:** MCP `tools/list` shows a read-only surface, but `tools/call` can still reach write/admin capabilities — a presentation vs execution mismatch.

**Abstract model mapping:** SpecGap encodes this as **privilege-layer** drift (strict `no_privilege_escalation` vs `setuid_allowed`). The sandbox vocabulary is the declared TCB; it is not a live MCP audit.

## Layered specs

| Layer | Source |
| --- | --- |
| Stakeholder intent | [`spec.json`](spec.json) → `stakeholder_intent` |
| Formalized policy | `formalized_policy` (tools/list + seccomp narrative) |
| Implementation claim | `implementation_claim` (hidden write tool + setuid) |

## Run

```bash
python -m specgap.cli examples/operational/01_mcp_tool_drift/spec.json \
  --out examples/operational/01_mcp_tool_drift/evidence/report.md
```

## Expected terminal output

```
SpecGap: analyzed 'MCP tool surface drift — read-only registry vs hidden write capability' (extractor: rule)
  triangulation: structural diff and Z3 agree
  semantic divergences: 3
  failed implication checks: 2 of 2
  report written to: examples/operational/01_mcp_tool_drift/evidence/report.md
```

## Expected report excerpt

```markdown
### Implementation Claim ⇒ Stakeholder Intent

- **Result: implication FAILS.** …
- Violated target constraint(s): `no_privilege_escalation`

Counterexample behavior:
- `privilege_gain = true` — the process gains elevated privileges
- `setuid_exec = true` — a setuid binary is executed
```

Pre-generated copy: [`evidence/report.md`](evidence/report.md)

## What this does NOT prove

- Does **not** probe a live MCP server or call `tools/call`.
- Does **not** confirm `create_pull_request` exists on any real host.
- Does **not** replace responsible disclosure or runtime boundary testing.
- Counterexamples are **model behaviors** in the abstract sandbox encoding, not confirmed exploits.
