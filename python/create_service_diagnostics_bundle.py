#!/usr/bin/env python3

# Dependencies:
# - DC/OS CLI (specified in requirement.txt)

import argparse
import json
import logging
import os
import sys

from full_bundle import FullBundle
import sdk_cmd

log = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create an SDK service Diagnostics bundle")

    parser.add_argument(
        "--package-name",
        type=str,
        required=True,
        default=None,
        help="The package name for the service to create the bundle for",
    )

    parser.add_argument(
        "--service-name",
        type=str,
        required=True,
        default=None,
        help="The service name to create the bundle for",
    )

    parser.add_argument(
        "--bundles-directory",
        type=str,
        required=True,
        default=None,
        help="The directory where bundles will be written to",
    )

    parser.add_argument(
        "--yes",
        action="store_true",
        help="Disable interactive mode and assume 'yes' is the answer to all prompts.",
    )

    return parser.parse_args()


class ConfigurationException(Exception):
    def __init__(self, msg, code: int = 1):
        super().__init__(msg)
        log.error(msg)
        self._code = code

    @property
    def code(self) -> int:
        return self._code


class Configuration:

    def __init__(self):
        self._cluster_name = None
        self._clusters = None
        self._package_name = None
        self._service_name = None
        self._bundles_directory = None
        self._should_prompt_user = None
        self._package_version = None
        self._dcos_version = None
        self._cluster_url = None
        self._marathon_app = None
        self._service_diagnostics_version = None

    @staticmethod
    def get_cluster_name() -> str:
        rc, stdout, stderr = sdk_cmd.run_cli("config show cluster.name", print_output=False)

        if rc == 0:
            return stdout

        err = "Unexpected error\nstdout: '{}'\nstderr: '{}'".format(stdout, stderr)

        if "Property 'cluster.name' doesn't exist" in stderr:
            err = "No cluster is set up. Please run `dcos cluster setup`\nstdout: '{}'\nstderr: '{}'".format(
                stdout, stderr
            )
        raise ConfigurationException(err, rc)

    @staticmethod
    def get_attached_clusters() -> list:
        rc, stdout, stderr = sdk_cmd.run_cli(
            "cluster list --attached --json", print_output=False)

        if rc != 0:
            err = "Unexpected error\nstdout: '{}'\nstderr: '{}'".format(
                stdout, stderr)
            if "No cluster is attached" in stderr:
                err = stderr
            raise ConfigurationException(err, rc)

        try:
            return json.loads(stdout)
        except json.JSONDecodeError as e:
            raise ConfigurationException("Error decoding JSON while getting attached DC/OS cluster: {}".format(e))

    @staticmethod
    def get_marathon_app(service_name: str):
        rc, stdout, stderr = sdk_cmd.run_cli(
            "marathon app show {}".format(service_name), print_output=False
        )

        if rc == 0:
            try:
                return json.loads(stdout)
            except json.JSONDecodeError as e:
                err = "Error decoding JSON: {}".format(e)
        elif "does not exist" in stderr:
            err = "Service {} does not exist".format(service_name)
        else:
            err = "Unexpected error\nstdout: '{}'\nstderr: '{}'".format(
                stdout, stderr)

        if rc != 0:
            log.info(
                "We were unable to get details about '%s'.\nIssue: %s",
                service_name,
                stdout,
            )
            log.info(
                "Maybe the '%s' scheduler is not running. That's ok, " +
                "we can still try to fetch any artifacts related to it",
                service_name,
            )

        log.warning(err)

    @staticmethod
    def validate_package_name(defined_package_name: str, marathon_app, service_name: str):
        if marathon_app is None:
            return

        package_name = marathon_app.get("labels", {}).get("DCOS_PACKAGE_NAME")

        if defined_package_name != package_name:
            err = "Package name given '%s' is different than actual '%s' package name: '%s'".format(
                defined_package_name,
                service_name,
                package_name,
            )
            log.info("Try '--package-name=%s'", package_name)
            raise ConfigurationException(err)

    def check_cluster_state(self):
        print("Checking attached DC/OS cluster state...")

        clusters = self.clusters
        if len(clusters) == 1:
            return
        elif len(clusters) == 0:
            err = "No cluster is attached"
        else:
            err = "More than one attached clusters"
        raise ConfigurationException(err)

    def check_authentication(self):
        print("Checking authentication to DC/OS cluster...")

        rc, stdout, stderr = sdk_cmd.run_cli("service", print_output=False)

        if rc == 0:
            log.info("Authenticated")
            return

        err = "Unexpected error\nstdout: '{}'\nstderr: '{}'".format(stdout, stderr)
        if any(s in stderr for s in ("dcos auth login", "Missing required config parameter")):
            err = "Not authenticated to {}. Please run `dcos auth login`".format(self.cluster_name)
        raise ConfigurationException(err)

    def load_args(self):
        args = parse_args()

        self._package_name = args.package_name
        self._service_name = args.service_name
        self._bundles_directory = args.bundles_directory
        self._should_prompt_user = not args.yes

    @property
    def cluster_name(self) -> str:
        if self._cluster_name is not None:
            self._cluster_name = self.get_cluster_name()

        return self._cluster_name

    @property
    def clusters(self) -> list:
        if self._clusters is None:
            self._clusters = self.get_attached_clusters()

        return self._clusters

    @property
    def marathon_info(self):
        if self._marathon_app is None:
            self._marathon_app = self.get_marathon_app(self._service_name)
            self.validate_package_name(
                self._package_name, self._marathon_app, self.service_name)

        return self._marathon_app

    @property
    def package_name(self) -> str:
        if self._package_name is None:
            self.load_args()

        return self._package_name

    @property
    def service_name(self) -> str:
        if self._service_name is None:
            self.load_args()

        return self._service_name

    @property
    def bundles_directory(self) -> str:
        if self._bundles_directory is None:
            self.load_args()

        return self._bundles_directory

    @property
    def should_prompt_user(self) -> bool:
        if self._should_prompt_user is None:
            self.load_args()

        return self._should_prompt_user

    @property
    def package_version(self) -> str:
        if self._package_version is None:
            marathon_app = self.marathon_info
            self._package_version = "n/a"
            if marathon_app is not None:
                self._package_version = marathon_app.get("labels", {}).get(
                    "DCOS_PACKAGE_VERSION")

        return self._package_version

    @property
    def dcos_version(self) -> str:
        if self._dcos_version is None:
            self._dcos_version = self.clusters[0]["version"]
        return self._dcos_version

    @property
    def cluster_url(self) -> str:
        if self._cluster_url is None:
            self._cluster_url = self.clusters[0]["url"]
        return self._cluster_url

    @property
    def service_diagnostics_version(self) -> str:
        if self._service_diagnostics_version is None:
            __location__ = os.path.realpath(
                os.path.join(os.getcwd(), os.path.dirname(__file__)))

            with open(os.path.join(__location__, 'VERSION'), 'r') as f:
                self._service_diagnostics_version = f.readline()

        return self._service_diagnostics_version


def main() -> int:
    try:
        config = Configuration()
        config.check_authentication()
        config.check_cluster_state()

        s = "  {:18}{}"
        print("Will create bundle for:")
        print(s.format("Package:", config.package_name))
        print(s.format("Package version:", config.package_version))
        print(s.format("Service name:", config.service_name))
        print(s.format("DC/OS version:", config.dcos_version))
        print(s.format("Cluster URL:", config.cluster_url))

        if config.should_prompt_user:
            answer = input("\nProceed? [Y/n]: ")
            if answer.strip().lower() not in ["yes", "y", ""]:
                return 0

        rc, _ = FullBundle(
            config.package_name, config.service_name, config.bundles_directory,
            config.dcos_version, config.service_diagnostics_version
        ).create()

        return rc
    except ConfigurationException as e:
        return e.code


if __name__ == "__main__":
    sys.exit(main())
