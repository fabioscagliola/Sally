using Microsoft.Build.Locator;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp.Syntax;
using Microsoft.CodeAnalysis.MSBuild;

namespace IngestDotNet;

public sealed class ProjectIngestor
{
    private static readonly HashSet<string> SupportedTypes = new(StringComparer.Ordinal)
    {
        "Project", "Type", "Method", "Property",
    };

    private static readonly HashSet<string> SupportedRelationships = new(StringComparer.Ordinal)
    {
        "CONTAINS", "INHERITS", "IMPLEMENTS", "CALLS", "USES_TYPE",
    };

    public GraphDocument Ingest(string inputPath)
    {
        var fullInputPath = Path.GetFullPath(inputPath);
        if (!File.Exists(fullInputPath))
        {
            throw new FileNotFoundException("input project or solution was not found", fullInputPath);
        }

        if (!MSBuildLocator.IsRegistered)
        {
            MSBuildLocator.RegisterDefaults();
        }

        using var workspace = MSBuildWorkspace.Create();
        var workspaceErrors = new List<string>();
        workspace.WorkspaceFailed += (_, eventArgs) =>
        {
            if (eventArgs.Diagnostic.Kind == WorkspaceDiagnosticKind.Failure)
            {
                workspaceErrors.Add(eventArgs.Diagnostic.Message);
            }
        };

        var extension = Path.GetExtension(fullInputPath);
        var solution = extension.Equals(".sln", StringComparison.OrdinalIgnoreCase)
            ? workspace.OpenSolutionAsync(fullInputPath).GetAwaiter().GetResult()
            : extension.Equals(".csproj", StringComparison.OrdinalIgnoreCase)
                ? workspace.OpenProjectAsync(fullInputPath).GetAwaiter().GetResult().Solution
                : throw new ArgumentException("input must be a .csproj or .sln file", nameof(inputPath));

        if (workspaceErrors.Count > 0)
        {
            throw new InvalidDataException(string.Join(Environment.NewLine, workspaceErrors.Distinct(StringComparer.Ordinal)));
        }

        var selectedProjects = extension.Equals(".sln", StringComparison.OrdinalIgnoreCase)
            ? solution.Projects.Where(project => project.Language == LanguageNames.CSharp).ToArray()
            : solution.Projects.Where(project => project.FilePath is not null &&
                                                 Path.GetFullPath(project.FilePath).Equals(fullInputPath, StringComparison.OrdinalIgnoreCase)).ToArray();
        if (selectedProjects.Length == 0)
        {
            throw new InvalidDataException("no C# project was loaded from the input");
        }

        var rootPath = Path.GetDirectoryName(fullInputPath)!;
        var graph = new GraphBuilder(rootPath, selectedProjects);
        foreach (var project in selectedProjects)
        {
            var compilation = project.GetCompilationAsync().GetAwaiter().GetResult();
            if (compilation is null)
            {
                throw new InvalidDataException($"could not create compilation for project {project.Name}");
            }

            graph.AddProject(project, compilation);
        }

        return graph.Build();
    }

    private sealed class GraphBuilder
    {
        private readonly string rootPath;
        private readonly IReadOnlyCollection<Project> selectedProjects;
        private readonly Dictionary<ISymbol, string> symbolIds = new(SymbolEqualityComparer.Default);
        private readonly Dictionary<string, GraphNode> nodes = new(StringComparer.Ordinal);
        private readonly HashSet<(string SourceId, string TargetId, string Type)> relationships = [];

        public GraphBuilder(string rootPath, IReadOnlyCollection<Project> selectedProjects)
        {
            this.rootPath = rootPath;
            this.selectedProjects = selectedProjects;
        }

        public void AddProject(Project project, Compilation compilation)
        {
            var projectId = ProjectId(project);
            AddNode(new GraphNode(projectId, "Project", Properties(("name", project.Name), ("path", RelativePath(project.FilePath))), null));

            foreach (var syntaxTree in compilation.SyntaxTrees.OrderBy(tree => tree.FilePath, StringComparer.Ordinal))
            {
                if (string.IsNullOrWhiteSpace(syntaxTree.FilePath) || IsGenerated(syntaxTree.FilePath))
                {
                    continue;
                }

                var model = compilation.GetSemanticModel(syntaxTree);
                var root = syntaxTree.GetRoot();
                foreach (var declaration in root.DescendantNodes().OfType<BaseTypeDeclarationSyntax>())
                {
                    if (model.GetDeclaredSymbol(declaration) is INamedTypeSymbol typeSymbol)
                    {
                        AddType(project, typeSymbol, declaration.GetLocation());
                    }
                }

                foreach (var declaration in root.DescendantNodes().OfType<MethodDeclarationSyntax>())
                {
                    if (model.GetDeclaredSymbol(declaration) is IMethodSymbol methodSymbol)
                    {
                        AddMethod(project, methodSymbol, declaration.GetLocation());
                    }
                }

                foreach (var declaration in root.DescendantNodes().OfType<ConstructorDeclarationSyntax>())
                {
                    if (model.GetDeclaredSymbol(declaration) is IMethodSymbol constructorSymbol)
                    {
                        AddMethod(project, constructorSymbol, declaration.GetLocation());
                    }
                }

                foreach (var declaration in root.DescendantNodes().OfType<PropertyDeclarationSyntax>())
                {
                    if (model.GetDeclaredSymbol(declaration) is IPropertySymbol propertySymbol)
                    {
                        AddProperty(project, propertySymbol, declaration.GetLocation());
                    }
                }
            }

            AddRelationships(project, compilation);
        }

