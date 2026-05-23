# Tutorial 2: Rule vs Fuzzy Extraction

This tutorial shows why SpecGap uses a hybrid pipeline: deterministic rule extraction first, optional fuzzy recovery second, SMT checking last.

**Prerequisites:** Tutorial 1. Venv + `pip install -r requirements.txt` (see Tutorial 1).

---

## Background

Constraint extraction is the load-bearing step before any Z3 query runs.

| Mode | Flag | Behavior |
| --- | --- | --- |
| Rule (default) | `--extractor rule` | Deterministic pattern matching over a fixed vocabulary. Fully offline. Auditable. |
| Fuzzy (opt-in) | `--extractor fuzzy` | Rule pass first; then paraphrase fallback (Anthropic API if `ANTHROPIC_API_KEY` is set, otherwise a deterministic offline paraphrase map). |

**Critical guard:** if rule extraction yields **zero** constraints from the stakeholder intent, SpecGap reports an **extraction failure**. That is not a clean result. Implication checks against an empty intent are skipped.

Fuzzy-extracted constraints are **advisory**. They carry `source=fuzzy`, a confidence score, and `requires_human_review=true`. SMT validates the extracted atoms — it does not certify that "air-gapped" was correctly mapped to `no_network`.

---

## The example

File: `examples/04_paraphrased_sandbox.json`

The stakeholder intent says the container must be **"air-gapped from any external service"** — a paraphrase of strict network isolation. The policy allows localhost; the implementation permits loopback.

The divergence is the same as Tutorial 1 *once* the intent is recognized as `no_network`. The question is whether extraction recovers that atom.

---

## Step 1 — Rule extraction (vocabulary-bound)

```bash
cd specgap
python -m specgap.cli examples/04_paraphrased_sandbox.json --extractor rule --out reports/02_rule_report.md
```

**Expected terminal output:**

```
SpecGap: analyzed 'Paraphrased air-gapped sandbox' (extractor: rule)
  WARNING: extraction failure — stakeholder intent yielded zero constraints; this is NOT a clean result
  semantic divergences: 0
  failed implication checks: 0 of 2
  report written to: reports/02_rule_report.md
```

**Expected excerpt from the report (Summary):**

```
- ⚠️ **EXTRACTION FAILURE — NOT A CLEAN RESULT.** Stakeholder intent yielded zero extracted constraints.
  Divergence cannot be checked against an empty intent. This is NOT a clean result — it is an extraction failure.
```

**Expected excerpt (Extracted Constraints):**

```
**Stakeholder Intent**
- _(no constraints extracted)_

**Formalized Policy**
- `localhost_only` — Localhost/loopback network allowed [network/partial, via rule]
```

**Expected excerpt (Z3 Formal Check):**

```
### Formalized Policy ⇒ Stakeholder Intent

- No strict target constraints to check against. _(skipped)_
```

### What happened?

The rule extractor looks for phrases like "no network", "network-isolated", "no outbound" (see `specgap/extractor.py`). **"Air-gapped" is not in that vocabulary.** The intent layer extracts nothing.

With no intent constraints, SpecGap cannot run a meaningful implication check. The report shows zero divergences and zero failed checks — which looks like success but is an **extraction failure guard** firing on the CLI warning line.

This is intentional: silently treating an empty extraction as "no requirements" would hide the gap.

---

## Step 2 — Fuzzy extraction (paraphrase recovery)

```bash
python -m specgap.cli examples/04_paraphrased_sandbox.json --extractor fuzzy --out reports/02_fuzzy_report.md
```

**Expected terminal output:**

```
SpecGap: analyzed 'Paraphrased air-gapped sandbox' (extractor: fuzzy)
  semantic divergences: 3
  failed implication checks: 2 of 2
  report written to: reports/02_fuzzy_report.md
```

**Expected excerpt (Extracted Constraints):**

```
**Stakeholder Intent**
- `no_network` — No network access [network/strict, via fuzzy] _(source=fuzzy, confidence=0.55, requires_human_review=true)_
```

**Expected excerpt (Z3 implication failure — same as Tutorial 1):**

```
Counterexample behavior:
- `network_send = true` — a network connection is opened
- `dest_localhost = true` — the connection destination is localhost / loopback
```

### What happened?

Fuzzy mode ran the rule pass (still zero from intent), then the offline paraphrase map matched "air-gapped" → `no_network`. The constraint is flagged for human review before you treat it as authoritative.

With `no_network` recovered, the pipeline proceeds: structural diff finds weakened constraints, Z3 finds the localhost counterexample in the abstract model.

Without `ANTHROPIC_API_KEY`, the offline map is used. With the API key set, Anthropic extraction may produce different confidence values; the human-review requirement applies either way.

---

## Why hybrid fuzzy + SMT is useful

| Component | Strength | Weakness |
| --- | --- | --- |
| Rule extraction | Deterministic, auditable, offline | Vocabulary-bound; misses paraphrase |
| Fuzzy extraction | Recovers non-canonical phrasing | Nondeterministic (API) or map-limited (offline); requires review |
| Z3 implication check | Exact over given constraints | Only as good as the extracted atoms |

The hybrid design keeps auditability for the common case (rule mode) while allowing a bounded recovery path for paraphrase. SMT does not replace human judgment on fuzzy mappings — it checks implications **after** you decide whether to trust the recovered constraint.

---

## Human review requirement (explicit)

**Fuzzy extraction is advisory.** Before acting on a fuzzy-derived `no_network`:

1. Read the original intent text.
2. Confirm the mapping is faithful for your threat model.
3. If the mapping is wrong, fix the text or add a rule — do not rely on the counterexample alone.

Z3 will faithfully check wrong extractions. That is why `requires_human_review=true` is surfaced in the report, not buried in logs.

---

## Limitations

- Offline fuzzy coverage is a small hand-written map, not general NLP.
- API fuzzy mode adds nondeterminism and external dependency.
- A candidate or policy can "pass" by extraction omission (nothing extracted → nothing to violate). Rule mode makes omission visible via the extraction-failure warning.
- Fuzzy recovery does not expand the Z3 model — only the constraint set feeding it.

---

## Next step

- Add a rule pattern for domain phrasing you trust, then confirm fuzzy mode is no longer needed for that phrase.
- Run Tutorial 3 to evaluate multiple candidate policies against one extracted intent.
- Read `specgap/extractor.py` and `tests/test_semantic_diff.py` before extending the vocabulary.
