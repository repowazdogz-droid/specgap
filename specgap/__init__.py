"""SpecGap: specification-divergence detection via constrained extraction and Z3.

SpecGap does not prove the spec is correct. It identifies specification-divergence
zones and checks extracted constraints for implication failures over the abstract
sandbox model.
"""

__version__ = "0.1.0"

from .assurance import (
    ASSURANCE_RESULT_SCHEMA,
    ENCODING_VERSION,
    SPECGAP_DETAIL_SCHEMA,
    SPECGAP_KIND,
    analyze_structured,
    input_fingerprint,
)

__all__ = [
    "__version__",
    "ASSURANCE_RESULT_SCHEMA",
    "ENCODING_VERSION",
    "SPECGAP_DETAIL_SCHEMA",
    "SPECGAP_KIND",
    "analyze_structured",
    "input_fingerprint",
]
