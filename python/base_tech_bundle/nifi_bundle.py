import logging

import sdk_cmd

from base_tech_bundle import BaseTechBundle
import config

logger = logging.getLogger(__name__)


class NifiBundle(BaseTechBundle):

    def __init__(self, package_name, service_name, scheduler_tasks, service, output_directory):
        super().__init__(package_name,
                         service_name,
                         scheduler_tasks,
                         service,
                         output_directory)

    @config.retry
    def exec_cmd(self, cmd):
        rc, stdout, stderr = sdk_cmd.svc_cli(
            self.cli_subcommand_name, self.service_name, cmd, print_output=False
        )

        if rc != 0:
            logger.error(
                "Could not perform cmd: %s. return-code: '%s'\n"
                "stdout: '%s'\nstderr: '%s'", cmd, rc, stdout, stderr
            )
        else:
            if stderr:
                logger.warning("Non-fatal message for cmd: %s\nstderr: '%s'", cmd, stderr)
            self.write_file("service_" + cmd.replace(" ", "_") + ".json", stdout)

    # list ids of available configurations
    def create_debug_config_list_file(self):
        self.exec_cmd("debug config list")

    # list id of target configuration
    def create_debug_config_target_id_file(self):
        self.exec_cmd("debug config target_id")

    # Display the Mesos framework ID
    def create_debug_state_framework_id_file(self):
        self.exec_cmd("debug state framework_id")

    # List names of all custom properties
    def create_debug_state_properties_file(self):
        self.exec_cmd("debug state properties")

    # View client endpoints
    def create_endpoints_file(self):
        self.exec_cmd("endpoints")


    def create(self):
        logger.info("Creating Nifi bundle")
        self.create_configuration_file()  # this is identical to self.exec_cmd("describe")
        self.create_pod_status_file()     # this is identical to self.exec_cmd("pod status --json")
        self.create_plans_status_files()  # this is identical to plans: self.exec_cmd("plan status <plan> --json")

