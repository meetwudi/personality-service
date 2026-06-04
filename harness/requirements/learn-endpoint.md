# Requirement: Learn Endpoint

Acceptance criteria are human-authored only. Do not invent, infer, broaden, or fill in acceptance criteria.

## Scope

The `api/experimental/learn/` API takes questions and their answers, then ingests the answers back into the graph.

## Acceptance Test Criteria

- The API path is `api/experimental/learn/`.
- The API takes questions along with their answers.
- The API ingests the answers back into the graph.
- Hydration directly writes learned facts to the graph.
- The API acknowledges submitted answers.
- The API does not indicate the whole session is complete after every submitted batch.
- The API indicates the session is complete when the configurable answer cap has been reached.
