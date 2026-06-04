# 0008: Init-Driven AI Flow

## Topic

Knowledge graph hydration API

## Source

Human clarification.

## Raw Decision

The desired user flow is to point an AI client at `api/experimental/init/` and tell it to do whatever that endpoint instructs.

The `init/` response should lead the AI through the hydration process and ultimately to the graph download.

The current Google Cloud Platform project can be used for deployment when needed.
