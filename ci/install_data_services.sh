#!/bin/bash
set -eu -o pipefail

readonly HOST_DCOS_CLI_DIRECTORY="${DCOS_DIR:-${HOME}/.dcos}"
docker run \
  -t \
  --rm \
  -v "${HOST_DCOS_CLI_DIRECTORY}:/dcos-cli-directory":ro \
  -v "$(pwd)/ci:/ci" \
  "mesosphere/dcos-sdk-service-diagnostics:v0.4.0" \
  /ci/install_data_services.py "$@"
