"""Short-lived command-line interface for rebuilding the derived graph."""

import argparse
import os
import sys
from typing import Optional, Sequence

from neo4j import GraphDatabase

from .serialization import deserialize
from .writer import Neo4jWriter


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="graph-rag-cli")
    parser.add_argument("input", help="path to a version 1 graph JSON document")
    parser.add_argument("--uri", dest="uri", help="override NEO4J_URI")
    parser.add_argument("--username", dest="username", help="override NEO4J_USERNAME")
    parser.add_argument("--password", dest="password", help="override NEO4J_PASSWORD")
    parser.add_argument("--database", dest="database", help="override NEO4J_DATABASE")
    return parser


def main(arguments: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(arguments)
    try:
        with open(args.input, "r", encoding="utf-8") as stream:
            document = deserialize(stream)
        uri = args.uri or os.getenv("NEO4J_URI")
        username = args.username or os.getenv("NEO4J_USERNAME")
        password = args.password or os.getenv("NEO4J_PASSWORD")
        database = args.database or os.getenv("NEO4J_DATABASE", "neo4j")
        missing = [name for name, value in (("NEO4J_URI", uri), ("NEO4J_USERNAME", username), ("NEO4J_PASSWORD", password)) if not value]
        if missing:
            raise ValueError("missing Neo4j configuration: %s" % ", ".join(missing))
        driver = GraphDatabase.driver(uri, auth=(username, password))
        try:
            Neo4jWriter(driver).rebuild(document)
        finally:
            driver.close()
        return 0
    except Exception as error:
        print("graph-rag-cli: %s" % error, file=sys.stderr)
        return 1