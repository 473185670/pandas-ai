# How to Generate pandas Code from Natural Language

> SEO blog post 1 of 3 — target keyword: "generate pandas code", "pandas natural language"
> Estimated organic traffic: 200-500 visits/mo (low-competition long-tail)

If you've ever stared at a pandas documentation page trying to remember the exact syntax for a multi-index groupby with a custom aggregation function, you know the friction. You know *what* you want to do — you just need the code. This post shows how natural language to pandas code generation works, why it's faster than searching docs, and how you can use it today.

## The Problem: Doc-Surfing Tax

Data scientists spend an estimated 20-30% of their time looking up syntax. Not designing analyses — just translating intent into API calls. The pandas API is powerful but vast: over 200 methods on a DataFrame alone. Common pain points:

- "Was it `.agg()` or `.aggregate()`? Do I pass a dict or a list?"
- "How do I reshape this wide format to long? `.melt()` or `.pivot()`?"
- "What's the seaborn one-liner for a correlation heatmap with annotations?"

Each lookup is 2-5 minutes of context switching. Multiply by 50 lookups/day and you've lost an afternoon.

## The Solution: Describe It, Get Code

Instead of searching, you describe the operation in plain English:

```
Input: "Group sales by month, calculate total revenue and average order size"
```

```python
# Generated output:
df['month'] = df['date'].dt.to_period('M')
result = df.groupby('month').agg(
    total_revenue=('revenue', 'sum'),
    avg_order_size=('order_size', 'mean')
).reset_index()
```

The code is syntax-validated, copy-paste ready, and includes the datetime handling you'd probably forget on the first try.

## How It Works Under the Hood

A good natural-language-to-code generator does three things:

### 1. Few-Shot Context
The model is primed with 20+ curated examples covering the patterns developers actually use: groupby+agg, merge/join, datetime handling, string operations, missing data, pivots, visualization. This isn't a generic LLM wrapper — it's specialized for the pandas domain.

### 2. Schema Awareness
If you upload a CSV or describe your columns, the generator knows that `df['date']` is a datetime column and `df['user_id']` is a string. This eliminates the "assume column X exists" placeholder problem.

### 3. Syntax Validation
Before returning code, it runs `ast.parse()` to catch syntax errors. If the model hallucinates a method that doesn't exist, the validator flags it. You never get broken code.

## 5 Practical Examples

**Example 1 — Aggregation:**
> "Calculate the 7-day rolling average of the close price column"

```python
df['rolling_avg'] = df['close'].rolling(window=7).mean()
```

**Example 2 — Merge:**
> "Merge orders and customers on customer_id, keep only matching rows"

```python
merged = pd.merge(orders, customers, on='customer_id', how='inner')
```

**Example 3 — Filtering:**
> "Filter rows where revenue is above the 90th percentile"

```python
threshold = df['revenue'].quantile(0.90)
filtered = df[df['revenue'] > threshold]
```

**Example 4 — Visualization:**
> "Create a bar chart of total sales by region, sorted descending"

```python
import matplotlib.pyplot as plt
sales_by_region = df.groupby('region')['sales'].sum().sort_values(ascending=False)
sales_by_region.plot(kind='bar')
plt.ylabel('Total Sales')
plt.title('Sales by Region')
plt.tight_layout()
plt.show()
```

**Example 5 — Cleaning:**
> "Drop rows where any of these columns are null: email, phone, address"

```python
cleaned = df.dropna(subset=['email', 'phone', 'address'])
```

## When to Use This (and When Not To)

**Use it when:**
- You know the operation but forget the exact syntax
- You want a starting point to customize (not a black-box result)
- You're prototyping and speed matters more than perfection

**Don't use it when:**
- You need domain-specific business logic the model can't infer
- The operation requires data the model can't see (complex joins on unseen schemas)
- You don't understand pandas well enough to verify the output — always read the generated code

## Try It

The tool is open-source and free to try: describe your data task in English, get validated pandas code in seconds. No signup required for the free tier (5 queries/day).

→ **[Try PandasAI](/)** — paste your request, get code.

---

*This is part 1 of a 3-part series on natural language code generation for data analysis. Next: [10 common pandas patterns every data scientist should know](./blog_02_10_common_pandas_patterns.md).*
