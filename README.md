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

All templates share the same verbs through [just](https://just.systems/):
`setup`, `doctor`, `fmt`, `fmt-check`, `lint`, `test`, `cov`, `docs`, `build`
and `check` (the gate). Lint is strict (warnings are errors); coverage is
reported, not enforced. Git hooks run through [prek](https://prek.j178.dev).

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
just test            # generate every template and run its gate (needs the toolchains)
just test -k rust    # one template
just validate        # check the plugin manifests
```

Layout: `copier.yml` holds the questions and selects `templates/<template>/`;
each template is a complete, independent tree.
