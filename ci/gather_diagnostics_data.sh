#!/bin/bash
set -eu -o pipefail

if [ -z "${DIAGNOSTICS_TEST_DATA_SERVICES}" ]; then
  echo DcosSdkServiceDiagnostics_TEST_DATA_SERVICES is null or empty.
  exit 1
fi
echo DIAGNOSTICS_TEST_DATA_SERVICES: "${DIAGNOSTICS_TEST_DATA_SERVICES}"

chmod +x ../python/create_service_diagnostics_bundle.sh
mkdir ./logs
export TTY_OPTS="-t"
for service in "${DIAGNOSTICS_TEST_DATA_SERVICES[@]}"; do
    echo "Starting service diagnostics script for ${service}"
    ../python/create_service_diagnostics_bundle.sh \
        --package-name="${service}" \
        --service-name="${service}" \
        --yes || true  >> ./logs/"${service}".log
done