#!/bin/sh
# Stop hook: run `just check` if the working tree changed since it last passed.
# Exit 2 hands the failure back to Claude, which keeps working until it is green.
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0
input=$(cat)
ok=.claude/.gate-ok
tries=.claude/.gate-tries

if git rev-parse --git-dir >/dev/null 2>&1; then
  state=$({
    git rev-parse HEAD
    git diff --cached
    git diff
    git ls-files --others --exclude-standard -z | xargs -0 cksum
  } 2>/dev/null | cksum)
  if [ "$state" = "$(cat "$ok" 2>/dev/null)" ]; then
    rm -f "$tries"
    exit 0
  fi
fi

if out=$(just check 2>&1); then
  [ -n "$state" ] && echo "$state" >"$ok"
  rm -f "$tries"
  exit 0
fi

# Give up after three consecutive failed attempts in one turn, so an
# unfixable failure (for example a missing tool) cannot loop forever.
case "$input" in
  *'"stop_hook_active":true'* | *'"stop_hook_active": true'*)
    n=$(($(cat "$tries" 2>/dev/null || echo 0) + 1)) ;;
  *) n=1 ;;
esac
echo "$n" >"$tries"
if [ "$n" -gt 3 ]; then
  echo "just check is still failing after 3 fix attempts; stopping." >&2
  exit 1
fi

printf '%s\n' "$out" | tail -n 80 >&2
echo "\`just check\` failed. Fix the cause (do not silence the check), or if it cannot be fixed, say why." >&2
exit 2
