#!/bin/bash
set -eu -o pipefail

readonly HOST_DCOS_CLI_DIRECTORY="${DCOS_DIR:-${HOME}/.dcos}"
#ToDo: Once the image version will be manageble dont forget replace it here.
docker run -it --rm \
  -v "${HOST_DCOS_CLI_DIRECTORY}:/dcos-cli-directory":ro \
  -v "$(pwd)/../python:/dcos-service-diagnostics" \
  -v "$(pwd):/ci" \
  -w "/dcos-service-diagnostics" \
  "mesosphere/dcos-sdk-service-diagnostics:v0.4.0" \
  /ci/install_data_services.py cassandra confluent-kafka confluent-zookeeper datastax-dse datastax-ops elastic hdfs kafka-zookeeper dcos-monitoring
