# Requirement: Init Endpoint

Acceptance criteria are human-authored only. Do not invent, infer, broaden, or fill in acceptance criteria.

## Scope

The `api/experimental/init/` API returns the initial instruction to the AI, explaining the API mechanics the AI should follow without requiring prior knowledge of the experiment.

## Acceptance Test Criteria

- The API path is `api/experimental/init/`.
- The API returns the initial instruction to the AI.
- The instruction tells the AI how to use the APIs.
- The instruction is written for a client that does not know the experiment details.
- The instruction explains that there is an endpoint that gives questions.
- The instruction explains how to give answers.
- The instruction explains how many questions to aim for.
- The endpoint gives the identifier.
- The instruction explains that the client should use the identifier returned by `api/experimental/init/`.
- The instruction tells the AI to make API calls.
- The instruction tells the AI to ask the human the returned questions.
- The instruction tells the AI to submit the human's answers.
- The instruction tells the AI not to write scripts or local runners.
- The instruction tells the AI not to fabricate answers.
- The instruction tells the AI to call `api/experimental/interrogate/` again after `api/experimental/learn/` acknowledges submitted answers.
- The instruction tells the AI not to stop only because `api/experimental/learn/` acknowledged submitted answers.
- The instruction does not need to explain details like RDF or graphs.
- The instruction allows a user to point an AI client at `api/experimental/init/` and tell it to do whatever the endpoint instructs.
- The instruction leads the AI through the hydration process and ultimately to the graph download.
- The instruction tells the AI it needs to pass a stable UUID to get the right results.
- The instruction tells the AI to keep answering questions until the configurable answer cap is reached.
- The instruction tells the AI that `api/experimental/learn/` should acknowledge that learning was complete.
- The instruction tells the AI to provide the link to download the graph.
