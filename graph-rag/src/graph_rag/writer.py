"""Neo4j persistence behind the neutral graph boundary."""

from typing import Any, Mapping, Protocol

from neo4j import Driver

from .contract import GraphDocument


class GraphWriter(Protocol):
    def rebuild(self, document: GraphDocument) -> None:
        ...


class Neo4jWriter:
    def __init__(self, driver: Driver):
        self._driver = driver

    def rebuild(self, document: GraphDocument) -> None:
        document.validate()
        with self._driver.session() as session:
            session.execute_write(self._rebuild_transaction, document)

    @staticmethod
    def _rebuild_transaction(transaction: Any, document: GraphDocument) -> None:
        transaction.run("MATCH (entity) DETACH DELETE entity").consume()
        transaction.run(
            """
            UNWIND $nodes AS node
            MERGE (entity:Entity {source_id: node.source_id})
            SET entity:$(node.type),
                entity.type = node.type,
                entity.source_uri = node.source_uri,
                entity.start_line = node.start_line,
                entity.start_column = node.start_column,
                entity.end_line = node.end_line,
                entity.end_column = node.end_column,
                entity += node.properties
            """,
            nodes=[_node_parameters(node) for node in document.nodes],
        ).consume()
        transaction.run(
            """
            UNWIND $relationships AS relationship
            MATCH (source:Entity {source_id: relationship.source_id})
            MATCH (target:Entity {source_id: relationship.target_id})
            MERGE (source)-[edge:$(relationship.type) {type: relationship.type}]->(target)
            SET edge += relationship.properties
            """,
            relationships=[
                {
                    "source_id": relationship.source_id,
                    "target_id": relationship.target_id,
                    "type": relationship.type,
                    "properties": dict(relationship.properties),
                }
                for relationship in document.relationships
            ],
        ).consume()


def _node_parameters(node: Any) -> Mapping[str, Any]:
    location = node.location
    return {
        "source_id": node.source_id,
        "type": node.type,
        "source_uri": location.source_uri if location else None,
        "start_line": location.start_line if location else None,
        "start_column": location.start_column if location else None,
        "end_line": location.end_line if location else None,
        "end_column": location.end_column if location else None,
        "properties": dict(node.properties),
    }