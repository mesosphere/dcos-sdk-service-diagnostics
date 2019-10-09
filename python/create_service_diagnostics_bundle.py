#!/usr/bin/env python3

# Dependencies:
# - DC/OS CLI (specified in requirement.txt)

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

        s = "  {:18}{}"
        print("Will create bundle for:")
        print(s.format("Package:", bootstrap.package_name))
        print(s.format("Package version:", bootstrap.package_version))
        print(s.format("Service name:", bootstrap.service_name))
        print(s.format("DC/OS version:", bootstrap.dcos_version))
        print(s.format("Cluster URL:", bootstrap.cluster_url))

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
