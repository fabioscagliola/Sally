import fs from "node:fs";
import path from "node:path";
import ts from "typescript";

export type Scalar = string | number | boolean;

export interface SourceLocation {
  source_uri: string;
  start_line: number;
  start_column: number;
  end_line: number;
  end_column: number;
}

export interface GraphNode {
  source_id: string;
  type: "Project" | "Type" | "Function" | "Method" | "Property";
  properties: Record<string, Scalar | string[]>;
  location?: SourceLocation;
}

export interface GraphRelationship {
  source_id: string;
  target_id: string;
  type: "CONTAINS" | "CALLS" | "USES_TYPE" | "INHERITS" | "IMPLEMENTS";
  properties: Record<string, Scalar | string[]>;
}

export interface GraphDocument {
  format: "sally-graph-rag";
  version: 1;
  nodes: GraphNode[];
  relationships: GraphRelationship[];
}

interface Entity {
  id: string;
  node: GraphNode;
  symbol: ts.Symbol;
  declaration: ts.Declaration;
}

const supportedSourceExtensions = new Set([".ts", ".tsx", ".mts", ".cts"]);

export interface IngestOptions {
  tsconfigPath: string;
  repositoryRoot?: string;
  projectId?: string;
}

export function ingest(options: IngestOptions): GraphDocument {
  const configPath = path.resolve(options.tsconfigPath);
  const configDirectory = path.dirname(configPath);
  const repositoryRoot = path.resolve(options.repositoryRoot ?? configDirectory);
  const config = ts.readConfigFile(configPath, ts.sys.readFile);
  if (config.error) {
    throw new Error(formatDiagnostic(config.error));
  }

  const parsed = ts.parseJsonConfigFileContent(config.config, ts.sys, configDirectory, undefined, configPath);
  const errors = parsed.errors.filter((diagnostic) => diagnostic.category === ts.DiagnosticCategory.Error);
  if (errors.length > 0) {
    throw new Error(errors.map(formatDiagnostic).join("\n"));
  }

  const program = ts.createProgram({ rootNames: parsed.fileNames, options: parsed.options });
  const projectRoot = configDirectory;
  const sourceFiles = program.getSourceFiles().filter((sourceFile) => isProjectSource(sourceFile, projectRoot));
  const checker = program.getTypeChecker();
  const projectIdentity = projectId(configPath, projectRoot, repositoryRoot, options.projectId);
  const projectName = projectNameFor(projectRoot, projectIdentity);
  const nodes = new Map<string, GraphNode>();
  const entities = new Map<string, Entity>();
  const declarations = new Map<ts.Declaration, Entity>();
  const relationships = new Map<string, GraphRelationship>();

  const projectNode: GraphNode = {
    source_id: projectIdentity,
    type: "Project",
    properties: {
      name: projectName,
      path: relativePortable(repositoryRoot, projectRoot),
      tsconfig: relativePortable(repositoryRoot, configPath),
    },
  };
  nodes.set(projectIdentity, projectNode);

  const addEntity = (declaration: ts.Declaration, type: GraphNode["type"], properties: Record<string, Scalar | string[]>): Entity | undefined => {
    const symbol = declarationSymbol(checker, declaration);
    if (!symbol) return undefined;
    const normalized = normalizeSymbol(checker, symbol);
    const key = symbolKey(checker, normalized, declaration, projectRoot, repositoryRoot);
    const existing = entities.get(key);
    if (existing) {
      declarations.set(declaration, existing);
      return existing;
    }
    const id = `${projectIdentity}:${key}`;
    const node: GraphNode = {
      source_id: id,
      type,
      properties,
      location: locationFor(declaration.getSourceFile(), declaration, repositoryRoot),
    };
    const entity = { id, node, symbol: normalized, declaration };
    entities.set(key, entity);
    declarations.set(declaration, entity);
    nodes.set(id, node);
    return entity;
  };

  for (const sourceFile of sourceFiles.sort((left, right) => left.fileName.localeCompare(right.fileName))) {
    sourceFile.forEachChild((node) => collectDeclarations(node, addEntity, checker, repositoryRoot));
  }

  const addRelationship = (sourceId: string | undefined, targetId: string | undefined, type: GraphRelationship["type"]): void => {
    if (!sourceId || !targetId || sourceId === targetId || !nodes.has(sourceId) || !nodes.has(targetId)) return;
    const key = `${sourceId}\0${targetId}\0${type}`;
    relationships.set(key, { source_id: sourceId, target_id: targetId, type, properties: {} });
  };

  const entityForSymbol = (symbol: ts.Symbol | undefined, declaration?: ts.Declaration): Entity | undefined => {
    if (!symbol) return undefined;
    const normalized = normalizeSymbol(checker, symbol);
    if (declaration) {
      const fromDeclaration = declarations.get(declaration);
      if (fromDeclaration) return fromDeclaration;
    }
    const key = symbolKey(checker, normalized, declaration ?? normalized.declarations?.[0], projectRoot, repositoryRoot);
    return entities.get(key);
  };

  for (const entity of entities.values()) {
    const parent = containingEntity(entity.declaration, declarations, projectIdentity);
    addRelationship(parent, entity.id, "CONTAINS");
    collectDeclarationRelationships(entity, checker, entityForSymbol, addRelationship);
  }

  for (const sourceFile of sourceFiles) {
    sourceFile.forEachChild((node) => collectReferenceRelationships(node, checker, declarations, entityForSymbol, addRelationship));
  }

  const document: GraphDocument = {
    format: "sally-graph-rag",
    version: 1,
    nodes: [...nodes.values()].sort((left, right) => left.source_id.localeCompare(right.source_id)),
    relationships: [...relationships.values()].sort((left, right) =>
      left.source_id.localeCompare(right.source_id) || left.target_id.localeCompare(right.target_id) || left.type.localeCompare(right.type)),
  };
  validateDocument(document);
  return document;
}

