# project-templates

A Claude Code plugin whose `scaffold` skill generates projects with copier.

## Layout

- `copier.yml` - the questions; the `template` answer selects `templates/<template>/`
- `templates/<name>/` - five independent project trees; only `*.jinja` files are rendered, everything else is copied verbatim
- `includes/` - license texts, the only content shared between templates
- `skills/scaffold/SKILL.md` - the skill; `.claude-plugin/` - plugin and marketplace manifests
- `tests/test_templates.py` - generates every template and runs its `just check`

## Verification

A template change is done when `just test -k <template>` passes: it generates
a fresh project and runs that project's own gate. Run `just validate` after
touching `.claude-plugin/` or the skill.

## Gotchas

- Never run a template's recipes inside `templates/`; generate a project first (`just try <template> <dir>`).
- `just test` generates projects under `.pytest-tmp/`, not `/tmp`: a full run's
  Rust and C++ build trees are several GB, enough to fill a RAM-backed `/tmp`.
- Each generated project must stay self-contained: its `CLAUDE.md` is short
  (layout, commands, verification, gotchas) and its hooks call `just` recipes.
- Files that are identical across templates (`.claude/hooks/gate.sh`, the
  answers file, `LICENSE.jinja`) are deliberate copies; change all five together.
- `{{ args }}` in a justfile is just syntax, so justfiles are not `.jinja`
  files. In `.jinja` files, CMake's `${...}` next to `{{ ... }}` needs care.
- Formatters see rendered names: keep generated code formatted for the default
  answers, and `scaffold` runs `just fmt` for other names.
