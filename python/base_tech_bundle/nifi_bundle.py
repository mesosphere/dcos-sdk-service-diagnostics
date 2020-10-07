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
        self.short_toolkit_cmd = ""
        self.base_url = "http://node-http.nifi.l4lb.thisdcos.directory:8080"

    @config.retry
    def task_exec(self, task_id, cmd):
        full_cmd = " ".join(
            [
                "export JAVA_HOME=$(ls -d ${MESOS_SANDBOX}/jdk*/) &&",
                "export TASK_IP=$(${MESOS_SANDBOX}/bootstrap --get-task-ip) &&",
                "TOOLKIT_DIR=$(ls -d ${MESOS_SANDBOX}/nifi-toolkit-*/) &&",
                cmd,
            ]
        )

        return sdk_cmd.marathon_task_exec(task_id, "bash -c '{}'".format(full_cmd))

    def create_cli_output_file(self, task_id):
        cmd = self.short_toolkit_cmd
        full_toolkit_cmd = "${TOOLKIT_DIR}/bin/cli.sh {} -u {}".format(cmd, self.base_url)
        rc, stdout, stderr = self.task_exec(task_id, full_toolkit_cmd)

        if rc != 0:
            logger.error(
                "Could not perform Nifi toolkit cmd: %s. return-code: '%s'\n"
                "stdout: '%s'\nstderr: '%s'", full_toolkit_cmd, rc, stdout, stderr
            )
        else:
            if stderr:
                logger.warning("Non-fatal message for Nifi toolkit cmd: %s\nstderr: '%s'", full_toolkit_cmd, stderr)
            self.write_file(("nifi_toolkit_" + cmd.replace(" ", "_") + "_{}.txt").format(task_id), stdout)

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
            self.write_file("nifi_" + cmd.replace(" ", "_") + ".json", stdout)

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

    # View plans
    def create_plan_list_file(self):
        self.exec_cmd("plan list")

    # Execute diagnostic commands on each Nifi's data node by selecting tasks like 'nifi-0-node', 'nifi-1-node', etc
    # By default, Nifi toolkit is available on each such node.
    def create_tasks_toolkit_output_files(self):
        self.short_toolkit_cmd = "nifi cluster-summary"
        self.for_each_running_task_with_suffix("-node", self.create_cli_output_file)
        self.short_toolkit_cmd = "nifi get-root-id"
        self.for_each_running_task_with_suffix("-node", self.create_cli_output_file)
        self.short_toolkit_cmd = "nifi get-nodes"
        self.for_each_running_task_with_suffix("-node", self.create_cli_output_file)
        self.short_toolkit_cmd = "nifi list-reg-clients"
        self.for_each_running_task_with_suffix("-node", self.create_cli_output_file)
        self.short_toolkit_cmd = "nifi get-services"
        self.for_each_running_task_with_suffix("-node", self.create_cli_output_file)
        self.short_toolkit_cmd = "nifi get-reporting-tasks"
        self.for_each_running_task_with_suffix("-node", self.create_cli_output_file)
        self.short_toolkit_cmd = "nifi pg-list"
        self.for_each_running_task_with_suffix("-node", self.create_cli_output_file)
        self.short_toolkit_cmd = "nifi list-users"
        self.for_each_running_task_with_suffix("-node", self.create_cli_output_file)
        self.short_toolkit_cmd = "nifi list-templates"
        self.for_each_running_task_with_suffix("-node", self.create_cli_output_file)

    def create(self):
        logger.info("Creating Nifi bundle")
        self.create_configuration_file()  # this is identical to self.exec_cmd("describe")
        self.create_pod_status_file()     # this is identical to self.exec_cmd("pod status --json")
        self.create_plans_status_files()  # this is identical to plans: self.exec_cmd("plan status <plan> --json")
        # run dcos nifi package's diagnostic commands
        self.create_debug_config_list_file()
        self.create_debug_config_target_id_file()
        self.create_debug_state_framework_id_file()
        self.create_debug_state_properties_file()
        self.create_endpoints_file()
        self.create_plan_list_file()
        # run nifi toolkit's diagnostic commands
        self.create_tasks_toolkit_output_files()
        # download nifi log files like nifi-app.log, nifi-bootstrap.log, nifi-user.log, etc.
        self.download_task_log_files(
            self.get_tasks_with_suffix("-node", self.tasks()), ["^nifi-.*\\.log$"]
        )

