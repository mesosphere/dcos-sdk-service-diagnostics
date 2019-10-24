#!/bin/bash

## ##############################################################
#%
#% SYNOPSIS
#+    ${SCRIPT_NAME} <service> [<service> ...]
#%
#% DESCRIPTION
#%    Bulk installation required for DC/OS services in parallel.
#%
#% ARGUMENTS
#%    <service>    DC/OS service name, e.g., cassandra, elastic
#%
#% EXAMPLES
#%    ${SCRIPT_NAME} cassandra elastic hdfs
#%
#% NOTE
#%    Before run script user needs to run set up to communicate
#%    with a DC/OS cluster.
#%
## ##############################################################

# Exit immediately if a command exits with a non-zero status, or zero if all
# commands in the pipeline exit successfully.
set -eu

readonly HOST_DCOS_CLI_DIRECTORY="${DCOS_DIR:-${HOME}/.dcos}"
readonly SCRIPT_DIRECTORY="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null && pwd)"
readonly VERSION=$("${SCRIPT_DIRECTORY}"/../python/create_service_diagnostics_bundle.sh -v | tail -1)

docker run \
  -t \
  --rm \
  -v "${HOST_DCOS_CLI_DIRECTORY}:/dcos-cli-directory":ro \
  -v "${SCRIPT_DIRECTORY}:/ci" \
  "mesosphere/dcos-sdk-service-diagnostics:${VERSION}" \
  /ci/ci_cli.py --type=install "$@"
