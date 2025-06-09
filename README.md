# Dotnet Test Bathtub - Nicer Unit Test Soaking

## Soaker

`soaker.py` is a utility script for soak running .NET test suites using `dotnet test`, making it easier to identify flaky or intermittent test failures. It highlights failed and passed tests with color.

### Features

- Runs your .NET tests a specified number of times
- Highlights passed and failed tests in color for easy scanning
- Accepts any arguments you would normally pass to `dotnet test`

### Usage

```sh
python3 soaker.py [options] <number-of-runs> -- <target-sln-or-csproj> [dotnet-test-args]
```

- `[options]`: Optional flags to modify behavior (`--show-passed` to include passed tests).
- `<number-of-runs>`: The number of times to run the tests.
- `<target-sln-or-csproj>`: The path to your solution (`.sln`) or project (`.csproj`) file to test.
- `[dotnet-test-args]`: Any additional arguments you would normally pass to `dotnet test` (such as `--filter`, `--no-build`, etc).

#### Example

Run a specific test method in a solution:

```sh
python3 soaker.py 10 -- ~/Git/hudl-ticketing/Hudl.Ticketing.Webapp.sln
```

You can pass any arguments supported by `dotnet test` after the script name.

---

## Flake Finder

`flake_finder.py` is a utility script for repeatedly running .NET test suites using `dotnet test`, making it easier to catch flaky or intermittent test failures. It highlights failed and passed tests with color, prints out logs written via `ITestOutputHelper`, and pauses after failures to allow inspection before continuing.

### Features

- Runs your .NET tests in a loop
- Highlights passed and failed tests in color for easy scanning
- Prints out custom log output (from `ITestOutputHelper`)
- Pauses after any failed test run so you can review output before proceeding
- Accepts any arguments you would normally pass to `dotnet test`

### Usage

```sh
python3 flake_finder.py -- <target-sln-or-csproj> [dotnet-test-args]
```

- `<target-sln-or-csproj>`: The path to your solution (`.sln`) or project (`.csproj`) file to test.
- `[dotnet-test-args]`: Any additional arguments you would normally pass to `dotnet test` (such as `--filter`, `--no-build`, etc).

#### Example

Run a specific test method in a solution, repeating up to 1000 times:

```sh
python3 flake_finder.py -- ~/Git/hudl-ticketing/Hudl.Ticketing.Webapp.sln --filter "Fully.Qualified.Test.Name=Hudl.Ticketing.Tests.Dao.TicketedEventDaoTests.GetTicketedEventsByPassConfigIdTests.GetTicketedEventsByPassConfigId_PassingFirst_ReturnsCorrectModel"
```

You can pass any arguments supported by `dotnet test` after the script name.

---

_Tip: The script will pause after any failed run so you can review the output before continuing._

### Logging Output with ITestOutputHelper

To take advantage of the log capturing feature in `flake_finder.py`, use `ITestOutputHelper` in your xUnit tests to write log messages. Any output written with `ITestOutputHelper` will be displayed by the flake_finder script, making it easier to debug flaky tests.

#### Example (C#)

```csharp
using Xunit;

public class MyTests
{
    private readonly ITestOutputHelper _output;

    public MyTests(ITestOutputHelper output)
    {
        _output = output;
    }

    [Fact]
    public void ExampleTest()
    {
        _output.WriteLine("I want to check the out of this test");
        Assert.True(true);
    }
}
```
