import io
import json
from pathlib import Path

import pytest

from graph_rag.serialization import ContractError, deserialize, serialize


FIXTURE = Path(__file__).parents[1] / "fixtures" / "sample-graph.json"


def test_fixture_round_trips():
    with FIXTURE.open(encoding="utf-8") as stream:
        document = deserialize(stream)

    output = io.StringIO()
    serialize(document, output)

    assert deserialize(io.StringIO(output.getvalue())) == document


@pytest.mark.parametrize(
    "payload, message",
    [
        ({"format": "sally-graph-rag", "version": 1, "nodes": [], "relationships": [], "extra": True}, "unknown document"),
        ({"format": "sally-graph-rag", "version": 1, "nodes": [], "relationships": [{"source_id": "a"}]}, "relationship"),
        ({"format": "sally-graph-rag", "version": 2, "nodes": [], "relationships": []}, "version"),
    ],
)
def test_strict_reader_rejects_invalid_contract(payload, message):
    with pytest.raises(ContractError, match=message):
        deserialize(io.StringIO(json.dumps(payload)))


def test_invalid_json_is_reported_as_contract_error():
    with pytest.raises(ContractError, match="invalid JSON"):
        deserialize(io.StringIO("{"))