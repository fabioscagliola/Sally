import json

from graph_rag import cli


def test_cli_requires_connection_configuration(tmp_path, monkeypatch, capsys):
    input_path = tmp_path / "graph.json"
    input_path.write_text(json.dumps({"format": "sally-graph-rag", "version": 1, "nodes": [], "relationships": []}))
    for name in ("NEO4J_URI", "NEO4J_USERNAME", "NEO4J_PASSWORD"):
        monkeypatch.delenv(name, raising=False)

    result = cli.main([str(input_path)])

    assert result == 1
    assert "missing Neo4j configuration" in capsys.readouterr().err


def test_cli_flags_override_environment(tmp_path, monkeypatch):
    input_path = tmp_path / "graph.json"
    input_path.write_text(json.dumps({"format": "sally-graph-rag", "version": 1, "nodes": [], "relationships": []}))
    monkeypatch.setenv("NEO4J_URI", "bolt://environment")
    monkeypatch.setenv("NEO4J_USERNAME", "environment-user")
    monkeypatch.setenv("NEO4J_PASSWORD", "environment-password")

    class FakeDriver:
        def close(self):
            pass

    captured = {}

    class FakeWriter:
        def __init__(self, driver):
            captured["driver"] = driver

        def rebuild(self, document):
            captured["document"] = document

    monkeypatch.setattr(cli.GraphDatabase, "driver", lambda uri, auth: captured.update(uri=uri, auth=auth) or FakeDriver())
    monkeypatch.setattr(cli, "Neo4jWriter", FakeWriter)

    result = cli.main([
        str(input_path),
        "--uri", "bolt://override",
        "--username", "override-user",
        "--password", "override-password",
        "--database", "override-database",
    ])

    assert result == 0
    assert captured["uri"] == "bolt://override"
    assert captured["auth"] == ("override-user", "override-password")