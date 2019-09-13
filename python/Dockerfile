ARG base_image=python:3.7.3-slim
FROM $base_image

# dcos-cli and lint tooling require this to output cleanly
ENV LC_ALL=C.UTF-8 LANG=C.UTF-8

ENV DCOS_SERVICE_DIAGNOSTICS_DIRECTORY=/dcos-service-diagnostics-dist
RUN mkdir ${DCOS_SERVICE_DIAGNOSTICS_DIRECTORY}

COPY ./base_tech_bundle ${DCOS_SERVICE_DIAGNOSTICS_DIRECTORY}/base_tech_bundle
COPY ./dcos-commons/testing ${DCOS_SERVICE_DIAGNOSTICS_DIRECTORY}/dcos-commons/testing
COPY *.py *.sh Pipfile Pipfile.lock ${DCOS_SERVICE_DIAGNOSTICS_DIRECTORY}/
COPY entry_point.sh /tmp/

RUN ls -la ${DCOS_SERVICE_DIAGNOSTICS_DIRECTORY}

ARG dcos_cli_version=0.8.0
ADD https://downloads.dcos.io/binaries/cli/linux/x86-64/$dcos_cli_version/dcos /usr/local/bin/dcos
RUN chmod +x /usr/local/bin/dcos

ARG dcos110_core_cli_patch=1
ARG dcos111_core_cli_patch=1
ARG dcos112_core_cli_patch=11
ARG dcos113_core_cli_patch=5
ARG dcos114_core_cli_patch=2
ADD https://downloads.dcos.io/cli/releases/plugins/dcos-core-cli/linux/x86-64/dcos-core-cli-1.10-patch.$dcos110_core_cli_patch.zip /tmp/dcos-core-cli-1.10.zip
ADD https://downloads.dcos.io/cli/releases/plugins/dcos-core-cli/linux/x86-64/dcos-core-cli-1.11-patch.$dcos111_core_cli_patch.zip /tmp/dcos-core-cli-1.11.zip
ADD https://downloads.dcos.io/cli/releases/plugins/dcos-core-cli/linux/x86-64/dcos-core-cli-1.12-patch.$dcos112_core_cli_patch.zip /tmp/dcos-core-cli-1.12.zip
ADD https://downloads.dcos.io/cli/releases/plugins/dcos-core-cli/linux/x86-64/dcos-core-cli-1.13-patch.$dcos113_core_cli_patch.zip /tmp/dcos-core-cli-1.13.zip
ADD https://downloads.dcos.io/cli/releases/plugins/dcos-core-cli/linux/x86-64/dcos-core-cli-1.14-patch.$dcos114_core_cli_patch.zip /tmp/dcos-core-cli-1.14.zip

RUN pip install --upgrade pip && \
        pip install pipenv && \
        cd ${DCOS_SERVICE_DIAGNOSTICS_DIRECTORY} && \
        pipenv install --system

ENV DCOS_CLI_AUTO_INIT=""
ENTRYPOINT ["/tmp/entry_point.sh"]