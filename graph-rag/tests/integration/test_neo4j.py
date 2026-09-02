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
        nodes=(GraphNode("a", "Function"), GraphNode("b", "Method")),
        relationships=(GraphRelationship("a", "b", "CALLS"),),
    )
    writer = Neo4jWriter(neo4j_driver)

    writer.rebuild(document)
    writer.rebuild(document)

    with neo4j_driver.session() as session:
        assert session.run("MATCH (entity:Entity) RETURN count(entity) AS count").single()["count"] == 2
        assert session.run("MATCH ()-[edge:RELATES_TO]->() RETURN count(edge) AS count").single()["count"] == 1

        stale = GraphDocument((GraphNode("stale", "File"),), ())
        writer.rebuild(stale)
        assert session.run("MATCH (entity:Entity) RETURN collect(entity.source_id) AS ids").single()["ids"] == ["stale"]