# 03 — Configuration drift

**Operational pressure:** Deployment config (`NETWORK_MODE=open`) **silently broadens** network scope while health checks on loopback still pass — runtime "works," intent does not.

**Primary signal:** Implication **FAIL** on network layer; structural weakening from `no_network` → `localhost_only` → `network_allowed`.

## Layered specs

| Layer | Content |
| --- | --- |
| Stakeholder intent | Production: no outbound network |
| Formalized policy | Helm: localhost egress for metrics sidecar |
| Implementation claim | Config declares full network access; health checks on loopback only |

## Run

```bash
python -m specgap.cli examples/operational/03_configuration_drift/spec.json \
  --out examples/operational/03_configuration_drift/evidence/report.md
```

## Expected terminal output

```
SpecGap: analyzed 'Deployment configuration drift — silent network broadening' (extractor: rule)
  triangulation: structural diff and Z3 agree
  semantic divergences: 5
  failed implication checks: 2 of 2
  report written to: examples/operational/03_configuration_drift/evidence/report.md
```

## Expected report excerpt

```markdown
- **[contradictory_constraint]** … 'No network access' is contradicted in Implementation Claim

### Implementation Claim ⇒ Stakeholder Intent

- **Result: implication FAILS.** …
- Violated target constraint(s): `no_network`

Counterexample behavior:
- `network_send = true` — a network connection is opened
- `dest_localhost = true` — the connection destination is localhost / loopback
```

Structural section also flags `network_allowed` contradicting strict `no_network` — the config broadening is visible before runtime.

Pre-generated copy: [`evidence/report.md`](evidence/report.md)

## Operational note

Catch this **before** deploy: config review is cheaper than incident reconstruction. A green health check does not reconcile a broadened config layer with strict no-network intent.

## What this does NOT prove

- Does **not** read live Helm values, Kubernetes APIs, or environment variables.
- Does **not** predict production egress behavior.
- Does **not** certify compliance with any regulatory framework.
- Extraction uses fixed phrase rules — rephrase config text and constraints may not extract.
