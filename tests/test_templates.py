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
RUST = ["cargo", "cargo-nextest", "cargo-llvm-cov", "cargo-deny"]
CPP = ["cmake", "ninja", "clang-format", "clang-tidy", "gcovr", "doxygen"]

# name -> (copier answers, tools required on PATH, recipes to run after setup)
# Defaults run every recipe; variants run the gate for answers that change
# rendered code: a custom package_name, the oldest and newest Python, Apache-2.0.
CASES: dict[str, tuple[dict[str, str], list[str], list[str]]] = {
    "python-lib": ({"template": "python", "python_kind": "lib"}, UV, ["check", "cov", "docs", "build"]),
    "python-app": ({"template": "python", "python_kind": "app"}, UV, ["check", "cov", "docs", "build"]),
    "python-maturin": ({"template": "python-maturin"}, UV + RUST, ["check", "cov", "deny", "docs", "build"]),
    "python-nanobind": ({"template": "python-nanobind"}, UV, ["check", "test-san", "cov", "docs", "build"]),
    "rust": ({"template": "rust"}, RUST, ["check", "cov", "deny", "docs", "build"]),
    "cpp": ({"template": "cpp"}, CPP, ["check", "test-san", "cov", "docs", "build"]),
    "python-lib-variant": (
        {"template": "python", "package_name": "demo_pkg", "python_version": "3.14", "license": "Apache-2.0"},
        UV,
        ["check", "docs"],
    ),
    "python-maturin-variant": (
        {"template": "python-maturin", "package_name": "demo_pkg", "python_version": "3.11", "license": "Apache-2.0"},
        UV + RUST,
        ["check", "docs", "build"],
    ),
    "python-maturin-py314": ({"template": "python-maturin", "python_version": "3.14"}, UV + RUST, ["check"]),
    "python-nanobind-variant": (
        {"template": "python-nanobind", "package_name": "demo_pkg", "python_version": "3.11", "license": "Apache-2.0"},
        UV,
        ["check", "docs"],
    ),
    "python-nanobind-py314": ({"template": "python-nanobind", "python_version": "3.14"}, UV, ["check"]),
    "rust-variant": ({"template": "rust", "package_name": "demo_crate", "license": "Apache-2.0"}, RUST, ["check", "docs"]),
    "cpp-variant": (
        {"template": "cpp", "package_name": "demo_ns", "cpp_standard": "20", "license": "Apache-2.0"},
        CPP,
        ["check", "docs"],
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

    # Build trees reach ~1 GB per project; keep only failed ones for inspection.
    shutil.rmtree(project)
