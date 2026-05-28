# SpecGap positioning anti-patterns

Wrong descriptions that trigger justified skepticism. Preferred framing for each. Share before DMs: link this file.

---

## "Formal verification" (misuse)

| | |
| --- | --- |
| **Dangerous because** | FM readers expect soundness proofs over real systems; investors expect certifiable deployments |
| **Preferred framing** | "Implication checks over **extracted** constraints in a **declared abstract model**"; full FM is [`omega-lean-proof`](https://github.com/repowazdogz-droid/omega-lean-proof), separate layer |

---

## "Proves systems are safe"

| | |
| --- | --- |
| **Dangerous because** | Implies runtime, implementation, and adversary models are covered |
| **Preferred framing** | "Reports implication failure or divergence **in the spec stack as encoded**"; PASS ≠ safe |

---

## AGI / alignment theater

| | |
| --- | --- |
| **Dangerous because** | Attracts wrong reviewers, wrong fellowship fit, wrong expectations |
| **Preferred framing** | "Pre-runtime spec drift evidence"; "assurance before runtime" — not alignment solution |

---

## "AI governance platform"

| | |
| --- | --- |
| **Dangerous because** | Suggests product UI, policy packs, org-wide enforcement |
| **Preferred framing** | "Assurance-layer CLI + replayable reports in OMEGA Lab trunk" |

---

## "Runtime safety guarantee"

| | |
| --- | --- |
| **Dangerous because** | SpecGap never executes code, MCP, or containers |
| **Preferred framing** | "Pre-runtime; runtime assurance is a separate obligation (sandbox, pentest, monitoring)" |

---

## "Trustworthy AI" / "ethical AI engine"

| | |
| --- | --- |
| **Dangerous because** | Marketing vapor; no technical referent |
| **Preferred framing** | Name the check: structural weakening, Z3 implication, triangulation disagreement |

---

## Benchmark obsession

| | |
| --- | --- |
| **Dangerous because** | Invites leaderboard gaming; hides TCB and extraction gaps |
| **Preferred framing** | Cite **example IDs** and report paths; [`EXAMPLE_INDEX.md`](EXAMPLE_INDEX.md) not scores |

---

## Autonomous gating claims

| | |
| --- | --- |
| **Dangerous because** | Implies SpecGap blocks deploy, stops agents, or emits enforceable HOLD |
| **Preferred framing** | "Evidence for human/integrator review"; OMEGA `HELD` is record encoding elsewhere—not SpecGap output |

---

## "Single spec would be enough"

| | |
| --- | --- |
| **Dangerous because** | Denies the actual failure mode (hand-offs between layers) |
| **Preferred framing** | "Drift accumulates **across** intent, policy, and implementation claim" |

---

## "MCP / multi-agent fully modeled"

| | |
| --- | --- |
| **Dangerous because** | Operational examples use sandbox atom mapping; readers expect live protocol checks |
| **Preferred framing** | "Operational **narrative** on fixed vocabulary"; see [`OPERATIONAL_EXAMPLES.md`](OPERATIONAL_EXAMPLES.md) honesty section |

---

## "Compliance automation" / "satisfies ISO / EU AI Act"

| | |
| --- | --- |
| **Dangerous because** | Legal/regulatory liability; misstates integrator scope |
| **Preferred framing** | "Illustrative evidence shape for reviewers—not certification" |

---

## "Kernel verified" / "seccomp proved"

| | |
| --- | --- |
| **Dangerous because** | Syscall/network atoms are propositional abstractions, not Linux models |
| **Preferred framing** | "Abstract sandbox encoding in [`ENCODING.md`](ENCODING.md)" |

---

## "One merged PASS/FAIL score"

| | |
| --- | --- |
| **Dangerous because** | Hides triangulation disagreement—the most informative rows |
| **Preferred framing** | "Structural and Z3 reported separately; Agreement = no is signal" |

---

## "Please mentor me" / prestige name-dropping

| | |
| --- | --- |
| **Dangerous because** | Shifts frame from falsifiable artifact to social proof |
| **Preferred framing** | "One failing fixture or boundary critique welcome" — [`RESEARCH_DIRECTIONS.md`](RESEARCH_DIRECTIONS.md) collaboration norms |

---

## Quick self-check before send

1. Did I say **pre-runtime**?
2. Did I say **extracted constraints / abstract model**?
3. Did I avoid **safe, aligned, compliant, autonomous gate**?
4. Is the link **SpecGap repo**, not whole OMEGA product surface?
5. Is there a **replay command** they can run without me?

If any fail → revise using [`SPECGAP_ABSTRACT.md`](SPECGAP_ABSTRACT.md) and [`OUTREACH_PACKETS.md`](OUTREACH_PACKETS.md).
