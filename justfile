# Commands for working on the templates themselves.

default:
    @just --list

# Generate every template and run its own `just check` (slow: builds Rust and C++).
# Extra arguments go to pytest, e.g. `just test -k rust`.
[positional-arguments]
test *args:
    uv run pytest "$@"

# Validate the plugin and marketplace manifests
validate:
    claude plugin validate .

# Generate one template into a directory for manual inspection: just try rust /tmp/demo
try template dest:
    uv run copier copy --defaults --vcs-ref HEAD --data template={{ template }} --data project_name=demo-project . {{ dest }}
