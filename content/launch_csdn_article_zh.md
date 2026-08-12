# 用AI自动生成pandas代码：自然语言转Python数据分析师

> CSDN launch article — paste-ready markdown (Chinese)
> Target audience: 中文Python开发者、数据分析师
> 预期流量: 200-500阅读（CSDN已有237阅读的pandas相关文章基础）

---

## 前言

如果你每天都在用pandas做数据分析，你大概也经历过这样的场景：明明知道自己想做什么操作，却记不清具体的API语法，于是在文档里翻来翻去。

- "是`.agg()`传字典还是传列表？"
- "滚动平均是`.rolling()`然后`.mean()`吗？窗口参数叫什么？"
- "seaborn画相关系数热力图的一行代码是什么来着？"

每次查文档2-5分钟，一天查30次就是一个小时——不是花在分析上，是花在记语法上。

## 我做了什么

一个工具：用英语描述你想对数据做什么操作，它返回语法验证过的、可以直接复制粘贴的pandas代码。

**输入示例：**
```
Group sales by month, calculate total revenue and average order size
```

**生成输出：**
```python
df['month'] = df['date'].dt.to_period('M')
result = df.groupby('month').agg(
    total_revenue=('revenue', 'sum'),
    avg_order_size=('order_size', 'mean')
).reset_index()
```

注意它自动处理了datetime转换——这种细节第一次写很容易漏，然后debug 10分钟。

## 工作原理

三个组件，没有黑魔法：

### 1. Few-shot示例（22个精选模式）
系统提示词包含22个示例，覆盖开发者真正常用的模式：groupby+agg、merge/join、datetime处理、字符串操作、缺失值处理、pivot、可视化、分箱、过滤、链式调用。这不是通用的LLM包装——是专门针对pandas优化的。

### 2. Schema感知
上传CSV或描述你的列，生成器就知道`df['date']`是datetime类型，`df['user_id']`是字符串。不再有"假设列X存在"的占位符问题。

### 3. AST语法验证
返回代码前，用`ast.parse()`检查语法错误。如果模型幻觉出一个不存在的方法，验证器会标记出来。你永远不会拿到有语法错误的代码——同时还会扫描危险操作（`eval`、`exec`、`subprocess`、`os.remove`）。

## 更多示例

**滚动平均：**
```
Calculate the 7-day rolling average of the close price column
```
```python
df['rolling_avg'] = df['close'].rolling(window=7).mean()
```

**合并+冲突处理：**
```
Merge orders and customers on customer_id, keep only matching rows
```
```python
merged = pd.merge(orders, customers, on='customer_id', how='inner')
```

**分位数分箱：**
```
Create quartile bins for income and label them Q1 through Q4
```
```python
df['income_quartile'] = pd.qcut(df['income'], q=4, labels=['Q1', 'Q2', 'Q3', 'Q4'])
```

**相关系数热力图：**
```
Create a heatmap of the correlation matrix with annotations
```
```python
import seaborn as sns
sns.heatmap(df.corr(numeric_only=True), annot=True, cmap='coolwarm')
```

## 它不是什么

诚实地说明边界：

- **它不是黑盒分析师。** 它生成代码，你需要阅读和验证。`df.groupby('date')['revenue'].sum()`不管是否回答了你的问题都能运行。
- **它不了解你的数据。** 它不知道"revenue"列的单位是分还是元，也不知道null代表"不适用"还是"零"。领域知识仍然是人的。
- **它不处理复杂的多步管道（目前）。** 2-3步的组合效果不错。10步的探索性分析还是你的工作。

诚实的价值主张：它节省了20-30%花在语法查询上的时间，让你把时间花在真正重要的70-80%上——理解你的数据和解读结果。

## 技术栈

- **后端**：Python FastAPI，可插拔的LLM provider（OpenAI / Anthropic / Ollama / stub）
- **前端**：React + Vite，语法高亮，自然主题UI
- **验证**：`ast.parse()` + 危险操作扫描
- **限流**：免费层每IP每天5次查询

## 试试看

免费层每天5次查询，不需要注册：

→ **[PandasAI — 在这里试试](https://473185670.github.io/pandas-ai/)**

用英语输入一个数据操作，拿到验证过的pandas代码。如果你发现有处理得好（或不好）的模式，欢迎评论告诉我。

---

*我最关心的边界情况：它能处理你真实世界的混乱数据任务，还是只能处理干净的示例？用你今天正在做的事情试试，然后告诉我结果。*
