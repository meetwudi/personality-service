# Requirement: Graph Identifier

Acceptance criteria are human-authored only. Do not invent, infer, broaden, or fill in acceptance criteria.

## Scope

Downstream clients pass a stable identifier so the server can operate on the correct graph. Each identifier corresponds to a graph.

## Acceptance Test Criteria

- GPT or any downstream client should pass an identifier to `api/experimental/interrogate/`.
- Each identifier corresponds to a graph.
- The identifier should be in UUID format.
- The server validates that the identifier is in UUID format.
- The UUID validation helps ensure the identifier is not easily guessable.
- The same stable UUID is used to get the right results.
- `api/experimental/init/` gives the identifier for the normal client flow.
