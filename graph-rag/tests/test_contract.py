import pytest

from graph_rag.contract import GraphDocument, GraphNode, GraphRelationship, SourceLocation


def valid_document() -> GraphDocument:
    return GraphDocument(
        nodes=(
            GraphNode("a", "Function", {"name": "main"}, SourceLocation(start_line=1)),
            GraphNode("b", "Method"),
        ),
        relationships=(GraphRelationship("a", "b", "CALLS"),),
    )


def test_valid_document_passes_validation():
    valid_document().validate()


@pytest.mark.parametrize(
    "document, message",
    [
        (
            GraphDocument((GraphNode("a", "Function"), GraphNode("a", "Method")), ()),
            "duplicate node",
        ),
        (
            GraphDocument((GraphNode("a", "Function"),), (GraphRelationship("a", "missing", "CALLS"),)),
            "relationship target",
        ),
        (
            GraphDocument((GraphNode("a", ""),), ()),
            "node type",
        ),
        (
            GraphDocument((GraphNode("a", "Function", {"metadata": {"nested": True}}),), ()),
            "node properties",
        ),
    ],
)
def test_invalid_document_is_rejected(document, message):
    with pytest.raises(ValueError, match=message):
        document.validate()


def test_invalid_source_location_is_rejected():
    document = GraphDocument((GraphNode("a", "Function", location=SourceLocation(start_line=0)),), ())

    with pytest.raises(ValueError, match="start_line"):
        document.validate()