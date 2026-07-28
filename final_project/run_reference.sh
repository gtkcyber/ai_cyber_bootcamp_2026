#!/usr/bin/env bash
# Run the instructor reference solution.
#
# Handles:
#   - symlinking the root .env into the reference dir (if not already there)
#   - cd-ing into the reference tree so imports resolve against its own eval/
#   - forwarding args to the chosen entrypoint
#
# Usage:
#   ./run_reference.sh                        # default: agent run with 100 steps
#   ./run_reference.sh dry-run                # harness --dry-run
#   ./run_reference.sh score                  # harness --report
#   ./run_reference.sh run --max-steps 20     # custom agent args

set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ref_dir="$root_dir/_instructor/reference_solution"

if [[ ! -d "$ref_dir" ]]; then
  echo "Error: reference solution not found at $ref_dir" >&2
  exit 1
fi

if [[ ! -f "$root_dir/.env" ]]; then
  echo "Error: $root_dir/.env not found. Copy .env.example and fill in credentials." >&2
  exit 1
fi

if [[ ! -e "$ref_dir/.env" ]]; then
  ln -s ../../.env "$ref_dir/.env"
  echo "Linked $ref_dir/.env -> ../../.env"
fi

cd "$ref_dir"

mode="${1:-run}"
shift || true

case "$mode" in
  dry-run)
    exec python -m eval.harness --dry-run "$@"
    ;;
  score|report)
    exec python -m eval.harness --report "$@"
    ;;
  json)
    exec python -m eval.harness --json "$@"
    ;;
  run)
    exec python -m agent.main "$@"
    ;;
  *)
    echo "Unknown mode: $mode" >&2
    echo "Usage: $0 [dry-run|score|json|run] [args...]" >&2
    exit 2
    ;;
esac
