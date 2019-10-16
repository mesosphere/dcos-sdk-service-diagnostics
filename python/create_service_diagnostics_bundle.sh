#!/usr/bin/env bash

set -eu -o pipefail

readonly SCRIPT_DIRECTORY="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null && pwd)"
readonly DCOS_SERVICE_DIAGNOSTICS_SCRIPT_PATH="dcos-sdk-service-diagnostics/python"

readonly VERSION='v0.7.0'

readonly BUNDLES_DIRECTORY="service-diagnostic-bundles"
readonly DOCKER_IMAGE="mesosphere/dcos-sdk-service-diagnostics:${VERSION}"
readonly SCRIPT_NAME="create_service_diagnostics_bundle.py"
readonly TTY_OPTS="${TTY_OPTS:=-it}"

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
  readonly CONTAINER_DCOS_SERVICE_DIAGNOSTIC_VOLUME_MOUNT="-v ${SCRIPT_DIRECTORY}:/dcos-service-diagnostics:ro"
  readonly CONTAINER_DCOS_SERVICE_DIAGNOSTIC_WORKDIR="-w /dcos-service-diagnostics"
fi

function version() {
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
         "${TTY_OPTS}" \
         --rm \
         -v "$(pwd)/${BUNDLES_DIRECTORY}:/${BUNDLES_DIRECTORY}" \
         -v "${DCOS_DIR:-${HOME}/.dcos}:/dcos-cli-directory":ro \
         ${CONTAINER_DCOS_SERVICE_DIAGNOSTIC_VOLUME_MOUNT:-""} \
         ${CONTAINER_DCOS_SERVICE_DIAGNOSTIC_WORKDIR:-""} \
         -e SKIP_DCOS_CLI_INIT="${SKIP_DCOS_CLI_INIT:-""}" \
         "${DOCKER_IMAGE}" \
         sh -l -c "${command}"
}

function usage () {
  SKIP_DCOS_CLI_INIT="yes"
  container_run "./${SCRIPT_NAME} --help"
}

if [ "${#}" -eq 1 ] && [[ "${1}" =~ ^(--help|-help|help|--h|-h)$ ]]; then
  usage
  exit 0
fi

container_run "./${SCRIPT_NAME} ${*} --bundles-directory /${BUNDLES_DIRECTORY}"
