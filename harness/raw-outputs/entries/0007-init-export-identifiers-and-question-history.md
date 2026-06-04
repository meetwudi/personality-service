# 0007: Init, Export, Identifiers, and Question History

## Topic

Knowledge graph hydration API

## Source

Human design discussion.

## Raw Discussion

The graph should be downloadable so it can be visualized locally. This suggests an `api/experimental/export/` API that can take an identifier.

GPT or any downstream client should pass an identifier to `api/experimental/interrogate/`. Each identifier corresponds to a graph. The identifier should be in UUID format, and the server should validate this so the identifier is not easily guessable. This is experimental rather than production, but basic safety is important.

The `api/experimental/interrogate/` AI behavior should be exploratory. It can decide to go back and forth to clarify what to ask. The goal is to hydrate the graph with diverse information.

There should be an `api/experimental/init/` API that returns the initial instruction to AI. The instruction should tell the AI how to use the APIs and the goal.

The AI needs to pass a stable UUID to use in order to get the right results. The AI should keep answering questions until the API returns no questions, or it has answered 100 questions already using the `api/experimental/learn/` API. The `learn/` API should acknowledge that learning was complete.

The graph should store questions that have already been asked so they are not repeated. `interrogate/` asks questions based on the ontology, questions already asked, and data in the graph.

Finally, the AI should provide the link to download the graph.
