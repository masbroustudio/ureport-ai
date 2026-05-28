import os
import tempfile

from app.data.profiler import auto_profile


def test_auto_profile_csv():
    """Test profiling a CSV file returns correct structure."""
    csv_content = "name,age,city\nAlice,30,NYC\nBob,25,LA\nCharlie,35,NYC\nDiana,28,Chicago\n"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(csv_content)
        tmp_path = f.name

    try:
        result = auto_profile(tmp_path, "text/csv")

        assert result["n_rows"] == 4
        assert result["n_cols"] == 3
        assert len(result["columns"]) == 3
        assert "head_preview" in result
        assert "memory_mb" in result
        assert len(result["head_preview"]) == 4

        # Check column details
        name_col = result["columns"][0]
        assert name_col["name"] == "name"
        assert name_col["n_unique"] == 4
        assert name_col["missing_pct"] == 0.0
        assert "stats" in name_col
        assert "top_values" in name_col["stats"]

        age_col = result["columns"][1]
        assert age_col["name"] == "age"
        assert "stats" in age_col
        assert "min" in age_col["stats"]
        assert "max" in age_col["stats"]
        assert "mean" in age_col["stats"]
        assert age_col["stats"]["min"] == 25.0
        assert age_col["stats"]["max"] == 35.0
    finally:
        os.unlink(tmp_path)


def test_auto_profile_with_missing_values():
    """Test profiling handles missing values correctly."""
    csv_content = "x,y\n1,a\n2,\n3,c\n,d\n"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(csv_content)
        tmp_path = f.name

    try:
        result = auto_profile(tmp_path, "text/csv")

        assert result["n_rows"] == 4

        x_col = result["columns"][0]
        assert x_col["missing_pct"] == 25.0

        y_col = result["columns"][1]
        assert y_col["missing_pct"] == 25.0
    finally:
        os.unlink(tmp_path)
