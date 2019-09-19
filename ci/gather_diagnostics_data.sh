#!/bin/bash
set -eu -o pipefail

export TTY_OPTS="-t"
for service in "$@"; do
    echo "Starting service diagnostics script for ${service}"
    ./python/create_service_diagnostics_bundle.sh \
        --package-name="${service}" \
        --service-name="${service}" \
        --yes || true &
done

wait