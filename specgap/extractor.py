"""Constraint extraction.

Extraction is rule-first. The default ``rule`` mode uses deterministic
rule-based parsing only and needs no API key. The opt-in ``fuzzy`` mode
(``--extractor fuzzy``) adds paraphrase-aware fallback extraction: the
Anthropic API when ``ANTHROPIC_API_KEY`` is set, otherwise a deterministic
offline paraphrase map. Fuzzy-extracted constraints are flagged
``requires_human_review`` and are not authoritative.
"""

from __future__ import annotations

import re

from .models import Constraint, SpecInput

# Hedge words that make a constraint statement ambiguous.
HEDGES = ("should", "generally", "typically", "mostly", "as needed",
          "where possible", "if possible", "preferably", "usually")


def _ambiguous(text: str) -> bool:
    low = text.lower()
    return any(h in low for h in HEDGES)


def _network(text: str, low: str, source: str, ambiguous: bool) -> list[Constraint]:
    found: list[Constraint] = []
    if any(p in low for p in ("no network", "cannot reach the internet",
                              "no internet", "network-isolated", "no outbound",
                              "without network")):
        found.append(Constraint("no_network", source, "no network access", ambiguous=ambiguous))
    if "localhost" in low or "loopback" in low:
        found.append(Constraint("localhost_only", source, "localhost/loopback allowed",
                                ambiguous=ambiguous))
    if any(p in low for p in ("network access is allowed", "internet access is allowed",
                              "outbound connections are allowed", "full network access")):
        found.append(Constraint("network_allowed", source, "network access allowed",
                                ambiguous=ambiguous))
    return found


def _filesystem(text: str, low: str, source: str, ambiguous: bool) -> list[Constraint]:
    found: list[Constraint] = []
    has_ro = "read-only" in low or "read only" in low
    if has_ro:
        if any(p in low for p in ("root filesystem", "root fs", "mounts / read-only",
                                  "/ read-only")):
            found.append(Constraint("readonly_root_fs", source,
                                    "root filesystem read-only", ambiguous=ambiguous))
        elif "filesystem" in low or "cannot modify any files" in low or "no file modification" in low:
            found.append(Constraint("readonly_fs", source,
                                    "read-only filesystem", ambiguous=ambiguous))
    # writable path
    path = None
    if "/tmp" in low and any(p in low for p in ("write", "writable", "tmpfs")):
        path = "/tmp"
    else:
        m = re.search(r"writes? allowed to (\S+)", low) or re.search(r"write access to (\S+)", low)
        if m:
            path = m.group(1).rstrip(".,;")
    if path:
        found.append(Constraint("write_allowed", source, f"writes allowed to {path}",
                                params={"path": path}, ambiguous=ambiguous))
    if "no write outside" in low or "writes outside" in low and "forbidden" in low:
        found.append(Constraint("no_write_outside_dir", source,
                                "no writes outside declared directory", ambiguous=ambiguous))
    return found


def _privilege(text: str, low: str, source: str, ambiguous: bool) -> list[Constraint]:
    found: list[Constraint] = []
    if any(p in low for p in ("no privilege escalation", "escalate privilege",
                              "no privesc", "privilege-bounded")):
        found.append(Constraint("no_privilege_escalation", source,
                                "no privilege escalation", ambiguous=ambiguous))
    if "setuid" in low and "no setuid" not in low:
        found.append(Constraint("setuid_allowed", source, "setuid binaries allowed",
                                ambiguous=ambiguous))
    if "cap_sys_admin" in low and any(p in low for p in ("dropped", "unavailable",
                                                         "removed", "not available")):
        found.append(Constraint("no_cap_sys_admin", source, "CAP_SYS_ADMIN dropped/unavailable",
                                ambiguous=ambiguous))
    if any(p in low for p in ("non-root", "no root", "not run as root",
                              "cannot run as root", "not running as root")):
        found.append(Constraint("no_root", source, "non-root execution", ambiguous=ambiguous))
    return found


def _syscall(text: str, low: str, source: str, ambiguous: bool) -> list[Constraint]:
    found: list[Constraint] = []
    if any(p in low for p in ("syscall denylist", "syscall blacklist", "blocked syscalls")) or (
        "seccomp" in low and "denylist" in low
    ):
        syscalls = _parse_syscall_list(low, ("blocking", "denylist", "blacklist", "blocks"))
        found.append(Constraint("syscall_denylist", source, "syscall denylist",
                                params={"syscalls": syscalls}, ambiguous=ambiguous))
    if any(p in low for p in ("syscall allowlist", "syscall whitelist", "allowed syscalls")):
        syscalls = _parse_syscall_list(low, ("allowlist", "whitelist", "allowing"))
        found.append(Constraint("syscall_allowlist", source, "syscall allowlist",
                                params={"syscalls": syscalls}, ambiguous=ambiguous))
    return found


