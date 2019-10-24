#!/bin/bash

## ##############################################################
#%
#% SYNOPSIS
#+    ${SCRIPT_NAME} <service> [<service> ...]
#%
#% DESCRIPTION
#%    Gather DC/OS services diagnostic from specific cluster.
#%
#% ARGUMENTS
#%    <service>    DC/OS service name, e.g., cassandra, elastic
#%
#% EXAMPLES
#%    ${SCRIPT_NAME} cassandra elastic hdfs
#%
#% NOTE
#%    Script can be replaced by direct usage ci_cli.py as on
#%    example below:
#%
#%    $ ci_cli.py --type=diagnostic <service> [<service> ...]
#%
## ##############################################################

# Exit immediately if a command exits with a non-zero status, or zero if all
# commands in the pipeline exit successfully.
set -eu

readonly SCRIPT_DIRECTORY="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null && pwd)"
export TTY_OPTS="-t"

"${SCRIPT_DIRECTORY}"/ci_cli.py --type=diagnostic "$@"
