# 0013: Init Must Not Trigger Script Writing

## Topic

Knowledge graph hydration API

## Source

Human clarification after testing another AI client.

## Raw Learning

The init instruction caused an AI client to misunderstand the task and write a script that fabricated answers.

The init instruction should say to make API calls, ask the human the returned questions, and submit the human's answers.

The init instruction should not cause the AI client to write a script, create a local runner, or fabricate answers.
