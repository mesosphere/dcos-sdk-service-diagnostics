#!/usr/bin/env python3

import sys
from concurrent.futures.thread import ThreadPoolExecutor

import sdk_install
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def install_package(package_name, service_name):
    log.info("Starting %s installation.", package_name)
    sdk_install.install(package_name, service_name, 0, package_version=sdk_install.PackageVersion.LATEST_UNIVERSE)


def main(argv) -> int:
    log.info("Specified data services list: %s", argv[1])
    data_services = argv[1].split(",")
    executor = ThreadPoolExecutor(max_workers=10)
    for data_service in data_services:
        executor.submit(install_package, data_service, data_service)

    executor.shutdown(wait=True)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
