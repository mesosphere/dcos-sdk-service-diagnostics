#!/usr/bin/env bash

set -e -o pipefail

if [ -z "${CLUSTER_URL}" ]; then
    echo "Error: DC/OS cluster cluster url is not specified. Please, ensure CLUSTER_URL variable is exported in shell environment."
    exit 1
fi

if [ $# -lt 2 ]; then
    echo "Error: DC/OS cluster username or password is not specified. Please, ensure you run the script with paramenters
     'setup_dcos-cli.sh <username> <password>'"
    exit 2
fi

DCOS_USERNAME="$1"
DCOS_PASSWORD="$2"

mkdir ./bin
curl -o ./bin/dcos https://downloads.dcos.io/binaries/cli/linux/x86-64/0.8.0/dcos
chmod +x ./bin/dcos

export PATH=./bin/:$PATH
echo "##teamcity[setParameter name='env.PATH' value='${PATH}']"
echo PATH: "$PATH"

mkdir ./dcos_dir
DCOS_DIR=$(pwd)/dcos_dir
export DCOS_DIR
echo "##teamcity[setParameter name='env.DCOS_DIR' value='${DCOS_DIR}']"

echo "Setup the cluster with dcos-cli - " "${CLUSTER_URL}"
dcos cluster setup \
    --insecure \
    --username="${DCOS_USERNAME}" \
    --password="${DCOS_PASSWORD}" \
    "${CLUSTER_URL}" || true