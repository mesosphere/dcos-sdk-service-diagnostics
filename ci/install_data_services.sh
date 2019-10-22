#!/bin/bash

# Exit immediately if a command exits with a non-zero status, or zero if all
# commands in the pipeline exit successfully.
set -eu

readonly HOST_DCOS_CLI_DIRECTORY="${DCOS_DIR:-${HOME}/.dcos}"
readonly SCRIPT_DIRECTORY="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null && pwd)"
readonly VERSION=$("${SCRIPT_DIRECTORY}"/../python/create_service_diagnostics_bundle.sh -v | tail -1)

if [ "${#}" -eq 0 ]; then
  echo "At least one argument required."
  exit 1
fi

echo "Run container for data service installation: $@"

docker run \
  -t \
  --rm \
  -v "${HOST_DCOS_CLI_DIRECTORY}:/dcos-cli-directory":ro \
  -v "${SCRIPT_DIRECTORY}:/ci" \
  "mesosphere/dcos-sdk-service-diagnostics:${VERSION}" \
  /ci/install_data_services.py "$@"
