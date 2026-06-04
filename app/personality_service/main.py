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
from .settings import answer_cap

app = FastAPI(title="Personality Service", version="0.1.0")
store = GraphStore()


@app.get("/api/experimental/init/")
def init() -> dict[str, str | int]:
    identifier = str(uuid4())
    cap = answer_cap()
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
            "Call POST /api/experimental/interrogate/ with JSON like "
            '{"identifier":"<uuid>","limit":3}. It returns up to 3 questions by default. '
            "Ask these questions to the human."
        ),
        "answer_instruction": (
            "After the human answers questions, call POST /api/experimental/learn/ with JSON like "
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
            f"/api/experimental/export/?identifier={identifier}"
        ),
        "interrogate_endpoint": "/api/experimental/interrogate/",
        "learn_endpoint": "/api/experimental/learn/",
        "export_endpoint": "/api/experimental/export/",
        "max_learned_answers": cap,
    }


@app.post("/api/experimental/interrogate/", response_model=InterrogateResponse)
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


@app.post("/api/experimental/learn/", response_model=LearnResponse)
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


@app.get("/api/experimental/export/")
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
    return f"/api/experimental/export/?identifier={identifier}"
