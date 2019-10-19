#!/usr/bin/env python3

import sys

import sdk_install, sdk_cmd
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# TODO get_cluster_name and check_authentication functions in duplicate from bundle_bootstrap.py
#      this functions MUST be moved in one place after refactoring


def get_cluster_name() -> str:
    rc, stdout, stderr = sdk_cmd.run_cli("config show cluster.name", print_output=False)

    if rc == 0:
        return stdout

    err = "Unexpected error\nstdout: '{}'\nstderr: '{}'".format(stdout, stderr)

    if "Property 'cluster.name' doesn't exist" in stderr:
        err = "No cluster is set up. Please run `dcos cluster setup`\nstdout: '{}'\nstderr: '{}'".format(
            stdout, stderr
        )
    raise Exception(err)


def check_authentication():
    print("Checking authentication to DC/OS cluster...")
    rc, stdout, stderr = sdk_cmd.run_cli("service", print_output=False)

    if rc == 0:
        log.info("Authenticated.")
        return

    err = "Unexpected error\nstdout: '{}'\nstderr: '{}'".format(stdout, stderr)
    if any(s in stderr for s in ("dcos auth login", "Missing required config parameter")):
        err = "Not authenticated to {}. Please run `dcos auth login`".format(get_cluster_name())

    raise Exception(err)


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
        check_authentication()

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
