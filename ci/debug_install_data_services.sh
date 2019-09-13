#!/bin/bash
set -eu -o pipefail

readonly HOST_DCOS_CLI_DIRECTORY="${DCOS_DIR:-${HOME}/.dcos}"
docker run -it --rm \
  -v "${HOST_DCOS_CLI_DIRECTORY}:/dcos-cli-directory":ro \
  -v "$(pwd)/../python:/dcos-service-diagnostics" \
  -v "$(pwd):/ci" \
  -w "/ci" \
  -e DCOS_SERVICE_DIAGNOSTICS_DIRECTORY=/dcos-service-diagnostics \
  -e DCOS_CLI_AUTO_INIT="yes" \
  "mesosphere/dcos-sdk-service-diagnostics:v0.4.0" \
  ./install_data_services.py 'cassandra,confluent-kafka,confluent-zookeeper,datastax-dse,datastax-ops,elastic,hdfs,kafka-zookeeper,dcos-monitoring'
