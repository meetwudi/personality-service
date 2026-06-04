# Personality Service

Experimental API for AI-assisted RDF knowledge graph hydration.

## Run locally

```bash
cd app
python3 -m pip install -e .
python3 -m uvicorn personality_service.main:app --reload
```

Start an AI client at:

```text
GET /api/experimental/init/
```

The init response gives the client the full loop: create or reuse a stable UUID, call `interrogate`, answer through `learn`, and finish with `export`.