function collectDeclarations(
  node: ts.Node,
  addEntity: (declaration: ts.Declaration, type: GraphNode["type"], properties: Record<string, Scalar | string[]>) => Entity | undefined,
  checker: ts.TypeChecker,
  repositoryRoot: string,
): void {
  if (ts.isClassDeclaration(node) || ts.isInterfaceDeclaration(node) || ts.isTypeAliasDeclaration(node) || ts.isEnumDeclaration(node)) {
    const symbol = node.name && checker.getSymbolAtLocation(node.name);
    if (symbol) {
      addEntity(node, "Type", {
        name: node.name!.text,
        kind: typeKind(node),
        fully_qualified_name: qualifiedNameForGraph(checker, symbol, repositoryRoot),
      });
    }
  } else if (ts.isFunctionDeclaration(node) && node.name) {
    const symbol = checker.getSymbolAtLocation(node.name);
    if (symbol) addEntity(node, "Function", functionProperties(node, checker, symbol, repositoryRoot));
  } else if (ts.isMethodDeclaration(node) || ts.isMethodSignature(node) || ts.isConstructorDeclaration(node) || ts.isGetAccessorDeclaration(node) || ts.isSetAccessorDeclaration(node)) {
    const name = node.name && ts.isIdentifier(node.name) ? node.name.text : "constructor";
    const symbol = node.name ? checker.getSymbolAtLocation(node.name) : undefined;
    if (symbol) addEntity(node, "Method", methodProperties(node, checker, symbol, repositoryRoot));
  } else if (ts.isPropertyDeclaration(node) || ts.isPropertySignature(node) || ts.isAccessor(node)) {
    const name = node.name && ts.isIdentifier(node.name) ? node.name.text : undefined;
    const symbol = node.name ? checker.getSymbolAtLocation(node.name) : undefined;
    if (name && symbol) {
      addEntity(node, "Property", {
        name,
        fully_qualified_name: qualifiedNameForGraph(checker, symbol, repositoryRoot),
        declared_type: safeTypeString(checker, checker.getTypeAtLocation(node), repositoryRoot),
      });
    }
  } else if (ts.isVariableDeclaration(node) && ts.isIdentifier(node.name) && node.initializer &&
             (ts.isArrowFunction(node.initializer) || ts.isFunctionExpression(node.initializer))) {
    const symbol = checker.getSymbolAtLocation(node.name);
    if (symbol) addEntity(node, "Function", functionProperties(node.initializer, checker, symbol, repositoryRoot, node.name.text));
  }

  node.forEachChild((child) => collectDeclarations(child, addEntity, checker, repositoryRoot));
}

