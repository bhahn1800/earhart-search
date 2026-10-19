import json

import pytest

from earhart.evidence import EvidenceRecord, load_registry

BASE = dict(
    id="TST-001", category="OTHER", observation="synthetic test record",
    source_title="test", source_type="MODERN_ANALYSIS", source_quality=3,
)


def test_minimal_valid():
    assert EvidenceRecord(**BASE).verified is False


def test_primary_requires_quote():
    with pytest.raises(ValueError):
        EvidenceRecord(**{**BASE, "source_type": "PRIMARY"})


def test_speculative_quality_capped():
    with pytest.raises(ValueError):
        EvidenceRecord(**{**BASE, "source_type": "SPECULATIVE", "source_quality": 4})


def test_position_needs_pair_and_uncertainty():
    with pytest.raises(ValueError):
        EvidenceRecord(**{**BASE, "latitude": 1.0})
    with pytest.raises(ValueError):
        EvidenceRecord(**{**BASE, "latitude": 1.0, "longitude": 2.0})
    EvidenceRecord(**{**BASE, "latitude": 1.0, "longitude": 2.0, "uncertainty": {"horizontal_nm": 5}})


def test_registry_loader(tmp_path):
    p = tmp_path / "r.jsonl"
    p.write_text("# c\n" + json.dumps(BASE) + "\n" + json.dumps(BASE) + "\n")
    with pytest.raises(ValueError, match="duplicate"):
        load_registry(p)
    p.write_text("# c\n" + json.dumps(BASE) + "\n")
    assert len(load_registry(p)) == 1


def test_shipped_registry_loads():
    assert load_registry("data/sources/evidence.jsonl") == []