        public GraphDocument Build()
        {
            var document = new GraphDocument(
                nodes.Values.OrderBy(node => node.SourceId, StringComparer.Ordinal).ToArray(),
                relationships.OrderBy(edge => edge.SourceId, StringComparer.Ordinal)
                    .ThenBy(edge => edge.TargetId, StringComparer.Ordinal)
                    .ThenBy(edge => edge.Type, StringComparer.Ordinal)
                    .Select(edge => new GraphRelationship(edge.SourceId, edge.TargetId, edge.Type, new Dictionary<string, object?>()))
                    .ToArray());
            document.Validate();
            return document;
        }

        private void AddType(Project project, INamedTypeSymbol symbol, Location location)
        {
            var id = GetId(project, symbol);
            var kind = symbol.TypeKind switch
            {
                TypeKind.Class => symbol.IsRecord ? "record" : "class",
                TypeKind.Interface => "interface",
                TypeKind.Struct => symbol.IsRecord ? "record" : "struct",
                TypeKind.Enum => "enum",
                _ => symbol.TypeKind.ToString().ToLowerInvariant(),
            };
            AddNode(new GraphNode(id, "Type", Properties(("name", symbol.Name), ("kind", kind), ("fully_qualified_name", symbol.ToDisplayString())), LocationFor(location)));
        }

        private void AddMethod(Project project, IMethodSymbol symbol, Location location)
        {
            var id = GetId(project, symbol);
            var kind = symbol.MethodKind == MethodKind.Constructor ? "constructor" : "method";
            var properties = Properties(
                ("name", symbol.Name),
                ("kind", kind),
                ("fully_qualified_name", symbol.ToDisplayString()),
                ("return_type", symbol.ReturnType.ToDisplayString()));
            var parameterTypes = symbol.Parameters.Select(parameter => parameter.Type.ToDisplayString()).ToArray();
            if (parameterTypes.Length > 0)
            {
                properties["parameter_types"] = parameterTypes;
            }

            AddNode(new GraphNode(id, "Method", properties, LocationFor(location)));
        }

        private void AddProperty(Project project, IPropertySymbol symbol, Location location)
        {
            var id = GetId(project, symbol);
            AddNode(new GraphNode(id, "Property", Properties(
                ("name", symbol.Name),
                ("fully_qualified_name", symbol.ToDisplayString()),
                ("declared_type", symbol.Type.ToDisplayString())), LocationFor(location)));
        }

        private void AddRelationships(Project project, Compilation compilation)
        {
            var projectId = ProjectId(project);
            foreach (var node in nodes.Values.Where(node => node.SourceId.StartsWith(projectId + ":", StringComparison.Ordinal)).ToArray())
            {
                var symbol = symbolIds.FirstOrDefault(pair => pair.Value == node.SourceId).Key;
                if (symbol is null)
                {
                    continue;
                }

                var containerId = FindContainingEntity(symbol, projectId);
                AddRelationship(containerId, node.SourceId, "CONTAINS");

                if (symbol is INamedTypeSymbol type)
                {
                    foreach (var baseType in type.BaseType is { SpecialType: not SpecialType.System_Object } ? new[] { type.BaseType } : Array.Empty<INamedTypeSymbol>())
                    {
                        AddRelationship(node.SourceId, GetIdIfInScope(baseType), "INHERITS");
                    }

                    foreach (var implemented in type.Interfaces)
                    {
                        AddRelationship(node.SourceId, GetIdIfInScope(implemented), "IMPLEMENTS");
                    }
                }

                if (symbol is IMethodSymbol method)
                {
                    foreach (var parameter in method.Parameters)
                    {
                        AddTypeRelationship(node.SourceId, parameter.Type);
                    }

                    AddTypeRelationship(node.SourceId, method.ReturnType);
                }

                if (symbol is IPropertySymbol property)
                {
                    AddTypeRelationship(node.SourceId, property.Type);
                }
            }

            foreach (var syntaxTree in compilation.SyntaxTrees.Where(tree => !IsGenerated(tree.FilePath)))
            {
                var model = compilation.GetSemanticModel(syntaxTree);
                foreach (var invocation in syntaxTree.GetRoot().DescendantNodes().OfType<InvocationExpressionSyntax>())
                {
                    var caller = model.GetEnclosingSymbol(invocation.SpanStart);
                    var target = model.GetSymbolInfo(invocation).Symbol as IMethodSymbol;
                    AddRelationship(GetIdIfInScope(caller), GetIdIfInScope(target), "CALLS");
                }

                foreach (var creation in syntaxTree.GetRoot().DescendantNodes().OfType<ObjectCreationExpressionSyntax>())
                {
                    var caller = model.GetEnclosingSymbol(creation.SpanStart);
                    var target = model.GetTypeInfo(creation).Type;
                    AddTypeRelationship(GetIdIfInScope(caller), target);
                }
            }
        }

