#!/bin/bash

# Exit immediately if a command exits with a non-zero status, or zero if all
# commands in the pipeline exit successfully.
set -eu

readonly SCRIPT_DIRECTORY="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null && pwd)"
export TTY_OPTS="-t"

"${SCRIPT_DIRECTORY}"/ci_cli.py --type=diagnostic "$@"
