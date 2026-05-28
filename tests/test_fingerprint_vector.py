"""Cross-language RFC 8785 fingerprint vector (contracts alignment)."""

from __future__ import annotations

import hashlib
import json
import pathlib
import sys

import rfc8785

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from specgap.assurance import ingress_fingerprint, input_fingerprint, specgap_input_payload
from specgap.models import SpecInput

VECTOR = pathlib.Path(__file__).resolve().parents[1] / "fixtures" / "specgap" / "fingerprint_vector.json"


def test_fingerprint_vector_matches_rfc8785():
    data = json.loads(VECTOR.read_text(encoding="utf-8"))
    ingress = data["ingress"]
    expected = data["input_fingerprint"]
    assert len(expected) == 64
    actual = ingress_fingerprint(ingress)
    assert actual == expected
    canonical = rfc8785.dumps(ingress)
    assert hashlib.sha256(canonical).hexdigest() == expected


def test_input_fingerprint_matches_vector_for_sandbox_example():
    data = json.loads(VECTOR.read_text(encoding="utf-8"))
    spec = SpecInput(
        title=data["ingress"]["title"],
        stakeholder_intent=data["ingress"]["stakeholder_intent"],
        formalized_policy=data["ingress"]["formalized_policy"],
        implementation_claim=data["ingress"]["implementation_claim"],
    )
    assert specgap_input_payload(spec) == data["ingress"]
    assert input_fingerprint(spec) == data["input_fingerprint"]
