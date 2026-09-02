from graph_rag.contract import GraphDocument, GraphNode, GraphRelationship
from graph_rag.writer import Neo4jWriter


class FakeResult:
    def consume(self):
        return None


class FakeTransaction:
    def __init__(self):
        self.calls = []

    def run(self, query, **parameters):
        self.calls.append((query, parameters))
        return FakeResult()


class FakeSession:
    def __init__(self):
        self.transaction = FakeTransaction()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def execute_write(self, callback, document):
        callback(self.transaction, document)


class FakeDriver:
    def __init__(self):
        self.session_instance = FakeSession()

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
    assert "MERGE (entity:Entity" in calls[1][0]
    assert calls[1][1]["nodes"][0]["source_id"] == "a"
    assert "MERGE (source)-[edge:RELATES_TO" in calls[2][0]
    assert calls[2][1]["relationships"][0]["type"] == "CALLS"