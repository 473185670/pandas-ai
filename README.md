# PandasAI 🌿 — Natural Language to pandas Code

> Rebuild project (Aug 12, 2026). Precedent: FormulaBot $200K/mo. Niche gap: dedicated Python/pandas code generator for developers.

Describe what you want to do with your data in English → get ready-to-run, syntax-validated Python/pandas code.

## Architecture

```
pandas_ai/
├── backend/
│   ├── main.py          # FastAPI app: POST /generate, GET /health, GET /examples
│   ├── few_shot.py      # 22 few-shot examples across 11 categories (core differentiator)
│   ├── llm.py           # Pluggable providers: OpenAI / Anthropic / Ollama / Stub
│   ├── validator.py     # ast.parse syntax check + dangerous-op safety scan
│   ├── rate_limit.py    # IP-based 5/day free tier (in-memory, Redis-swappable)
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── App.jsx      # Single-page React app
    │   ├── main.jsx
    │   └── styles.css   # Nature-themed light green palette
    ├── index.html
    ├── vite.config.js
    └── package.json
```

## How it works

1. User types a natural-language request (+ optional data schema hint).
2. `few_shot.build_prompt()` assembles a system prompt with 22 curated pandas examples.
3. The LLM provider (`llm.get_provider()`) generates code — auto-selects OpenAI → Anthropic → Ollama → Stub based on available env vars.
4. `validator.validate()` extracts the code block, syntax-checks with `ast.parse`, and flags dangerous operations (eval/exec/subprocess/os.remove).
5. Validated code + safety status returned to the React frontend with syntax highlighting.

## Quick start

### Backend
```bash
cd pandas_ai/backend
pip install -r requirements.txt
cp .env.example .env       # fill in OPENAI_API_KEY or ANTHROPIC_API_KEY
python main.py             # → http://localhost:8000
```

### Frontend
```bash
cd pandas_ai/frontend
npm install
npm run dev                # → http://localhost:5173 (proxies /api → backend)
```

## API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/generate` | POST | `{description, schema_hint?}` → `{code, is_valid, safety_warnings, provider, remaining_quota}` |
| `/examples` | GET | List built-in few-shot examples |
| `/health` | GET | Service health check |

## Status (Aug 12, 2026)

- ✅ Backend scaffold complete + smoke-tested (22 examples, validator catches syntax errors + dangerous ops)
- ✅ Frontend scaffold complete (nature-themed UI, 8 one-click examples, syntax highlighting, copy button)
- ⏳ **BLOCKING**: Needs `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` to generate real code (currently returns stub)
- ⏳ Deploy: Render (backend) + Vercel (frontend)
- ⏳ Billing: Stripe ($9/mo Pro tier)
- ⏳ Launch: Product Hunt + Dev.to + CSDN + RapidAPI

## Revenue model

- Free tier: 5 queries/day
- Pro: $9/mo (unlimited + CSV upload + history)
- RapidAPI: $0.01/call (dual revenue)
- Break-even: month 2 (10 paying users)
