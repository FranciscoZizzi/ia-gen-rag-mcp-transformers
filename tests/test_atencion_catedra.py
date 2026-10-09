"""Part 4: the graders' atencion/test_atencion.py, unmodified, run against atencion.py.

That file rewrites sys.argv at import time, so pytest never collects it (see pyproject.toml); it runs here
as a subprocess, exactly as the graders run it.
"""
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_the_graders_attention_tests_pass_against_atencion_py():
    result = subprocess.run([sys.executable, "atencion/test_atencion.py", "atencion.py"], cwd=REPO_ROOT,
                            capture_output=True, text=True, timeout=120)

    assert result.returncode == 0, result.stderr
    assert "Ran 14 tests" in result.stderr and result.stderr.rstrip().endswith("OK")
