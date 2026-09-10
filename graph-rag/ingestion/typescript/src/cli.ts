import fs from "node:fs";
import path from "node:path";
import { ingest } from "./graph.js";

const args = process.argv.slice(2);
const optionValue = (name: string): string | undefined => {
  const index = args.indexOf(name);
  return index >= 0 ? args[index + 1] : undefined;
};
const optionValues = new Set([optionValue("--repository-root"), optionValue("--project-id")]);
const positional = args.filter((argument) => !argument.startsWith("--") && !optionValues.has(argument));
if (positional.length !== 2 || args.some((argument) => argument.startsWith("--") && argument !== "--repository-root" && argument !== "--project-id") ||
    (args.includes("--repository-root") && !optionValue("--repository-root")) || (args.includes("--project-id") && !optionValue("--project-id"))) {
  console.error("Usage: ingest-typescript <tsconfig.json> <output.json> [--repository-root <path>] [--project-id <id>]");
  process.exit(2);
}

try {
  const document = ingest({
    tsconfigPath: positional[0],
    repositoryRoot: optionValue("--repository-root"),
    projectId: optionValue("--project-id"),
  });
  const outputPath = path.resolve(positional[1]);
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, `${JSON.stringify(document, null, 2)}\n`, "utf8");
} catch (error) {
  console.error(`ingest-typescript: ${error instanceof Error ? error.message : String(error)}`);
  process.exit(1);
}
