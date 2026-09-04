using System.Text.Json;

namespace IngestDotNet;

public sealed record SourceLocation(
    string? SourceUri = null,
    int? StartLine = null,
    int? StartColumn = null,
    int? EndLine = null,
    int? EndColumn = null);

public sealed record GraphNode(
    string SourceId,
    string Type,
    IReadOnlyDictionary<string, object?> Properties,
    SourceLocation? Location = null);

public sealed record GraphRelationship(
    string SourceId,
    string TargetId,
    string Type,
    IReadOnlyDictionary<string, object?> Properties);

public sealed record GraphDocument(
    IReadOnlyList<GraphNode> Nodes,
    IReadOnlyList<GraphRelationship> Relationships,
    string Format = "sally-graph-rag",
    int Version = 1)
{
    public void Validate()
    {
        if (Format != "sally-graph-rag")
        {
            throw new InvalidDataException("format must be 'sally-graph-rag'");
        }

        if (Version != 1)
        {
            throw new InvalidDataException("version must be 1");
        }

        var nodeIds = new HashSet<string>(StringComparer.Ordinal);
        foreach (var node in Nodes)
        {
            ValidateText(node.SourceId, "node source_id");
            ValidateText(node.Type, "node type");
            if (!nodeIds.Add(node.SourceId))
            {
                throw new InvalidDataException($"duplicate node source_id: {node.SourceId}");
            }

            ValidateProperties(node.Properties, "node properties");
            ValidateLocation(node.Location);
        }

        foreach (var relationship in Relationships)
        {
            ValidateText(relationship.SourceId, "relationship source_id");
            ValidateText(relationship.TargetId, "relationship target_id");
            ValidateText(relationship.Type, "relationship type");
            if (!nodeIds.Contains(relationship.SourceId))
            {
                throw new InvalidDataException($"relationship source does not exist: {relationship.SourceId}");
            }

            if (!nodeIds.Contains(relationship.TargetId))
            {
                throw new InvalidDataException($"relationship target does not exist: {relationship.TargetId}");
            }

            ValidateProperties(relationship.Properties, "relationship properties");
        }
    }

    private static void ValidateText(string? value, string fieldName)
    {
        if (string.IsNullOrWhiteSpace(value))
        {
            throw new InvalidDataException($"{fieldName} must be a non-empty string");
        }
    }

    private static void ValidateLocation(SourceLocation? location)
    {
        if (location is null)
        {
            return;
        }

        if (location.SourceUri is not null)
        {
            ValidateText(location.SourceUri, "source_uri");
        }

        foreach (var value in new[] { location.StartLine, location.StartColumn, location.EndLine, location.EndColumn })
        {
            if (value is <= 0)
            {
                throw new InvalidDataException("source location values must be positive integers");
            }
        }
    }

    private static void ValidateProperties(IReadOnlyDictionary<string, object?> properties, string fieldName)
    {
        foreach (var pair in properties)
        {
            ValidateText(pair.Key, $"{fieldName} key");
            if (pair.Value is null || pair.Value is JsonElement { ValueKind: JsonValueKind.Object or JsonValueKind.Array })
            {
                throw new InvalidDataException($"{fieldName}[{pair.Key}] must be a scalar or list of scalar values");
            }

            if (pair.Value is IEnumerable<object?> values && pair.Value is not string)
            {
                if (!values.Any())
                {
                    throw new InvalidDataException($"{fieldName}[{pair.Key}] must be a non-empty list");
                }

                if (values.Any(value => value is null || value is IEnumerable<object?>))
                {
                    throw new InvalidDataException($"{fieldName}[{pair.Key}] must contain scalar values");
                }
            }
        }
    }
}