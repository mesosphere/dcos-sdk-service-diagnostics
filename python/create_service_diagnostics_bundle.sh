#!/usr/bin/env bash

set -eu -o pipefail

readonly SCRIPT_DIRECTORY="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null && pwd)"
readonly DCOS_SERVICE_DIAGNOSTICS_SCRIPT_PATH="dcos-sdk-service-diagnostics/python"

readonly VERSION='v0.3.2'

readonly BUNDLES_DIRECTORY="service-diagnostic-bundles"
readonly DOCKER_IMAGE="mesosphere/dcos-sdk-service-diagnostics:${VERSION}"
readonly SCRIPT_NAME="create_service_diagnostics_bundle.py"

readonly HOST_DCOS_CLI_DIRECTORY="${HOME}/.dcos"

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
         -it \
         --rm \
         -v "$(pwd)/${BUNDLES_DIRECTORY}:${CONTAINER_BUNDLES_DIRECTORY}" \
         -v "${HOME}/.dcos:${CONTAINER_DCOS_CLI_DIRECTORY_RO}":ro \
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

HOST_DCOS_CLI_MAJOR_VERSION=$(dcos --version | grep dcoscli.version | awk -F"=" '{split($2,verPart,".");print verPart[1]"."verPart[2]}')
echo "Host's dcos-cli major version is ${HOST_DCOS_CLI_MAJOR_VERSION}"

DCOS_CLUSTER_MAJOR_VERSION=$(dcos --version | grep dcos.version | awk -F"=" '{split($2,verPart,".");print verPart[1]"."verPart[2]}')
echo "Lincked DC/OS cluster major version is ${DCOS_CLUSTER_MAJOR_VERSION}"
readonly DCOS_TO_CLI_COMPATIBILITY="
1.10 0.5
1.11 0.6
1.12 0.7
1.13 0.8"

DCOS_CLI_COMPATIBLE_VERSION=$(echo "${DCOS_TO_CLI_COMPATIBILITY}" | grep  "${DCOS_CLUSTER_MAJOR_VERSION}" | awk '{print $2}')
echo "dcos-cli compatible version for DC/OS ${DCOS_CLUSTER_MAJOR_VERSION}.x is ${DCOS_CLI_COMPATIBLE_VERSION}.x"

if [ "${HOST_DCOS_CLI_MAJOR_VERSION}" != "${DCOS_CLI_COMPATIBLE_VERSION}" ]; then
  echo "Warning! Installed dcoscli version is NOT compatible with attached DC/OS cluster version.
  Please, take care of install dcos-cli ${DCOS_CLI_COMPATIBLE_VERSION}.x"
  exit 1;
fi;


container_run "rm -rf ${CONTAINER_DCOS_CLI_DIRECTORY} && mkdir ${CONTAINER_DCOS_CLI_DIRECTORY}
               cd ${CONTAINER_DCOS_CLI_DIRECTORY_RO}
               find . \
                 \( -name 'dcos.toml' -or -name 'attached' \) \
                 -exec cp --parents \{\} ${CONTAINER_DCOS_CLI_DIRECTORY} \;
               cd /
               rm -f /usr/local/bin/dcos && ln -s /usr/local/bin/dcos${HOST_DCOS_CLI_MAJOR_VERSION} /usr/local/bin/dcos
               ${CONTAINER_SCRIPT_PATH} ${*} --bundles-directory ${CONTAINER_BUNDLES_DIRECTORY}"
