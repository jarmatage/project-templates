---
name: scaffold
description: Scaffold a new project from a copier template - python, python-maturin (Rust extension via PyO3), python-nanobind (C++ extension via scikit-build-core), rust, or cpp (pitchfork layout). Use when the user wants to create, start, bootstrap or scaffold a new project or package in one of these languages.
argument-hint: "[template] [destination]"
---

# Scaffold a project

Arguments: `$ARGUMENTS` (optional: template name, then destination directory).

The copier templates live in this plugin: `${CLAUDE_PLUGIN_ROOT}` (questions in
`copier.yml`, one tree per template under `templates/`).

## 1. Collect answers

Read `${CLAUDE_PLUGIN_ROOT}/copier.yml` for the authoritative question list.
Take what the user already gave (arguments, conversation) and ask only for what
is missing, in one batch. Do not ask about questions whose `when` is false for
the chosen template.

| Answer | Applies to | Default |
| --- | --- | --- |
| `template` | all | ask: `python`, `python-maturin`, `python-nanobind`, `rust`, `cpp` |
| destination | all | `./<project_name>`; must not exist or must be empty |
| `project_name` | all | destination directory name (lowercase, hyphenated) |
| `package_name` | all | `project_name` with `-` replaced by `_` |
| `description` | all | ask |
| `author_name`, `author_email` | all | `git config user.name` / `user.email` |
| `license` | all | `MIT` (or `Apache-2.0`) |
| `python_kind` | `python` | `lib` (or `app`) |
| `python_version` | `python*` | `3.12` |
| `rust_channel` | `rust`, `python-maturin` | the installed stable version from `rustc --version`, else `stable` |
| `cpp_standard` | `cpp`, `python-nanobind` | `23` |

## 2. Generate

Pass every answer with `--data` so copier never prompts:

```sh
uvx copier copy --defaults \
  --data template=<template> --data project_name=<name> ... \
  "${CLAUDE_PLUGIN_ROOT}" <destination>
```

If the user gives a git URL for this template repository, use it instead of
`${CLAUDE_PLUGIN_ROOT}`: only projects generated from a git source can later
pull template changes with `uvx copier update`.

## 3. Prove it works

In the destination:

1. `git init` (skip if it is already inside a repository) and `git add -A`.
2. `just doctor` - report any missing tool to the user with the printed install
   hint. Do not install system tools without asking.
3. `just setup`, `just fmt` (rendered names can change line wrapping), then `just check`. Both must succeed; if `check` fails because
   of the template rather than a missing tool, fix the generated project and
   tell the user what was wrong.

Do not commit unless asked.

## 4. Report

Tell the user where the project is, which tools were missing (if any), the
`just check` result, and that the project ships its own `CLAUDE.md` and
`.claude/settings.json` (hooks, permissions, language-server plugin) which
take effect when Claude Code is started in that directory and the folder is
trusted.
