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

# ###
# 2. section: Define functions.
# ###
function install_service() {
  echo "Run container for data service installation: $@"

  docker run \
    -t \
    --rm \
    -v "${HOST_DCOS_CLI_DIRECTORY}:/dcos-cli-directory":ro \
    -v "${SCRIPT_DIRECTORY}:/ci" \
    "mesosphere/dcos-sdk-service-diagnostics:${VERSION}" \
    /ci/install_data_services.py "$@"
}

function install_services() {
  echo "Install DC/OS services: $@"

  declare -a PIDS

  # Run installation for all services.
  for service in "$@"; do
    install_service ${service} &

    # store PID of process
    PIDS[$!]=${service}
  done

  # Wait for all child processes to finish and handle error codes.
  for PID in "${!PIDS[@]}"; do
    wait "$PID" || (
      echo "Error occurred during service installation: ${PIDS[PID]}" >&2
      exit 1
    )
  done
}

# ###
# 3. section: Main script execution.
# ###
if [ "${#}" -eq 1 ] && [ "$1" == "--debug" ]; then
  eval "${SCRIPT_DIRECTORY}/$(basename $0) cassandra confluent-kafka confluent-zookeeper datastax-dse datastax-ops elastic hdfs kafka-zookeeper dcos-monitoring"
else
  install_services $@
fi
