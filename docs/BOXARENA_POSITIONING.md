# SpecGap × BoxArena — Positioning & Workflow

## Core framing

> **BoxArena** tests whether the sandbox resists adversarial behavior.
> **SpecGap** checks whether the sandbox policy/specification actually encodes
> the confinement guarantees humans intended — *before the agent runs.*

**SpecGap is a pre-flight specification divergence check, not runtime enforcement.**

The two are complementary, not competing:

- BoxArena answers: *"Does the box hold against an adversary?"*
- SpecGap answers: *"Does the box's written policy even describe the box we
  meant to build?"*

A clean BoxArena run on a sandbox whose policy quietly diverged from intent is a
false sense of security: the agent did not escape *this time*, but the
confinement spec still permits behavior the stakeholder forbade. SpecGap closes
that gap before the run.

## Threat model

**What SpecGap addresses — specification drift, not runtime escape:**

- Intent rephrased into policy rephrased into implementation claim, where each
  step is locally reasonable but the end-to-end result is weaker than intended.
- Silent constraint weakening (`no_network` becomes `localhost_only`).
- Permissions appearing in the implementation that the intent never granted
  (`claim_not_implied`).
- Paraphrased intent that the rule vocabulary misses — surfaced as an explicit
  *extraction failure*, never hidden as a clean result.

**What SpecGap explicitly does NOT address:**

- It does not run the agent or observe runtime behavior — that is BoxArena.
- It does not enforce anything at runtime — that is the seccomp/namespace layer.
- It does not model a real kernel, container runtime, or seccomp engine; the Z3
  model is an abstract propositional model of sandbox behavior.
- It does not certify the specification is correct — it locates divergence
  zones and produces counterexamples.
- It does not catch a correctly-specified-but-buggy *implementation* — a
  faithful spec with a broken build is exactly what BoxArena is for.

**Trust boundary:** SpecGap operates on the *written specification*, not the
running system.

## Where SpecGap fits in the pipeline

```
1. Author intent / policy / implementation claim
2. SpecGap  ── pre-flight ──▶  extract constraints, Z3 implication check
                               divergence? fix the spec before building
3. Build the sandbox
4. BoxArena ── runtime ────▶  adversarial agent evaluation of the built sandbox
5. Runtime enforcement (seccomp, namespaces, ...) — the actual box
```

SpecGap sits at **step 2**: between writing a confinement spec and trusting it
enough to build and adversarially test. It is the cheapest place to catch a
confinement gap — before compute is spent on a build or a BoxArena run, and
before a divergent spec is mistaken for a safe one.

## One concrete workflow

### Pre-flight (SpecGap — specification divergence)

Before spending BoxArena adversarial budget on a target whose written policy may
already diverge from intent:

```bash
cd specgap
python -m specgap.cli examples/boxarena_preflight_divergence.json \
  --boxarena-preflight \
  --out reports/boxarena_preflight_report.md \
  --evidence-out reports/boxarena_preflight_evidence.json
```

SpecGap emits:
- a Markdown report (including triangulation summary)
- a JSON **evidence-chain** artifact (`phase: specgap_preflight`)
- an **advisory** `proceed_to_boxarena` flag and a **suggested** BoxArena harness
  command (not executed)

Exit code `1` on pre-flight `fail` (divergence / implication failure / empty
intent extraction) so CI may gate runtime evaluation.

### Runtime evaluation (BoxArena — empirical adversarial)

After reviewing (and optionally fixing) the spec:

```bash
cd box-arena/harness
uv run harness run --runtime=runc --quest=net_lateral --model=mockllm/model --no-publish
```

BoxArena observes **runtime behavior** under adversarial pressure. It does **not**
re-check specification alignment — that was SpecGap's pre-flight job.

---

### Worked example: network isolation drift

A "no network access" sandbox is headed into BoxArena.

1. **Stakeholder intent:** "The sandbox must have no network access."
2. **Policy author formalizes:** "Localhost connections are allowed for the
   local metrics collector."
3. **Implementation claim:** "Only loopback (localhost) traffic is permitted."

**Without SpecGap:** BoxArena runs an adversarial agent. If the agent does not
happen to exfiltrate over localhost during the run, the result reads as clean —
and the team ships a sandbox whose policy permits localhost network traffic the
stakeholder forbade. The divergence was on paper the whole time.

**With SpecGap pre-flight:**

```bash
python -m specgap.cli examples/boxarena_preflight_divergence.json --boxarena-preflight
```

Or the generic triple example:

```bash
python -m specgap.cli examples/sandbox_no_network.json --out report.md
```

SpecGap extracts `no_network` from the intent and `localhost_only` from the
policy and implementation, then Z3 returns a concrete implication failure in
the abstract sandbox model:

```
network_send = true, dest_localhost = true
→ the policy permits a network behavior the intent forbids
```

The team fixes the policy — or amends the intent, if localhost really is
acceptable — *before* the BoxArena run. BoxArena then spends its adversarial
budget on a target whose specification actually matches intent, instead of one
that was already wrong on paper.

## Summary

SpecGap is the pre-flight check; BoxArena is the runtime test; the
seccomp/namespace layer is the enforcement. SpecGap reporting "no divergence"
means only that no divergence was detected between the spec layers — runtime
confinement remains BoxArena's and the enforcement layer's responsibility.
