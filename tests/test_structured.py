"""Tests for AssuranceResult envelope (analyze_structured)."""

from __future__ import annotations

import copy
import json
import pathlib
import sys

import jsonschema
import pytest
from jsonschema import Draft7Validator
from jsonschema.validators import RefResolver

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from specgap import __version__
from specgap.assurance import analyze_structured, input_fingerprint
from specgap.models import SpecInput

EXAMPLES = pathlib.Path(__file__).resolve().parents[1] / "examples"
SCHEMAS = pathlib.Path(__file__).resolve().parents[1] / "schemas"


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _schema_validator() -> Draft7Validator:
    schema_dir = SCHEMAS
    base = schema_dir.as_uri() + "/"
    assurance = json.loads(
        (schema_dir / "assurance-result-1.0.schema.json").read_text(encoding="utf-8")
    )
    detail = json.loads(
        (schema_dir / "specgap-detail-1.0.schema.json").read_text(encoding="utf-8")
    )
    resolver = RefResolver(
        base_uri=base,
        referrer=assurance,
        store={
            f"{base}assurance-result-1.0.schema.json": assurance,
            f"{base}specgap-detail-1.0.schema.json": detail,
        },
    )
    return Draft7Validator(assurance, resolver=resolver)


def _load(name: str) -> SpecInput:
    return SpecInput.from_dict(json.loads((EXAMPLES / name).read_text(encoding="utf-8")))


@pytest.fixture(scope="module")
def validator() -> Draft7Validator:
    return _schema_validator()


def test_analyze_structured_validates_against_schema(validator: Draft7Validator):
    envelope = analyze_structured(_load("sandbox_no_network.json"), mode="rule")
    validator.validate(envelope)


def test_analyze_structured_envelope_fields(validator: Draft7Validator):
    envelope = analyze_structured(_load("sandbox_no_network.json"), mode="rule")
    assert envelope["assurance_result_schema"] == "1.0"
    assert envelope["kind"] == "specgap"
    assert envelope["producer"] == {"name": "specgap", "version": __version__}
    assert len(envelope["input_fingerprint"]) == 64
    assert envelope["verdict"] == "divergence_detected"
    detail = envelope["detail"]
    assert detail["specgap_detail_schema"] == "1.0"
    assert detail["encoding_version"] == "sandbox-propositional/1.0"
    assert len(detail["triangulation"]["records"]) == 2
    failed = [c for c in detail["implication_checks"] if c["status"] == "implication_failed"]
    assert len(failed) == 2
    assert "network_send" in failed[0]["counterexample_atoms"]


def test_rule_mode_determinism_byte_identical_envelope():
    spec = _load("sandbox_no_network.json")
    fp1 = input_fingerprint(spec)
    fp2 = input_fingerprint(spec)
    assert fp1 == fp2

    env1 = analyze_structured(spec, mode="rule")
    env2 = analyze_structured(spec, mode="rule")
    assert env1["input_fingerprint"] == env2["input_fingerprint"]
    assert _canonical_json(env1) == _canonical_json(env2)


def test_malformed_detail_fails_schema_validation(validator: Draft7Validator):
    envelope = analyze_structured(_load("sandbox_no_network.json"), mode="rule")
    bad = copy.deepcopy(envelope)
    bad["detail"]["not_a_specgap_field"] = True
    with pytest.raises(jsonschema.ValidationError):
        validator.validate(bad)


def test_wrong_detail_schema_version_fails_validation(validator: Draft7Validator):
    envelope = analyze_structured(_load("sandbox_no_network.json"), mode="rule")
    bad = copy.deepcopy(envelope)
    bad["detail"]["specgap_detail_schema"] = "9.9"
    with pytest.raises(jsonschema.ValidationError):
        validator.validate(bad)
