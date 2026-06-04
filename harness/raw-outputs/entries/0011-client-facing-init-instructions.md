# 0011: Client-Facing Init Instructions

## Topic

Knowledge graph hydration API

## Source

Human clarification.

## Raw Decision

The `api/experimental/init/` response should be written for a client that does not know the experiment details.

The init response should explain only the mechanics:

- There is an endpoint that gives questions.
- There is a way to give answers.
- How many questions to aim for.
- How to generate or use identifiers.

The init response does not need to explain details like RDF or graphs.
