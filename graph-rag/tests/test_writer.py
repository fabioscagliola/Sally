import pytest
from neo4j.exceptions import ClientError

from graph_rag.contract import GraphDocument, GraphNode, GraphRelationship
from graph_rag.writer import Neo4jPersistenceError, Neo4jWriter


class FakeResult:
    def consume(self):
        return None


class FakeTransaction:
    def __init__(self, rejected_type=None):
        self.calls = []
        self.rejected_type = rejected_type

    def run(self, query, **parameters):
        self.calls.append((query, parameters))
        if self.rejected_type is not None and parameters.get("semantic_type") == self.rejected_type:
            raise ClientError("label rejected")
        return FakeResult()


class FakeSession:
    def __init__(self, rejected_type=None):
        self.transaction = FakeTransaction(rejected_type)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def execute_write(self, callback, document):
        callback(self.transaction, document)


class FakeDriver:
    def __init__(self, rejected_type=None):
        self.session_instance = FakeSession(rejected_type)

    def session(self):
        return self.session_instance


def test_rebuild_deletes_then_writes_nodes_and_relationships():
    driver = FakeDriver()
    document = GraphDocument(
        nodes=(GraphNode("a", "Function"), GraphNode("b", "Method")),
        relationships=(GraphRelationship("a", "b", "CALLS"),),
    )

    Neo4jWriter(driver).rebuild(document)

    calls = driver.session_instance.transaction.calls
    assert "DETACH DELETE" in calls[0][0]
    assert "MERGE (entity:$($semantic_type)" in calls[1][0]
    assert ":Entity" not in calls[1][0]
    assert calls[1][1]["semantic_type"] == "Function"
    assert calls[1][1]["nodes"][0]["source_id"] == "a"
    assert calls[2][1]["semantic_type"] == "Method"
    assert "MATCH (source {source_id:" in calls[3][0]
    assert "MATCH (target {source_id:" in calls[3][0]
    assert ":Entity" not in calls[3][0]
    assert "MERGE (source)-[edge:$(relationship.type)" in calls[3][0]
    assert calls[3][1]["relationships"][0]["type"] == "CALLS"


def test_rebuild_passes_arbitrary_semantic_types_without_changing_them():
    driver = FakeDriver()
    document = GraphDocument(
        nodes=(GraphNode("a", "Domain Thing"), GraphNode("b", "Result/Value")),
        relationships=(GraphRelationship("a", "b", "READS-VALUE"),),
    )

    Neo4jWriter(driver).rebuild(document)

    calls = driver.session_instance.transaction.calls
    assert calls[1][1]["semantic_type"] == "Domain Thing"
    assert calls[1][1]["nodes"] == [
        {
            "source_id": "a",
            "type": "Domain Thing",
            "source_uri": None,
            "start_line": None,
            "start_column": None,
            "end_line": None,
            "end_column": None,
            "properties": {},
        },
    ]
    assert calls[2][1]["semantic_type"] == "Result/Value"
    assert calls[2][1]["nodes"] == [
        {
            "source_id": "b",
            "type": "Result/Value",
            "source_uri": None,
            "start_line": None,
            "start_column": None,
            "end_line": None,
            "end_column": None,
            "properties": {},
        },
    ]
    assert calls[3][1]["relationships"] == [
        {"source_id": "a", "target_id": "b", "type": "READS-VALUE", "properties": {}}
    ]
    assert "RELATES_TO" not in calls[3][0]


def test_rebuild_groups_nodes_by_type_deterministically():
    driver = FakeDriver()
    document = GraphDocument(
        nodes=(
            GraphNode("method-a", "Method"),
            GraphNode("function", "Function"),
            GraphNode("method-b", "Method"),
        ),
        relationships=(),
    )

    Neo4jWriter(driver).rebuild(document)

    calls = driver.session_instance.transaction.calls
    assert [call[1].get("semantic_type") for call in calls[1:3]] == ["Function", "Method"]
    assert [node["source_id"] for node in calls[2][1]["nodes"]] == ["method-a", "method-b"]


def test_rebuild_wraps_rejected_semantic_label_and_stops():
    driver = FakeDriver(rejected_type="Rejected Type")
    document = GraphDocument(
        nodes=(GraphNode("a", "Accepted"), GraphNode("b", "Rejected Type")),
        relationships=(GraphRelationship("a", "b", "CALLS"),),
    )

    with pytest.raises(Neo4jPersistenceError, match="Rejected Type") as captured:
        Neo4jWriter(driver).rebuild(document)

    assert captured.value.semantic_type == "Rejected Type"
    assert isinstance(captured.value.__cause__, ClientError)
    calls = driver.session_instance.transaction.calls
    assert [call[1].get("semantic_type") for call in calls[1:]] == ["Accepted", "Rejected Type"]
    assert all("relationships" not in call[1] for call in calls)
