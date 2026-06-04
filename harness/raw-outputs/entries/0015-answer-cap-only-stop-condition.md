# 0015: Answer Cap Only Stop Condition

## Topic

Knowledge graph hydration API

## Source

Human clarification after local testing.

## Raw Decision

For now, the stopping condition should be only that the answer cap is reached.

The cap is 100 by default and should be configurable.

The alternative stopping condition, where the AI decides the graph is sufficiently hydrated, is tabled for later.

This saves time because the project does not need to define what counts as sufficiently hydrated yet.
