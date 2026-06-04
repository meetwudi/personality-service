# 0012: Init Provides Session Identifier

## Topic

Knowledge graph hydration API

## Source

Human clarification.

## Raw Decision

Clients should not generate identifiers themselves for the normal flow.

The `api/experimental/init/` endpoint gives the identifier, and clients should use that returned identifier for the session.
