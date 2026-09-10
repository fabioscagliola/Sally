# TypeScript ingestion

A Node application that analyzes a TypeScript project with the TypeScript Compiler API and writes the Graph RAG JSON representation.

## Build and run

From the repository root, build the image.

```
docker build -t ingest-typescript graph-rag/ingestion/typescript
```

```
docker run --rm \
  -v /path/to/repository:/source \
  -v "$PWD":/target \
  ingest-typescript \
  /source/tsconfig.json \
  /target/example.json
```

