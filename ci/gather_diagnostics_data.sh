#!/bin/bash
set -eu -o pipefail

echo "Services list: $1"

IFS=',' read -ra SERVICES <<< "$1"

if [ -z "${SERVICES}" ]; then
  echo SERVICES is null or empty.
  exit 1
fi

chmod +x ./python/create_service_diagnostics_bundle.sh
export TTY_OPTS="-t"
for service in "${SERVICES[@]}"; do
    echo "Starting service diagnostics script for ${service}"
    ./python/create_service_diagnostics_bundle.sh \
        --package-name="${service}" \
        --service-name="${service}" \
        --yes || true &
done

wait