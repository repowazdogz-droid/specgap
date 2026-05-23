"""SpecGap MCP tool handlers."""

from .analyze_spec import run as analyze_spec
from .evaluate_candidates import run as evaluate_candidates
from .boxarena_preflight import run as boxarena_preflight

__all__ = ["analyze_spec", "evaluate_candidates", "boxarena_preflight"]
