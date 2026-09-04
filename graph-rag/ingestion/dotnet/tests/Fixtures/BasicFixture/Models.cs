namespace BasicFixture;

public interface IContract
{
    string Name { get; }
}

public abstract class BaseModel
{
    public abstract string Describe();
}

public partial class ExampleModel : BaseModel, IContract
{
    public string Name { get; }
    public List<ExampleRecord> Records { get; } = [];

    public ExampleModel(string name)
    {
        Name = name;
    }

    public override string Describe()
    {
        return Name;
    }

    public string Describe(string prefix)
    {
        return prefix + Name;
    }

    public static ExampleModel Create(string name)
    {
        return new ExampleModel(name);
    }

    public static string CreateAndDescribe(string name)
    {
        return Create(name).Describe();
    }

    public static void UseRecords(IEnumerable<ExampleRecord> records)
    {
    }
}

public record ExampleRecord(int Value);

public enum ExampleKind
{
    First,
}