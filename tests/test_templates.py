"""Generate each template and run the generated project's own gate.

A template is only correct if a fresh project passes `just check`, so that is
what these tests assert. A case is skipped when a tool it needs is not on PATH.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest
from copier import run_copy

ROOT = Path(__file__).parent.parent

UV = ["uv"]
RUST = ["cargo", "cargo-nextest"]
CPP = ["cmake", "ninja", "clang-format", "clang-tidy"]

# name -> (copier answers, tools required on PATH, recipes to run after setup)
CASES: dict[str, tuple[dict[str, str], list[str], list[str]]] = {
    "python-lib": ({"template": "python", "python_kind": "lib"}, UV, ["check", "cov", "docs", "build"]),
    "python-app": ({"template": "python", "python_kind": "app"}, UV, ["check", "cov", "docs", "build"]),
    "python-maturin": ({"template": "python-maturin"}, UV + RUST, ["check", "docs", "build"]),
    "python-nanobind": ({"template": "python-nanobind"}, UV, ["check", "test-san", "cov", "docs", "build"]),
    "rust": ({"template": "rust"}, RUST, ["check", "docs", "build"]),
    "cpp": ({"template": "cpp"}, CPP, ["check", "test-san", "build"]),
    "cpp-20-apache": (
        {"template": "cpp", "cpp_standard": "20", "license": "Apache-2.0"},
        CPP,
        ["check"],
    ),
}


def run(project: Path, *command: str) -> None:
    result = subprocess.run(command, cwd=project, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        output = (result.stdout + result.stderr)[-4000:]
        pytest.fail(f"`{' '.join(command)}` failed in {project}:\n{output}")


@pytest.mark.parametrize("case", CASES)
def test_generated_project_passes_its_gate(case: str, tmp_path: Path) -> None:
    answers, tools, recipes = CASES[case]
    missing = [tool for tool in ["just", "git", *tools] if shutil.which(tool) is None]
    if missing:
        pytest.skip(f"missing tools: {', '.join(missing)}")

    project = tmp_path / "demo-project"
    run_copy(
        str(ROOT),
        project,
        data={"project_name": "demo-project", **answers},
        defaults=True,
        vcs_ref="HEAD",
        quiet=True,
    )

    unrendered = [p for p in project.rglob("*") if "{{" in p.name or p.suffix == ".jinja"]
    assert not unrendered, f"unrendered template files: {unrendered}"
    for expected in ["CLAUDE.md", ".claude/settings.json", ".claude/hooks/gate.sh", "justfile", "LICENSE"]:
        assert (project / expected).is_file(), f"{expected} was not generated"

    run(project, "git", "init", "--quiet")
    run(project, "git", "add", "--all")
    run(project, "just", "setup")
    for recipe in recipes:
        run(project, "just", recipe)
