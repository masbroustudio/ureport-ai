import ast
import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass

BLOCKED_MODULES = {
    "os", "subprocess", "sys", "socket", "shutil",
    "importlib", "ctypes", "signal", "multiprocessing", "threading",
}

BLOCKED_CALLS = {
    "exec", "eval", "compile", "getattr", "open", "breakpoint",
}


@dataclass
class ExecutionResult:
    stdout: str = ""
    table_data: list[dict] | None = None
    chart_spec: dict | None = None
    error: str | None = None
    code: str = ""


def check_code_safety(code: str) -> str | None:
    """Returns error message if code is unsafe, None if safe."""
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return f"Syntax error: {e}"

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                module_root = alias.name.split(".")[0]
                if module_root in BLOCKED_MODULES:
                    return f"Blocked import: {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                module_root = node.module.split(".")[0]
                if module_root in BLOCKED_MODULES:
                    return f"Blocked import: {node.module}"
        elif isinstance(node, ast.Call):
            # Block __import__ calls and other dangerous built-in calls
            if isinstance(node.func, ast.Name):
                if node.func.id == "__import__":
                    return "Blocked: __import__ call"
                if node.func.id in BLOCKED_CALLS:
                    return f"Blocked call: {node.func.id}"
            elif isinstance(node.func, ast.Attribute):
                if node.func.attr in BLOCKED_CALLS:
                    return f"Blocked call: {node.func.attr}"

    return None


WRAPPER_TEMPLATE = '''
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load data
file_path = {file_path!r}
mime = {mime!r}

if mime in ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-excel"):
    df = pd.read_excel(file_path)
else:
    df = pd.read_csv(file_path)

# User code execution
result_table = None
fig = None

{code}

# Serialize output
output = {{"stdout": "", "table_data": None, "chart_spec": None}}

if result_table is not None:
    if isinstance(result_table, pd.DataFrame):
        output["table_data"] = result_table.head(100).to_dict(orient="records")
    elif isinstance(result_table, list):
        output["table_data"] = result_table[:100]

if fig is not None:
    output["chart_spec"] = fig.to_dict()

print("__SANDBOX_JSON_START__")
print(json.dumps(output, default=str))
print("__SANDBOX_JSON_END__")
'''


class SandboxExecutor:
    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    def execute(self, code: str, file_path: str, mime: str) -> ExecutionResult:
        """Execute code in a sandboxed subprocess."""
        # 1. Safety check
        safety_error = check_code_safety(code)
        if safety_error:
            return ExecutionResult(error=safety_error, code=code)

        # 2. Build wrapper script
        wrapper = WRAPPER_TEMPLATE.format(
            file_path=file_path,
            mime=mime,
            code=code,
        )

        # 3. Execute in subprocess
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as tmp:
            tmp.write(wrapper)
            tmp_path = tmp.name

        try:
            result = subprocess.run(
                [sys.executable, tmp_path],
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                error=f"Execution timed out after {self.timeout} seconds",
                code=code,
            )
        except Exception as e:
            return ExecutionResult(error=str(e), code=code)
        finally:
            import os
            os.unlink(tmp_path)

        # 4. Parse output
        if result.returncode != 0:
            return ExecutionResult(
                stdout=result.stdout,
                error=result.stderr or f"Process exited with code {result.returncode}",
                code=code,
            )

        # Extract JSON from output
        stdout = result.stdout
        table_data = None
        chart_spec = None

        start_marker = "__SANDBOX_JSON_START__"
        end_marker = "__SANDBOX_JSON_END__"

        if start_marker in stdout and end_marker in stdout:
            json_start = stdout.index(start_marker) + len(start_marker)
            json_end = stdout.index(end_marker)
            json_str = stdout[json_start:json_end].strip()

            try:
                output = json.loads(json_str)
                table_data = output.get("table_data")
                chart_spec = output.get("chart_spec")
                # Remove markers from stdout for display
                stdout = stdout[:stdout.index(start_marker)].strip()
            except json.JSONDecodeError:
                pass

        return ExecutionResult(
            stdout=stdout,
            table_data=table_data,
            chart_spec=chart_spec,
            error=None,
            code=code,
        )
