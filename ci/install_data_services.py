#!/usr/bin/env python3

import sys

import sdk_install, sdk_cmd
import logging

from concurrent import futures

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

MAX_WORKERS=10


def install_package(service_name):
    """
    :param service_name: DC/OS service name
    :type service_name: str
    """
    log.info("Starting %s installation.", service_name)
    package_name = service_name

    sdk_install.install(
        package_name,
        service_name,
        0,
        package_version=sdk_install.PackageVersion.LATEST_UNIVERSE
    )


def main(args) -> int:
    """
    This function setup DC/OS service

    :param args: CLI arguments
    :type args: list

    :return: Execution status
    :rtype: list
    """
    log.info("Starting %s installation.", ' '.join(args))

    result = 0
    # Statement to ensure threads are cleaned up promptly
    with futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        threads = {pool.submit(install_package, service) for service in args}
        for thread in futures.as_completed(threads):
            try:
                thread.result()
            except Exception as e:
                log.error(str(e))
                result = 1

    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        log.error("At least one argument required.")
        sys.exit(1)

    sys.exit(main(sys.argv[1:]))
