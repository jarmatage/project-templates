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
a fresh project and runs that project's own gate. `just test-fast` only renders
every template (seconds), for quick feedback while editing. Run `just validate` after
touching `.claude-plugin/` or the skill.

## Gotchas

- Never run a template's recipes inside `templates/`; generate a project first (`just try <template> <dir>`).
- `just test` deletes each generated project once its case passes (build trees
  reach ~1 GB each, and `/tmp` may be RAM-backed); failed ones are kept in
  pytest's temp directory for inspection.
- Each generated project must stay self-contained: its `CLAUDE.md` is short
  (layout, commands, verification, gotchas) and its hooks call `just` recipes.
- Files that are identical across templates (`.claude/hooks/gate.sh`, the
  answers file, `LICENSE.jinja`) are deliberate copies; change all five together.
  `just test-fast` fails when they drift (`COPIES` in the tests).
- Answers land inside quoted strings (TOML, CMake, YAML, docstrings): a new use
  of `description` or an author field needs the quoting its file format wants.
- `{{ args }}` in a justfile is just syntax, so justfiles are not `.jinja`
  files. In `.jinja` files, CMake's `${...}` next to `{{ ... }}` needs care.
- Formatters see rendered names: keep generated code formatted for the default
  answers, and `scaffold` runs `just fmt` for other names.
