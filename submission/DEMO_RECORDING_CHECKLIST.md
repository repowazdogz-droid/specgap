# SpecGap Demo Recording Checklist

For Apart Research judging, researcher onboarding, or public demo recordings.

**Before recording:** fresh venv, commands run once offline to confirm output.

```bash
cd specgap
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

**Fallback if `pip` fails (PEP 668):** ensure venv is activated; never use `--break-system-packages` on camera unless you explain why.

---

## Screen layout

- Terminal: full width, font ≥ 14pt, light or dark theme with good contrast.
- Optional second pane: Markdown report (`reports/demo_report.md`) in an editor — open *after* the CLI run, not instead of it.
- Working directory visible in prompt: `…/specgap`.

---

## 3-minute version (~180 s)

| Time | Action | What to say (optional, one line) |
| --- | --- | --- |
| 0:00–0:20 | Show README opening paragraph | "Specs drift between intent, policy, and implementation." |
| 0:20–0:50 | **Command 1** (headline demo) | "Rule extraction plus Z3 implication check over an abstract sandbox model." |
| 0:50–1:30 | Open report → **Z3 Formal Check** + **Counterexample** | Point at `network_send=true`, `dest_localhost=true` — implication failure, not exploit proof. |
| 1:30–2:10 | **Command 2** (rule mode, paraphrase) | "Rule vocabulary misses 'air-gapped' — extraction failure, not a clean pass." |
| 2:10–2:40 | **Command 3** (fuzzy mode, same file) | "Fuzzy recovery is advisory; human review required — then same counterexample." |
| 2:40–3:00 | **Command 4** (`pytest`) | "Z3 calls are real, not mocked." |

### Commands (3-minute)

```bash
python -m specgap.cli examples/sandbox_no_network.json --out reports/demo_report.md
```

**Expected:**

```
SpecGap: analyzed 'Network-isolated analysis sandbox' (extractor: rule)
  semantic divergences: 3
  failed implication checks: 2 of 2
  report written to: reports/demo_report.md
```

**Show in report:** Counterexample with `network_send = true`, `dest_localhost = true`.

```bash
python -m specgap.cli examples/04_paraphrased_sandbox.json --extractor rule --out reports/04_rule_report.md
```

**Expected (note WARNING):**

```
  WARNING: extraction failure — stakeholder intent yielded zero constraints; this is NOT a clean result
  semantic divergences: 0
  failed implication checks: 0 of 2
```

```bash
python -m specgap.cli examples/04_paraphrased_sandbox.json --extractor fuzzy --out reports/04_fuzzy_report.md
```

**Expected:**

```
  semantic divergences: 3
  failed implication checks: 2 of 2
```

**Show in report:** `source=fuzzy`, `requires_human_review=true` on intent constraint.

```bash
pytest -q
```

**Expected:** `41 passed` (count may change — run once before recording and pin the number on screen).

---

## 5-minute version (~300 s)

Everything in the 3-minute flow, plus:

| Time | Action |
| --- | --- |
| 3:00–3:45 | **Command 5** — candidate evaluation |
| 3:45–4:30 | Scroll report: Validation Outcomes table + one counterexample each for B and C |
| 4:30–5:00 | State limitations aloud: abstract model, no semantic correctness proof, ordering is not a score |

### Command 5 (5-minute add-on)

```bash
python -m specgap.cli examples/05_candidate_policy_ranking.json --evaluate-candidates --out reports/05_candidate_evaluation_report.md
```

**Expected:**

```
SpecGap: evaluated 3 candidate(s) for 'Candidate sandbox policies for a network-isolated, privilege-bounded cell' (extractor: rule)
  Candidate A: PASS
  Candidate B: FAIL (1 implication failure(s))
  Candidate C: FAIL (1 implication failure(s))
  candidate order (fewest implication failures first): A > B > C
  report written to: reports/05_candidate_evaluation_report.md
```

**Show in report:**

- Candidate B counterexample: `network_send`, `dest_localhost`
- Candidate C counterexample: `privilege_gain`, `cap_sys_admin`
- **Candidate Ordering** section — stress "not a leaderboard"

---

## Fallback plan

| Failure | Recovery |
| --- | --- |
| `ModuleNotFoundError: z3` | `pip install -r requirements.txt` in active venv |
| `pip install` PEP 668 error | `python3 -m venv .venv && source .venv/bin/activate` then retry |
| `python` not found | Use `python3 -m specgap.cli …` |
| Wrong directory | `cd specgap` — examples path must exist |
| pytest count differs | Run `pytest -q` once pre-recording; update spoken line |
| Fuzzy mode slow (>5 s) | Normal offline; cut to terminal output only, skip scrolling full fuzzy report |
| Report file missing | Re-run the same `--out` command; path is relative to `specgap/` |

**Do not** improvise new examples on camera — stick to the five JSON files in `examples/`.

---

## Claims discipline (say or show on slide)

- "Implication failure over **extracted constraints** in an **abstract sandbox model**."
- "Does **not** prove semantic correctness or runtime security."
- "Fuzzy extraction requires **human review**."
- Candidate order = **implication-failure count**, not policy quality.

---

## Post-recording

- [ ] Verify recording shows WARNING line on rule-mode paraphrase run
- [ ] Verify counterexample literals match report (not paraphrased from memory)
- [ ] Optional: link to `tutorials/` in video description
