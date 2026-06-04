# 0014: Learn Complete Stop Condition

## Topic

Knowledge graph hydration API

## Source

Human testing feedback.

## Raw Learning

The client stopped after 3 answers because `api/experimental/learn/` returned `complete: true`.

This is wrong for the intended flow. `learn/` should acknowledge submitted answers, but it should not tell the client the whole session is complete after every batch.

The client should continue by calling `api/experimental/interrogate/` again until `interrogate/` returns no questions or the 100-answer target is reached.
