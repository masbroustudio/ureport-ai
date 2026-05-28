import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.sandbox import ExecutionResult, SandboxExecutor
from app.model.file import File
from app.service.files import get_full_path
from app.settings import Settings


async def get_dataframe_profile(
    file_id: str, db: AsyncSession, user_id: uuid.UUID | None = None
) -> dict | None:
    """Get stored profile for a file."""
    if user_id:
        result = await db.execute(
            select(File).where(File.id == uuid.UUID(file_id), File.user_id == user_id)
        )
    else:
        result = await db.execute(
            select(File).where(File.id == uuid.UUID(file_id))
        )
    file = result.scalar_one_or_none()
    if not file:
        return None
    return file.profile_json


async def run_python_code(
    file_id: str, code: str, db: AsyncSession, settings: Settings,
    user_id: uuid.UUID | None = None,
) -> ExecutionResult:
    """Run user code against a file's data."""
    if user_id:
        result = await db.execute(
            select(File).where(File.id == uuid.UUID(file_id), File.user_id == user_id)
        )
    else:
        result = await db.execute(
            select(File).where(File.id == uuid.UUID(file_id))
        )
    file = result.scalar_one_or_none()
    if not file:
        return ExecutionResult(error="File not found", code=code)

    full_path = get_full_path(file.storage_path, settings)
    executor = SandboxExecutor(timeout=settings.DATA_SANDBOX_TIMEOUT_SECONDS)
    return executor.execute(code, full_path, file.mime)


async def make_chart(
    file_id: str,
    chart_type: str,
    x: str,
    y: str | None,
    color: str | None,
    aggregation: str | None,
    title: str | None,
    db: AsyncSession,
    settings: Settings,
    user_id: uuid.UUID | None = None,
) -> ExecutionResult:
    """Generate a chart from parameters."""
    # Get the file profile to validate column names
    if user_id:
        result = await db.execute(
            select(File).where(File.id == uuid.UUID(file_id), File.user_id == user_id)
        )
    else:
        result = await db.execute(
            select(File).where(File.id == uuid.UUID(file_id))
        )
    file = result.scalar_one_or_none()
    if not file:
        return ExecutionResult(error="File not found", code="")

    # Validate column names against the profile
    valid_columns: set[str] = set()
    if file.profile_json and "columns" in file.profile_json:
        valid_columns = {col["name"] for col in file.profile_json["columns"]}

    if valid_columns:
        if x not in valid_columns:
            return ExecutionResult(error=f"Column '{x}' not found in file", code="")
        if y and y not in valid_columns:
            return ExecutionResult(error=f"Column '{y}' not found in file", code="")
        if color and color not in valid_columns:
            return ExecutionResult(error=f"Column '{color}' not found in file", code="")

    # Escape single quotes in string values
    safe_x = x.replace("'", "\\'")
    safe_y = y.replace("'", "\\'") if y else None
    safe_color = color.replace("'", "\\'") if color else None
    safe_title = title.replace("'", "\\'") if title else None

    # Validate aggregation against allowed values
    allowed_aggregations = {"sum", "mean", "count", "min", "max", "median", "std"}
    if aggregation and aggregation not in allowed_aggregations:
        return ExecutionResult(error=f"Invalid aggregation: {aggregation}", code="")

    # Validate chart_type against allowed plotly express functions
    allowed_chart_types = {"bar", "line", "scatter", "histogram", "pie", "box", "violin", "area"}
    if chart_type not in allowed_chart_types:
        return ExecutionResult(error=f"Invalid chart type: {chart_type}", code="")

    lines = []

    if aggregation and safe_y:
        lines.append(f"plot_df = df.groupby('{safe_x}')['{safe_y}'].{aggregation}().reset_index()")
    else:
        lines.append("plot_df = df")

    func_name = f"px.{chart_type}"
    args = [f"plot_df, x='{safe_x}'"]
    if safe_y:
        args.append(f"y='{safe_y}'")
    if safe_color:
        args.append(f"color='{safe_color}'")
    if safe_title:
        args.append(f"title='{safe_title}'")

    lines.append(f"fig = {func_name}({', '.join(args)})")

    code = "\n".join(lines)
    return await run_python_code(file_id, code, db, settings, user_id=user_id)
