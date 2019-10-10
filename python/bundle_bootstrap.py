#!/usr/bin/env python3

# Dependencies:
# - DC/OS CLI (specified in Pipfile)


import argparse
import json

import sdk_cmd

from full_bundle import BaseBundleConfiguration


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

    parser.add_argument(
        "--diagnostics-version",
        required=True,
        help="Service diagnostics version.",
    )

    return parser.parse_args()


class BootstrapException(Exception):
    def __init__(self, msg, code: int = 1):
        super().__init__(msg)
        self._code = code

    @property
    def code(self) -> int:
        return self._code


class Bootstrap(BaseBundleConfiguration):

    def __init__(self, logger):
        self._cluster_name = None
        self._clusters = None
        self._package_version = None
        self._dcos_version = None
        self._cluster_url = None
        self._marathon_app = None

        args = parse_args()
        self._package_name = args.package_name
        self._service_name = args.service_name
        self._bundles_directory = args.bundles_directory
        self._should_prompt_user = not args.yes
        self._service_diagnostics_version = args.diagnostics_version

        self.logger = logger

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
        raise BootstrapException(err, rc)

    @staticmethod
    def get_attached_clusters() -> list:
        rc, stdout, stderr = sdk_cmd.run_cli(
            "cluster list --attached --json", print_output=False)

        if rc != 0:
            err = "Unexpected error\nstdout: '{}'\nstderr: '{}'".format(
                stdout, stderr)
            if "No cluster is attached" in stderr:
                err = stderr
            raise BootstrapException(err, rc)

        try:
            return json.loads(stdout)
        except json.JSONDecodeError as e:
            raise BootstrapException("Error decoding JSON while getting attached DC/OS cluster: {}".format(e))

    def get_marathon_app(self, service_name: str):
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
            self.logger.info(
                "We were unable to get details about '%s'.\nIssue: %s",
                service_name,
                stdout,
            )
            self.logger.info((
                "The '%s' scheduler might not be running. That's ok, "
                "we can still try to fetch any artifacts related to it"),
                service_name,
            )

            self.logger.warning(err)

    def validate_package_name(self, defined_package_name: str, marathon_app, service_name: str):
        if marathon_app is None:
            return

        package_name = marathon_app.get("labels", {}).get("DCOS_PACKAGE_NAME")

        if defined_package_name != package_name:
            err = "Package name given '%s' is different than actual '%s' package name: '%s'".format(
                defined_package_name,
                service_name,
                package_name,
            )
            self.logger.info("Try '--package-name=%s'", package_name)
            raise BootstrapException(err)

    def check_attached_cluster(self):
        print("Checking attached DC/OS cluster state...")

        if len(self.clusters) == 1:
            self.logger.info("Attached.")
            return
        elif len(self.clusters) == 0:
            err = "No cluster is attached"
        else:
            err = "More than one attached cluster"
        raise BootstrapException(err)

    def check_authentication(self):
        print("Checking authentication to DC/OS cluster...")

        rc, stdout, stderr = sdk_cmd.run_cli("service", print_output=False)

        if rc == 0:
            self.logger.info("Authenticated.")
            return

        err = "Unexpected error\nstdout: '{}'\nstderr: '{}'".format(stdout, stderr)
        if any(s in stderr for s in ("dcos auth login", "Missing required config parameter")):
            err = "Not authenticated to {}. Please run `dcos auth login`".format(self.cluster_name)
        raise BootstrapException(err)

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
        return self._package_name

    @property
    def service_name(self) -> str:
        return self._service_name

    @property
    def bundles_directory(self) -> str:
        return self._bundles_directory

    @property
    def should_prompt_user(self) -> bool:
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
        return self._service_diagnostics_version
