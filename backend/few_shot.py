"""
Few-shot examples library for pandas code generation.

This is the core differentiator: high-quality, domain-specific examples
that guide the LLM to produce correct, idiomatic pandas code.
Each example covers a common real-world data analysis pattern.
"""

from dataclasses import dataclass


@dataclass
class FewShotExample:
    description: str
    code: str
    category: str
    # Optional data schema hint (column names + dtypes) that makes the example concrete
    schema_hint: str = ""


# 22 examples covering the patterns from the build plan + extras
EXAMPLES: list[FewShotExample] = [
    # --- groupby + aggregation ---
    FewShotExample(
        description="Group sales by month and calculate total revenue",
        code=(
            "df['date'] = pd.to_datetime(df['date'])\n"
            "monthly = df.groupby(df['date'].dt.to_period('M'))['revenue'].sum()\n"
            "print(monthly)"
        ),
        category="groupby",
        schema_hint="date(str), revenue(float)",
    ),
    FewShotExample(
        description="Group by region and show average order value plus order count",
        code=(
            "summary = df.groupby('region').agg(\n"
            "    avg_order_value=('amount', 'mean'),\n"
            "    order_count=('amount', 'size'),\n"
            ")\n"
            "print(summary)"
        ),
        category="groupby",
        schema_hint="region(str), amount(float)",
    ),
    FewShotExample(
        description="Pivot table: rows=product, columns=quarter, values=total sales",
        code=(
            "df['date'] = pd.to_datetime(df['date'])\n"
            "df['quarter'] = df['date'].dt.to_period('Q').astype(str)\n"
            "pivot = df.pivot_table(index='product', columns='quarter',\n"
            "                       values='sales', aggfunc='sum', fill_value=0)\n"
            "print(pivot)"
        ),
        category="groupby",
        schema_hint="product(str), date(str), sales(float)",
    ),

    # --- merge / join ---
    FewShotExample(
        description="Merge two CSVs on user_id and drop duplicates",
        code=(
            "df1 = pd.read_csv('users.csv')\n"
            "df2 = pd.read_csv('events.csv')\n"
            "merged = pd.merge(df1, df2, on='user_id').drop_duplicates()\n"
            "print(merged.shape)"
        ),
        category="merge",
    ),
    FewShotExample(
        description="Left join orders onto customers, keeping all customers even with no orders",
        code=(
            "result = pd.merge(customers, orders, on='customer_id',\n"
            "                  how='left', indicator=True)\n"
            "print(result.head())"
        ),
        category="merge",
        schema_hint="customers: customer_id(int), name(str); orders: customer_id(int), total(float)",
    ),

    # --- filtering ---
    FewShotExample(
        description="Filter rows where revenue is above 1000 and region is not null",
        code=(
            "filtered = df[(df['revenue'] > 1000) & df['region'].notna()]\n"
            "print(filtered)"
        ),
        category="filter",
        schema_hint="revenue(float), region(str)",
    ),
    FewShotExample(
        description="Keep only the top 10 customers by total spend",
        code=(
            "top10 = (\n"
            "    df.groupby('customer_id')['spend'].sum()\n"
            "      .nlargest(10)\n"
            "      .reset_index()\n"
            ")\n"
            "print(top10)"
        ),
        category="filter",
        schema_hint="customer_id(int), spend(float)",
    ),

    # --- datetime handling ---
    FewShotExample(
        description="Add a column for day of week and flag weekend rows",
        code=(
            "df['date'] = pd.to_datetime(df['date'])\n"
            "df['day_of_week'] = df['date'].dt.day_name()\n"
            "df['is_weekend'] = df['date'].dt.dayofweek >= 5\n"
            "print(df.head())"
        ),
        category="datetime",
        schema_hint="date(str)",
    ),
    FewShotExample(
        description="Calculate days since each user signed up",
        code=(
            "df['signup_date'] = pd.to_datetime(df['signup_date'])\n"
            "df['days_since_signup'] = (pd.Timestamp.today() - df['signup_date']).dt.days\n"
            "print(df[['user_id', 'days_since_signup']].head())"
        ),
        category="datetime",
        schema_hint="user_id(int), signup_date(str)",
    ),

    # --- string operations ---
    FewShotExample(
        description="Extract the domain from email addresses and count occurrences",
        code=(
            "df['domain'] = df['email'].str.extract(r'@([\\w.]+)')\n"
            "counts = df['domain'].value_counts().head(20)\n"
            "print(counts)"
        ),
        category="string",
        schema_hint="email(str)",
    ),
    FewShotExample(
        description="Split full name into first and last name columns",
        code=(
            "df[['first_name', 'last_name']] = df['full_name'].str.split(' ', n=1, expand=True)\n"
            "print(df.head())"
        ),
        category="string",
        schema_hint="full_name(str)",
    ),

    # --- visualization ---
    FewShotExample(
        description="Create a heatmap of the correlation matrix",
        code=(
            "import matplotlib.pyplot as plt\n"
            "import seaborn as sns\n\n"
            "plt.figure(figsize=(10, 8))\n"
            "sns.heatmap(df.corr(numeric_only=True), annot=True, cmap='coolwarm', center=0)\n"
            "plt.title('Correlation Matrix')\n"
            "plt.tight_layout()\n"
            "plt.show()"
        ),
        category="viz",
    ),
    FewShotExample(
        description="Plot monthly revenue as a line chart with markers",
        code=(
            "import matplotlib.pyplot as plt\n\n"
            "df['date'] = pd.to_datetime(df['date'])\n"
            "monthly = df.groupby(df['date'].dt.to_period('M'))['revenue'].sum()\n"
            "monthly.plot(kind='line', marker='o', figsize=(12, 6))\n"
            "plt.title('Monthly Revenue')\n"
            "plt.xlabel('Month')\n"
            "plt.ylabel('Revenue')\n"
            "plt.grid(True, alpha=0.3)\n"
            "plt.show()"
        ),
        category="viz",
        schema_hint="date(str), revenue(float)",
    ),
    FewShotExample(
        description="Make a bar chart of total sales by category, sorted descending",
        code=(
            "import matplotlib.pyplot as plt\n\n"
            "sales = df.groupby('category')['sales'].sum().sort_values(ascending=False)\n"
            "sales.plot(kind='bar', figsize=(10, 6), color='#4CAF50')\n"
            "plt.title('Total Sales by Category')\n"
            "plt.ylabel('Sales')\n"
            "plt.xticks(rotation=45, ha='right')\n"
            "plt.tight_layout()\n"
            "plt.show()"
        ),
        category="viz",
        schema_hint="category(str), sales(float)",
    ),

    # --- missing data ---
    FewShotExample(
        description="Show count and percentage of missing values per column",
        code=(
            "missing = df.isna().sum()\n"
            "pct = (missing / len(df) * 100).round(2)\n"
            "report = pd.DataFrame({'missing': missing, 'percent': pct})\n"
            "print(report[report['missing'] > 0])"
        ),
        category="missing",
    ),
    FewShotExample(
        description="Fill missing numeric columns with the median and categorical with the mode",
        code=(
            "for col in df.select_dtypes(include='number').columns:\n"
            "    df[col] = df[col].fillna(df[col].median())\n"
            "for col in df.select_dtypes(exclude='number').columns:\n"
            "    df[col] = df[col].fillna(df[col].mode().iloc[0])\n"
            "print(df.isna().sum().sum(), 'missing remaining')"
        ),
        category="missing",
    ),

    # --- I/O ---
    FewShotExample(
        description="Read all CSV files in a folder and concatenate into one DataFrame",
        code=(
            "import glob\n\n"
            "files = glob.glob('data/*.csv')\n"
            "df = pd.concat((pd.read_csv(f) for f in files), ignore_index=True)\n"
            "print(f'Loaded {len(files)} files, {len(df)} rows total')"
        ),
        category="io",
    ),
    FewShotExample(
        description="Export a DataFrame to Excel with a formatted header",
        code=(
            "with pd.ExcelWriter('output.xlsx', engine='openpyxl') as writer:\n"
            "    df.to_excel(writer, sheet_name='Data', index=False)\n"
            "    worksheet = writer.sheets['Data']\n"
            "    for cell in worksheet[1]:\n"
            "        cell.font = cell.font.copy(bold=True)\n"
            "print('Saved output.xlsx')"
        ),
        category="io",
    ),

    # --- melt / reshape ---
    FewShotExample(
        description="Melt a wide table (columns Q1..Q4) into long format",
        code=(
            "long = df.melt(id_vars=['product'],\n"
            "               value_vars=['Q1', 'Q2', 'Q3', 'Q4'],\n"
            "               var_name='quarter', value_name='sales')\n"
            "print(long.head())"
        ),
        category="reshape",
        schema_hint="product(str), Q1(float), Q2(float), Q3(float), Q4(float)",
    ),

    # --- scraping ---
    FewShotExample(
        description="Scrape all product names and prices from a URL using BeautifulSoup",
        code=(
            "import requests\n"
            "from bs4 import BeautifulSoup\n\n"
            "resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})\n"
            "soup = BeautifulSoup(resp.text, 'html.parser')\n"
            "products = []\n"
            "for item in soup.select('.product-item'):\n"
            "    name = item.select_one('.name').get_text(strip=True)\n"
            "    price = item.select_one('.price').get_text(strip=True)\n"
            "    products.append({'name': name, 'price': price})\n"
            "df = pd.DataFrame(products)\n"
            "print(df.head())"
        ),
        category="scrape",
    ),

    # --- window functions ---
    FewShotExample(
        description="Calculate 7-day rolling average of daily sales",
        code=(
            "df['date'] = pd.to_datetime(df['date'])\n"
            "df = df.sort_values('date')\n"
            "df['rolling_7d'] = df['sales'].rolling(window=7, min_periods=1).mean()\n"
            "print(df.tail())"
        ),
        category="window",
        schema_hint="date(str), sales(float)",
    ),
    FewShotExample(
        description="Add a cumulative sum column and percent of total",
        code=(
            "df['cumulative'] = df['amount'].cumsum()\n"
            "df['pct_of_total'] = (df['amount'] / df['amount'].sum() * 100).round(2)\n"
            "print(df.head())"
        ),
        category="window",
        schema_hint="amount(float)",
    ),
]


