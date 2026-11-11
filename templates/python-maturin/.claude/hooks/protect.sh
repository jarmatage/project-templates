#!/bin/sh
# PreToolUse hook (Edit|Write): generated files are changed through their tool,
# never by hand. Exit 2 blocks the edit and shows the reason to Claude.
file=$(grep -o '"file_path" *: *"[^"]*"' | head -n 1 | sed 's/.*: *"\(.*\)"/\1/')
case "$file" in
  */uv.lock)
    echo "uv.lock is generated. Change pyproject.toml (or use \`uv add\` / \`uv remove\`) and run \`uv lock\`." >&2
    exit 2 ;;
  */Cargo.lock)
    echo "Cargo.lock is generated. Change a Cargo.toml (or use \`cargo add\` / \`cargo update\`)." >&2
    exit 2 ;;
  */.copier-answers.yml)
    echo ".copier-answers.yml is managed by copier. Use \`uvx copier update\`." >&2
    exit 2 ;;
esac