function collectDeclarationRelationships(
  entity: Entity,
  checker: ts.TypeChecker,
  entityForSymbol: (symbol: ts.Symbol | undefined, declaration?: ts.Declaration) => Entity | undefined,
  addRelationship: (sourceId: string | undefined, targetId: string | undefined, type: GraphRelationship["type"]) => void,
): void {
  const node = entity.declaration;
  if (ts.isClassDeclaration(node) || ts.isInterfaceDeclaration(node)) {
    for (const clause of node.heritageClauses ?? []) {
      for (const expression of clause.types) {
        const target = entityForSymbol(checker.getSymbolAtLocation(expression.expression));
        addRelationship(entity.id, target?.id, clause.token === ts.SyntaxKind.ExtendsKeyword ? "INHERITS" : "IMPLEMENTS");
        collectTypeRelationships(entity.id, checker.getTypeAtLocation(expression), checker, entityForSymbol, addRelationship);
      }
    }
  }
  if (ts.isFunctionLike(node)) {
    for (const parameter of node.parameters) collectTypeNodeRelationships(entity.id, parameter.type, checker, entityForSymbol, addRelationship);
    collectTypeNodeRelationships(entity.id, node.type, checker, entityForSymbol, addRelationship);
  }
  if (ts.isPropertyDeclaration(node) || ts.isPropertySignature(node)) {
    collectTypeNodeRelationships(entity.id, node.type, checker, entityForSymbol, addRelationship);
  }
}

function collectReferenceRelationships(
  node: ts.Node,
  checker: ts.TypeChecker,
  declarations: Map<ts.Declaration, Entity>,
  entityForSymbol: (symbol: ts.Symbol | undefined, declaration?: ts.Declaration) => Entity | undefined,
  addRelationship: (sourceId: string | undefined, targetId: string | undefined, type: GraphRelationship["type"]) => void,
): void {
  if (ts.isCallExpression(node) || ts.isNewExpression(node)) {
    const callerEntity = enclosingEntity(node, declarations);
    const targetDeclaration = checker.getResolvedSignature(node)?.declaration;
    const targetSymbol = targetDeclaration ? declarationSymbol(checker, targetDeclaration) : undefined;
    addRelationship(callerEntity?.id, entityForSymbol(targetSymbol, targetDeclaration)?.id, "CALLS");
    if (ts.isNewExpression(node)) {
      collectTypeRelationships(callerEntity?.id, checker.getTypeAtLocation(node), checker, entityForSymbol, addRelationship);
    }
  }
  if (ts.isTypeReferenceNode(node)) {
    const source = enclosingEntity(node, declarations)?.id;
    collectTypeNodeRelationships(source, node, checker, entityForSymbol, addRelationship);
  }
  node.forEachChild((child) => collectReferenceRelationships(child, checker, declarations, entityForSymbol, addRelationship));
}

function collectTypeNodeRelationships(
  sourceId: string | undefined,
  node: ts.TypeNode | undefined,
  checker: ts.TypeChecker,
  entityForSymbol: (symbol: ts.Symbol | undefined, declaration?: ts.Declaration) => Entity | undefined,
  addRelationship: (sourceId: string | undefined, targetId: string | undefined, type: GraphRelationship["type"]) => void,
): void {
  if (!sourceId || !node) return;
  collectTypeRelationships(sourceId, checker.getTypeAtLocation(node), checker, entityForSymbol, addRelationship);
}

function collectTypeRelationships(
  sourceId: string | undefined,
  type: ts.Type,
  checker: ts.TypeChecker,
  entityForSymbol: (symbol: ts.Symbol | undefined, declaration?: ts.Declaration) => Entity | undefined,
  addRelationship: (sourceId: string | undefined, targetId: string | undefined, type: GraphRelationship["type"]) => void,
  seen: Set<ts.Type> = new Set(),
): void {
  if (!sourceId) return;
  if (seen.has(type)) return;
  seen.add(type);
  if (type.isUnionOrIntersection()) {
    for (const member of type.types) collectTypeRelationships(sourceId, member, checker, entityForSymbol, addRelationship, seen);
    return;
  }
  if (type.symbol) addRelationship(sourceId, entityForSymbol(type.symbol)?.id, "USES_TYPE");
  if (type.aliasSymbol) addRelationship(sourceId, entityForSymbol(type.aliasSymbol)?.id, "USES_TYPE");
  if (type.flags & ts.TypeFlags.Object && typeReferenceHasArguments(type)) {
    for (const argument of checker.getTypeArguments(type as ts.TypeReference)) {
      collectTypeRelationships(sourceId, argument, checker, entityForSymbol, addRelationship, seen);
    }
  }
}

