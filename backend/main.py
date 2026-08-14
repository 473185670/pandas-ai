"""
PandasAI — FastAPI backend.

POST /generate   → natural language description → validated pandas code
GET  /health     → service health check
GET  /examples   → list built-in few-shot examples (for the frontend sidebar)

Run:  uvicorn main:app --reload --port 8000
"""

from __future__ import annotations

import os
from typing import Optional

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from few_shot import EXAMPLES, build_prompt, suggest_schema
from llm import get_provider
from rate_limit import limiter
from validator import validate

app = FastAPI(
    title="PandasAI — Natural Language to pandas Code",
    version="0.1.0",
    description="Generate ready-to-run Python/pandas code from English.",
)

# CORS — allow the Vercel/Netlify frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class GenerateRequest(BaseModel):
    description: str = Field(..., min_length=3, max_length=2000)
    schema_hint: Optional[str] = Field(
        None, description="Optional column names/dtypes, e.g. 'date(str), revenue(float)'"
    )


class GenerateResponse(BaseModel):
    code: str
    is_valid: bool
    syntax_error: str = ""
    safety_warnings: list[str] = []
    provider: str
    tokens_used: int = 0
    remaining_quota: int
    # Moat signal (non-breaking, added Aug 15): makes the schema-aware
    # differentiator visible. "schema-aware" when user provides column
    # hints, "guess-mode" when they don't — nudges users toward the
    # differentiated path without breaking the demo or API examples.
    schema_hint_used: bool = False
    quality_tier: str = "guess-mode"
    # Moat nudge (added Aug 15): when the user skipped schema_hint, suggest
    # one inferred from few-shot examples so they can re-run in schema-aware
    # mode. Empty string when no confident match. Non-breaking.
    schema_suggestion: str = ""


class ExampleOut(BaseModel):
    description: str
    category: str
    schema_hint: str


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok", "version": app.version}


@app.get("/examples", response_model=list[ExampleOut])
def examples():
    return [
        ExampleOut(description=e.description, category=e.category, schema_hint=e.schema_hint)
        for e in EXAMPLES
    ]


@app.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest, x_forwarded_for: Optional[str] = Header(None)):
    # Rate limit (by IP)
    client_ip = (x_forwarded_for or "local").split(",")[0].strip()
    allowed, remaining, _ = limiter.check(client_ip)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Free-tier limit reached ({limiter.limit}/day). Upgrade for unlimited queries.",
        )

    # Build prompt + call LLM
    schema_used = bool(req.schema_hint)
    prompt = build_prompt(req.description, req.schema_hint or "")
    provider = get_provider()
    llm_resp = provider.generate(prompt)

    # Validate
    result = validate(llm_resp.text)

    # Moat nudge: suggest a schema for guess-mode users so they can upgrade
    # to the schema-aware (differentiated) path on their next call.
    suggestion = "" if schema_used else suggest_schema(req.description)

    return GenerateResponse(
        code=result.code,
        is_valid=result.is_valid,
        syntax_error=result.syntax_error,
        safety_warnings=result.safety_warnings,
        provider=llm_resp.provider,
        tokens_used=llm_resp.tokens_used,
        remaining_quota=remaining,
        schema_hint_used=schema_used,
        quality_tier="schema-aware" if schema_used else "guess-mode",
        schema_suggestion=suggestion,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
