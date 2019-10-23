#!/usr/bin/env python3

import argparse
import logging
import os
import subprocess
import sys

from concurrent import futures

MAX_WORKERS = 10

JOB_TYPE_INSTALL = 'install'
JOB_TYPE_DIAGNOSTIC = 'diagnostic'

JOB_TYPES = [JOB_TYPE_INSTALL, JOB_TYPE_DIAGNOSTIC]

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def install(service_name):
    import sdk_install

    log.info("Starting %s installation.", service_name)

    sdk_install.install(
        service_name,
        service_name,
        0,
        package_version=sdk_install.PackageVersion.LATEST_UNIVERSE
    )


def diagnostic(service_name):
    log.info("Starting %s diagnostic.", service_name)

    script_under_test = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'python', 'create_service_diagnostics_bundle.sh'
    )

    cmd = [
        script_under_test,
        "--package-name={service}".format(service=service_name),
        "--service-name={service}".format(service=service_name),
        "--yes"]

    subprocess.check_call(cmd)


def get_args() -> (str, list):
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--type",
        choices=JOB_TYPES,
        required=True,
        help='Job type'
    )

    parser.add_argument(
        'services',
        nargs='+',
        default='',
        help='Services list'
    )
    args = parser.parse_args()

    jobs = {
        JOB_TYPE_INSTALL: install,
        JOB_TYPE_DIAGNOSTIC: diagnostic,
    }

    return args.type, jobs[args.type], args.services


def main() -> int:
    """
    :param func: CI function for loop execution

    :param services: DC/OS services list
    :type services: list

    :return: exit code
    :rtype: int
    """

    val, func, services = get_args()

    result = 0
    # Statement to ensure threads are cleaned up promptly
    with futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        threads = {pool.submit(func, service) for service in services}
        for thread in futures.as_completed(threads):
            try:
                thread.result()
            except Exception:
                log.error("Execution failed: {}".format(val))
                result = 1

    return result


if __name__ == "__main__":
    sys.exit(main())
