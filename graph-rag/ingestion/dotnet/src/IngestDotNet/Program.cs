namespace IngestDotNet;

public static class Program
{
    public static int Main(string[] args)
    {
        var restore = args.Length > 0 && args[0] == "--restore";
        var arguments = restore ? args[1..] : args;
        if (arguments.Length != 2)
        {
            Console.Error.WriteLine("Usage: ingest-dotnet [--restore] <input.csproj|input.sln> <output.json>");
            return 2;
        }

        try
        {
            var inputPath = arguments[0];
            if (restore)
            {
                Restore(inputPath);
            }

            var document = new ProjectIngestor().Ingest(inputPath);
            GraphJson.Write(document, arguments[1]);
            return 0;
        }
        catch (Exception error)
        {
            Console.Error.WriteLine($"ingest-dotnet: {error.Message}");
            return 1;
        }
    }

    private static void Restore(string inputPath)
    {
        var startInfo = new System.Diagnostics.ProcessStartInfo("dotnet")
        {
            RedirectStandardError = true,
            RedirectStandardOutput = true,
            UseShellExecute = false,
        };
        startInfo.ArgumentList.Add("restore");
        startInfo.ArgumentList.Add(inputPath);

        using var process = System.Diagnostics.Process.Start(startInfo)
            ?? throw new InvalidOperationException("could not start dotnet restore");
        var output = process.StandardOutput.ReadToEnd();
        var error = process.StandardError.ReadToEnd();
        process.WaitForExit();
        if (process.ExitCode != 0)
        {
            var details = string.IsNullOrWhiteSpace(error) ? output : error;
            throw new InvalidOperationException($"dotnet restore failed for '{inputPath}': {details.Trim()}");
        }
    }
}