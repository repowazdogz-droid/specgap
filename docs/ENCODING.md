# Abstract Sandbox Model

SpecGap represents sandbox **behaviors** as assignments to a fixed set of **boolean atoms**. Each extracted **constraint** compiles to a Z3 formula over those atoms. A behavior is **permitted by a layer** when it satisfies all of that layer’s constraint formulas **and** the domain axioms.

**Implication check:** for downstream constraints **P** and intent constraints **I**, Z3 searches for an assignment such that:

```
domain_axioms ∧ ⋀_{c ∈ P} formula(c) ∧ ⋁_{c ∈ I} ¬formula(c)
```

If the query is `sat`, an **implication failure** exists; the model is reported as a counterexample. If `unsat`, no such assignment exists under this encoding.

Source of truth: `specgap/z3_checker.py` (`ATOM_NAMES`, `_domain_axioms`, `_constraint_formula`).

---

# Behavior Atoms

| Atom | Intended reading (abstract) |
| --- | --- |
| `network_send` | A network connection is opened |
| `dest_localhost` | Destination is localhost / loopback |
| `dest_external` | Destination is an external host |
| `fs_write` | A filesystem write occurs |
| `write_tmp` | Write target is `/tmp` (class) |
| `write_other` | Write target is outside `/tmp` (class) |
| `privilege_gain` | Process gains elevated privileges |
| `setuid_exec` | A setuid binary is executed |
| `cap_sys_admin` | CAP_SYS_ADMIN is exercised |
| `run_as_root` | Process runs as root |
| `syscall_invoked` | A guarded syscall is invoked |
| `syscall_on_allowlist` | Invoked syscall is on allowlist |
| `syscall_on_denylist` | Invoked syscall is on denylist |

These are **propositional flags**, not an executable semantics of Linux, seccomp, or containers.

---

# Constraint Encoding Table

Each row is the formula a behavior must satisfy to be **permitted** by that constraint (i.e. the constraint is a restriction on allowed behaviors).

| Constraint | Meaning (informal) | Z3 interpretation |
| --- | --- | --- |
| `no_network` | No network access | `¬network_send` |
| `localhost_only` | If network is used, destination is localhost only | `network_send → dest_localhost` |
| `network_allowed` | Network permitted (unrestricted in model) | `true` *(vacuous)* |
| `readonly_fs` | No filesystem writes | `¬fs_write` |
| `readonly_root_fs` | Writes only to `/tmp` class if any write | `fs_write → write_tmp` |
| `write_allowed` | Writes permitted (path in extraction metadata only) | `true` *(vacuous)* |
| `no_write_outside_dir` | Writes only to `/tmp` class if any write | `fs_write → write_tmp` |
| `no_privilege_escalation` | No privilege gain | `¬privilege_gain` |
| `no_root` | Does not run as root | `¬run_as_root` |
| `no_cap_sys_admin` | CAP_SYS_ADMIN not exercised | `¬cap_sys_admin` |
| `setuid_allowed` | If privilege is gained, it is via setuid (not cap) | `(privilege_gain → setuid_exec) ∧ (privilege_gain → ¬cap_sys_admin)` |
| `syscall_allowlist` | If syscall invoked, it is on allowlist | `syscall_invoked → syscall_on_allowlist` |
| `syscall_denylist` | If syscall invoked, it is not on denylist | `syscall_invoked → ¬syscall_on_denylist` |

**Required rows (minimum):**

| Constraint | Meaning | Z3 interpretation |
| --- | --- | --- |
| `no_network` | Strict prohibition on network send | `¬network_send` |
| `localhost_only` | Loopback-only egress when sending | `network_send → dest_localhost` |
| `no_privilege_escalation` | No abstract privilege gain | `¬privilege_gain` |
| `setuid_allowed` | Privilege gain, if modeled, uses setuid vector | `(privilege_gain → setuid_exec) ∧ (privilege_gain → ¬cap_sys_admin)` |
| `no_cap_sys_admin` | CAP_SYS_ADMIN not used | `¬cap_sys_admin` |

Unknown constraint names compile to **`true`** (no restriction) — a latent vacuity if extraction invents unmapped names.

---

# Domain Axioms

Always enforced in both consistency and implication queries:

| Axiom | Formula (conceptual) |
| --- | --- |
| Network destination | `network_send ↔ (dest_localhost ∨ dest_external)` |
| Exclusive destinations | `¬(dest_localhost ∧ dest_external)` |
| Write location | `fs_write ↔ (write_tmp ∨ write_other)` |
| Exclusive write classes | `¬(write_tmp ∧ write_other)` |
| Privilege vectors | `privilege_gain ↔ (setuid_exec ∨ cap_sys_admin)` |
| Syscall lists disjoint | `syscall_on_allowlist → ¬syscall_on_denylist` |
| List membership implies invocation | `(syscall_on_allowlist ∨ syscall_on_denylist) → syscall_invoked` |

**Localhost semantics:** `localhost_only` does not forbid `network_send`; it restricts destination when send occurs. Therefore a behavior with `network_send ∧ dest_localhost` satisfies `localhost_only` but violates `no_network` — the canonical SpecGap demo case.

**Privilege semantics:** `setuid_allowed` does not force `setuid_exec` in all models; it constrains how **privilege_gain** may occur. Combined with `no_privilege_escalation` on the intent side, counterexamples typically show `privilege_gain ∧ setuid_exec`.

**Not modeled:** coupling between `run_as_root` and `privilege_gain`; per-syscall names from extracted denylist parameters; temporal ordering; multiple processes.

---

# Known Vacuities / Simplifications

| Issue | Impact |
| --- | --- |
| `network_allowed`, `write_allowed` → `true` | Extraction may record permission; Z3 adds no restriction |
| Syscall parameters ignored | Parsed syscall names in constraint metadata are not atoms in Z3 |
| `run_as_root` isolated | May be true without triggering `privilege_gain` under axioms |
| `WEAKER_OF` lattice | Structural diff only; not exported as Z3 formulas |
| Default `true` for unknown constraints | Silent permissiveness if vocabulary drifts |
| No state / no traces | Single-shot propositional snapshot only |
| No kernel / seccomp / cgroup semantics | Abstraction is intentional; see [`TCB.md`](TCB.md) |

Documenting vacuities is required for expert trust. A reported implication failure is **relative to this encoding**, not relative to full sandbox semantics.

---

# Counterexamples

When an implication query returns `sat`, Z3 produces a **model** — one satisfying assignment.

SpecGap:

1. Evaluates each atom with `model.eval(atom, model_completion=True)`
2. Lists atoms assigned `true` as **counterexample behavior**
3. Identifies which intent constraint formulas evaluate to `false` under that model

**Interpretation:**

- Counterexamples witness **∃** violating assignment in the abstract model
- They are **illustrative**, not unique minimal witnesses
- They are **not exploit proofs** and do not demonstrate runtime sandbox bypass
- `model_completion=True` may set atoms to default values; spurious `true` atoms should be read cautiously — prefer atoms tied to violated constraints and domain axioms

Example (network divergence): `network_send = true`, `dest_localhost = true` — permitted by `localhost_only`, violates `no_network`.

Example (setuid divergence): `privilege_gain = true`, `setuid_exec = true` — consistent with `setuid_allowed`, violates `no_privilege_escalation`.

For the correctness target and implication direction, see [`SPECIFICATION.md`](SPECIFICATION.md).
