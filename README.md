![Sally](assets/favicon_io/android-chrome-192x192.png)

# Sally

Human-driven AI-augmented SDLC powered by Graph RAG

## What is Sally

Sally is an AI-augmented software delivery lifecycle that helps teams move from backlog item to pull request while keeping humans in control.

## Where Sally came from

The ideas behind Sally came from a large enterprise software project I came to lead earlier this year, with forty developers working on a huge, ten-year-old codebase.

The documentation was obsolete. Those who had designed the original architecture had left the team or the company. No one knew the whole system anymore. The only reliable source of truth was the code itself.

At the same time, development was moving fast and under considerable pressure. Business Analysts were adding backlog items faster than developers could implement them.

Release scopes were being planned while requirements were still unclear and effort had not yet been estimated, but that is another story.

Someone came up with an apparently obvious solution. Add more developers and give them AI. Needless to say, that did not solve the problem.

New joiners struggled to understand the system.

Veterans became even more valuable, and an even greater bottleneck, because everyone depended on their knowledge.

And Business Analysts continued filling the backlog. They were under pressure too, being responsible for UAT as well. Some were also new to the project. As a result, many backlog items contained barely enough information for veterans and nowhere near enough for new joiners.

Developers were already using AI, but for code generation only and in very different ways.

This is the environment in which I introduced an approach similar to Sally.

Then another problem appeared. Around that time, AI coding tools were changing their pricing models, and using the new lifecycle suddenly became much more expensive. One of the main reasons was context. Agents had to repeatedly search the huge codebase to understand how things worked and where changes belonged.

That is what led me to introduce Graph RAG. The idea was to build a searchable representation of the codebase and its relationships and make that knowledge available to agents to avoid having them repeatedly search the codebase.

## Why “Sally”

Sally is the protagonist of the eponymous 1953 short story by Isaac Asimov. She is an autonomous car.

Like Asimov’s more famous robots, Sally and her fellow cars are equipped with positronic brains. But unlike most of Asimov’s robots, the autonomous cars in this story are not bound by the Three Laws of Robotics.

That is why I named this project after her. Modern AI has no equivalent of Asimov’s Laws. And therefore it should never be trusted blindly. Just like the autonomous cars in Asimov’s story, as you will learn if you read it.

My favorite passage is the one where the elderly, wise Mr. Harridge insists that his driver Jake remain behind the wheel, just in case.

> I said, “You won’t be needing me any more, Mr. Harridge?”
>
> He said, “What are you dithering about, Jake? You don’t think I’ll trust myself to a contraption like that, do you? You stay right at the controls.”
>
> I said, “But it works by itself, Mr. Harridge. It scans the road, reacts properly to obstacles, humans, and other cars, and remembers routes to travel.”
>
> “So they say. So they say. Just the same, you’re sitting right behind the wheel in case anything goes wrong.”

That is the spirit guiding this project. Leverage AI, but always keep human hands on the steering wheel.

## Lifecycle

Sally supports the journey from backlog item to pull request through a lifecycle with three AI-augmented stages.

See [Lifecycle](docs/lifecycle.md) for more info.

![Lifecycle](/assets/lifecycle.jpg)

## Graph RAG

Sally uses Graph RAG to give agents structured knowledge about the target project without requiring them to repeatedly search the codebase.

Language-specific ingestion pipelines analyze the source project and produce a common, technology-independent graph representation.

The current .NET ingestion pipeline uses Roslyn to analyze C# projects and solutions. TypeScript and Markdown ingestion pipelines will follow.

The resulting graph is serialized as JSON and ingested into Neo4j.

The source project remains the source of truth. The Neo4j graph is disposable derived data and is rebuilt from scratch when the project is ingested again.

![Graph](/assets/graph.png)

## Documentation

- [Lifecycle](docs/lifecycle.md)
- [Sally Graph RAG](graph-rag/README.md)
- [.NET ingestion](graph-rag/ingestion/dotnet/README.md)
- [GitHub quickstart guide](docs/github-quickstart-guide.md)