        private void AddTypeRelationship(string? sourceId, ITypeSymbol? type)
        {
            if (type is null || type.TypeKind == TypeKind.Error)
            {
                return;
            }

            if (type is IArrayTypeSymbol arrayType)
            {
                AddTypeRelationship(sourceId, arrayType.ElementType);
                return;
            }

            if (type is INamedTypeSymbol namedType)
            {
                foreach (var typeArgument in namedType.TypeArguments)
                {
                    AddTypeRelationship(sourceId, typeArgument);
                }

                AddRelationship(sourceId, GetIdIfInScope(namedType.OriginalDefinition), "USES_TYPE");
                return;
            }

            AddRelationship(sourceId, GetIdIfInScope(type), "USES_TYPE");
        }

        private string FindContainingEntity(ISymbol symbol, string projectId)
        {
            for (var container = symbol.ContainingSymbol; container is not null; container = container.ContainingSymbol)
            {
                var containerId = GetIdIfInScope(container);
                if (containerId is not null && nodes.ContainsKey(containerId))
                {
                    return containerId;
                }
            }

            return projectId;
        }

        private string GetId(Project project, ISymbol symbol)
        {
            var id = SymbolId(project, symbol);
            symbolIds[symbol] = id;
            return id;
        }

        private string? GetIdIfInScope(ISymbol? symbol)
        {
            if (symbol is null)
            {
                return null;
            }

            var declaration = symbol.ContainingAssembly?.Identity.Name;
            var project = selectedProjects.FirstOrDefault(candidate => candidate.AssemblyName == declaration);
            if (project is null)
            {
                return null;
            }

            return SymbolId(project, symbol);
        }

        private void AddNode(GraphNode node)
        {
            nodes[node.SourceId] = node;
        }

        private void AddRelationship(string? sourceId, string? targetId, string type)
        {
            if (sourceId is null || targetId is null || !nodes.ContainsKey(sourceId) || !nodes.ContainsKey(targetId))
            {
                return;
            }

            relationships.Add((sourceId, targetId, type));
        }

        private string ProjectId(Project project) => "project:" + RelativePath(project.FilePath);

        private string SymbolId(Project project, ISymbol symbol)
        {
            var documentationId = DocumentationCommentId.CreateDeclarationId(symbol) ?? symbol.ToDisplayString(SymbolDisplayFormat.FullyQualifiedFormat);
            return ProjectId(project) + ":" + documentationId;
        }

        private string RelativePath(string? path)
        {
            if (string.IsNullOrWhiteSpace(path))
            {
                return "unknown";
            }

            return Path.GetRelativePath(rootPath, Path.GetFullPath(path)).Replace(Path.DirectorySeparatorChar, '/');
        }

        private SourceLocation? LocationFor(Location location)
        {
            if (!location.IsInSource)
            {
                return null;
            }

            var lineSpan = location.GetLineSpan();
            return new SourceLocation(
                RelativePath(lineSpan.Path),
                lineSpan.StartLinePosition.Line + 1,
                lineSpan.StartLinePosition.Character + 1,
                lineSpan.EndLinePosition.Line + 1,
                lineSpan.EndLinePosition.Character + 1);
        }

        private static bool IsGenerated(string? path) => path is not null &&
            (path.EndsWith(".g.cs", StringComparison.OrdinalIgnoreCase) || path.EndsWith(".generated.cs", StringComparison.OrdinalIgnoreCase));

        private static Dictionary<string, object?> Properties(params (string Key, object? Value)[] values) =>
            values.ToDictionary(value => value.Key, value => value.Value, StringComparer.Ordinal);
    }
}