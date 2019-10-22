#!/usr/bin/env python3

import sys

import sdk_install, sdk_cmd
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def main() -> int:
    """
    This function checking authentication and setup DC/OS service

    :return: Execution status
    :rtype: int
    """
    if len(sys.argv) != 2:
        log.error("Script %s support only one argument", sys.argv[0])
        return 1

    service_name = sys.argv[1]
    log.info("Starting %s installation.", service_name)

    try:
        sdk_install.install(
            service_name,
            service_name,
            0,
            package_version=sdk_install.PackageVersion.LATEST_UNIVERSE
        )
    except Exception as e:
        print(str(e))
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
