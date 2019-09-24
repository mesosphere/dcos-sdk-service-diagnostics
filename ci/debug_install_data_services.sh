#!/bin/bash
set -eu -o pipefail

readonly HOST_DCOS_CLI_DIRECTORY="${DCOS_DIR:-${HOME}/.dcos}"
readonly SCRIPT_DIRECTORY="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null && pwd)"
readonly VERSION=${VERSION:-$(<"${SCRIPT_DIRECTORY}"/../python/VERSION)}
docker run -it --rm \
  -v "${HOST_DCOS_CLI_DIRECTORY}:/dcos-cli-directory":ro \
  -v "$(pwd)/../python:/dcos-service-diagnostics" \
  -v "$(pwd):/ci" \
  -w "/dcos-service-diagnostics" \
  "mesosphere/dcos-sdk-service-diagnostics:${VERSION}" \
  /ci/install_data_services.py cassandra confluent-kafka confluent-zookeeper datastax-dse datastax-ops elastic hdfs kafka-zookeeper dcos-monitoring
