import pandas as pd


def auto_profile(file_path: str, mime: str) -> dict:
    """Profile a data file and return summary statistics."""
    if mime in ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "application/vnd.ms-excel"):
        df = pd.read_excel(file_path)
    else:
        df = pd.read_csv(file_path)

    columns_info = []
    for col in df.columns:
        col_data = df[col]
        n_total = len(col_data)
        n_missing = int(col_data.isna().sum())
        missing_pct = round(n_missing / n_total * 100, 2) if n_total > 0 else 0.0
        n_unique = int(col_data.nunique())
        sample_values = col_data.dropna().head(5).tolist()

        col_info: dict = {
            "name": str(col),
            "dtype": str(col_data.dtype),
            "missing_pct": missing_pct,
            "n_unique": n_unique,
            "sample_values": sample_values,
        }

        if pd.api.types.is_numeric_dtype(col_data):
            col_info["stats"] = {
                "min": float(col_data.min()) if not col_data.isna().all() else None,
                "max": float(col_data.max()) if not col_data.isna().all() else None,
                "mean": float(col_data.mean()) if not col_data.isna().all() else None,
                "std": float(col_data.std()) if not col_data.isna().all() else None,
            }
        else:
            value_counts = col_data.value_counts().head(5)
            col_info["stats"] = {
                "top_values": [
                    (str(val), int(count))
                    for val, count in value_counts.items()
                ]
            }

        columns_info.append(col_info)

    head_preview = df.head(20).to_dict(orient="records")
    # Convert any non-serializable types in preview
    for row in head_preview:
        for key, val in row.items():
            if pd.isna(val):
                row[key] = None

    memory_mb = round(df.memory_usage(deep=True).sum() / (1024 * 1024), 3)

    return {
        "n_rows": len(df),
        "n_cols": len(df.columns),
        "columns": columns_info,
        "head_preview": head_preview,
        "memory_mb": memory_mb,
    }
