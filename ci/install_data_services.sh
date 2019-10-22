#!/bin/bash

# Exit immediately if a command exits with a non-zero status, or zero if all
# commands in the pipeline exit successfully.
set -eu -o pipefail

# ###
# 1. section: Define script variables.
# ###
readonly HOST_DCOS_CLI_DIRECTORY="${DCOS_DIR:-${HOME}/.dcos}"
readonly SCRIPT_DIRECTORY="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null && pwd)"
readonly VERSION=$("${SCRIPT_DIRECTORY}"/../python/create_service_diagnostics_bundle.sh -v | tail -1)

echo "Run container for data service installation: $@"

docker run \
  -t \
  --rm \
  -v "${HOST_DCOS_CLI_DIRECTORY}:/dcos-cli-directory":ro \
  -v "${SCRIPT_DIRECTORY}:/ci" \
  "mesosphere/dcos-sdk-service-diagnostics:${VERSION}" \
  /ci/install_data_services.py "$@"
