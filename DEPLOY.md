# DEPLOY.md — PandasAI → Render (backend) + Vercel (frontend)

**Goal**: ship a live demo URL before Alarm 5 (Aug 17, 2026). MVP is verified
deploy-ready; with `GEMINI_API_KEY` set, `/generate` returns real LLM output
(Gemini 2.5 Flash, FREE tier: 10 RPM / 250 RPD).

## Prerequisites (user, 2 min — the only true blocker)
1. Get a **Gemini API key** (RECOMMENDED — FREE tier, no credit card needed)
   at https://aistudio.google.com/apikey — **or** an OpenAI key (`gpt-4o-mini`)
   **or** an Anthropic key (`claude-3-5-haiku`).
2. Have a GitHub repo with the `pandas_ai/` folder pushed. (Render/Vercel both
   deploy from a GitHub branch.)

---

## Step 1 — Backend → Render (5 min)

1. New → Web Service → connect your GitHub repo → set **Root Directory** =
   `pandas_ai/backend` (Render reads `render.yaml` from `pandas_ai/`; if it
   doesn't auto-detect, paste the `startCommand` manually).
2. **Environment tab** → add `GEMINI_API_KEY` (recommended — free) **or**
   `OPENAI_API_KEY` **or** `ANTHROPIC_API_KEY`.
3. Set `CORS_ORIGINS` = your future Vercel URL (use `*` first, tighten later).
4. Deploy. Render runs `pip install -r requirements.txt` then
   `uvicorn main:app --host 0.0.0.0 --port $PORT`. Health check hits `/health`.
5. Note the backend URL, e.g. `https://pandasai-backend.onrender.com`.
   Verify: `curl https://pandasai-backend.onrender.com/health` →
   `{"status":"ok","version":"0.1.0"}`.

> **Stub vs real**: with no key, `/generate` returns a commented template
> (provider: `stub`). With a key, it returns real pandas code. The same deploy
> serves both — no redeploy needed when you add the key, just set the env var
> and Render redeploys automatically.

---

## Step 2 — Frontend → Vercel (3 min)

1. New Project → import the same GitHub repo → **Root Directory** =
   `pandas_ai/frontend`. Vercel auto-detects Vite via `vercel.json`.
2. **Environment Variables** → add
   `VITE_API_BASE` = `https://pandasai-backend.onrender.com` (the Render URL
   from Step 1, **no** trailing slash, **no** `/api` — backend routes are at
   root). This is a **build-time** var (Vite inlines it), so set it before the
   first deploy.
3. Deploy. Vercel runs `npm run build` → serves `dist/`.
4. Note the frontend URL, e.g. `https://pandas-ai.vercel.app`.

---

## Step 3 — Tighten CORS (1 min, after both URLs are known)

Back on Render, set `CORS_ORIGINS` = `https://pandas-ai.vercel.app` (replace
`*`). Redeploy. This prevents other sites from calling your backend directly.

---

## Verify end-to-end

Open the Vercel URL → type "Group sales by month and calculate total revenue"
→ click **Generate code**. You should get a valid pandas code block with
`provider: gemini` and `Free-tier queries remaining today: 4`
(rate limiter allows 5/day/IP).

## Rollback / kill

- Render: Settings → Suspend (free tier, no cost when suspended).
- Vercel: delete the project.
- No data stores → nothing to migrate or lose.

## Why this config

- `requirements.txt` now installs `google-generativeai` + `openai` +
  `anthropic` so the deploy doesn't crash on the first real query (`llm.py`
  imports lazily, but the package must be present at runtime — this was the
  deploy-readiness bug fixed in a prior session).
- `render.yaml` healthCheckPath = `/health` → Render marks the service green
  only when FastAPI is actually responding.
- `vercel.json` rewrites all paths to `/index.html` (SPA fallback) so deep
  links don't 404.
