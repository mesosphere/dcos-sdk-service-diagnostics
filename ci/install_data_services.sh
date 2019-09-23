#!/bin/bash
set -eu -o pipefail

readonly HOST_DCOS_CLI_DIRECTORY="${DCOS_DIR:-${HOME}/.dcos}"
readonly BUILD_IMAGE_VERSION=${BUILD_IMAGE_VERSION:-$(<VERSION)}
docker run \
  -t \
  --rm \
  -v "${HOST_DCOS_CLI_DIRECTORY}:/dcos-cli-directory":ro \
  -v "$(pwd)/ci:/ci" \
  "mesosphere/dcos-sdk-service-diagnostics:${BUILD_IMAGE_VERSION}" \
  /ci/install_data_services.py "$@"
