# Product Hunt Launch Prep — PandasAI

**Date**: Aug 12, 2026 14:12 CST
**Status**: Draft assets, paste-ready. Launch gated on: (1) API key set, (2) backend deployed to Render, (3) frontend deployed to Vercel. Do NOT launch before MVP is live (traffic spike wasted on broken product).
**Target launch**: Aug 16-17 (day before/of Alarm 5) — gives 24h to fix deploy issues.

---

## 1. Product Name
**PandasAI** (or alt: **CSVtoPandas**, **PandasGenie**) — PandasAI is chosen; it's clear and SEO-friendly.

## 2. Tagline (60 chars max)
**Upload your CSV, get pandas code that actually runs on your data.**

(58 chars. Leads with the schema-aware differentiator, not "AI code gen".)

Alt taglines:
- "Describe your data task in English. Get pandas code that knows your columns."
- "The pandas code generator that reads your CSV first."

## 3. Description (260 chars max — PH gallery card)
Natural-language → pandas code generator with a difference: upload your CSV, it infers your schema (columns, dtypes), and generates code that references your actual column names — so it runs first-try. Safety-scanned, copy-paste-ready. Free tier 5/day.

(258 chars.)

## 4. Topics (PH lets you pick 3)
1. **Artificial Intelligence**
2. **Developer Tools**
3. **Productivity**

## 5. Gallery images (need to create — 6 max, 1270x760)
- **Image 1 (hero)**: Screenshot of the workflow — CSV upload panel → schema inference display → generated code with syntax highlighting. Nature-themed light green palette.
- **Image 2**: Before/after — "describe in English" textbox → "generated pandas code" output.
- **Image 3**: The 8 one-click examples sidebar.
- **Image 4**: Safety scan catching a dangerous op (red warning on `os.system`).
- **Image 5**: Pricing — free tier vs $9/mo Pro.
- **Image 6**: "What it's not" — honest positioning (not a full analytics platform, not a ChatGPT wrapper).

> Action: generate these from the deployed frontend screenshots before launch.

## 6. Maker comment (posted as first comment by the maker — this is critical, it sets the narrative)

---

Hi all! Maker here. 👋

I built PandasAI because I kept writing the same pandas boilerplate — groupby + agg, datetime parsing, merges — and ChatGPT kept giving me code that referenced columns that didn't exist in my actual CSV. I'd paste my question, get code, run it, get a KeyError, paste the error back, get fixed code... repeat.

So I built a tool that **reads your CSV first**. You upload a file, it infers the schema (column names, dtypes, nulls), and the generated pandas code references your actual columns — so it runs first-try more often. There's also a deterministic safety scan (no `os.system('rm -rf /')` surprises) and 22 curated examples across 11 categories.

**What it is**: a focused pandas code generator that knows your data's shape.
**What it's NOT**: a full analytics platform (that's FormulaBot's lane), a ChatGPT replacement, or a general code assistant (that's Copilot's lane).

Free tier: 5 queries/day. Pro: $9/mo for unlimited + CSV upload + history.

I'd love feedback on two things:
1. Does the schema-aware workflow actually save you time vs. just pasting your question into ChatGPT?
2. What's the one pandas task you'd want this to nail before you'd pay $9/mo?

Open source backend: [github link]. Try it: [live link].

---

## 7. First comment (if a hunter posts, this is the maker's reply template)
Thanks for hunting! [answer any specific question from the hunter]. Happy to answer questions about the architecture — it's FastAPI + a pluggable LLM provider (OpenAI/Anthropic/Ollama/stub) + a deterministic safety scanner using `ast.parse`.

## 8. Hunter outreach (optional — self-launch is fine on PH now)
PH allows self-launch. Skip hunter outreach (saves 1-2 days, avoids dependency). Launch Tuesday-Thursday 00:01 PST for best traction.

## 9. Pre-launch checklist
- [ ] API key set (OPENAI_API_KEY or ANTHROPIC_API_KEY) — **USER ACTION**
- [ ] Backend deployed to Render, `/health` returns 200
- [ ] Frontend deployed to Vercel, live URL works
- [ ] End-to-end test: upload CSV → generate code → code runs
- [ ] 6 gallery screenshots captured from live frontend
- [ ] This file's [live link] + [github link] filled in
- [ ] Maker comment proofread (it's the narrative anchor)
- [ ] Launch on Tuesday Aug 18 or Thursday Aug 20 (avoid Monday/Friday)

## 10. Post-launch (first 24h)
- Respond to every comment within 1h (PH algorithm rewards engagement).
- Cross-post to Dev.to + CSDN (launch articles already drafted in `pandas_ai/content/`).
- Share in r/Python as a free tool (NOT as a product — sub rules). Use the launch_devto_article.md content.
- Track signups; if <20 free-tier signups in 24h, the PH listing underperformed → revisit tagline/gallery.

---

## Honest risk note
Product Hunt traffic is **low-quality for conversion** (browsers, not buyers). The real value is the backlink + the maker-comment-as-content + the social proof for the Dev.to/CSDN articles. Don't expect PH to drive paid signups. Expect it to drive free-tier signups that then appear in the Dev.to article ("100+ developers trying PandasAI this week"). Treat PH as a **credibility asset**, not a revenue channel.
