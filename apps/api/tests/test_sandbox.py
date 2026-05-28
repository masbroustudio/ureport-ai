import os
import tempfile

from app.data.sandbox import SandboxExecutor, check_code_safety


def test_check_code_safety_allows_safe_code():
    """Safe code should pass the check."""
    code = "result_table = df.describe()"
    assert check_code_safety(code) is None


def test_check_code_safety_blocks_exec():
    """exec() calls should be blocked."""
    code = "exec('import os')"
    result = check_code_safety(code)
    assert result is not None
    assert "Blocked call: exec" in result


def test_check_code_safety_blocks_eval():
    """eval() calls should be blocked."""
    code = "x = eval('1+1')"
    result = check_code_safety(code)
    assert result is not None
    assert "Blocked call: eval" in result


def test_check_code_safety_blocks_compile():
    """compile() calls should be blocked."""
    code = "c = compile('import os', '<string>', 'exec')"
    result = check_code_safety(code)
    assert result is not None
    assert "Blocked call: compile" in result


def test_check_code_safety_blocks_open():
    """open() calls should be blocked."""
    code = "f = open('/etc/passwd')"
    result = check_code_safety(code)
    assert result is not None
    assert "Blocked call: open" in result


def test_check_code_safety_blocks_getattr():
    """getattr() calls should be blocked."""
    code = "getattr(__builtins__, '__import__')('os')"
    result = check_code_safety(code)
    assert result is not None
    assert "Blocked call: getattr" in result


def test_check_code_safety_blocks_breakpoint():
    """breakpoint() calls should be blocked."""
    code = "breakpoint()"
    result = check_code_safety(code)
    assert result is not None
    assert "Blocked call: breakpoint" in result


def test_check_code_safety_blocks_os_import():
    """Import os should be blocked."""
    code = "import os\nos.system('ls')"
    result = check_code_safety(code)
    assert result is not None
    assert "Blocked import" in result


def test_check_code_safety_blocks_subprocess():
    """Import subprocess should be blocked."""
    code = "import subprocess"
    result = check_code_safety(code)
    assert result is not None
    assert "Blocked import" in result


def test_check_code_safety_blocks_from_import():
    """from os import path should be blocked."""
    code = "from os import path"
    result = check_code_safety(code)
    assert result is not None
    assert "Blocked import" in result


def test_check_code_safety_blocks_dunder_import():
    """__import__('os') should be blocked."""
    code = "__import__('os')"
    result = check_code_safety(code)
    assert result is not None
    assert "Blocked" in result


def test_safe_code_execution():
    """Test executing safe pandas code."""
    csv_content = "name,age\nAlice,30\nBob,25\nCharlie,35\n"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(csv_content)
        tmp_path = f.name

    try:
        executor = SandboxExecutor(timeout=30)
        code = "result_table = df[df['age'] > 28]"
        result = executor.execute(code, tmp_path, "text/csv")

        assert result.error is None
        assert result.table_data is not None
        assert len(result.table_data) == 2  # Alice(30) and Charlie(35)
    finally:
        os.unlink(tmp_path)


def test_blocked_import_rejected():
    """Code with blocked imports should fail safety check."""
    csv_content = "x,y\n1,2\n"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(csv_content)
        tmp_path = f.name

    try:
        executor = SandboxExecutor(timeout=30)
        code = "import os\nos.listdir('/')"
        result = executor.execute(code, tmp_path, "text/csv")

        assert result.error is not None
        assert "Blocked import" in result.error
    finally:
        os.unlink(tmp_path)


def test_timeout_handling():
    """Long-running code should timeout."""
    csv_content = "x\n1\n"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(csv_content)
        tmp_path = f.name

    try:
        executor = SandboxExecutor(timeout=2)
        code = "import time\ntime.sleep(10)"
        result = executor.execute(code, tmp_path, "text/csv")

        assert result.error is not None
        assert "timed out" in result.error
    finally:
        os.unlink(tmp_path)
