FROM python:3.7.3-slim

# dcos-cli and lint tooling require this to output cleanly
ENV LC_ALL=C.UTF-8 LANG=C.UTF-8

RUN mkdir /dcos-service-diagnostics-dist

COPY ./base_tech_bundle /dcos-service-diagnostics-dist/base_tech_bundle
COPY ./dcos-commons/testing /dcos-service-diagnostics-dist/dcos-commons/testing
COPY *.py *.sh Pipfile Pipfile.lock /dcos-service-diagnostics-dist/

RUN ls -la /dcos-service-diagnostics-dist

ARG dcos_cli_version=1.0.1
ADD https://downloads.dcos.io/binaries/cli/linux/x86-64/$dcos_cli_version/dcos /usr/local/bin/dcos
RUN chmod +x /usr/local/bin/dcos

ARG dcos110_core_cli_patch=1
ARG dcos111_core_cli_patch=1
ARG dcos112_core_cli_patch=11
ARG dcos113_core_cli_patch=6
ARG dcos114_core_cli_patch=4
ARG dcos2_core_cli_patch=2
ADD https://downloads.dcos.io/cli/releases/plugins/dcos-core-cli/linux/x86-64/dcos-core-cli-1.10-patch.$dcos110_core_cli_patch.zip /tmp/dcos-core-cli-1.10.zip
ADD https://downloads.dcos.io/cli/releases/plugins/dcos-core-cli/linux/x86-64/dcos-core-cli-1.11-patch.$dcos111_core_cli_patch.zip /tmp/dcos-core-cli-1.11.zip
ADD https://downloads.dcos.io/cli/releases/plugins/dcos-core-cli/linux/x86-64/dcos-core-cli-1.12-patch.$dcos112_core_cli_patch.zip /tmp/dcos-core-cli-1.12.zip
ADD https://downloads.dcos.io/cli/releases/plugins/dcos-core-cli/linux/x86-64/dcos-core-cli-1.13-patch.$dcos113_core_cli_patch.zip /tmp/dcos-core-cli-1.13.zip
ADD https://downloads.dcos.io/cli/releases/plugins/dcos-core-cli/linux/x86-64/dcos-core-cli-1.14-patch.$dcos114_core_cli_patch.zip /tmp/dcos-core-cli-1.14.zip
ADD https://downloads.dcos.io/cli/releases/plugins/dcos-core-cli/linux/x86-64/dcos-core-cli-2.0-patch.$dcos2_core_cli_patch.zip /tmp/dcos-core-cli-2.0.zip

RUN pip install --upgrade pip &&\
        pip install pipenv && \
        cd /dcos-service-diagnostics-dist/ &&\
        pipenv install --system