def suggest_schema(description: str) -> str:
    """Suggest a schema_hint by keyword-matching the request against examples.

    Used to nudge users who skipped schema_hint toward the schema-aware path
    (the product moat). Returns "" if no confident match.
    """
    desc_tokens = {t for t in description.lower().split() if len(t) > 2}
    if not desc_tokens:
        return ""
    best, best_score = "", 0
    for ex in EXAMPLES:
        if not ex.schema_hint:
            continue
        ex_tokens = {t for t in ex.description.lower().split() if len(t) > 2}
        score = len(desc_tokens & ex_tokens)
        # Weighted: overlap fraction of the request tokens
        if score > best_score:
            best_score, best = score, ex.schema_hint
    # Require at least 2 token overlap to avoid noisy suggestions
    return best if best_score >= 2 else ""


def build_prompt(description: str, schema_hint: str = "") -> str:
    """Build the full system + few-shot prompt for the LLM."""
    examples_block = "\n\n".join(
        f"### Example {i + 1} ({ex.category})\n"
        f"Request: {ex.description}\n"
        f"Code:\n```python\n{ex.code}\n```"
        for i, ex in enumerate(EXAMPLES)
    )

    schema_line = f"\nThe user's data has these columns: {schema_hint}" if schema_hint else ""

    return (
        "You are an expert Python data analyst. Generate ready-to-run, idiomatic "
        "pandas code from a natural-language request. Rules:\n"
        "1. Output ONLY a single Python code block (```python ... ```).\n"
        "2. Assume `pd` and a DataFrame `df` are already imported/loaded unless the "
        "request specifies otherwise.\n"
        "3. Prefer vectorized pandas operations over loops.\n"
        "4. Add a print() at the end so the user sees the result.\n"
        "5. Keep it minimal and correct — no explanations outside the code block.\n\n"
        f"{examples_block}\n\n"
        f"### Now generate code for this request:{schema_line}\n"
        f"Request: {description}\n"
        "Code:"
    )


if __name__ == "__main__":
    # Smoke test: print categories and a sample prompt
    cats = {}
    for ex in EXAMPLES:
        cats[ex.category] = cats.get(ex.category, 0) + 1
    print(f"Total examples: {len(EXAMPLES)}")
    print("By category:", cats)
    print("\n--- Sample prompt (first 600 chars) ---")
    print(build_prompt("Group by city and sum population")[:600])
