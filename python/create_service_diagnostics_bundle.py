#!/usr/bin/env python3

# Dependencies:
# - DC/OS CLI (specified in Pipfile)

import logging
import sys

from full_bundle import FullBundle
from bundle_bootstrap import Bootstrap, BootstrapException

log = logging.getLogger(__name__)


def main() -> int:
    try:
        bootstrap = Bootstrap(log)
        bootstrap.check_authentication()
        bootstrap.check_attached_cluster()

        info = {
            "Package": bootstrap.package_name,
            "Package version": bootstrap.package_version,
            "Service name": bootstrap.service_name,
            "DC/OS version": bootstrap.dcos_version,
            "Cluster URL": bootstrap.cluster_url,
        }

        print("Will create bundle for:")
        for title, val in info.items():
            print("  {:18}{}".format(title + ":", val))

        if bootstrap.should_prompt_user:
            answer = input("\nProceed? [Y/n]: ")
            if answer.strip().lower() not in ["yes", "y", ""]:
                return 0

        rc, _ = FullBundle(bootstrap).create()

        return rc
    except BootstrapException as e:
        log.error(str(e))
        return e.code


if __name__ == "__main__":
    sys.exit(main())
