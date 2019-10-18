#!/bin/bash

# Exit immediately if a command exits with a non-zero status, or zero if all
# commands in the pipeline exit successfully.
set -eu -o pipefail

# ###
# 1. section: Define script variables
# ###
readonly SCRIPT_DIRECTORY="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null && pwd)"
export TTY_OPTS="-t"

# ###
# 2. section: Run diagnostic for all services
# ###
declare -a PIDS
for service in "$@"; do
    echo "Starting service diagnostics script for ${service}"
    "${SCRIPT_DIRECTORY}"/../python/create_service_diagnostics_bundle.sh \
        --package-name="${service}" \
        --service-name="${service}" \
        --yes &

    # store PID of process
    PIDS[$!]=${service}
done

# ###
# 3. section: Wait for all child processes to finnish and handle error codes
# ###
for PID in "${!PIDS[@]}"; do
  wait "$PID" || (
    echo "Error occurred during service diagnostics script execution for service: ${PIDS[PID]}"
    exit 1
  )
done
