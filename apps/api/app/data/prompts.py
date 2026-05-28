import re


def build_data_analysis_system_prompt(profile: dict) -> str:
    """Build a system prompt for data analysis given a file profile."""
    columns_desc = []
    for col in profile.get("columns", []):
        desc = f"  - {col['name']} ({col['dtype']}): {col['n_unique']} unique values, {col['missing_pct']}% missing"
        if "stats" in col:
            stats = col["stats"]
            if "mean" in stats:
                desc += f", range [{stats.get('min')}, {stats.get('max')}], mean={stats.get('mean'):.2f}"
            elif "top_values" in stats:
                top = stats["top_values"][:3]
                top_str = ", ".join(f"'{v}' ({c})" for v, c in top)
                desc += f", top: {top_str}"
        columns_desc.append(desc)

    columns_text = "\n".join(columns_desc)

    return f"""You are a data analysis assistant. The user has uploaded a dataset with the following profile:

- Rows: {profile.get('n_rows', 0)}
- Columns: {profile.get('n_cols', 0)}
- Memory: {profile.get('memory_mb', 0)} MB

Column details:
{columns_text}

When the user asks for analysis, generate Python code using pandas and plotly.
The DataFrame is pre-loaded as `df`. Available libraries: pandas (as pd), plotly.express (as px), plotly.graph_objects (as go).

To return a table, assign a DataFrame to `result_table`.
To return a chart, assign a plotly figure to `fig`.

Always wrap your code in a ```python code block.
Keep code concise and focused on the user's request."""


def extract_code_from_response(llm_response: str) -> str | None:
    """Extract Python code from markdown code blocks in LLM response."""
    pattern = r"```python\s*\n(.*?)```"
    matches = re.findall(pattern, llm_response, re.DOTALL)
    if matches:
        return matches[0].strip()
    return None
