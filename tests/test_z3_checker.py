"""Tests for the Z3 formal layer. These exercise real Z3 calls, not mocks."""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from specgap.models import Constraint
from specgap.z3_checker import check_consistency, check_implication


def _c(name, source="formalized_policy", **params):
    return Constraint(name=name, source=source, raw_text=name, params=params)


def test_localhost_only_does_not_imply_no_network():
    """Example A: 'localhost only' must not imply 'no network access'."""
    result = check_implication([_c("localhost_only")], [_c("no_network", "stakeholder_intent")],
                               "Policy", "Intent")
    assert result.implied is False
    assert result.z3_check == "sat"
    assert "no_network" in result.consequent_violated
    # the counterexample is a real network behavior to localhost
    assert result.counterexample["network_send"] is True
    assert result.counterexample["dest_localhost"] is True


def test_readonly_root_plus_write_does_not_imply_readonly_fs():
    """Example B: root-read-only + /tmp write must not imply strict read-only."""
    antecedent = [_c("readonly_root_fs"), _c("write_allowed", path="/tmp")]
    result = check_implication(antecedent, [_c("readonly_fs", "stakeholder_intent")],
                               "Policy", "Intent")
    assert result.implied is False
    assert result.counterexample["fs_write"] is True
    assert result.counterexample["write_tmp"] is True


def test_setuid_allowed_does_not_imply_no_privilege_escalation():
    """Example C: allowing setuid binaries must not imply no privilege escalation."""
    antecedent = [_c("no_cap_sys_admin"), _c("setuid_allowed")]
    result = check_implication(antecedent, [_c("no_privilege_escalation", "stakeholder_intent")],
                               "Implementation", "Intent")
    assert result.implied is False
    # privilege is gained specifically via the setuid vector
    assert result.counterexample["privilege_gain"] is True
    assert result.counterexample["setuid_exec"] is True
    assert result.counterexample["cap_sys_admin"] is False


def test_identical_constraint_implies_itself():
    """A constraint set trivially implies itself: Z3 returns unsat for the negation."""
    result = check_implication([_c("no_network")], [_c("no_network", "stakeholder_intent")],
                               "Policy", "Intent")
    assert result.implied is True
    assert result.z3_check == "unsat"


def test_no_consequent_is_skipped():
    result = check_implication([_c("no_network")], [], "Policy", "Intent")
    assert result.status == "no_consequent"
    assert result.implied is True


def test_consistency_of_normal_constraint_set():
    """A normal sandbox constraint set is internally satisfiable."""
    result = check_consistency([_c("no_network"), _c("readonly_fs"),
                                _c("no_privilege_escalation")], "Intent")
    assert result.consistent is True
    assert result.z3_check == "sat"


def test_policy_denylist_still_misses_setuid_vector():
    """A syscall denylist + capability drop still does not imply no-privesc."""
    antecedent = [_c("no_cap_sys_admin"), _c("syscall_denylist", syscalls=["ptrace", "clone"])]
    result = check_implication(antecedent, [_c("no_privilege_escalation", "stakeholder_intent")],
                               "Policy", "Intent")
    assert result.implied is False
    assert result.counterexample["setuid_exec"] is True
