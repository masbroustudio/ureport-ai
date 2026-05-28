import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.sandbox import ExecutionResult, SandboxExecutor
from app.model.file import File
from app.service.files import get_full_path
from app.settings import Settings


async def get_dataframe_profile(file_id: str, db: AsyncSession) -> dict | None:
    """Get stored profile for a file."""
    result = await db.execute(
        select(File).where(File.id == uuid.UUID(file_id))
    )
    file = result.scalar_one_or_none()
    if not file:
        return None
    return file.profile_json


async def run_python_code(
    file_id: str, code: str, db: AsyncSession, settings: Settings
) -> ExecutionResult:
    """Run user code against a file's data."""
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
) -> ExecutionResult:
    """Generate a chart from parameters."""
    lines = []

    if aggregation and y:
        lines.append(f"plot_df = df.groupby('{x}')['{y}'].{aggregation}().reset_index()")
    else:
        lines.append("plot_df = df")

    func_name = f"px.{chart_type}"
    args = [f"plot_df, x='{x}'"]
    if y:
        args.append(f"y='{y}'")
    if color:
        args.append(f"color='{color}'")
    if title:
        args.append(f"title='{title}'")

    lines.append(f"fig = {func_name}({', '.join(args)})")

    code = "\n".join(lines)
    return await run_python_code(file_id, code, db, settings)
