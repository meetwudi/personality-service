# Requirement: Interrogate Endpoint

Acceptance criteria are human-authored only. Do not invent, infer, broaden, or fill in acceptance criteria.

## Scope

The `api/experimental/interrogate/` API examines the ontology, previously asked questions, and current graph data, then returns questions that the graph wants answered in order to hydrate itself incrementally.

## Acceptance Test Criteria

- The API path is `api/experimental/interrogate/`.
- The API accepts an identifier.
- When called, the API looks at the ontology.
- When called, the API looks at previously asked questions.
- When called, the API queries the graph.
- The API returns useful questions that the graph wants answered.
- The returned questions support incremental graph hydration.
- The API returns up to three questions by default.
- The question limit is configurable.
- For now, the API only returns no questions when the configurable answer cap has been reached.
