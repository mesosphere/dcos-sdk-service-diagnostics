#!/bin/bash
set -eu -o pipefail

if [ -z "${DIAGNOSTICS_TEST_DATA_SERVICES}" ]; then
  echo DcosSdkServiceDiagnostics_TEST_DATA_SERVICES var is null or empty.
  exit 1
fi

echo PATH: "${PATH}"
echo DCOS_DIR: "${DCOS_DIR}"
echo DIAGNOSTICS_TEST_DATA_SERVICES: "${DIAGNOSTICS_TEST_DATA_SERVICES}"

for service in "${DIAGNOSTICS_TEST_DATA_SERVICES[@]}"; do
    echo "Installing package '${service}'."
    dcos package install "${service}" --app --yes
done