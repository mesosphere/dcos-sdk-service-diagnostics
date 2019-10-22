#!/usr/bin/env bash

# Script that gathers SDK-related service diagnostics artifacts.

# Exit immediately if a command exits with a non-zero status, or zero if all
# commands in the pipeline exit successfully.
set -eu -o pipefail

# Script version goes here
readonly VERSION='v0.7.0'

# ###
# section: Check requirements before main execution.
# ###
readonly REQUIREMENTS=("docker" "dcos")

for requirement in ${REQUIREMENTS[*]}; do
  if ! [[ -x $(command -v "${requirement}") ]]; then
    echo "You need to install '${requirement}' to run this script"
  fi
done

# ###
# section: Define readonly variables (script configuration).
# ###
readonly SCRIPT_DIRECTORY="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null && pwd)"
readonly DCOS_SERVICE_DIAGNOSTICS_SCRIPT_PATH="dcos-sdk-service-diagnostics/python"
readonly BUNDLES_DIRECTORY="service-diagnostic-bundles"
readonly PYTHON_SCRIPT_NAME="create_service_diagnostics_bundle.py"

# ###
# section: Define functions.
# ###
function is_development_mode() {
  [[ ${SCRIPT_DIRECTORY} = *${DCOS_SERVICE_DIAGNOSTICS_SCRIPT_PATH} ]]
}

function run_in_container() {
  local TTY_OPTS="${TTY_OPTS:=-it}"
  local DOCKER_IMAGE="mesosphere/dcos-sdk-service-diagnostics:${VERSION}"

  # Docker volumes configuration
  local HOST_DCOS_CLI_DIRECTORY="${DCOS_DIR:-${HOME}/.dcos}"
  local CONTAINER_BUNDLES_DIRECTORY="/${BUNDLES_DIRECTORY}"
  local CONTAINER_DCOS_CLI_DIRECTORY_RO="/dcos-cli-directory"

  docker run \
          "${TTY_OPTS}" \
          --rm \
          -v "$(pwd)/${BUNDLES_DIRECTORY}:${CONTAINER_BUNDLES_DIRECTORY}" \
          -v "${HOST_DCOS_CLI_DIRECTORY}:${CONTAINER_DCOS_CLI_DIRECTORY_RO}":ro \
          ${CONTAINER_DCOS_SERVICE_DIAGNOSTIC_VOLUME_MOUNT} \
          -e PYTHONPATH=${CONTAINER_DCOS_SERVICE_DIAGNOSTICS_DIRECTORY}/dcos-commons/testing:${CONTAINER_DCOS_SERVICE_DIAGNOSTICS_DIRECTORY} \
          "${DOCKER_IMAGE}" \
          sh -l -c "${*:-}"
}

function show_version() {
  echo "${VERSION}"
}

function show_usage() {
  # Show usage instructions.
  run_in_container "./${PYTHON_SCRIPT_NAME} --help"
}

# ###
# section: Defining additional variables dependent on runtime mode.
# ###
if is_development_mode; then
  echo "dcos-sdk-service-diagnostics repository detected,"
  echo "running in development mode"
  echo
  echo "In development mode all Python modules will be picked up from your"
  echo "current dcos-sdk-service-diagnostics repository instead of the Docker"
  echo "image's /dcos-sdk-service-diagnostics-dist directory that contains a"
  echo "static git checkout"
  echo

  # Print a trace of simple commands.
  set -x
  readonly CONTAINER_DCOS_SERVICE_DIAGNOSTICS_DIRECTORY="/dcos-service-diagnostics"
  readonly CONTAINER_DCOS_SERVICE_DIAGNOSTIC_VOLUME_MOUNT="-v ${SCRIPT_DIRECTORY}:${CONTAINER_DCOS_SERVICE_DIAGNOSTICS_DIRECTORY}:ro"
else
  readonly CONTAINER_DCOS_SERVICE_DIAGNOSTICS_DIRECTORY="/dcos-service-diagnostics-dist"

  # We don't mount the /dcos-service-diagnostics directory in the container because the
  # script will use /dcos-sdk-service-diagnostics-dist which is added to the Docker image during
  # build time.
  readonly CONTAINER_DCOS_SERVICE_DIAGNOSTIC_VOLUME_MOUNT=
fi


# ###
# section: Main script execution.
# ###
if [ "${#}" -eq 1 ]; then
  case "$1" in
    --version|-version|version|--v|-v)
      show_version
      exit 0
      ;;
    --help|-help|help|--h|-h)
      show_usage
      exit 0
      ;;
  esac
elif [ "${#}" -eq 0 ]; then
  show_usage
  exit 0
fi

mkdir -p "${BUNDLES_DIRECTORY}"

run_in_container "./${PYTHON_SCRIPT_NAME} ${*} \
              --bundles-directory /${BUNDLES_DIRECTORY} \
              --diagnostics-version ${VERSION}"
