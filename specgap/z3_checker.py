"""Z3 layer: real SMT consistency and implication checks.

SpecGap models each specification layer as a set of restrictions over an
abstract sandbox *behavior*. A behavior is a propositional assignment to atoms
such as ``network_send`` or ``setuid_exec``.

A constraint set C is satisfied by a behavior b when b violates none of C's
restrictions. The implication check ``C_a => C_b`` asks: is every behavior
permitted by C_a also permitted by C_b? Z3 looks for a counterexample — a
behavior permitted by the antecedent but forbidden by the consequent.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import z3

from .models import Constraint

# Abstract behavior atoms.
ATOM_NAMES = (
    "network_send", "dest_localhost", "dest_external",
    "fs_write", "write_tmp", "write_other",
    "privilege_gain", "setuid_exec", "cap_sys_admin", "run_as_root",
    "syscall_invoked", "syscall_on_allowlist", "syscall_on_denylist",
)

ATOM_HUMAN = {
    "network_send": "a network connection is opened",
    "dest_localhost": "the connection destination is localhost / loopback",
    "dest_external": "the connection destination is an external host",
    "fs_write": "a filesystem write occurs",
    "write_tmp": "the write target is /tmp",
    "write_other": "the write target is outside /tmp",
    "privilege_gain": "the process gains elevated privileges",
    "setuid_exec": "a setuid binary is executed",
    "cap_sys_admin": "CAP_SYS_ADMIN is exercised",
    "run_as_root": "the process runs as root",
    "syscall_invoked": "a guarded syscall is invoked",
    "syscall_on_allowlist": "the invoked syscall is on the allowlist",
    "syscall_on_denylist": "the invoked syscall is on the denylist",
}


def _atoms() -> dict[str, z3.BoolRef]:
    return {name: z3.Bool(name) for name in ATOM_NAMES}


def _domain_axioms(a: dict[str, z3.BoolRef]) -> list[z3.BoolRef]:
    """Facts true of every behavior, independent of any spec layer."""
    return [
        # a network send goes to exactly one kind of destination
        a["network_send"] == z3.Or(a["dest_localhost"], a["dest_external"]),
        z3.Not(z3.And(a["dest_localhost"], a["dest_external"])),
        # a filesystem write targets exactly one location class
        a["fs_write"] == z3.Or(a["write_tmp"], a["write_other"]),
        z3.Not(z3.And(a["write_tmp"], a["write_other"])),
        # privilege is gained only via a known vector (setuid or CAP_SYS_ADMIN)
        a["privilege_gain"] == z3.Or(a["setuid_exec"], a["cap_sys_admin"]),
        # a syscall cannot be on both lists, and listing implies invocation
        z3.Implies(a["syscall_on_allowlist"], z3.Not(a["syscall_on_denylist"])),
        z3.Implies(z3.Or(a["syscall_on_allowlist"], a["syscall_on_denylist"]),
                   a["syscall_invoked"]),
    ]


def _constraint_formula(c: Constraint, a: dict[str, z3.BoolRef]) -> z3.BoolRef:
    """Restriction a behavior must satisfy to be permitted by constraint ``c``."""
    true = z3.BoolVal(True)
    mapping = {
        "no_network": z3.Not(a["network_send"]),
        "network_allowed": true,
        "localhost_only": z3.Implies(a["network_send"], a["dest_localhost"]),
        "readonly_fs": z3.Not(a["fs_write"]),
        "readonly_root_fs": z3.Implies(a["fs_write"], a["write_tmp"]),
        "write_allowed": true,
        "no_write_outside_dir": z3.Implies(a["fs_write"], a["write_tmp"]),
        "no_privilege_escalation": z3.Not(a["privilege_gain"]),
        "no_root": z3.Not(a["run_as_root"]),
        "no_cap_sys_admin": z3.Not(a["cap_sys_admin"]),
        # setuid allowance: privilege gain, if any, must use the setuid vector
        "setuid_allowed": z3.And(
            z3.Implies(a["privilege_gain"], a["setuid_exec"]),
            z3.Implies(a["privilege_gain"], z3.Not(a["cap_sys_admin"])),
        ),
        "syscall_allowlist": z3.Implies(a["syscall_invoked"], a["syscall_on_allowlist"]),
        "syscall_denylist": z3.Implies(a["syscall_invoked"], z3.Not(a["syscall_on_denylist"])),
    }
    return mapping.get(c.name, true)


@dataclass
class ImplicationResult:
    antecedent_label: str
    consequent_label: str
    status: str                       # implied | implication_failed | no_consequent
    implied: bool
    z3_check: str = ""                # sat | unsat | (empty)
    counterexample: dict = field(default_factory=dict)
    counterexample_atoms: list = field(default_factory=list)  # atoms true in CE
    consequent_violated: list = field(default_factory=list)   # constraint names


@dataclass
class ConsistencyResult:
    label: str
    consistent: bool
    z3_check: str


def check_consistency(constraints: list[Constraint], label: str) -> ConsistencyResult:
    """Is this constraint set internally satisfiable (no contradiction)?"""
    a = _atoms()
    solver = z3.Solver()
    for axiom in _domain_axioms(a):
        solver.add(axiom)
    for c in constraints:
        solver.add(_constraint_formula(c, a))
    result = solver.check()
    return ConsistencyResult(label=label, consistent=(result == z3.sat),
                             z3_check=str(result))


def check_implication(antecedent: list[Constraint], consequent: list[Constraint],
                      antecedent_label: str, consequent_label: str) -> ImplicationResult:
    """Check whether the antecedent constraint set implies the consequent set.

    Returns an ``implication_failed`` result with a concrete counterexample
    behavior when the antecedent permits something the consequent forbids.
    """
    if not consequent:
        return ImplicationResult(antecedent_label, consequent_label,
                                 status="no_consequent", implied=True)

    a = _atoms()
    solver = z3.Solver()
    for axiom in _domain_axioms(a):
        solver.add(axiom)
    for c in antecedent:
        solver.add(_constraint_formula(c, a))
    # a behavior permitted by the antecedent but violating >=1 consequent rule
    solver.add(z3.Or([z3.Not(_constraint_formula(c, a)) for c in consequent]))

    result = solver.check()
    if result == z3.sat:
        model = solver.model()
        ce = {n: z3.is_true(model.eval(a[n], model_completion=True)) for n in ATOM_NAMES}
        violated = [
            c.name for c in consequent
            if not z3.is_true(model.eval(_constraint_formula(c, a), model_completion=True))
        ]
        return ImplicationResult(
            antecedent_label, consequent_label,
            status="implication_failed", implied=False, z3_check="sat",
            counterexample=ce,
            counterexample_atoms=[n for n, v in ce.items() if v],
            consequent_violated=violated,
        )
    return ImplicationResult(antecedent_label, consequent_label,
                             status="implied", implied=True, z3_check="unsat")
