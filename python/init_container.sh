#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status, or zero if all
# commands in the pipeline exit successfully.
set -e

# ###
# 1. section: Define functions
# ###
function initialize() {
  echo "Initializing diagnostics..."

  rm -rf /root/.dcos && mkdir /root/.dcos
  cd /dcos-cli-directory || exit
  find . \
    \( -name 'dcos.toml' -or -name 'attached' \) \
    -exec cp --parents \{\} /root/.dcos \;
  cd - || exit

  DCOS_CLUSTER_MAJOR_MINOR_VERSION=$(dcos --version | awk -F"=" '/^dcos.version=/ {split($2,verPart,".");print verPart[1]"."verPart[2]}')
  echo "Detected attached DC/OS cluster major and minor version as '${DCOS_CLUSTER_MAJOR_MINOR_VERSION}'"

  readonly SUPPORTED_DCOS_VERSIONS="
1.10
1.11
1.12
1.13
1.14"
  if ! echo "${SUPPORTED_DCOS_VERSIONS}" | grep -qx "${DCOS_CLUSTER_MAJOR_MINOR_VERSION}"; then
    echo "DC/OS ${DCOS_CLUSTER_MAJOR_MINOR_VERSION}.x is not supported by this tool."
    echo "Supported DC/OS versions: ${SUPPORTED_DCOS_VERSIONS}."
    exit 1
  fi

  dcos plugin add /tmp/dcos-core-cli-"${DCOS_CLUSTER_MAJOR_MINOR_VERSION}".zip
}

function is_help() {
    # Check is help mode
    if [ "${#}" -eq 1 ]; then
        case "$1" in
            --help|-help|help|--h|-h)
                echo "YES"
                ;;
        esac
    fi
}

# ###
# 2. section: Main script execution
# ###
if [ -z "$(is_help $@)" ]; then initialize; fi

exec "$@"
