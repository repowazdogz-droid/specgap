"""Semantic divergence detection across the three specification layers.

This layer is structural: it compares the *sets* of extracted constraints. The
Z3 layer (``z3_checker``) then checks implication failures over extracted
constraints and returns counterexamples when they exist.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import CATEGORY_ORDER, Constraint, Divergence, SOURCE_LABELS

# Strict intent constraints that downstream layers are expected to preserve.
STRICT = {"no_network", "readonly_fs", "no_privilege_escalation", "no_write_outside_dir"}

# Weaker / partial forms a strict constraint can be silently relaxed into.
WEAKER_OF: dict[str, set[str]] = {
    "no_network": {"localhost_only", "network_allowed"},
    "readonly_fs": {"readonly_root_fs", "write_allowed"},
    "no_privilege_escalation": {"setuid_allowed", "no_cap_sys_admin", "no_root"},
    "no_write_outside_dir": {"write_allowed"},
}

# Constraints that directly contradict a strict intent constraint.
DIRECT_CONTRADICTION: dict[str, set[str]] = {
    "no_network": {"network_allowed"},
    "readonly_fs": set(),
    "no_privilege_escalation": set(),
    "no_write_outside_dir": set(),
}

# Permission-granting constraints (an allowance, not a restriction).
PERMISSIONS = {"localhost_only", "network_allowed", "write_allowed", "setuid_allowed"}


@dataclass
class DiffResult:
    divergences: list[Divergence] = field(default_factory=list)
    table: list[dict] = field(default_factory=list)  # one row per category

    @property
    def high_severity(self) -> list[Divergence]:
        return [d for d in self.divergences if d.severity == "high"]


def _names(constraints: list[Constraint]) -> set[str]:
    return {c.name for c in constraints}


def _labels(constraints: list[Constraint], category: str) -> str:
    items = [c.label() for c in constraints if c.category == category]
    return "; ".join(items) if items else "—"


def build_table(by_source: dict[str, list[Constraint]]) -> list[dict]:
    """Build a per-category comparison row across the three layers."""
    rows: list[dict] = []
    present = {c.category for cs in by_source.values() for c in cs}
    for category in CATEGORY_ORDER:
        if category not in present:
            continue
        rows.append({
            "category": category,
            "stakeholder_intent": _labels(by_source["stakeholder_intent"], category),
            "formalized_policy": _labels(by_source["formalized_policy"], category),
            "implementation_claim": _labels(by_source["implementation_claim"], category),
        })
    return rows


def diff(by_source: dict[str, list[Constraint]]) -> DiffResult:
    """Detect semantic divergences between the three specification layers."""
    divergences: list[Divergence] = []
    intent = by_source["stakeholder_intent"]
    intent_names = _names(intent)
    intent_strict_categories = {c.category for c in intent if c.name in STRICT}

    for downstream in ("formalized_policy", "implementation_claim"):
        d_constraints = by_source[downstream]
        for sc in intent:
            if sc.name not in STRICT:
                continue
            cat = sc.category
            d_cat = {c.name for c in d_constraints if c.category == cat}

            if sc.name in d_cat:
                pass  # constraint preserved verbatim
            else:
                weaker = d_cat & WEAKER_OF.get(sc.name, set())
                if weaker:
                    divergences.append(Divergence(
                        kind="weakened_constraint",
                        category=cat,
                        severity="high",
                        summary=f"'{sc.label()}' is weakened in {SOURCE_LABELS[downstream]}",
                        detail=(f"Stakeholder intent states the strict constraint "
                                f"'{sc.label()}', but {SOURCE_LABELS[downstream]} only "
                                f"expresses the weaker form(s): "
                                f"{', '.join(sorted(weaker))}."),
                        sources=["stakeholder_intent", downstream],
                    ))
                elif not d_cat:
                    divergences.append(Divergence(
                        kind="missing_constraint",
                        category=cat,
                        severity="high",
                        summary=f"'{sc.label()}' is missing from {SOURCE_LABELS[downstream]}",
                        detail=(f"Stakeholder intent states '{sc.label()}', but "
                                f"{SOURCE_LABELS[downstream]} contains no {cat} "
                                f"constraint at all."),
                        sources=["stakeholder_intent", downstream],
                    ))
                else:
                    divergences.append(Divergence(
                        kind="weakened_constraint",
                        category=cat,
                        severity="high",
                        summary=f"'{sc.label()}' is only partially covered in "
                                f"{SOURCE_LABELS[downstream]}",
                        detail=(f"Stakeholder intent states '{sc.label()}', but "
                                f"{SOURCE_LABELS[downstream]} expresses different "
                                f"{cat} constraints: {', '.join(sorted(d_cat))}."),
                        sources=["stakeholder_intent", downstream],
                    ))

            contra = d_cat & DIRECT_CONTRADICTION.get(sc.name, set())
            if contra:
                divergences.append(Divergence(
                    kind="contradictory_constraint",
                    category=cat,
                    severity="high",
                    summary=f"'{sc.label()}' is contradicted in {SOURCE_LABELS[downstream]}",
                    detail=(f"Stakeholder intent forbids this, but "
                            f"{SOURCE_LABELS[downstream]} explicitly allows it "
                            f"({', '.join(sorted(contra))})."),
                    sources=["stakeholder_intent", downstream],
                ))

    # implementation claim not implied by stated intent
    for c in by_source["implementation_claim"]:
        if c.name in PERMISSIONS and c.name not in intent_names \
                and c.category in intent_strict_categories:
            divergences.append(Divergence(
                kind="claim_not_implied",
                category=c.category,
                severity="high",
                summary=f"Implementation claim '{c.label()}' is not implied by intent",
                detail=(f"The implementation claim grants '{c.label()}', a permission "
                        f"the stakeholder intent never states. The intent's {c.category} "
                        f"requirement is strict, so this claim broadens behavior beyond "
                        f"what was asked for."),
                sources=["stakeholder_intent", "implementation_claim"],
            ))

    # ambiguous constraints
    for source, constraints in by_source.items():
        for c in constraints:
            if c.ambiguous:
                divergences.append(Divergence(
                    kind="ambiguous_constraint",
                    category=c.category,
                    severity="medium",
                    summary=f"'{c.label()}' is stated ambiguously in {SOURCE_LABELS[source]}",
                    detail=(f"The {c.category} constraint in {SOURCE_LABELS[source]} uses "
                            f"hedging language, so its strength cannot be determined "
                            f"deterministically."),
                    sources=[source],
                ))

    return DiffResult(divergences=divergences, table=build_table(by_source))
