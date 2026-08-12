# I Built a Natural Language → pandas Code Generator (Open Source + Free)

> Dev.to launch article — paste-ready markdown with frontmatter
> Target audience: Python developers, data scientists
> Tags: python, pandas, ai, datascience, productivity

---
title: "I Built a Natural Language → pandas Code Generator (Open Source + Free)"
published: true
description: "Describe your data task in English → get syntax-validated pandas code. 22 curated few-shot examples, AST validation, no black-box."
tags: python, pandas, ai, datascience
canonical_url: https://473185670.github.io/pandas-ai/blog/generate-pandas-code-from-natural-language
---

If you've spent more time in pandas documentation than in your actual data, this is for you.

## The Problem

I analyze data with pandas every day. And every day, I spend a non-trivial chunk of time looking up syntax I've used a hundred times but can't remember exactly:

- "Was it `.agg()` with a dict or a list of tuples?"
- "How do I do a rolling average with a min period?"
- "What's the seaborn one-liner for a correlation heatmap?"

Each lookup is 2-5 minutes of context-switching. Multiply by 30 lookups/day and that's an hour gone — not on analysis, just on syntax.

## What I Built

A tool where you describe what you want in English, and it returns syntax-validated, copy-paste-ready pandas code.

**Example input:**
```
Group sales by month, calculate total revenue and average order size
```

**Generated output:**
```python
df['month'] = df['date'].dt.to_period('M')
result = df.groupby('month').agg(
    total_revenue=('revenue', 'sum'),
    avg_order_size=('order_size', 'mean')
).reset_index()
```

Note the datetime handling — the kind of thing you'd forget on the first pass and debug for 10 minutes.

## How It Works

Three components, no magic:

### 1. Few-Shot Examples (22 curated patterns)
The system prompt includes 22 examples covering the patterns developers actually use: groupby+agg, merge/join, datetime, string ops, missing data, pivots, visualization, binning, filtering, chaining. This isn't a generic LLM wrapper — it's specialized for pandas.

### 2. Schema Awareness
Upload a CSV or describe your columns, and the generator knows `df['date']` is datetime and `df['user_id']` is a string. No more "assume column X exists" placeholders.

### 3. AST Validation
Before returning code, it runs `ast.parse()` to catch syntax errors. If the model hallucinates a method, the validator flags it. You never get broken code — and it also scans for dangerous operations (`eval`, `exec`, `subprocess`, `os.remove`).

## More Examples

**Rolling average:**
```
Calculate the 7-day rolling average of the close price column
```
```python
df['rolling_avg'] = df['close'].rolling(window=7).mean()
```

**Merge with conflict handling:**
```
Merge orders and customers on customer_id, keep only matching rows
```
```python
merged = pd.merge(orders, customers, on='customer_id', how='inner')
```

**Quantile binning:**
```
Create quartile bins for income and label them Q1 through Q4
```
```python
df['income_quartile'] = pd.qcut(df['income'], q=4, labels=['Q1', 'Q2', 'Q3', 'Q4'])
```

**Correlation heatmap:**
```
Create a heatmap of the correlation matrix with annotations
```
```python
import seaborn as sns
sns.heatmap(df.corr(numeric_only=True), annot=True, cmap='coolwarm')
```

## What It's Not

Let me be honest about the boundaries:

- **It's not a black-box analyst.** It generates code you should read and verify. `df.groupby('date')['revenue'].sum()` runs whether or not it answers your question.
- **It doesn't know your data.** It doesn't know "revenue" is in cents, or that null means "not applicable." Domain knowledge stays human.
- **It's not for complex multi-step pipelines (yet).** 2-3 step compositions work well. 10-step exploratory analysis is still your job.

The honest value prop: it saves the 20-30% of time spent on syntax lookup, so you can spend it on the 70-80% that matters — understanding your data and interpreting results.

## Tech Stack

- **Backend**: Python FastAPI, pluggable LLM providers (OpenAI / Anthropic / Ollama / stub)
- **Frontend**: React + Vite, syntax highlighting, nature-themed UI
- **Validation**: `ast.parse()` + dangerous-op scanner
- **Rate limiting**: 5 free queries/day per IP

## Try It

The free tier gives you 5 queries/day, no signup required:

→ **[PandasAI — try it here](https://473185670.github.io/pandas-ai/)**

Type a data operation in English, get validated pandas code. If you find a pattern it handles well (or badly), I'd love to hear about it.

---

*The edge case I care about most: does it handle your real-world messy data tasks, or just the clean examples? Try it on something you're working on today and let me know.*