function typeReferenceHasArguments(type: ts.Type): boolean {
  return (type as ts.TypeReference).typeArguments !== undefined;
}

function enclosingEntity(node: ts.Node, declarations: Map<ts.Declaration, Entity>): Entity | undefined {
  for (let current: ts.Node | undefined = node.parent; current; current = current.parent) {
    const entity = declarations.get(current as ts.Declaration);
    if (entity) return entity;
  }
  return undefined;
}

function containingEntity(symbolEntity: ts.Declaration, declarations: Map<ts.Declaration, Entity>, projectIdValue: string): string {
  for (let current: ts.Node | undefined = symbolEntity.parent; current; current = current.parent) {
    if (ts.isSourceFile(current)) break;
    const entity = declarations.get(current as ts.Declaration);
    if (entity) return entity.id;
  }
  return projectIdValue;
}

function declarationSymbol(checker: ts.TypeChecker, declaration: ts.Declaration): ts.Symbol | undefined {
  const named = declaration as ts.NamedDeclaration;
  if (named.name) return checker.getSymbolAtLocation(named.name);
  if (ts.isConstructorDeclaration(declaration)) return checker.getSymbolAtLocation(declaration.parent.name!);
  return undefined;
}

function normalizeSymbol(checker: ts.TypeChecker, symbol: ts.Symbol): ts.Symbol {
  return symbol.flags & ts.SymbolFlags.Alias ? checker.getAliasedSymbol(symbol) : symbol;
}

function symbolKey(checker: ts.TypeChecker, symbol: ts.Symbol, declaration: ts.Declaration | undefined, projectRoot: string, repositoryRoot: string): string {
  const name = qualifiedNameForGraph(checker, symbol, repositoryRoot);
  const declarationIdentity = declaration
    ? `${relativePortable(projectRoot, declaration.getSourceFile().fileName)}:${declaration.getStart(declaration.getSourceFile())}`
    : "unknown";
  if (declaration && ts.isFunctionLike(declaration)) {
    const signature = checker.getSignatureFromDeclaration(declaration);
    if (signature) return `${declarationIdentity}:${name}|${signature.parameters.map((parameter) => safeTypeString(checker, checker.getTypeOfSymbolAtLocation(parameter, declaration), repositoryRoot)).join(",")}`;
  }
  return `${declarationIdentity}:${name}`;
}

function qualifiedNameForGraph(checker: ts.TypeChecker, symbol: ts.Symbol, repositoryRoot: string): string {
  return normalizeQualifiedName(safeQualifiedName(checker, symbol), repositoryRoot);
}

function normalizeQualifiedName(name: string, repositoryRoot: string): string {
  if (!name.startsWith('"')) return name;
  const closingQuote = name.indexOf('"', 1);
  if (closingQuote < 0) return name;
  const sourcePath = name.slice(1, closingQuote);
  if (!path.isAbsolute(sourcePath)) return name;
  return `"${relativePortable(repositoryRoot, sourcePath)}"${name.slice(closingQuote + 1)}`;
}

function functionProperties(node: ts.SignatureDeclaration, checker: ts.TypeChecker, symbol: ts.Symbol, repositoryRoot: string, nameOverride?: string): Record<string, Scalar | string[]> {
  return {
    name: nameOverride ?? (node.name && ts.isIdentifier(node.name) ? node.name.text : qualifiedNameForGraph(checker, symbol, repositoryRoot)),
    fully_qualified_name: qualifiedNameForGraph(checker, symbol, repositoryRoot),
    return_type: safeTypeString(checker, checker.getSignatureFromDeclaration(node)?.getReturnType() ?? checker.getTypeAtLocation(node), repositoryRoot),
  };
}

