ARG base_image=python:3.7.3-alpine3.9
FROM $base_image

# dcos-cli and lint tooling require this to output cleanly
ENV LC_ALL=C.UTF-8 LANG=C.UTF-8

RUN mkdir /dcos-service-diagnostics-dist

COPY ./base_tech_bundle /dcos-service-diagnostics-dist/base_tech_bundle
COPY ./dcos-commons/testing /dcos-service-diagnostics-dist/dcos-commons/testing
COPY *.py *.sh Pipfile Pipfile.lock /dcos-service-diagnostics-dist/

RUN ls -la /dcos-service-diagnostics-dist

## Here we install GNU libc (aka glibc). This is necessary because dcos-core-cli plugin binary doesn't work on Alpine's Musl libc.
RUN ALPINE_GLIBC_BASE_URL="https://github.com/sgerrand/alpine-pkg-glibc/releases/download" && \
    ALPINE_GLIBC_PACKAGE_VERSION="2.29-r0" && \
    ALPINE_GLIBC_BASE_PACKAGE_FILENAME="glibc-$ALPINE_GLIBC_PACKAGE_VERSION.apk" && \
    ALPINE_GLIBC_BIN_PACKAGE_FILENAME="glibc-bin-$ALPINE_GLIBC_PACKAGE_VERSION.apk" && \
    ALPINE_GLIBC_I18N_PACKAGE_FILENAME="glibc-i18n-$ALPINE_GLIBC_PACKAGE_VERSION.apk" && \
    apk add --no-cache --virtual=.build-dependencies wget ca-certificates && \
    echo \
        "-----BEGIN PUBLIC KEY-----\
        MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEApZ2u1KJKUu/fW4A25y9m\
        y70AGEa/J3Wi5ibNVGNn1gT1r0VfgeWd0pUybS4UmcHdiNzxJPgoWQhV2SSW1JYu\
        tOqKZF5QSN6X937PTUpNBjUvLtTQ1ve1fp39uf/lEXPpFpOPL88LKnDBgbh7wkCp\
        m2KzLVGChf83MS0ShL6G9EQIAUxLm99VpgRjwqTQ/KfzGtpke1wqws4au0Ab4qPY\
        KXvMLSPLUp7cfulWvhmZSegr5AdhNw5KNizPqCJT8ZrGvgHypXyiFvvAH5YRtSsc\
        Zvo9GI2e2MaZyo9/lvb+LbLEJZKEQckqRj4P26gmASrZEPStwc+yqy1ShHLA0j6m\
        1QIDAQAB\
        -----END PUBLIC KEY-----" | sed 's/   */\n/g' > "/etc/apk/keys/sgerrand.rsa.pub" && \
    wget \
        "$ALPINE_GLIBC_BASE_URL/$ALPINE_GLIBC_PACKAGE_VERSION/$ALPINE_GLIBC_BASE_PACKAGE_FILENAME" \
        "$ALPINE_GLIBC_BASE_URL/$ALPINE_GLIBC_PACKAGE_VERSION/$ALPINE_GLIBC_BIN_PACKAGE_FILENAME" \
        "$ALPINE_GLIBC_BASE_URL/$ALPINE_GLIBC_PACKAGE_VERSION/$ALPINE_GLIBC_I18N_PACKAGE_FILENAME" && \
    apk add --no-cache \
        "$ALPINE_GLIBC_BASE_PACKAGE_FILENAME" \
        "$ALPINE_GLIBC_BIN_PACKAGE_FILENAME" \
        "$ALPINE_GLIBC_I18N_PACKAGE_FILENAME" && \
    \
    rm "/etc/apk/keys/sgerrand.rsa.pub" && \
    /usr/glibc-compat/bin/localedef --force --inputfile POSIX --charmap UTF-8 "$LANG" || true && \
    echo "export LANG=$LANG" > /etc/profile.d/locale.sh && \
    \
    apk del glibc-i18n && \
    \
    rm "/root/.wget-hsts" && \
    apk del .build-dependencies && \
    rm \
        "$ALPINE_GLIBC_BASE_PACKAGE_FILENAME" \
        "$ALPINE_GLIBC_BIN_PACKAGE_FILENAME" \
        "$ALPINE_GLIBC_I18N_PACKAGE_FILENAME"

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

RUN pip install --upgrade pip &&\
        pip install pipenv && \
        cd /dcos-service-diagnostics-dist/ &&\
        pipenv install --system
