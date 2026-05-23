"""Shared path resolution and JSON helpers for SpecGap MCP tools."""

from __future__ import annotations

import json
import sys
from pathlib import Path

# specgap-mcp/tools/ → specgap repo root (two levels up)
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORT_DIR = REPO_ROOT / "reports" / "mcp"


def ensure_specgap_importable() -> None:
    """Allow `import specgap` when the package is not installed editable."""
    root = str(REPO_ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)


def resolve_input_path(raw: str) -> Path:
    """Resolve a spec JSON path relative to the SpecGap repo root."""
    path = Path(raw)
    if path.is_absolute():
        return path
    return (REPO_ROOT / path).resolve()


def resolve_output_path(raw: str | None, *, default_name: str) -> Path:
    if raw:
        path = Path(raw)
        if not path.is_absolute():
            path = (REPO_ROOT / path).resolve()
    else:
        DEFAULT_REPORT_DIR.mkdir(parents=True, exist_ok=True)
        path = DEFAULT_REPORT_DIR / default_name
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def triangulation_label(*, intent_empty: bool, any_disagreement: bool) -> str:
    if intent_empty:
        return "indeterminate"
    return "disagree" if any_disagreement else "agree"


def json_text(payload: dict) -> str:
    return json.dumps(payload, indent=2, sort_keys=True)
