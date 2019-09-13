#!/usr/bin/env bash

if [ -n "${DCOS_CLI_AUTO_INIT}" ]; then
  echo "Initializing diagnostics..."

  rm -rf /root/.dcos && mkdir /root/.dcos
  pushd "$(pwd)" || exit
  cd /dcos-cli-directory || exit
  find . \
    \( -name 'dcos.toml' -or -name 'attached' \) \
    -exec cp --parents \{\} /root/.dcos \;
  popd || exit

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
fi

export PYTHONPATH=${DCOS_SERVICE_DIAGNOSTICS_DIRECTORY}/dcos-commons/testing:${DCOS_SERVICE_DIAGNOSTICS_DIRECTORY}

exec "$@"