def _parse_syscall_list(low: str, anchors: tuple[str, ...]) -> list[str]:
    """Pull syscall names appearing shortly after an anchor word."""
    for anchor in anchors:
        idx = low.find(anchor)
        if idx == -1:
            continue
        tail = low[idx + len(anchor): idx + len(anchor) + 80]
        names = re.findall(r"[a-z_]{3,}", tail)
        stop = {"and", "the", "syscall", "syscalls", "profile", "uses", "for"}
        picked = [n for n in names if n not in stop][:6]
        if picked:
            return picked
    return []


_CATEGORY_RULES = (_network, _filesystem, _privilege, _syscall)


def extract_constraints(text: str, source: str) -> list[Constraint]:
    """Deterministically extract canonical constraints from one spec layer."""
    low = text.lower()
    ambiguous = _ambiguous(text)
    out: list[Constraint] = []
    for rule in _CATEGORY_RULES:
        out.extend(rule(text, low, source, ambiguous))
    out.extend(llm_extract_stub(text, source))
    return out


def extract_all(spec: SpecInput, mode: str = "rule") -> dict[str, list[Constraint]]:
    """Extract constraints for all three specification layers.

    ``mode`` is ``"rule"`` (default, deterministic) or ``"fuzzy"`` (rule-first,
    then fuzzy fallback for paraphrases the rules missed).
    """
    by_source: dict[str, list[Constraint]] = {}
    for source in ("stakeholder_intent", "formalized_policy", "implementation_claim"):
        text = getattr(spec, source)
        constraints = extract_constraints(text, source)
        if mode == "fuzzy":
            known = {c.name for c in constraints}
            for fuzzy_c in fuzzy_extract(text, source):
                if fuzzy_c.name not in known:    # rule-first: fuzzy only fills gaps
                    known.add(fuzzy_c.name)
                    constraints.append(fuzzy_c)
        by_source[source] = constraints
    return by_source


# --- Fuzzy / LLM hook ---------------------------------------------------------

LLM_EXTRACTION_ENABLED = False

# Deterministic offline fuzzy paraphrase fallback. This is NOT a real LLM; it
# is a tiny hand-written paraphrase map so the hybrid demo runs offline.
PARAPHRASE_MAP = {
    "air-gapped": "no_network",
    "external service": "no_network",
    "outside its own isolated execution cell": "no_network",
}


def llm_extract_stub(text: str, source: str) -> list[Constraint]:
    """Reserved hook inside the rule pass. Always returns nothing."""
    if not LLM_EXTRACTION_ENABLED:
        return []
    return []  # pragma: no cover - reserved


def fuzzy_extract(text: str, source: str) -> list[Constraint]:
    """Fuzzy/paraphrase-aware extraction for a single spec layer.

    Uses the Anthropic API when ``ANTHROPIC_API_KEY`` is set; otherwise falls
    back to the deterministic offline paraphrase map. Every constraint produced
    here is marked ``method="fuzzy"``, carries a confidence, and is flagged
    ``requires_human_review=True`` — fuzzy extraction is not authoritative.
    """
    import os

    if os.environ.get("ANTHROPIC_API_KEY"):
        try:
            return _fuzzy_extract_via_anthropic(text, source)
        except Exception:  # noqa: BLE001 - any failure falls back, never crashes
            pass
    return _fuzzy_extract_via_paraphrase_map(text, source)


def _fuzzy_extract_via_paraphrase_map(text: str, source: str) -> list[Constraint]:
    """Offline fuzzy paraphrase fallback (deterministic, no API, no key)."""
    low = text.lower()
    out: list[Constraint] = []
    seen: set[str] = set()
    for phrase, name in PARAPHRASE_MAP.items():
        if phrase in low and name not in seen:
            seen.add(name)
            out.append(Constraint(
                name=name, source=source,
                raw_text=f"offline fuzzy paraphrase fallback: matched '{phrase}'",
                method="fuzzy", confidence=0.55, requires_human_review=True,
            ))
    return out


def _fuzzy_extract_via_anthropic(text: str, source: str) -> list[Constraint]:
    """Map paraphrased spec text to canonical constraints via the Anthropic API.

    Raises on any problem (missing SDK, network, bad JSON); ``fuzzy_extract``
    catches that and falls back to the offline paraphrase map.
    """
    import json as _json

    import anthropic  # raises ImportError if the SDK is not installed

    from .models import CONSTRAINT_META

    allowed = sorted(CONSTRAINT_META)
    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
    prompt = (
        "You map a sandbox specification sentence to canonical security "
        f"constraints. Allowed constraint names: {allowed}. "
        'Return ONLY a JSON list of {"name": <allowed name>, "confidence": 0-1}. '
        "Return [] if none apply.\n\nSentence: " + text
    )
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )
    data = _json.loads(message.content[0].text)
    out: list[Constraint] = []
    for item in data:
        name = item.get("name")
        if name in CONSTRAINT_META:
            out.append(Constraint(
                name=name, source=source,
                raw_text=f"fuzzy/LLM extraction: {text[:70]}",
                method="fuzzy", confidence=float(item.get("confidence", 0.5)),
                requires_human_review=True,
            ))
    return out
