#!/bin/bash
set -eu -o pipefail

mkdir ./bin
curl -o ./bin/dcos https://downloads.dcos.io/binaries/cli/linux/x86-64/0.8.0/dcos
chmod +x ./bin/dcos

export PATH=./bin/:$PATH
echo "##teamcity[setParameter name='env.PATH' value='${PATH}']"
echo PATH: "$PATH"

mkdir ./dcos_dir
export DCOS_DIR=./dcos_dir
echo "##teamcity[setParameter name='env.DCOS_DIR' value='${DCOS_DIR}']"

readonly USERNAME=bootstrapuser
readonly PASSWORD=deleteme

echo "Setup the cluster with dcos-cli - " "${CLUSTER_URL}"
dcos cluster setup \
    --insecure \
    --username="${USERNAME}" \
    --password="${PASSWORD}" \
    "${CLUSTER_URL}" || true