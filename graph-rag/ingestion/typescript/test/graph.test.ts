import assert from "node:assert/strict";
import path from "node:path";
import test from "node:test";
import { ingest } from "../src/graph.js";

const fixtureRoot = path.resolve("test/fixtures/basic");
const tsconfigPath = path.join(fixtureRoot, "tsconfig.json");
const repositoryRoot = path.resolve("test/fixtures");

function graph() {
  return ingest({ tsconfigPath, repositoryRoot });
}

test("emits the strict graph contract from a configured TypeScript project", () => {
  const document = graph();
  assert.equal(document.format, "sally-graph-rag");
  assert.equal(document.version, 1);
  assert.ok(document.nodes.some((node) => node.type === "Project"));
  assert.ok(document.nodes.some((node) => node.type === "Type" && node.properties.name === "Child"));
  assert.ok(document.nodes.some((node) => node.type === "Function" && node.properties.name === "namedArrow"));
  assert.ok(document.nodes.some((node) => node.type === "Method" && node.properties.name === "run"));
  assert.ok(document.nodes.some((node) => node.type === "Property" && node.properties.name === "value"));
  assert.ok(!document.nodes.some((node) => node.properties.name === "Ignored"));
  assert.ok(!document.nodes.some((node) => node.properties.name === "anonymous"));

  const location = document.nodes.find((node) => node.properties.name === "Child")?.location;
  assert.equal(location?.source_uri, "basic/src/main.ts");
  assert.ok(document.relationships.some((relationship) => relationship.type === "INHERITS"));
  assert.ok(document.relationships.some((relationship) => relationship.type === "IMPLEMENTS"));
  assert.ok(document.relationships.some((relationship) => relationship.type === "CALLS"));
  assert.ok(document.relationships.some((relationship) => relationship.type === "USES_TYPE"));
  assert.ok(document.relationships.some((relationship) => relationship.type === "CONTAINS"));
});

test("uses stable project-aware and source-scoped declaration identities", () => {
  const first = graph();
  const second = graph();
  assert.deepEqual(first, second);
  assert.equal(first.nodes[0].source_id, "project:basic:basic/tsconfig.json");
  assert.ok(first.nodes.slice(1).every((node) => node.source_id.startsWith("project:basic:basic/tsconfig.json:")));
  const submitIds = first.nodes.filter((node) => node.properties.name === "submit").map((node) => node.source_id);
  assert.equal(submitIds.length, 2);
  assert.notEqual(submitIds[0], submitIds[1]);
  assert.ok(submitIds.some((id) => id.includes("src/first.ts")));
  assert.ok(submitIds.some((id) => id.includes("src/second.ts")));
  assert.ok(first.nodes.every((node) => !JSON.stringify(node).includes(fixtureRoot)));
});

test("uses the supplied project identity when package metadata is not globally unique", () => {
  const document = ingest({ tsconfigPath, repositoryRoot, projectId: "github.com/example/basic" });
  assert.equal(document.nodes[0].source_id, "project:github.com/example/basic:basic/tsconfig.json");
});
