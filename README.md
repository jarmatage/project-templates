# project-templates

A Claude Code plugin that scaffolds new projects with
[copier](https://copier.readthedocs.io). Every template produces a small
working example package, the full toolchain for its language, and Claude Code
settings that teach Claude how to develop in it.

| Template | What you get |
| --- | --- |
| `python` | uv, ruff, ty, pytest + pytest-cov, MkDocs Material; library or application (as `uv init --lib` / `--package`) |
| `python-maturin` | the Python toolchain plus a Rust extension: maturin, PyO3 (abi3), cargo workspace with a pure-Rust core crate, clippy, rustfmt, nextest, llvm-cov, cargo-deny |
| `python-nanobind` | the Python toolchain plus a C++ extension: scikit-build-core, nanobind, CMake presets, Catch2, clang-format, clang-tidy, sanitizers, gcovr |
| `rust` | cargo, pinned toolchain, rustfmt, clippy (pedantic), nextest, llvm-cov, cargo-deny, rustdoc |
| `cpp` | pitchfork layout, CMake presets + Ninja, CPM.cmake, Catch2 v3, clang-format, clang-tidy, ASan/UBSan, gcovr, ccache, Doxygen |

All templates share a core set of verbs through [just](https://just.systems/),
and add a few where their toolchain needs them. Lint is strict (warnings are
errors); coverage is reported, not enforced. Git hooks run through
[prek](https://prek.j178.dev).

## Verbs

| Verb | `python` | `python-maturin` | `python-nanobind` | `rust` | `cpp` |
| --- | --- | --- | --- | --- | --- |
| `setup` | `uv sync` | `uv sync` (builds the extension) | `uv sync` (builds the extension), `cmake --preset dev` | `cargo fetch` | `cmake --preset dev` (downloads dependencies) |
| `fmt` | ruff safe fixes, `ruff format` | `cargo fmt`, ruff safe fixes, `ruff format` | `clang-format -i`, ruff safe fixes, `ruff format` | `cargo fmt` | `clang-format -i` |
| `fmt-check` | `ruff format --check` | `cargo fmt --check`, `ruff format --check` | `clang-format --dry-run --Werror`, `ruff format --check` | `cargo fmt --check` | `clang-format --dry-run --Werror` |
| `lint` | `ruff check` | `cargo clippy -D warnings`, `ruff check` | `clang-tidy`, `ruff check` | `cargo clippy -D warnings` | `clang-tidy` |
| `typecheck` | `ty check` | `ty check` | stub freshness check (`nanobind.stubgen` + `diff`), `ty check` | - | - |
| `test` | `pytest` | `test-rust`, `test-py` | `test-cpp`, `test-py` | `cargo nextest run`, doctests | `cmake --workflow --preset dev` (build + run Catch2) |
| `test-py` | - | `pytest` | `pytest` | - | - |
| `test-rust` | - | `cargo nextest run`, doctests | - | - | - |
| `test-cpp` | - | - | `cmake --workflow --preset dev` | - | - |
| `test-san` | - | - | `san` preset (ASan + UBSan) | - | `san` preset (ASan + UBSan) |
| `cov` | `pytest --cov` | `cargo llvm-cov nextest`, `pytest --cov` | `coverage` preset + `gcovr`, `pytest --cov` | `cargo llvm-cov nextest` | `coverage` preset + `gcovr` |
| `deny` | - | `cargo deny check` | - | `cargo deny check` | - |
| `docs` | `mkdocs build --strict` | `cargo doc` (`-D warnings`), `mkdocs build --strict` | `mkdocs build --strict` | `cargo doc` (`-D warnings`) | `doxygen` |
| `build` | `uv build` (sdist + wheel) | `uv build` (sdist + wheel) | `uv build` (sdist + wheel) | `cargo build --release` | `release` preset |
| `stubs` | - | - | regenerate `_core.pyi` with `nanobind.stubgen` | - | - |
| **`check`** | `fmt-check lint typecheck test` | `fmt-check lint typecheck test` | `fmt-check lint typecheck test` | `fmt-check lint test` | `fmt-check lint test` |

Every template also has `doctor`, which reports missing tools and setup steps,
and `default`, which lists the recipes. `setup` also installs the git hooks.
`check` is the gate: work is done when it passes. Rust and C++ have no
`typecheck` because the compiler does it during `lint` and `test`.

## Use

Install the plugin, then ask Claude to scaffold a project:

```
/plugin marketplace add <path-or-git-url-of-this-repository>
/plugin install project-templates@project-templates
/project-templates:scaffold rust ~/code/my-crate
```

The skill collects the answers, runs copier, then runs the new project's
`just setup` and `just check` to prove it works.

Without Claude:

```sh
uvx copier copy <path-or-git-url-of-this-repository> my-project
```

Projects generated from a git URL can pull later template changes with
`uvx copier update`.

## Claude Code settings in generated projects

Kept deliberately small: one `CLAUDE.md` and one `.claude/settings.json` with
two short hook scripts.

- **Verification** - `CLAUDE.md` names `just check` as the definition of done
  and says what kind of test each change needs.
- **Hooks**
  - `SessionStart` runs `just doctor`, so Claude knows about missing tools up front.
  - `PreToolUse` blocks hand-edits of generated files (lockfiles, copier
    answers, generated stubs, vendored CPM.cmake) and says what to do instead.
  - `PostToolUse` runs `just fmt` after every edit.
  - `Stop` runs `just check` when the tree changed since it last passed and
    hands failures back to Claude, giving up after three failed fix attempts.
- **Language servers** - the settings enable the matching plugin:
  `astral@astral-sh` (ty), `rust-analyzer-lsp` and `clangd-lsp` from the
  official marketplace.
- **Permissions** - `just` and the template's own toolchain commands are
  pre-allowed; build output directories are excluded from reads.

## Develop

```sh
just test-fast       # only render every template (seconds)
just test            # generate every template and run its gate (needs the toolchains)
just test -k rust    # one template
just validate        # check the plugin manifests
```

Layout: `copier.yml` holds the questions and selects `templates/<template>/`;
each template is a complete, independent tree.
