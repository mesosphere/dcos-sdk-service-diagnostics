#!/bin/bash
set -eu -o pipefail

readonly SCRIPT_DIRECTORY="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null && pwd)"
export TTY_OPTS="-t"
for service in "$@"; do
    echo "Starting service diagnostics script for ${service}"
    "${SCRIPT_DIRECTORY}"/../python/create_service_diagnostics_bundle.sh \
        --package-name="${service}" \
        --service-name="${service}" \
        --yes || true &
done

wait
