# Sally Graph RAG

A Python application that ingests a graph representation of a project into Neo4j.

## Setup

1. Start the Neo4j instance.

```
docker compose up -d
```

|Setting|Value|
|---|---|
|URI|bolt://localhost:7687|
|Username|neo4j|
|Password|whatever|
|Database|neo4j|


2. Create and activate the virtual environment.

```
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

3. Ingest a JSON document.

IMPORTANT: The database is cleared before each ingestion.

```
graph-rag-cli \
  --uri=bolt://localhost:7687 \
  --username=neo4j \
  --password=whatever \
  source.json
```

4. Stop the Neo4j instance.

```
docker compose down --volumes
```

