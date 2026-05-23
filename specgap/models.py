"""Core data models for SpecGap.

A ``Constraint`` is a single canonical security capability statement extracted
from one of the three specification layers. The layers are deliberately kept
separate so divergence between them can be measured.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# The three specification layers SpecGap compares.
SOURCES = ("stakeholder_intent", "formalized_policy", "implementation_claim")

SOURCE_LABELS = {
    "stakeholder_intent": "Stakeholder Intent",
    "formalized_policy": "Formalized Policy",
    "implementation_claim": "Implementation Claim",
}

# canonical constraint name -> (category, strength, polarity)
#   strength: strict | partial | permission | policy
CONSTRAINT_META: dict[str, tuple[str, str, str]] = {
    "no_network": ("network", "strict", "forbid"),
    "network_allowed": ("network", "permission", "allow"),
    "localhost_only": ("network", "partial", "allow"),
    "readonly_fs": ("filesystem", "strict", "forbid"),
    "readonly_root_fs": ("filesystem", "partial", "restrict"),
    "write_allowed": ("filesystem", "permission", "allow"),
    "no_write_outside_dir": ("filesystem", "strict", "restrict"),
    "no_privilege_escalation": ("privilege", "strict", "forbid"),
    "no_root": ("privilege", "partial", "forbid"),
    "no_cap_sys_admin": ("privilege", "partial", "forbid"),
    "setuid_allowed": ("privilege", "permission", "allow"),
    "syscall_allowlist": ("syscall", "policy", "restrict"),
    "syscall_denylist": ("syscall", "policy", "restrict"),
}

LABELS = {
    "no_network": "No network access",
    "network_allowed": "Network access allowed",
    "localhost_only": "Localhost/loopback network allowed",
    "readonly_fs": "Read-only filesystem (strict, no writes)",
    "readonly_root_fs": "Root filesystem read-only (writes possible elsewhere)",
    "write_allowed": "Writes allowed",
    "no_write_outside_dir": "No writes outside declared directory",
    "no_privilege_escalation": "No privilege escalation",
    "no_root": "No root / non-root execution",
    "no_cap_sys_admin": "CAP_SYS_ADMIN dropped/unavailable",
    "setuid_allowed": "setuid binary execution allowed",
    "syscall_allowlist": "Syscall allowlist",
    "syscall_denylist": "Syscall denylist",
}

CATEGORY_ORDER = ("network", "filesystem", "privilege", "syscall")


@dataclass
class Constraint:
    """One canonical capability statement extracted from a spec layer."""

    name: str
    source: str
    raw_text: str
    params: dict = field(default_factory=dict)
    method: str = "rule"          # rule | fuzzy | llm_stub
    ambiguous: bool = False
    confidence: float = 1.0       # 1.0 for deterministic rule extraction
    requires_human_review: bool = False  # always True for fuzzy-extracted constraints

    @property
    def category(self) -> str:
        return CONSTRAINT_META.get(self.name, ("unknown", "", ""))[0]

    @property
    def strength(self) -> str:
        return CONSTRAINT_META.get(self.name, ("", "unknown", ""))[1]

    @property
    def polarity(self) -> str:
        return CONSTRAINT_META.get(self.name, ("", "", "unknown"))[2]

    def label(self) -> str:
        base = LABELS.get(self.name, self.name)
        if self.name == "write_allowed" and self.params.get("path"):
            return f"Writes allowed to {self.params['path']}"
        if self.name in ("syscall_denylist", "syscall_allowlist") and self.params.get("syscalls"):
            return f"{base} ({', '.join(self.params['syscalls'])})"
        return base


@dataclass
class SpecInput:
    """A single specification triple plus its title and expected issue."""

    title: str
    stakeholder_intent: str
    formalized_policy: str
    implementation_claim: str
    expected_issue: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "SpecInput":
        missing = [k for k in ("title", "stakeholder_intent", "formalized_policy",
                               "implementation_claim") if k not in data]
        if missing:
            raise ValueError(f"input is missing required fields: {', '.join(missing)}")
        return cls(
            title=data["title"],
            stakeholder_intent=data["stakeholder_intent"],
            formalized_policy=data["formalized_policy"],
            implementation_claim=data["implementation_claim"],
            expected_issue=data.get("expected_issue", ""),
        )

    def text_for(self, source: str) -> str:
        return getattr(self, source)


@dataclass
class Candidate:
    """One candidate policy implementation to evaluate against an intent."""

    id: str
    label: str
    policy: str


@dataclass
class CandidateSpec:
    """One stakeholder intent plus N candidate policy implementations.

    This is the candidate-evaluation input shape. Instead of the fixed intent /
    claim triple, it pairs a single stakeholder intent with a list of candidate
    policies that are extracted and evaluated independently against that intent.
    """

    title: str
    stakeholder_intent: str
    candidates: list = field(default_factory=list)
    expected: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "CandidateSpec":
        missing = [k for k in ("title", "stakeholder_intent", "candidates")
                   if k not in data]
        if missing:
            raise ValueError(
                f"candidate input is missing required fields: {', '.join(missing)}")
        raw = data["candidates"]
        if not isinstance(raw, list) or not raw:
            raise ValueError("candidate input must contain a non-empty "
                             "'candidates' list")
        candidates: list[Candidate] = []
        for i, c in enumerate(raw):
            cmissing = [k for k in ("id", "label", "policy") if k not in c]
            if cmissing:
                raise ValueError(
                    f"candidate #{i + 1} is missing fields: {', '.join(cmissing)}")
            candidates.append(Candidate(id=str(c["id"]), label=str(c["label"]),
                                        policy=str(c["policy"])))
        return cls(title=data["title"],
                   stakeholder_intent=data["stakeholder_intent"],
                   candidates=candidates, expected=data.get("expected", ""))


@dataclass
class Divergence:
    """A detected semantic divergence between specification layers."""

    kind: str          # missing_constraint | weakened_constraint | contradictory_constraint
                       # | ambiguous_constraint | claim_not_implied
    category: str
    severity: str      # high | medium | low
    summary: str
    detail: str
    sources: list = field(default_factory=list)
