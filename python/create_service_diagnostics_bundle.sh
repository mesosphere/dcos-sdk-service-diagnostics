#!/usr/bin/env bash

set -eu -o pipefail

readonly SCRIPT_DIRECTORY="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null && pwd)"
readonly DCOS_SERVICE_DIAGNOSTICS_SCRIPT_PATH="dcos-sdk-service-diagnostics/python"

readonly VERSION='v0.4.0'

readonly BUNDLES_DIRECTORY="service-diagnostic-bundles"
readonly DOCKER_IMAGE="mesosphere/dcos-sdk-service-diagnostics:${VERSION}"
readonly SCRIPT_NAME="create_service_diagnostics_bundle.py"
readonly HOST_DCOS_CLI_DIRECTORY="${DCOS_DIR:-${HOME}/.dcos}"

readonly CONTAINER_BUNDLES_DIRECTORY="/${BUNDLES_DIRECTORY}"
readonly CONTAINER_DCOS_CLI_DIRECTORY_RO="/dcos-cli-directory"
readonly CONTAINER_DCOS_CLI_DIRECTORY="/root/.dcos"

function is_development_mode() {
  [[ ${SCRIPT_DIRECTORY} = *${DCOS_SERVICE_DIAGNOSTICS_SCRIPT_PATH} ]]
}

if is_development_mode; then
  echo "dcos-sdk-service-diagnostics repository detected,"
  echo "running in development mode"
  echo
  echo "In development mode all Python modules will be picked up from your"
  echo "current dcos-sdk-service-diagnostics repository instead of the Docker"
  echo "image's /dcos-sdk-service-diagnostics-dist directory that contains a"
  echo "static git checkout"
  echo
  set -x
  readonly CONTAINER_DCOS_SERVICE_DIAGNOSTICS_DIRECTORY="/dcos-service-diagnostics"
  readonly CONTAINER_DCOS_SERVICE_DIAGNOSTIC_VOLUME_MOUNT="-v $(pwd):${CONTAINER_DCOS_SERVICE_DIAGNOSTICS_DIRECTORY}:ro"
else
  readonly CONTAINER_DCOS_SERVICE_DIAGNOSTICS_DIRECTORY="/dcos-service-diagnostics-dist"

  # We don't mount the /dcos-service-diagnostics directory in the container because the
  # script will use /dcos-sdk-service-diagnostics-dist which is added to the Docker image during
  # build time.
  readonly CONTAINER_DCOS_SERVICE_DIAGNOSTIC_VOLUME_MOUNT=
fi

readonly CONTAINER_SCRIPT_PATH="${CONTAINER_DCOS_SERVICE_DIAGNOSTICS_DIRECTORY}/${SCRIPT_NAME}"

function version () {
  echo "${VERSION}"
}

if [ "${#}" -eq 1 ] && [[ "${1}" =~ ^(--version|-version|version|--v|-v)$ ]]; then
  version
  exit 0
fi

readonly REQUIREMENTS=('docker' 'dcos')

for requirement in ${REQUIREMENTS}; do
  if ! [[ -x $(command -v "${requirement}") ]]; then
    echo "You need to install '${requirement}' to run this script"
    exit 1
  fi
done

mkdir -p "${BUNDLES_DIRECTORY}"

function container_run () {
  local -r command="${*:-}"
  docker run \
         -t \
         --rm \
         -v "$(pwd)/${BUNDLES_DIRECTORY}:${CONTAINER_BUNDLES_DIRECTORY}" \
         -v "${HOST_DCOS_CLI_DIRECTORY}:${CONTAINER_DCOS_CLI_DIRECTORY_RO}":ro \
         ${CONTAINER_DCOS_SERVICE_DIAGNOSTIC_VOLUME_MOUNT} \
         -e PYTHONPATH=${CONTAINER_DCOS_SERVICE_DIAGNOSTICS_DIRECTORY}/dcos-commons/testing:${CONTAINER_DCOS_SERVICE_DIAGNOSTICS_DIRECTORY} \
         "${DOCKER_IMAGE}" \
         sh -l -c "${command}"
}

function usage () {
  container_run "${CONTAINER_SCRIPT_PATH} --help"
}

if [ "${#}" -eq 1 ] && [[ "${1}" =~ ^(--help|-help|help|--h|-h)$ ]]; then
  usage
  exit 0
fi

echo "Initializing diagnostics..."

DCOS_CLUSTER_MAJOR_MINOR_VERSION=$(dcos --version | awk -F"=" '/^dcos.version=/ {split($2,verPart,".");print verPart[1]"."verPart[2]}')
echo "Detected attached DC/OS cluster major and minor version as '${DCOS_CLUSTER_MAJOR_MINOR_VERSION}'"

readonly SUPPORTED_DCOS_VERSIONS="
1.10
1.11
1.12
1.13
1.14"
if ! echo "${SUPPORTED_DCOS_VERSIONS}" | grep -qx "${DCOS_CLUSTER_MAJOR_MINOR_VERSION}"; then
  echo "DC/OS ${DCOS_CLUSTER_MAJOR_MINOR_VERSION}.x is not supported by this tool."
  echo "Supported DC/OS versions: ${DCOS_CLUSTER_MAJOR_MINOR_VERSION}."
  exit 1
fi

container_run "rm -rf ${CONTAINER_DCOS_CLI_DIRECTORY} && mkdir ${CONTAINER_DCOS_CLI_DIRECTORY}
               cd ${CONTAINER_DCOS_CLI_DIRECTORY_RO}
               find . \
                 \( -name 'dcos.toml' -or -name 'attached' \) \
                 -exec cp --parents \{\} ${CONTAINER_DCOS_CLI_DIRECTORY} \;
               cd /
               dcos plugin add /tmp/dcos-core-cli-${DCOS_CLUSTER_MAJOR_MINOR_VERSION}.zip
               ${CONTAINER_SCRIPT_PATH} ${*} --bundles-directory ${CONTAINER_BUNDLES_DIRECTORY}"
