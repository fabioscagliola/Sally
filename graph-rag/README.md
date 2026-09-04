# Sally Graph RAG

This is a self-contained Sally subsystem that rebuilds a disposable, derived representation of a project in Neo4j. It is a short-lived Python library and CLI, not a running service.

## Scope

Version 1 provides a neutral graph contract, strict JSON input, Neo4j persistence, and full delete-and-rebuild behavior. Retrieval, embeddings, AI integration, and language-specific ingestion pipelines are separate backlog items.

The standalone .NET C# ingestion pipeline is documented under [`ingestion/dotnet/`](ingestion/dotnet/). It produces version-1 JSON for this foundation and does not depend on Neo4j or Python at build/test time.

The graph uses generic entities and relationships. Neo4j persists every node with the common `Entity` label plus its semantic node label, and every relationship with its semantic relationship type:

```text
(:Entity:Method {type: "Method"})-[:CALLS {type: "CALLS"}]->(:Entity:Method)
```

Each entity has a stable `source_id`; source URI and source-location fields are optional.

## Setup

Use Python 3.9 or newer. From this directory:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[test]'
```

Start the dedicated disposable Neo4j instance:

```sh
docker compose up -d
```

The default connection settings are `NEO4J_URI=bolt://localhost:7687`, `NEO4J_USERNAME=neo4j`, `NEO4J_PASSWORD=whatever`, and `NEO4J_DATABASE=neo4j`. Set these environment variables for other values; never commit real credentials.

## CLI

`graph-rag-cli` reads a strict version-1 JSON document and replaces the graph in one transaction:

```sh
NEO4J_URI=bolt://localhost:7687 \
NEO4J_USERNAME=neo4j \
NEO4J_PASSWORD=whatever \
graph-rag-cli fixtures/sample-graph.json
```

The `--uri`, `--username`, `--password`, and `--database` options override their corresponding environment values. The configured database is disposable and is cleared before each rebuild.

## Tests

Unit tests do not require Neo4j or Docker:

```sh
pytest -m 'not integration'
```

Run the real Neo4j integration suite separately after starting Compose:

```sh
docker compose up -d
pytest -m integration
```

Stop and remove the disposable database with `docker compose down --volumes`.