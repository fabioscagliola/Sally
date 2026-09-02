"""Strict JSON serialization for the version 1 graph contract."""

import json
from typing import Any, Dict, TextIO

from .contract import GraphDocument, GraphNode, GraphRelationship, SourceLocation


class ContractError(ValueError):
    """Raised when serialized graph input does not match the version 1 contract."""


def serialize(document: GraphDocument, stream: TextIO) -> None:
    document.validate()
    json.dump(_document_to_dict(document), stream, indent=2, sort_keys=True)
    stream.write("\n")


def deserialize(stream: TextIO) -> GraphDocument:
    try:
        value = json.load(stream)
    except json.JSONDecodeError as error:
        raise ContractError("invalid JSON: %s" % error.msg) from error
    try:
        document = _document_from_dict(value)
        document.validate()
        return document
    except (TypeError, ValueError, KeyError) as error:
        raise ContractError(str(error)) from error


def _document_to_dict(document: GraphDocument) -> Dict[str, Any]:
    return {
        "format": document.format,
        "version": document.version,
        "nodes": [_node_to_dict(node) for node in document.nodes],
        "relationships": [_relationship_to_dict(relationship) for relationship in document.relationships],
    }


def _node_to_dict(node: GraphNode) -> Dict[str, Any]:
    value: Dict[str, Any] = {
        "source_id": node.source_id,
        "type": node.type,
        "properties": dict(node.properties),
    }
    if node.location is not None:
        value["location"] = {
            key: item for key, item in {
                "source_uri": node.location.source_uri,
                "start_line": node.location.start_line,
                "start_column": node.location.start_column,
                "end_line": node.location.end_line,
                "end_column": node.location.end_column,
            }.items() if item is not None
        }
    return value


def _relationship_to_dict(relationship: GraphRelationship) -> Dict[str, Any]:
    return {
        "source_id": relationship.source_id,
        "target_id": relationship.target_id,
        "type": relationship.type,
        "properties": dict(relationship.properties),
    }


def _document_from_dict(value: Any) -> GraphDocument:
    data = _object(value, "document")
    _fields(data, {"format", "version", "nodes", "relationships"}, "document")
    _required(data, {"format", "version", "nodes", "relationships"}, "document")
    nodes = _array(data["nodes"], "nodes")
    relationships = _array(data["relationships"], "relationships")
    return GraphDocument(
        nodes=tuple(_node_from_dict(item) for item in nodes),
        relationships=tuple(_relationship_from_dict(item) for item in relationships),
        format=data["format"],
        version=data["version"],
    )


def _node_from_dict(value: Any) -> GraphNode:
    data = _object(value, "node")
    _fields(data, {"source_id", "type", "properties", "location"}, "node")
    _required(data, {"source_id", "type", "properties"}, "node")
    location = data.get("location")
    return GraphNode(
        source_id=data["source_id"],
        type=data["type"],
        properties=data["properties"],
        location=_location_from_dict(location) if location is not None else None,
    )


def _relationship_from_dict(value: Any) -> GraphRelationship:
    data = _object(value, "relationship")
    _fields(data, {"source_id", "target_id", "type", "properties"}, "relationship")
    _required(data, {"source_id", "target_id", "type", "properties"}, "relationship")
    return GraphRelationship(
        source_id=data["source_id"],
        target_id=data["target_id"],
        type=data["type"],
        properties=data["properties"],
    )


def _location_from_dict(value: Any) -> SourceLocation:
    data = _object(value, "location")
    _fields(data, {"source_uri", "start_line", "start_column", "end_line", "end_column"}, "location")
    return SourceLocation(**data)


def _object(value: Any, name: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractError("%s must be an object" % name)
    return value


def _array(value: Any, name: str) -> list:
    if not isinstance(value, list):
        raise ContractError("%s must be an array" % name)
    return value


def _fields(data: Dict[str, Any], allowed: set, name: str) -> None:
    unknown = set(data) - allowed
    if unknown:
        raise ContractError("unknown %s field(s): %s" % (name, ", ".join(sorted(unknown))))


def _required(data: Dict[str, Any], required: set, name: str) -> None:
    missing = required - set(data)
    if missing:
        raise ContractError("invalid %s: missing field(s): %s" % (name, ", ".join(sorted(missing))))