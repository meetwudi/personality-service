# 0017: Cloud Run OpenAI Key

## Topic

Knowledge graph hydration API

## Source

Human deployment clarification.

## Raw Decision

The Cloud Run test deployment should use the same `OPENAI_API_KEY` from the local shell environment.

For this deployment, using that key in the production-like test service is acceptable.
