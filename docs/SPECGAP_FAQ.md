# SpecGap — FAQ

Short answers for external readers. Details: [`ASSURANCE_BOUNDARY.md`](ASSURANCE_BOUNDARY.md) · [`TCB.md`](TCB.md).

---

**Is this formal verification?**

Partially, and narrowly. SpecGap uses Z3 to check implication between **extracted** constraints in a **declared abstract model**. It is not end-to-end verification of a deployment, kernel, or implementation.

**Does this prove systems are safe?**

No. FAIL means preservation failed in the model for extracted constraints. PASS means no such failure was found—not that the system is safe, the English spec is complete, or runtime enforcement matches the document.

**Why not use one spec?**

Real systems accumulate layers (intent → policy → implementation claim) across teams and tools. SpecGap targets drift **between** those layers, not syntax within one file.

**Why preserve disagreement?**

Structural diff and Z3 inspect different abstractions. When they diverge, merging them hides signal. Disagreement rows often flag lattice or encoding gaps worth fixing before trusting a single verdict.

**Is this runtime monitoring?**

No. SpecGap reads written specs only. Runtime assurance, penetration testing, and sandbox execution are separate obligations.

**What does replayable evidence mean?**

Same JSON input + `--extractor rule` → same extraction and Z3 results. A reviewer clones the repo, runs one CLI command, and compares Markdown reports—no vendor attestation required.

**Why Z3?**

To produce concrete implication failures and counterexample assignments in a small propositional sandbox encoding. Scope is quantifier-free SAT/SMT over documented atoms—not full system models.

**Relationship to OMEGA Lab?**

SpecGap is the public **Assurance** trunk repo: evidence before runtime. It complements **Replay** (clearpath), **Substrate** (omega-contracts), and **Doctrine** (omega-lean-proof). Stack map: [TRUST_STACK](https://github.com/repowazdogz-droid/omega-contracts/blob/main/docs/TRUST_STACK.md).

**What are the biggest limitations?**

1. **Partial extraction** — unmatched English is omitted, not interpreted.  
2. **Abstract model only** — not Linux, MCP live traffic, or containers.  
3. **No runtime truth** — a consistent spec stack can still be mis-implemented.  
4. **Fixed vocabulary** — operational domains (MCP, multi-agent) map onto sandbox atoms honestly, not exhaustively.

More: [`THREAT_MODEL_SUMMARY.md`](THREAT_MODEL_SUMMARY.md) · [`ENCODING.md`](ENCODING.md).
