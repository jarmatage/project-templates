#!/bin/sh
# PreToolUse hook (Edit|Write): generated files are changed through their tool,
# never by hand. Exit 2 blocks the edit and shows the reason to Claude.
file=$(grep -o '"file_path" *: *"[^"]*"' | head -n 1 | sed 's/.*: *"\(.*\)"/\1/')
case "$file" in
  */Cargo.lock)
    echo "Cargo.lock is generated. Change Cargo.toml (or use \`cargo add\` / \`cargo update\`)." >&2
    exit 2 ;;
  */.copier-answers.yml)
    echo ".copier-answers.yml is managed by copier. Use \`uvx copier update\`." >&2
    exit 2 ;;
esac
