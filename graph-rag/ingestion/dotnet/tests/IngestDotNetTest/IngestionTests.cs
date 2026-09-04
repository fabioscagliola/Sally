using System.Text.Json;
using NUnit.Framework;

namespace IngestDotNetTest;

public sealed class IngestionTests
{
    [Test]
    public void GivenFixtureProject_WhenIngested_ThenVersionOneGraphIsProduced()
    {
        var inputPath = Path.Combine(TestContext.CurrentContext.TestDirectory, "..", "..", "..", "..", "Fixtures", "BasicFixture", "BasicFixture.csproj");
        var document = new IngestDotNet.ProjectIngestor().Ingest(inputPath);

        Assert.That(document.Format, Is.EqualTo("sally-graph-rag"));
        Assert.That(document.Version, Is.EqualTo(1));
        Assert.That(document.Nodes, Is.Not.Empty);
        Assert.That(document.Nodes.Select(node => node.Type), Does.Contain("Project"));
        Assert.That(document.Nodes.Select(node => node.Type), Does.Contain("Type"));
        Assert.That(document.Nodes.Select(node => node.Type), Does.Contain("Method"));
        Assert.That(document.Nodes.Select(node => node.Type), Does.Contain("Property"));
        Assert.That(document.Relationships.Select(relationship => relationship.Type), Does.Contain("CONTAINS"));
        Assert.That(document.Relationships.Select(relationship => relationship.Type), Does.Contain("INHERITS"));
        Assert.That(document.Relationships.Select(relationship => relationship.Type), Does.Contain("IMPLEMENTS"));
        Assert.That(document.Relationships.Select(relationship => relationship.Type), Does.Contain("CALLS"));
        Assert.That(document.Relationships.Select(relationship => relationship.Type), Does.Contain("USES_TYPE"));

        var projectId = document.Nodes.Single(node => node.Type == "Project").SourceId;
        var exampleTypeId = document.Nodes.Single(node => node.Type == "Type" &&
                                                           Equals(node.Properties["name"], "ExampleModel")).SourceId;
        var recordsPropertyId = document.Nodes.Single(node => node.Type == "Property" &&
                                                               Equals(node.Properties["name"], "Records")).SourceId;
        var useRecordsMethodId = document.Nodes.Single(node => node.Type == "Method" &&
                                                                Equals(node.Properties["name"], "UseRecords")).SourceId;
        var exampleRecordTypeId = document.Nodes.Single(node => node.Type == "Type" &&
                                                                 Equals(node.Properties["name"], "ExampleRecord")).SourceId;

        Assert.That(HasRelationship(document, projectId, exampleTypeId, "CONTAINS"), Is.True);
        Assert.That(HasRelationship(document, exampleTypeId, recordsPropertyId, "CONTAINS"), Is.True);
        Assert.That(HasRelationship(document, exampleTypeId, useRecordsMethodId, "CONTAINS"), Is.True);
        Assert.That(HasRelationship(document, recordsPropertyId, exampleRecordTypeId, "USES_TYPE"), Is.True);
        Assert.That(HasRelationship(document, useRecordsMethodId, exampleRecordTypeId, "USES_TYPE"), Is.True);
        Assert.That(document.Relationships.Any(relationship => relationship.Type == "CONTAINS" && relationship.TargetId == projectId), Is.False);
        Assert.That(document.Nodes.Single(node => node.SourceId == recordsPropertyId).Properties["declared_type"], Is.EqualTo("System.Collections.Generic.List<BasicFixture.ExampleRecord>"));
    }

    private static bool HasRelationship(IngestDotNet.GraphDocument document, string sourceId, string targetId, string type) =>
        document.Relationships.Any(relationship => relationship.SourceId == sourceId &&
                                                   relationship.TargetId == targetId &&
                                                   relationship.Type == type);

    [Test]
    public void GivenGraphDocument_WhenSerialized_ThenVersionOneJsonIsWritten()
    {
        var outputPath = Path.Combine(TestContext.CurrentContext.WorkDirectory, "graph.json");
        var document = new IngestDotNet.GraphDocument(
            [new IngestDotNet.GraphNode("a", "Type", new Dictionary<string, object?> { ["name"] = "Example" })],
            []);

        IngestDotNet.GraphJson.Write(document, outputPath);

        using var json = JsonDocument.Parse(File.ReadAllText(outputPath));
        Assert.That(json.RootElement.GetProperty("format").GetString(), Is.EqualTo("sally-graph-rag"));
        Assert.That(json.RootElement.GetProperty("version").GetInt32(), Is.EqualTo(1));
        Assert.That(json.RootElement.GetProperty("nodes").GetArrayLength(), Is.EqualTo(1));
    }

    [Test]
    public void GivenFixtureProject_WhenIngestedTwice_ThenJsonOutputIsDeterministic()
    {
        var inputPath = Path.Combine(TestContext.CurrentContext.TestDirectory, "..", "..", "..", "..", "Fixtures", "BasicFixture", "BasicFixture.csproj");
        var firstPath = Path.Combine(TestContext.CurrentContext.WorkDirectory, "first.json");
        var secondPath = Path.Combine(TestContext.CurrentContext.WorkDirectory, "second.json");
        var parser = new IngestDotNet.ProjectIngestor();

        IngestDotNet.GraphJson.Write(parser.Ingest(inputPath), firstPath);
        IngestDotNet.GraphJson.Write(parser.Ingest(inputPath), secondPath);

        Assert.That(File.ReadAllText(secondPath), Is.EqualTo(File.ReadAllText(firstPath)));
    }
}