function methodProperties(node: ts.SignatureDeclaration, checker: ts.TypeChecker, symbol: ts.Symbol, repositoryRoot: string): Record<string, Scalar | string[]> {
  return {
    ...functionProperties(node, checker, symbol, repositoryRoot),
    kind: ts.isConstructorDeclaration(node) ? "constructor" : "method",
  };
}

function typeKind(node: ts.ClassDeclaration | ts.InterfaceDeclaration | ts.TypeAliasDeclaration | ts.EnumDeclaration): string {
  if (ts.isClassDeclaration(node)) return "class";
  if (ts.isInterfaceDeclaration(node)) return "interface";
  if (ts.isEnumDeclaration(node)) return "enum";
  return "type_alias";
}

function safeTypeString(checker: ts.TypeChecker, type: ts.Type, repositoryRoot?: string): string {
  try {
    const value = checker.typeToString(type);
    return repositoryRoot ? normalizeEmbeddedPaths(value, repositoryRoot) : value;
  } catch {
    return "unknown";
  }
}

function normalizeEmbeddedPaths(value: string, repositoryRoot: string): string {
  return value.replace(/(["'])((?:\\.|[^"'])*)\1/g, (match, quote: string, candidate: string) =>
    path.isAbsolute(candidate) ? `${quote}${relativePortable(repositoryRoot, candidate)}${quote}` : match);
}

function safeQualifiedName(checker: ts.TypeChecker, symbol: ts.Symbol): string {
  try {
    return checker.getFullyQualifiedName(symbol);
  } catch {
    return symbol.getName();
  }
}

function isProjectSource(sourceFile: ts.SourceFile, projectRoot: string): boolean {
  const filePath = path.resolve(sourceFile.fileName);
  return supportedSourceExtensions.has(path.extname(filePath).toLowerCase()) &&
    !sourceFile.isDeclarationFile &&
    !filePath.split(path.sep).includes("node_modules") &&
    isWithin(projectRoot, filePath);
}

function locationFor(sourceFile: ts.SourceFile, declaration: ts.Declaration, repositoryRoot: string): SourceLocation {
  const start = sourceFile.getLineAndCharacterOfPosition(declaration.getStart(sourceFile));
  const end = sourceFile.getLineAndCharacterOfPosition(declaration.end);
  return {
    source_uri: relativePortable(repositoryRoot, sourceFile.fileName),
    start_line: start.line + 1,
    start_column: start.character + 1,
    end_line: end.line + 1,
    end_column: end.character + 1,
  };
}

function projectId(configPath: string, projectRoot: string, repositoryRoot: string, explicitProjectId?: string): string {
  const identity = explicitProjectId?.trim() || projectNameFor(projectRoot) || relativePortable(repositoryRoot, projectRoot);
  return `project:${identity}:${relativePortable(repositoryRoot, configPath)}`;
}

function projectNameFor(projectRoot: string, projectIdentity?: string): string {
  const packagePath = path.join(projectRoot, "package.json");
  try {
    const packageName = JSON.parse(fs.readFileSync(packagePath, "utf8")).name;
    if (typeof packageName === "string" && packageName.trim()) return packageName;
  } catch {
    // A package manifest is optional for TypeScript projects.
  }
  return projectIdentity?.replace(/^project:/, "").split(":")[0] || path.basename(projectRoot);
}

function relativePortable(root: string, value: string): string {
  return path.relative(root, path.resolve(value)).split(path.sep).join("/") || ".";
}

function isWithin(root: string, value: string): boolean {
  const relative = path.relative(root, value);
  return relative === "" || (!relative.startsWith(".." + path.sep) && relative !== "..");
}

function validateDocument(document: GraphDocument): void {
  const ids = new Set(document.nodes.map((node) => node.source_id));
  if (document.format !== "sally-graph-rag" || document.version !== 1) throw new Error("invalid Graph RAG contract header");
  for (const node of document.nodes) if (!node.source_id.trim() || !node.type) throw new Error("invalid graph node");
  for (const relationship of document.relationships) {
    if (!ids.has(relationship.source_id) || !ids.has(relationship.target_id)) throw new Error("relationship endpoint is missing");
  }
}

function formatDiagnostic(diagnostic: ts.Diagnostic): string {
  return ts.flattenDiagnosticMessageText(diagnostic.messageText, "\n");
}
