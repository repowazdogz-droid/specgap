# SpecGap diagrams

Three small diagrams. Full pipeline detail: [`ARCHITECTURE_OVERVIEW.md`](ARCHITECTURE_OVERVIEW.md).

---

## A. Layered spec flow

```mermaid
flowchart LR
  P[Policy layers<br/>intent · policy · claim] --> N[Normalized rules<br/>extracted constraints]
  N --> I[Implication check<br/>Z3 + structural diff]
  I --> D[Divergence<br/>weakening · not implied]
  D --> E[Evidence<br/>Markdown report]
```

**Read:** Written layers → canonical constraints → logical checks → findings → replayable artifact. No runtime step.

---

## B. Triangulation model

Three spec layers checked by two independent mechanisms. Outcomes are **not merged**.

```mermaid
flowchart TB
  subgraph SPECS["Three layers"]
    A[Intent A]
    B[Policy B]
    C[Claim C]
  end

  A --> SD[Structural diff]
  B --> SD
  C --> SD

  A --> Z3[Z3 implication]
  B --> Z3
  C --> Z3

  SD --> T{Per layer}
  Z3 --> T
  T -->|agree| OK[Both signals align]
  T -->|disagree| DIS[Both rows kept<br/>no single verdict]
```

**Read:** Structural diff can be silent while Z3 fails (or vice versa). **Disagreement preserved** in the report table — not averaged away.

Example: [`examples/operational/02_multi_agent_policy_divergence/`](../examples/operational/02_multi_agent_policy_divergence/).

---

## C. Replayable evidence lifecycle

```mermaid
flowchart LR
  IN[Input JSON] --> RUN[CLI run<br/>--extractor rule]
  RUN --> REP[Report .md]
  REP --> RE[Replay<br/>same command]
  RE --> AUD[Audit<br/>diff reports]
```

**Read:** Evidence is a regenerable file. Independent reviewer runs the same command and compares output — no platform attestation required.

Walkthrough: [`REPLAYABLE_EVIDENCE_EXAMPLE.md`](REPLAYABLE_EVIDENCE_EXAMPLE.md).
