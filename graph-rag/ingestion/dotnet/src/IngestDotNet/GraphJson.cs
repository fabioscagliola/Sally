using System.Text.Json;
using System.Text.Json.Serialization;

namespace IngestDotNet;

public static class GraphJson
{
    private static readonly JsonSerializerOptions Options = new()
    {
        WriteIndented = true,
        PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
        DictionaryKeyPolicy = null,
        DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
    };

    public static void Write(GraphDocument document, string outputPath)
    {
        document.Validate();
        var directory = Path.GetDirectoryName(Path.GetFullPath(outputPath));
        if (directory is not null)
        {
            Directory.CreateDirectory(directory);
        }

        var ordered = document with
        {
            Nodes = document.Nodes.OrderBy(node => node.SourceId, StringComparer.Ordinal).ToArray(),
            Relationships = document.Relationships
                .OrderBy(relationship => relationship.SourceId, StringComparer.Ordinal)
                .ThenBy(relationship => relationship.TargetId, StringComparer.Ordinal)
                .ThenBy(relationship => relationship.Type, StringComparer.Ordinal)
                .ToArray(),
        };

        using var stream = File.Create(outputPath);
        JsonSerializer.Serialize(stream, ordered, Options);
    }
}