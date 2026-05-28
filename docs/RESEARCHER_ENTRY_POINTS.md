# SpecGap researcher entry points

Route readers by type. Full packets: [`OUTREACH_PACKETS.md`](OUTREACH_PACKETS.md). Anti-hype: [`SPECGAP_POSITIONING_ANTI_PATTERNS.md`](SPECGAP_POSITIONING_ANTI_PATTERNS.md).

| Person type | Starting file | Why it matters to them | Likely reaction | Best follow-up artifact |
| --- | --- | --- | --- | --- |
| **FM person** | [`ENCODING.md`](ENCODING.md) | Shows exact atoms, axioms, and implication queries—not hand-wavy "verified" | "Small model; where's the soundness story?" | [`TCB.md`](TCB.md) + regenerated report from [`sandbox_no_network.json`](../examples/sandbox_no_network.json) |
| **Infra / security** | [`EXAMPLE_INDEX.md`](EXAMPLE_INDEX.md) | Maps operator scenarios to detections without claiming runtime proof | "Nice linter; will it catch my prod config?" | [`operational/03_configuration_drift/`](../examples/operational/03_configuration_drift/evidence/report.md) + [`ASSURANCE_BOUNDARY.md`](ASSURANCE_BOUNDARY.md) |
| **Agent-evals** | [`THREAT_MODEL_SUMMARY.md`](THREAT_MODEL_SUMMARY.md) | Separates spec-faithfulness checks from runtime eval pass | "Not an eval harness" | [`operational/02_multi_agent_policy_divergence/`](../examples/operational/02_multi_agent_policy_divergence/) triangulation table |
| **Governance** | [`SPECGAP_ABSTRACT.md`](SPECGAP_ABSTRACT.md) | Bounded language suitable for audit trails and fellowship forms | "Not compliance-ready" | [`REPLAYABLE_EVIDENCE_EXAMPLE.md`](REPLAYABLE_EVIDENCE_EXAMPLE.md) + `diff` replay instructions |
| **Skeptical engineer** | [`SPECGAP_FAQ.md`](SPECGAP_FAQ.md) | Front-loads "what this is not" | "So it's grep + Z3?" | Live CLI output: `python -m specgap.cli examples/sandbox_no_network.json --out /tmp/x.md` |
| **Product-minded operator** | [`DEMO_PATHS.md`](DEMO_PATHS.md) (10-min) | Time-boxed path to thesis + one run | "Where's the dashboard?" | [`DIAGRAMS.md`](DIAGRAMS.md) diagram A + [`OPERATIONAL_EXAMPLES.md`](OPERATIONAL_EXAMPLES.md) |

---

## Fellowship / application fields

| Field | Paste from |
| --- | --- |
| Short abstract (250–400 words) | [`SPECGAP_ABSTRACT.md`](SPECGAP_ABSTRACT.md) |
| "Limitations" paragraph | [`SPECGAP_FAQ.md`](SPECGAP_FAQ.md) last Q + [`ASSURANCE_BOUNDARY.md`](ASSURANCE_BOUNDARY.md) opening |
| "Reproduce our results" | [`REPLAYABLE_EVIDENCE_EXAMPLE.md`](REPLAYABLE_EVIDENCE_EXAMPLE.md) one command |
| Link list | [`SHAREABLE_LINKS.md`](SHAREABLE_LINKS.md) |

---

## Follow-up rules

| Do | Don't |
| --- | --- |
| Send one artifact that answers their skepticism row | Send progressively more docs without a question |
| Offer a failing fixture PR scope | Promise integration timeline |
| Point to disagreement example if they ask about single PASS/FAIL | Schedule a call before they run quickstart |

---

## If they only click one link

Send: **repo root** with anchor to [`SPECGAP_ABSTRACT.md`](SPECGAP_ABSTRACT.md) — [`RESEARCHER_ENTRY_POINTS.md`](RESEARCHER_ENTRY_POINTS.md) (this file) is optional second link for routing.
