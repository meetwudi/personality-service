from dataclasses import dataclass
from itertools import count
import os
from uuid import UUID

from pydantic import BaseModel, Field

from .ontology import RAW_ONTOLOGY
from .graph_store import SELF, GraphRecord, GraphStore, normalize_question


@dataclass(frozen=True)
class CandidateQuestion:
    text: str
    focus: str


class AgentQuestion(BaseModel):
    text: str = Field(description="The exact question to ask.")
    focus: str = Field(description="Ontology-aligned focus, such as values, needs, states, or patterns.")


class AgentQuestionSet(BaseModel):
    questions: list[AgentQuestion] = Field(description="Useful non-repeated questions to hydrate the graph.")


@dataclass(frozen=True)
class QuestionSelection:
    questions: list[CandidateQuestion]
    engine: str


CANDIDATES = [
    CandidateQuestion(
        "What values feel most important to you right now, and why?",
        "values",
    ),
    CandidateQuestion(
        "What recurring emotional, cognitive, somatic, or motivational state have you noticed recently?",
        "current-state",
    ),
    CandidateQuestion(
        "What need feels most satisfied or most thwarted in your life right now?",
        "needs",
    ),
    CandidateQuestion(
        "What pattern do you notice repeating in your work, relationships, or self-management?",
        "patterns",
    ),
    CandidateQuestion(
        "What situation reliably triggers a difficult state for you?",
        "triggers",
    ),
    CandidateQuestion(
        "What practice reliably helps restore you when you are depleted or dysregulated?",
        "restorative-practices",
    ),
    CandidateQuestion(
        "What preference should others know when collaborating or communicating with you?",
        "preferences",
    ),
    CandidateQuestion(
        "What goal is currently shaping your choices, attention, or tradeoffs?",
        "goals",
    ),
    CandidateQuestion(
        "What boundary protects your attention, energy, values, or relationships?",
        "boundaries",
    ),
    CandidateQuestion(
        "What identity narrative are you currently living into, questioning, or revising?",
        "identity-narrative",
    ),
]

FOLLOW_UP_FOCI = [
    "values",
    "current-state",
    "needs",
    "patterns",
    "triggers",
    "restorative-practices",
    "preferences",
    "goals",
    "boundaries",
    "identity-narrative",
]


FOCUS_CLASSES = {
    "values": SELF.Value,
    "current-state": SELF.State,
    "needs": SELF.Need,
    "patterns": SELF.Pattern,
    "triggers": SELF.Trigger,
    "restorative-practices": SELF.RestorativePractice,
    "preferences": SELF.Preference,
    "goals": SELF.Goal,
    "boundaries": SELF.Boundary,
    "identity-narrative": SELF.IdentityNarrative,
}


def choose_questions(store: GraphStore, identifier: UUID, limit: int) -> QuestionSelection:
    record = store.get(identifier)
    if os.getenv("OPENAI_API_KEY"):
        agent_questions = choose_questions_with_agents_sdk(store, record, limit)
        if agent_questions:
            for question in agent_questions:
                store.mark_asked(record, question.text, question.focus)
            return QuestionSelection(questions=agent_questions, engine="openai-agents-sdk")

    fallback_questions = choose_questions_deterministically(store, record, limit)
    return QuestionSelection(questions=fallback_questions, engine="deterministic-fallback")


def choose_questions_deterministically(
    store: GraphStore,
    record: GraphRecord,
    limit: int,
) -> list[CandidateQuestion]:
    candidates = sorted(
        CANDIDATES,
        key=lambda candidate: (
            focus_count(record, candidate.focus),
            normalize_question(candidate.text) in record.asked_questions,
        ),
    )
    selected: list[CandidateQuestion] = []
    for candidate in candidates:
        if normalize_question(candidate.text) in record.asked_questions:
            continue
        selected.append(candidate)
        if len(selected) == limit:
            break

    for candidate in generated_followups(record):
        if len(selected) == limit:
            break
        if normalize_question(candidate.text) in record.asked_questions:
            continue
        selected.append(candidate)

    for question in selected:
        store.mark_asked(record, question.text, question.focus)

    return selected


def generated_followups(record: GraphRecord):
    for index in count(record.learned_count + len(record.asked_questions) + 1):
        focus = FOLLOW_UP_FOCI[index % len(FOLLOW_UP_FOCI)]
        yield CandidateQuestion(
            text=(
                f"Share another specific example about your {focus.replace('-', ' ')} "
                f"that has not already come up. What happened, why did it matter, and "
                f"what should be remembered? (detail {index})"
            ),
            focus=focus,
        )


def choose_questions_with_agents_sdk(
    store: GraphStore,
    record: GraphRecord,
    limit: int,
) -> list[CandidateQuestion]:
    from agents import Agent, Runner

    agent = Agent(
        name="Self graph hydration question designer",
        instructions=(
            "You design exploratory questions for incrementally hydrating an RDF knowledge graph. "
            "The ontology/TBox defines what the graph wants to know. Use the graph summary and "
            "asked-question history to avoid repeats. Prefer diverse questions across values, "
            "needs, states, preferences, patterns, triggers, restorative practices, relationships, "
            "goals, boundaries, and identity narratives. Return only useful questions that can be "
            "answered by a person and later written directly into the graph."
        ),
        output_type=AgentQuestionSet,
    )
    prompt = f"""
Return up to {limit} questions.

Ontology/TBox:
```turtle
{RAW_ONTOLOGY}
```

Graph summary from SPARQL queries:
```text
{store.graph_summary(record)}
```
"""
    result = Runner.run_sync(agent, prompt, max_turns=3)
    output = result.final_output
    questions = [
        CandidateQuestion(text=item.text.strip(), focus=item.focus.strip())
        for item in output.questions[:limit]
        if item.text.strip()
        and normalize_question(item.text) not in record.asked_questions
    ]
    return questions


def focus_count(record: GraphRecord, focus: str) -> int:
    rdf_class = FOCUS_CLASSES.get(focus)
    if rdf_class is None:
        return 0
    query = """
    SELECT (COUNT(?subject) AS ?count)
    WHERE {
      ?subject a ?class .
    }
    """
    result = record.graph.query(query, initBindings={"class": rdf_class})
    for row in result:
        return int(row[0])
    return 0
