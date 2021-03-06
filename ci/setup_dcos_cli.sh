#!/bin/bash

## ##############################################################
#%
#% SYNOPSIS
#+    ${SCRIPT_NAME} <username> <password>
#%
#% DESCRIPTION
#%    Set up the CLI to communicate with a DC/OS cluster.
#%
#% ARGUMENTS
#%    <username>    the username for DC/OS login.
#%    <password>    the password in the command line (insecure)
#%
#% EXAMPLES
#%    ${SCRIPT_NAME} root swordfish
#%
#% NOTE
#%    Make sure that the CLUSTER_URL environment variable was
#%    exported.
#%
## ##############################################################

# Exit immediately if a command exits with a non-zero status, or zero if all
# commands in the pipeline exit successfully.
set -eu

# ###
# section: Check input params and environment.
# ###
if [ -z "${CLUSTER_URL}" ]; then
  echo "Error: DC/OS cluster URL is not specified. Please make sure that the CLUSTER_URL environment variable is exported." >&2
  exit 1
fi

if [ $# -lt 2 ]; then
  BASENAME=`basename "$0"`
  echo "Error: DC/OS cluster username or password is not specified. Please, ensure you run the script with parameters
    '${BASENAME} <username> <password>'" >&2
  exit 2
fi

DCOS_USERNAME="$1"
DCOS_PASSWORD="$2"

# ###
# section: Prepare DC/OS CLI.
# ###
mkdir ./bin
# Assume that script will be executed from linux x86-64 OS.
curl -o ./bin/dcos https://downloads.dcos.io/binaries/cli/linux/x86-64/0.8.0/dcos
chmod +x ./bin/dcos

export PATH=./bin/:$PATH
echo "##teamcity[setParameter name='env.PATH' value='${PATH}']"
echo PATH: "$PATH"

mkdir ./dcos_dir
DCOS_DIR=$(pwd)/dcos_dir
export DCOS_DIR
echo "##teamcity[setParameter name='env.DCOS_DIR' value='${DCOS_DIR}']"

# ###
# section: Setup DC/OS cluster.
# ###
echo "Setup the cluster with dcos-cli - " "${CLUSTER_URL}"
dcos cluster setup \
  --insecure \
  --username="${DCOS_USERNAME}" \
  --password="${DCOS_PASSWORD}" \
  "${CLUSTER_URL}"
