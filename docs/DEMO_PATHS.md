# SpecGap demo paths

Pick one path by time budget. Index of examples: [`EXAMPLE_INDEX.md`](EXAMPLE_INDEX.md). Diagrams: [`DIAGRAMS.md`](DIAGRAMS.md).

---

## 2-minute skim

**Goal:** Understand the thesis without running code.

| Step | File | Time |
| --- | --- | --- |
| 1 | [`SPECGAP_ABSTRACT.md`](SPECGAP_ABSTRACT.md) | 1 min |
| 2 | [`DIAGRAMS.md`](DIAGRAMS.md) — diagram A only | 30 sec |
| 3 | [`EXAMPLE_INDEX.md`](EXAMPLE_INDEX.md) — sandbox no-network row | 30 sec |

**Expected takeaway:** SpecGap catches **layered spec drift** before runtime and emits **replayable evidence**; PASS/FAIL is bounded to extracted constraints in an abstract model.

**Do NOT infer:** That you have seen a working demo, formal proof of safety, or runtime validation.

---

## 10-minute technical walkthrough

**Goal:** Skim, run one example, read one report section.

| Step | File / command | Time |
| --- | --- | --- |
| 1 | [`SPECGAP_ONE_PAGE.md`](SPECGAP_ONE_PAGE.md) | 2 min |
| 2 | [`DIAGRAMS.md`](DIAGRAMS.md) — all three | 1 min |
| 3 | Clone repo; `pip install -r requirements.txt` | 2 min |
| 4 | `python -m specgap.cli examples/sandbox_no_network.json --out /tmp/demo.md` | 1 min |
| 5 | Open `/tmp/demo.md` → **Z3 Formal Check** + counterexample | 2 min |
| 6 | [`REPLAYABLE_EVIDENCE_EXAMPLE.md`](REPLAYABLE_EVIDENCE_EXAMPLE.md) — replay `diff` step | 2 min |

**Expected takeaway:** You can reproduce a **FAIL** with a concrete counterexample assignment; same input yields the same report.

**Do NOT infer:** Network isolation is verified in production; localhost loophole is exploitable; SpecGap replaces pentest or sandbox eval.

---

## 30-minute deep dive

**Goal:** Thesis + triangulation + operational mapping + boundaries.

| Step | File / command | Time |
| --- | --- | --- |
| 1 | Complete [10-minute path](#10-minute-technical-walkthrough) | 10 min |
| 2 | `python -m specgap.cli examples/operational/02_multi_agent_policy_divergence/spec.json --out /tmp/op2.md` | 2 min |
| 3 | Read `/tmp/op2.md` → **Triangulation Summary** (Agreement = **no**) | 3 min |
| 4 | [`WHY_DISAGREEMENT_MATTERS.md`](WHY_DISAGREEMENT_MATTERS.md) | 5 min |
| 5 | [`OPERATIONAL_EXAMPLES.md`](OPERATIONAL_EXAMPLES.md) + one operational README | 5 min |
| 6 | [`ASSURANCE_BOUNDARY.md`](ASSURANCE_BOUNDARY.md) or [`THREAT_MODEL_SUMMARY.md`](THREAT_MODEL_SUMMARY.md) | 5 min |

**Expected takeaway:** SpecGap preserves **heterogeneous signals**; operational narratives map honestly onto a **fixed sandbox TCB**; assurance stops at written spec layers.

**Do NOT infer:** Multi-agent runtime is modeled; MCP servers were tested; compliance or certification is implied; disagreement always means a bug in one mechanism (it may be lattice/encoding gap).

---

## One-liner for reviewers

> Pre-runtime layered spec divergence checks with triangulated structural + Z3 evidence, deterministic replay, explicit boundaries — not runtime safety proof.

Paste links: [`SHAREABLE_LINKS.md`](SHAREABLE_LINKS.md)
