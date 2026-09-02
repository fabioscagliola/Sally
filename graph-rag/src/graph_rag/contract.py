"""Technology-independent version 1 graph representation."""

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Optional, Tuple


PropertyValue = Any


@dataclass(frozen=True)
class SourceLocation:
    source_uri: Optional[str] = None
    start_line: Optional[int] = None
    start_column: Optional[int] = None
    end_line: Optional[int] = None
    end_column: Optional[int] = None


@dataclass(frozen=True)
class GraphNode:
    source_id: str
    type: str
    properties: Mapping[str, PropertyValue] = field(default_factory=dict)
    location: Optional[SourceLocation] = None


@dataclass(frozen=True)
class GraphRelationship:
    source_id: str
    target_id: str
    type: str
    properties: Mapping[str, PropertyValue] = field(default_factory=dict)


@dataclass(frozen=True)
class GraphDocument:
    nodes: Tuple[GraphNode, ...]
    relationships: Tuple[GraphRelationship, ...]
    format: str = "sally-graph-rag"
    version: int = 1

    def validate(self) -> None:
        if self.format != "sally-graph-rag":
            raise ValueError("format must be 'sally-graph-rag'")
        if self.version != 1:
            raise ValueError("version must be 1")

        node_ids = set()
        for node in self.nodes:
            _validate_text(node.source_id, "node source_id")
            _validate_text(node.type, "node type")
            if node.source_id in node_ids:
                raise ValueError("duplicate node source_id: %s" % node.source_id)
            node_ids.add(node.source_id)
            _validate_properties(node.properties, "node properties")
            if node.location is not None:
                _validate_location(node.location)

        for relationship in self.relationships:
            _validate_text(relationship.source_id, "relationship source_id")
            _validate_text(relationship.target_id, "relationship target_id")
            _validate_text(relationship.type, "relationship type")
            if relationship.source_id not in node_ids:
                raise ValueError("relationship source does not exist: %s" % relationship.source_id)
            if relationship.target_id not in node_ids:
                raise ValueError("relationship target does not exist: %s" % relationship.target_id)
            _validate_properties(relationship.properties, "relationship properties")


def _validate_text(value: Any, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("%s must be a non-empty string" % field_name)


def _validate_location(location: SourceLocation) -> None:
    if location.source_uri is not None:
        _validate_text(location.source_uri, "source_uri")
    for name in ("start_line", "start_column", "end_line", "end_column"):
        value = getattr(location, name)
        if value is not None and (not isinstance(value, int) or isinstance(value, bool) or value < 1):
            raise ValueError("%s must be a positive integer" % name)


def _validate_properties(properties: Mapping[str, PropertyValue], field_name: str) -> None:
    if not isinstance(properties, Mapping):
        raise ValueError("%s must be an object" % field_name)
    for key, value in properties.items():
        _validate_text(key, "%s key" % field_name)
        if isinstance(value, (dict, tuple)) or value is None:
            raise ValueError("%s[%s] must be a Neo4j-compatible scalar or list" % (field_name, key))
        if isinstance(value, list):
            if not value or any(item is None or isinstance(item, (dict, list, tuple)) for item in value):
                raise ValueError("%s[%s] must be a non-empty list of scalar values" % (field_name, key))