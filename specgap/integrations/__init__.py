"""Optional interoperability bridges (pre-runtime assurance only)."""

from .boxarena_adapter import BoxArenaPreflightResult, run_boxarena_preflight

__all__ = ["BoxArenaPreflightResult", "run_boxarena_preflight"]
