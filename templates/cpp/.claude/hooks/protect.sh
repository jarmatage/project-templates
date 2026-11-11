#!/bin/sh
# PreToolUse hook (Edit|Write): generated and vendored files are not edited by
# hand. Exit 2 blocks the edit and shows the reason to Claude.
file=$(grep -o '"file_path" *: *"[^"]*"' | head -n 1 | sed 's/.*: *"\(.*\)"/\1/')
root=${CLAUDE_PROJECT_DIR:-$PWD}
case "$file" in
  */cmake/CPM.cmake)
    echo "cmake/CPM.cmake is vendored from upstream. Replace it with a newer release instead of editing it." >&2
    exit 2 ;;
  # Only this project's own trees: a checkout may itself live under a build/ or .cache/ directory.
  "$root"/build/* | "$root"/.cache/* | build/* | .cache/*)
    echo "build/ and .cache/ are generated. Change the sources or CMake files and rebuild." >&2
    exit 2 ;;
  */.copier-answers.yml)
    echo ".copier-answers.yml is managed by copier. Use \`uvx copier update\`." >&2
    exit 2 ;;
esac
