import os

import pytest
from neo4j import GraphDatabase

from graph_rag.contract import GraphDocument, GraphNode, GraphRelationship
from graph_rag.writer import Neo4jWriter


pytestmark = pytest.mark.integration


@pytest.fixture
def neo4j_driver():
    driver = GraphDatabase.driver(
        os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        auth=(os.getenv("NEO4J_USERNAME", "neo4j"), os.getenv("NEO4J_PASSWORD", "whatever")),
    )
    driver.verify_connectivity()
    yield driver
    with driver.session(database=os.getenv("NEO4J_DATABASE", "neo4j")) as session:
        session.run("MATCH (entity) DETACH DELETE entity").consume()
    driver.close()


def test_write_and_rebuild_are_deterministic(neo4j_driver):
    document = GraphDocument(
        nodes=(
            GraphNode("a", "Function", properties={"name": "caller", "type": "custom override"}),
            GraphNode("b", "Method", properties={"name": "target"}),
            GraphNode("c", "Domain Thing", properties={"name": "generic"}),
        ),
        relationships=(GraphRelationship("a", "b", "CALLS", properties={"count": 2}),),
    )
    writer = Neo4jWriter(neo4j_driver)

    writer.rebuild(document)
    writer.rebuild(document)

    with neo4j_driver.session() as session:
        nodes = session.run(
            "MATCH (entity) "
            "RETURN entity.source_id AS source_id, labels(entity) AS labels, "
            "entity.type AS type, entity.name AS name "
            "ORDER BY source_id"
        ).data()
        assert nodes == [
            {"source_id": "a", "labels": ["Function"], "type": "Function", "name": "caller"},
            {"source_id": "b", "labels": ["Method"], "type": "Method", "name": "target"},
            {"source_id": "c", "labels": ["Domain Thing"], "type": "Domain Thing", "name": "generic"},
        ]
        assert session.run("MATCH (entity:Entity) RETURN count(entity) AS count").single()["count"] == 0
        assert session.run("MATCH (entity:GraphNode) RETURN count(entity) AS count").single()["count"] == 0
        assert session.run("MATCH ()-[edge:CALLS]->() RETURN count(edge) AS count").single()["count"] == 1
        assert session.run("MATCH ()-[edge:RELATES_TO]->() RETURN count(edge) AS count").single()["count"] == 0
        edge = session.run(
            "MATCH ()-[edge:CALLS]->() RETURN edge.type AS type, edge.count AS count"
        ).single()
        assert dict(edge) == {"type": "CALLS", "count": 2}

        stale = GraphDocument((GraphNode("stale", "File"),), ())
        writer.rebuild(stale)
        rebuilt = session.run(
            "MATCH (entity) RETURN entity.source_id AS source_id, labels(entity) AS labels, entity.type AS type"
        ).single()
        assert dict(rebuilt) == {"source_id": "stale", "labels": ["File"], "type": "File"}
        assert session.run("MATCH ()-[edge]->() RETURN count(edge) AS count").single()["count"] == 0
