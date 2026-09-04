# .NET ingestion

A .NET application that analyzes C# projects and solutions with Roslyn and writes the Graph RAG JSON representation.

## Build and run

From the repository root, build the image.

```
docker build -t ingest-dotnet graph-rag/ingestion/dotnet
```

And run the application.

```
docker run --rm \
  -v /example:/source \
  -v "$PWD":/target \
  ingest-dotnet \
  /source/example.csproj \
  /target/example.json
```
