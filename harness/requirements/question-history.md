# Requirement: Question History

Acceptance criteria are human-authored only. Do not invent, infer, broaden, or fill in acceptance criteria.

## Scope

The graph stores questions that have already been asked so `api/experimental/interrogate/` does not repeat them.

## Acceptance Test Criteria

- The graph stores the questions that have already been asked.
- `api/experimental/interrogate/` uses previously asked questions when deciding what to ask.
- `api/experimental/interrogate/` avoids repeating questions.
- `api/experimental/interrogate/` asks questions based on the ontology, questions already asked, and data in the graph.
