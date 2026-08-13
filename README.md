# PandasAI 🌿 — Natural Language to pandas Code

> Rebuild project (Aug 12, 2026). Precedent: FormulaBot $200K/mo. Niche gap: dedicated Python/pandas code generator for developers.

Describe what you want to do with your data in English → get ready-to-run, syntax-validated Python/pandas code.

## 🌿 Live Demo

- **App**: <https://pandasai-frontend.vercel.app> (React frontend, nature-themed UI)
- **API**: <https://pandasai-backend.vercel.app/docs> (FastAPI Swagger docs)
- **Health**: <https://pandasai-backend.vercel.app/health> → `{"status":"ok"}`

The deployed backend generates real code via Gemini and validates it with `ast.parse` before returning. No stub. Example: *"Group sales by month, calculate total revenue and average order size"* → ready-to-run pandas with correct datetime handling.

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

## Status (Aug 14, 2026)

- ✅ Backend scaffold complete + smoke-tested (22 examples, validator catches syntax errors + dangerous ops)
- ✅ Frontend scaffold complete (nature-themed UI, 8 one-click examples, syntax highlighting, copy button)
- ✅ **LIVE & DEPLOYED**: Backend on Vercel (`pandasai-backend.vercel.app`) + Frontend on Vercel (`pandasai-frontend.vercel.app`)
- ✅ **Real LLM output**: `/generate` returns Gemini-generated, syntax-validated code (`is_valid=True`, `provider=gemini`)
- ✅ Dev.to launch article published: <https://dev.to/473185670/i-built-a-natural-language-pandas-code-generator-open-source-free-10i>
- ⏳ Billing: Stripe ($9/mo Pro tier)
- ⏳ RapidAPI listing (dual revenue, $0.01/call)

## Revenue model

- Free tier: 5 queries/day
- Pro: $9/mo (unlimited + CSV upload + history)
- RapidAPI: $0.01/call (dual revenue)
- Break-even: month 2 (10 paying users)

## License

MIT — see [LICENSE](LICENSE). Free to use, modify, and distribute. Star ⭐ the repo if it saves you syntax-lookup time.

