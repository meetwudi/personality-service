from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response

from .graph_store import GraphStore, parse_identifier
from .models import (
    InterrogateRequest,
    InterrogateResponse,
    LearnRequest,
    LearnResponse,
    Question,
)
from .question_engine import choose_questions
from .settings import answer_cap, public_base_url

app = FastAPI(
    title="Personality Service",
    version="0.1.0",
    servers=[{"url": public_base_url()}],
)
store = GraphStore()


@app.get("/privacy", include_in_schema=False)
def privacy() -> Response:
    policy = """
Personality Service Privacy Policy

This service is an experimental prototype for AI-assisted question asking and knowledge graph hydration.

Do not submit sensitive personal, financial, medical, legal, or confidential information.

The service receives API requests containing session identifiers, questions, and answers. For this test deployment, graph data is stored in memory by the running service and may be lost when the service restarts. The service also uses OpenAI APIs to generate questions, so request context may be sent to OpenAI for that purpose. The service is hosted on Google Cloud Run.

This prototype does not provide production-grade authentication, retention controls, deletion workflows, or data export guarantees beyond the experimental graph export endpoint.

Use of this service is for testing only.
""".strip()
    return Response(content=policy, media_type="text/plain")


@app.get(
    "/api/experimental/init/",
    operation_id="initSession",
    summary="Start a question-answer session",
    description="Returns concise instructions and a stable UUID identifier for this session.",
)
def init() -> dict[str, str | int]:
    identifier = str(uuid4())
    cap = answer_cap()
    base_url = public_base_url()
    return {
        "instruction": (
            "Make API calls only. Do not write scripts, create a local runner, or fabricate "
            "answers. Use the identifier below for this session. Call the question endpoint, "
            "ask the human the questions it returns, then submit the human's answers to the "
            "answer endpoint. After the answer endpoint acknowledges the submitted answers, "
            "call the question endpoint again. Repeat with more API calls until the answer cap "
            "is reached. When finished, give the human the export link."
        ),
        "identifier": identifier,
        "identifier_instruction": (
            "Use this UUID for the full session. Pass it as `identifier` to every request. "
            "To start a separate session, call this init endpoint again and use the new UUID it returns."
        ),
        "question_instruction": (
            f"Call POST {base_url}/api/experimental/interrogate/ with JSON like "
            '{"identifier":"<uuid>","limit":3}. It returns up to 3 questions by default. '
            "Ask these questions to the human."
        ),
        "answer_instruction": (
            f"After the human answers questions, call POST {base_url}/api/experimental/learn/ with JSON like "
            '{"identifier":"<uuid>","answers":[{"question":"...","answer":"..."}]}. '
            "Use the exact questions and the human's answers. The response acknowledges the "
            "submitted answers and returns an export URL. Unless the 100-answer cap has been "
            "reached, continue by calling the question endpoint again."
        ),
        "stop_instruction": (
            f"Collect exactly up to {cap} human-answered questions unless the human stops. "
            "For now, completion is based only on this answer cap."
        ),
        "export_instruction": (
            "When finished, provide this download link to the user: "
            f"{base_url}/api/experimental/export/?identifier={identifier}"
        ),
        "interrogate_endpoint": f"{base_url}/api/experimental/interrogate/",
        "learn_endpoint": f"{base_url}/api/experimental/learn/",
        "export_endpoint": f"{base_url}/api/experimental/export/",
        "max_learned_answers": cap,
    }


@app.post(
    "/api/experimental/interrogate/",
    response_model=InterrogateResponse,
    operation_id="getQuestions",
    summary="Get questions to ask the human",
    description=(
        "Use this action after initSession. Pass the session identifier returned by initSession. "
        "Ask the returned questions to the human, then submit the human's answers with submitAnswers."
    ),
)
def interrogate(request: InterrogateRequest) -> InterrogateResponse:
    identifier = validate_identifier(request.identifier)
    record = store.get(identifier)
    cap = answer_cap()
    if record.learned_count >= cap:
        return InterrogateResponse(
            identifier=str(identifier),
            questions=[],
            complete=True,
            export_url=export_url(identifier),
            question_engine="complete",
        )

    remaining = cap - record.learned_count
    selection = choose_questions(store, identifier, min(request.limit, remaining))
    return InterrogateResponse(
        identifier=str(identifier),
        questions=[Question(text=question.text, focus=question.focus) for question in selection.questions],
        complete=False,
        export_url=None,
        question_engine=selection.engine,
    )


@app.post(
    "/api/experimental/learn/",
    response_model=LearnResponse,
    operation_id="submitAnswers",
    summary="Submit human answers",
    description=(
        "Submit exact question and human-answer pairs. This acknowledges the batch and returns "
        "the current answer count and export URL. Continue with getQuestions until complete is true."
    ),
)
def learn(request: LearnRequest) -> LearnResponse:
    identifier = validate_identifier(request.identifier)
    record = store.get(identifier)
    cap = answer_cap()
    for item in request.answers:
        if record.learned_count >= cap:
            break
        store.learn(record, item.question, item.answer)

    return LearnResponse(
        identifier=str(identifier),
        learned_count=record.learned_count,
        complete=record.learned_count >= cap,
        export_url=export_url(identifier),
    )


@app.get(
    "/api/experimental/export/",
    operation_id="exportGraph",
    summary="Export the session graph",
    description="Downloads the current session graph as Turtle.",
)
def export(identifier: str = Query(description="Stable UUID identifying the graph.")) -> Response:
    parsed = validate_identifier(identifier)
    turtle = store.export_turtle(parsed)
    return Response(
        content=turtle,
        media_type="text/turtle",
        headers={
            "Content-Disposition": f'attachment; filename="self-graph-{parsed}.ttl"',
        },
    )


def validate_identifier(raw_identifier: str):
    try:
        return parse_identifier(raw_identifier)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def export_url(identifier) -> str:
    return f"{public_base_url()}/api/experimental/export/?identifier={identifier}"
